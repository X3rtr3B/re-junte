"""Valida datos, UTF-8, integridad del sitio y referencias locales."""
import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from common import ROOT, load, validate_data

class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ('src', 'href', 'poster') and value:
                self.refs.append(value)

def validate(root=ROOT):
    root = Path(root)
    event, guests = load(root)
    validate_data(event, guests)
    docs = root / 'docs'
    for name in ('index.html', 'styles.css', 'app.js', 'data.js', '.nojekyll'):
        if not (docs / name).is_file():
            raise ValueError(f'Falta docs/{name}. Ejecuta build.py.')
    for path in list((root / 'src').rglob('*')) + list(docs.rglob('*')):
        if path.is_file() and path.suffix in {'.html', '.css', '.js', '.svg', '.json', '.txt', '.vtt'}:
            path.read_text(encoding='utf-8')
    payload = (docs / 'data.js').read_text(encoding='utf-8')
    generated = json.loads(payload.removeprefix('window.REJUNTE = ').rstrip().removesuffix(';'))
    if generated != {'evento': event, 'invitados': guests}:
        raise ValueError('docs/data.js está desactualizado. Reconstruye.')
    parser = References()
    parser.feed((docs / 'index.html').read_text(encoding='utf-8'))
    css = (docs / 'styles.css').read_text(encoding='utf-8')
    css_refs = re.findall(r"url\((?:\"([^\"]*)\"|'([^']*)'|([^)]*))\)", css)
    refs = parser.refs + [next(v for v in match if v) for match in css_refs]
    checked = 0
    for ref in refs:
        parts = urlsplit(ref)
        if ref.startswith(('data:', '#', '?')) or parts.scheme:
            continue
        if ref.startswith(('/', '\\')):
            raise ValueError(f'Ruta absoluta incompatible con GitHub Pages: {ref}')
        path = (docs / unquote(parts.path)).resolve()
        if not path.is_relative_to(docs.resolve()) or not path.is_file():
            raise ValueError(f'Recurso local ausente o fuera del sitio: {ref}')
        checked += 1
    for name in ('index.html', 'styles.css', 'app.js'):
        expected = (root / 'src' / name).read_text(encoding='utf-8')
        built = (docs / name).read_text(encoding='utf-8')
        if name == 'index.html':
            expected = expected.split('<!-- PUBLIC_METADATA -->')
            if not (built.startswith(expected[0]) and built.endswith(expected[1])):
                raise ValueError('docs/index.html no corresponde al fuente.')
        elif built != expected:
            raise ValueError(f'docs/{name} no corresponde al fuente.')
    if 'innerHTML' in (docs / 'app.js').read_text(encoding='utf-8'):
        raise ValueError('Revisa el uso de innerHTML en el frontend.')
    print(f'OK: {len(guests)} invitados, IDs únicos, datos sincronizados, UTF-8 y {checked} referencias locales.')
    if not event.get('url_publica'):
        print('Aviso: URL pública pendiente; aún no se exportan enlaces definitivos.')
    if event['video_habilitado']:
        for field in ('video_archivo', 'video_subtitulos'):
            if not (docs / event[field]).is_file():
                print(f'Aviso: falta {event[field]}; el video es opcional y no bloquea el texto.')
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    try:
        validate(parser.parse_args().root)
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, f'Validación fallida: {exc}\n')
