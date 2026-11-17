"""Pruebas de datos, persistencia y exportación; biblioteca estándar."""
import contextlib
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import zipfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from common import ROOT, load, write_guests, validate_data, public_url
from build import build
from generate_links import generate
from validate import validate
from guests import save_guest
from importlib import import_module
export = import_module('export').export

class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for name in ('src', 'config', 'scripts', 'tests'):
            shutil.copytree(ROOT / name, self.root / name, ignore=shutil.ignore_patterns('__pycache__'))
        for name in ('ReJunte.ipynb', 'README.md', '.gitignore'):
            shutil.copy2(ROOT / name, self.root / name)
        self.event, _ = load(self.root)
        self.event['url_publica'] = ''
        self.guests = [
            dict(id='test_token_camila_12345678',nombre='Camila',apodo='Macha',articulo_alias='la',forma_obligacion='obligada'),
            dict(id='test_token_mateo_123456789',nombre='Mateo',apodo='Chino',articulo_alias='el',forma_obligacion='obligado'),
            dict(id='test_token_sofia_123456789',nombre='Sofía',apodo='Sofi',articulo_alias='la',forma_obligacion='obligada'),
        ]
        self.config()
        write_guests(self.guests,self.root)
        self.output = contextlib.redirect_stdout(io.StringIO())
        self.output.__enter__()
    def tearDown(self):
        self.output.__exit__(None, None, None)
        self.temp.cleanup()
    def config(self):
        (self.root / 'config/evento.json').write_text(json.dumps(self.event, ensure_ascii=False), encoding='utf-8')
    def digest(self):
        return {str(p.relative_to(self.root/'docs')):hashlib.sha256(p.read_bytes()).hexdigest() for p in (self.root/'docs').rglob('*') if p.is_file()}
    def test_rebuild_preserves_ids_and_exact_files(self):
        build(self.root)
        first = self.digest()
        ids = [g['id'] for g in load(self.root)[1]]
        build(self.root)
        self.assertEqual(first, self.digest())
        self.assertEqual(ids, [g['id'] for g in load(self.root)[1]])
    def test_only_new_rows_get_ids(self):
        before = [g['id'] for g in self.guests]
        self.guests.append(dict(id='',nombre='Álex',apodo='Ale',articulo_alias='',forma_obligacion='obligado'))
        write_guests(self.guests, self.root)
        build(self.root)
        new = load(self.root)[1]
        self.assertEqual(before, [g['id'] for g in new[:-1]])
        self.assertRegex(new[-1]['id'], r'^[\w-]{24}$')
    def test_random_collision_is_retried(self):
        from unittest.mock import patch
        self.guests[1]['id'] = ''
        write_guests(self.guests, self.root)
        with patch('build.secrets.token_urlsafe', side_effect=[self.guests[0]['id'], 'new_random_token_123456789']):
            build(self.root)
        self.assertEqual(load(self.root)[1][1]['id'], 'new_random_token_123456789')
    def test_duplicate_ids_rejected(self):
        self.guests[1]['id'] = self.guests[0]['id']
        with self.assertRaisesRegex(ValueError, 'repetido'):
            validate_data(self.event, self.guests)
    def test_duplicate_people_rejected(self):
        self.guests.append(dict(self.guests[0],id='another_token_12345678'))
        with self.assertRaisesRegex(ValueError, 'duplicado'):
            validate_data(self.event, self.guests)
    def test_empty_names_and_aliases_rejected(self):
        for field in ('nombre', 'apodo'):
            with self.subTest(field=field):
                guests = [dict(self.guests[0], **{field:''})]
                with self.assertRaises(ValueError): validate_data(self.event, guests)
    def test_grammar_not_inferred(self):
        self.guests[0]['forma_obligacion']=''
        with self.assertRaisesRegex(ValueError, 'explícitamente'): validate_data(self.event, self.guests)
    def test_article_must_not_be_repeated(self):
        self.guests[0]['apodo']='la Macha'
        with self.assertRaisesRegex(ValueError, 'contiene el artículo'): validate_data(self.event, self.guests)
    def test_no_article_allowed(self):
        self.guests[0]['articulo_alias']=''
        validate_data(self.event, self.guests)
    def test_invalid_tokens_rejected(self):
        for token in ('name', '../escape', 'bad token with spaces', ''):
            with self.subTest(token=token):
                with self.assertRaises(ValueError): validate_data(self.event, [dict(self.guests[0],id=token)])
    def test_update_preserves_token(self):
        token=self.guests[0]['id']
        save_guest('Camila María', 'Macha', 'la', 'obligada', token, self.root)
        self.assertEqual(load(self.root)[1][0]['id'],token)
        self.assertEqual(load(self.root)[1][0]['nombre'],'Camila María')
    def test_unknown_update_cannot_create_id(self):
        with self.assertRaises(ValueError): save_guest('A','B','','obligada','unknown_id_12345678',self.root)
    def test_invalid_csv_header(self):
        (self.root/'config/invitados.csv').write_text('nombre,id\nUno,test\n')
        with self.assertRaisesRegex(ValueError, 'columnas'): load(self.root)
    def test_extra_or_missing_columns(self):
        for row in ('x,A,B,,obligado,extra','x,A,B,'):
            with self.subTest(row=row):
                (self.root/'config/invitados.csv').write_text('id,nombre,apodo,articulo_alias,forma_obligacion\n'+row+'\n')
                with self.assertRaises(ValueError): validate_data(*load(self.root))
    def test_bad_configuration(self):
        for field,value in [('fecha','2027-02-30'),('video_habilitado','false'),('video_archivo','../../private.mp4'),('opciones_visuales',{'confeti':'yes'})]:
            with self.subTest(field=field):
                with self.assertRaises(ValueError): validate_data(dict(self.event, **{field:value}),self.guests)
    def test_fake_urls_rejected(self):
        for url in ('','http://real.github.io/re-junte/','https://USUARIO.github.io/re-junte/','https://example.com/','https://localhost/','https://real.github.io/?a=1','https://x:y@real.github.io/'):
            with self.subTest(url=url):
                with self.assertRaises(ValueError): public_url(url)
    def test_links_unicode_and_subdirectory(self):
        self.event['url_publica']='https://X3rtr3B.github.io/re-junte/'
        self.config()
        output=generate(self.root)
        with output.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
        self.assertEqual(rows[2]['nombre'],'Sofía')
        self.assertEqual(rows[0]['url'],self.event['url_publica']+'?i='+self.guests[0]['id'])
    def test_links_blocked_without_url(self):
        with self.assertRaises(ValueError): generate(self.root)
        self.assertFalse((self.root/'exports/enlaces_personalizados.csv').exists())
    def test_script_data_escaped_and_roundtrips(self):
        self.guests[0]['nombre']='</script><img src=x onerror=alert(1)>'
        write_guests(self.guests,self.root)
        build(self.root)
        self.assertNotIn('</script>',(self.root/'docs/data.js').read_text())
        validate(self.root)
    def test_missing_video_does_not_block_build(self):
        self.event['video_habilitado']=True
        self.config()
        self.assertTrue(build(self.root)['avisos'])
        validate(self.root)
    def test_stale_build_detected(self):
        build(self.root)
        self.event['ciudad']='Otra ciudad';self.config()
        with self.assertRaisesRegex(ValueError, 'desactualizado'): validate(self.root)
    def test_missing_referenced_asset_detected(self):
        build(self.root)
        (self.root/'docs/assets/decorations/flor.svg').unlink()
        with self.assertRaisesRegex(ValueError, 'ausente'): validate(self.root)
    def test_absolute_paths_detected(self):
        build(self.root)
        path=self.root/'docs/index.html'
        path.write_text(path.read_text().replace('href="styles.css"','href="/styles.css"'))
        with self.assertRaisesRegex(ValueError, 'absoluta'): validate(self.root)
    def test_export_layout_and_no_secrets_or_cache(self):
        build(self.root)
        source,site,links=export(self.root)
        self.assertIsNone(links)
        with zipfile.ZipFile(source) as z:
            self.assertIn('re-junte/ReJunte.ipynb',z.namelist())
            self.assertIn('re-junte/config/invitados.csv',z.namelist())
            self.assertFalse(any('__pycache__' in n or '/.git/' in n for n in z.namelist()))
        with zipfile.ZipFile(site) as z:
            self.assertIn('index.html',z.namelist())
            self.assertIn('.nojekyll',z.namelist())
            self.assertNotIn('ReJunte.ipynb',z.namelist())
    def test_notebook_structure_and_python_syntax(self):
        nb=json.loads((self.root/'ReJunte.ipynb').read_text())
        self.assertEqual(nb['nbformat'],4)
        self.assertEqual(nb['metadata']['kernelspec']['name'],'python3')
        for i,c in enumerate(nb['cells']):
            if c['cell_type']=='code': compile(''.join(c['source']),f'cell-{i}','exec')

if __name__=='__main__': unittest.main()
