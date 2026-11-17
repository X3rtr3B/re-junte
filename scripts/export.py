"""Dos ZIP distintos: fuente recuperable y sitio con index.html en la raíz."""
import argparse
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from common import ROOT, load
from validate import validate
from generate_links import generate

SOURCE_ITEMS = ['ReJunte.ipynb', 'README.md', '.gitignore', 'config', 'src', 'scripts', 'tests', 'docs', 'reports', '.github']

def export(root=ROOT):
    root = Path(root)
    validate(root)
    directory = root / 'exports'
    directory.mkdir(exist_ok=True)
    source = directory / 're-junte-FUENTE.zip'
    site = directory / 're-junte-SITIO-PAGES.zip'
    with ZipFile(source, 'w', ZIP_DEFLATED) as archive:
        for item in SOURCE_ITEMS:
            path = root / item
            candidates = sorted(path.rglob('*')) if path.is_dir() else [path]
            for file in candidates:
                if file.is_file() and '__pycache__' not in file.parts and file.suffix != '.pyc':
                    archive.write(file, 're-junte/' + str(file.relative_to(root)))
    with ZipFile(site, 'w', ZIP_DEFLATED) as archive:
        for file in sorted((root / 'docs').rglob('*')):
            if file.is_file():
                archive.write(file, str(file.relative_to(root / 'docs')))
    event, guests = load(root)
    links = generate(root) if event.get('url_publica') else None
    print(f'Fuente: {source.name}\nSitio: {site.name}\nInvitados válidos: {len(guests)}; enlaces: {len(guests) if links else 0}')
    print('Los ZIP deben extraerse antes de subirlos a GitHub; GitHub Pages no publica el contenido interno de un ZIP.')
    return source, site, links

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    try:
        export(parser.parse_args().root)
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, f'Exportación detenida: {exc}\n')
