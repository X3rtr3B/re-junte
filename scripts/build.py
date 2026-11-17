"""Construye docs/; asigna tokens únicamente a las filas nuevas."""
import argparse
import json
import secrets
import shutil
import tempfile
from pathlib import Path
from html import escape
from common import ROOT, load, validate_data, write_guests


def build(root=ROOT):
    root = Path(root)
    event, guests = load(root)
    validate_data(event, guests, allow_missing_ids=True)
    used = {g['id'] for g in guests if g['id']}
    new = 0
    for guest in guests:
        if not guest['id']:
            token = secrets.token_urlsafe(18)
            while token in used:
                token = secrets.token_urlsafe(18)
            guest['id'] = token
            used.add(token)
            new += 1
    validate_data(event, guests)
    # Persistir antes de producir el sitio: nunca dejar enlaces sin correspondencia.
    if new:
        write_guests(guests, root)
    warnings = []
    if event['video_habilitado'] and not (root / 'src' / event['video_archivo']).is_file():
        warnings.append('Video habilitado pero archivo ausente: se mantiene el acceso a la invitación.')
    with tempfile.TemporaryDirectory(dir=root, prefix='.build-') as temp:
        stage = Path(temp) / 'docs'
        shutil.copytree(root / 'src', stage, ignore=shutil.ignore_patterns('README.md'))
        payload = {'evento': event, 'invitados': guests}
        serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True).replace('<', '\\u003c').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
        (stage / 'data.js').write_text('window.REJUNTE = ' + serialized + ';\n', encoding='utf-8')
        index = (stage / 'index.html').read_text(encoding='utf-8')
        metadata = ''
        if event.get('url_publica'):
            base = event['url_publica'].rstrip('/') + '/'
            metadata = f'<meta property="og:url" content="{escape(base, quote=True)}">\n<meta property="og:image" content="{escape(base, quote=True)}assets/images/social.png">'
        (stage / 'index.html').write_text(index.replace('<!-- PUBLIC_METADATA -->', metadata), encoding='utf-8')
        (stage / '.nojekyll').touch()
        for name in ('index.html', 'styles.css', 'app.js', 'data.js', '.nojekyll'):
            if not (stage / name).is_file():
                raise ValueError(f'Falta archivo esencial: {name}')
        destination = root / 'docs'
        if destination.exists():
            shutil.rmtree(destination)
        shutil.move(str(stage), destination)
    result = {'invitados': len(guests), 'identificadores_nuevos': new, 'salida': 'docs/', 'avisos': warnings}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    try:
        build(parser.parse_args().root)
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, f'Construcción detenida: {exc}\n')
