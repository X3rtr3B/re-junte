"""Edición explícita por ID: nunca inferir concordancia ni reemplazar tokens."""
from common import ROOT, load, validate_data, write_guests

def save_guest(nombre, apodo, articulo_alias, forma_obligacion, guest_id=None, root=ROOT):
    event, guests = load(root)
    row = dict(id=guest_id or '', nombre=nombre.strip(), apodo=apodo.strip(), articulo_alias=articulo_alias.strip(), forma_obligacion=forma_obligacion.strip())
    if guest_id:
        matches = [i for i, g in enumerate(guests) if g['id'] == guest_id]
        if len(matches) != 1:
            raise ValueError('ID inexistente o repetido: consulta primero el CSV.')
        guests[matches[0]] = row
    else:
        guests.append(row)
    validate_data(event, guests, allow_missing_ids=True)
    write_guests(guests, root)
    print('Invitado guardado; reconstruye para actualizar el sitio.')
