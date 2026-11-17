"""Modelo y validaciones compartidas; solamente biblioteca estándar."""
from pathlib import Path
import csv
import json
import re
from datetime import date
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ['id', 'nombre', 'apodo', 'articulo_alias', 'forma_obligacion']
TEXT_FIELDS = ['convocatoria', 'antecedentes', 'reserva', 'detalles', 'cierre', 'aviso']

def load(root=ROOT):
    root = Path(root)
    event = json.loads((root / 'config/evento.json').read_text(encoding='utf-8'))
    with (root / 'config/invitados.csv').open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != FIELDS:
            raise ValueError('CSV: las columnas deben ser ' + ','.join(FIELDS))
        guests = list(reader)
    return event, guests

def write_guests(guests, root=ROOT):
    path = Path(root) / 'config/invitados.csv'
    temporary = path.with_suffix('.csv.tmp')
    with temporary.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(guests)
    temporary.replace(path)

def public_url(value):
    p = urlsplit(value)
    host = p.hostname or ''
    reserved = host.endswith(('.example', '.invalid', '.test', '.localhost')) or host in {'example.com', 'example.org', 'example.net', 'localhost', '127.0.0.1', '::1'}
    placeholder = any(x in host.lower() for x in ('usuario', 'username', 'your-', 'tu-usuario'))
    if p.scheme != 'https' or not host or p.username or p.password or p.query or p.fragment or reserved or placeholder:
        raise ValueError('Configura una URL pública HTTPS real, sin consultas, credenciales ni marcadores ficticios.')
    return value.rstrip('/') + '/'

def validate_data(event, guests, allow_missing_ids=False):
    for field in ('titulo', 'ciudad', 'pais', 'festividad', 'repositorio'):
        if not isinstance(event.get(field), str) or not event[field].strip():
            raise ValueError(f'Evento: {field} es obligatorio.')
    if not isinstance(event.get('fecha'), str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', event['fecha']):
        raise ValueError('fecha debe tener formato AAAA-MM-DD.')
    date.fromisoformat(event['fecha'])
    if type(event.get('video_habilitado')) is not bool:
        raise ValueError('video_habilitado debe ser booleano.')
    for key in TEXT_FIELDS:
        if not isinstance(event.get('texto', {}).get(key), str) or not event['texto'][key].strip():
            raise ValueError(f'Falta texto.{key}.')
    for key, value in event.get('opciones_visuales', {}).items():
        if key not in {'animaciones', 'confeti'} or type(value) is not bool:
            raise ValueError('Opciones visuales inválidas.')
    for field, suffix in [('video_archivo', '.mp4'), ('video_subtitulos', '.vtt')]:
        value = event.get(field, '')
        path = Path(value)
        if not value or path.is_absolute() or '..' in path.parts or not value.startswith('assets/video/') or path.suffix != suffix:
            raise ValueError(f'{field}: utiliza una ruta relativa assets/video/ con extensión {suffix}.')
    if event.get('url_publica'):
        public_url(event['url_publica'])
    if not guests:
        raise ValueError('Agrega al menos un invitado.')
    ids, identities = set(), set()
    for i, g in enumerate(guests, 2):
        if set(g) != set(FIELDS) or any(not isinstance(v, str) or v != v.strip() for v in g.values()):
            raise ValueError(f'Fila {i}: columnas incompletas, adicionales o espacios en los extremos.')
        if not g['nombre'] or not g['apodo']:
            raise ValueError(f'Fila {i}: nombre y apodo son obligatorios.')
        if g['articulo_alias'] not in ('', 'el', 'la', 'los', 'las'):
            raise ValueError(f'Fila {i}: artículo inválido; se admite vacío, el, la, los o las.')
        if g['forma_obligacion'] not in ('obligado', 'obligada'):
            raise ValueError(f'Fila {i}: configura obligado u obligada explícitamente.')
        article = g['articulo_alias']
        if article and g['apodo'].casefold().startswith(article + ' '):
            raise ValueError(f'Fila {i}: el apodo ya contiene el artículo.')
        identity = (g['nombre'].casefold(), g['apodo'].casefold())
        if identity in identities:
            raise ValueError(f'Fila {i}: invitado duplicado.')
        identities.add(identity)
        token = g['id']
        if not token and allow_missing_ids:
            continue
        if not re.fullmatch(r'[A-Za-z0-9_-]{16,128}', token):
            raise ValueError(f'Fila {i}: identificador vacío o inválido (mínimo 16 caracteres URL-safe).')
        if token in ids:
            raise ValueError(f'Fila {i}: identificador repetido.')
        ids.add(token)
