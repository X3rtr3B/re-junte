"""Exporta enlaces solo después de configurar la URL pública real."""
import argparse
import csv
from pathlib import Path
from urllib.parse import urlencode
from common import ROOT, load, validate_data, public_url


def generate(root=ROOT, output=None):
    root = Path(root)
    event, guests = load(root)
    validate_data(event, guests)
    base = public_url(event.get('url_publica', ''))
    output = Path(output) if output else root / 'exports/enlaces_personalizados.csv'
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['nombre', 'url'])
        writer.writeheader()
        writer.writerows({'nombre': g['nombre'], 'url': base + '?' + urlencode({'i': g['id']})} for g in guests)
    print(f'{len(guests)} enlaces generados: {output.name}')
    return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        generate(args.root, args.output)
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, f'No se generaron enlaces: {exc}\n')
