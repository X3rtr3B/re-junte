"""Reproduce el Python del notebook con un ZIP y una API mínima simulada de Colab.

No prueba la interfaz, los permisos ni el proxy real de Google Colab.
"""
from pathlib import Path
import contextlib
import importlib
import io
import json
import subprocess
import sys
import tempfile
import types
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def run():
    subprocess.run([sys.executable,str(ROOT/'scripts/export.py')],cwd=ROOT,check=True)
    source=ROOT/'exports/re-junte-FUENTE.zip'
    nb=json.loads((ROOT/'ReJunte.ipynb').read_text(encoding='utf-8'))
    with tempfile.TemporaryDirectory() as temp:
        target=Path(temp)/'content/re-junte'
        downloaded=[]
        colab=types.ModuleType('google.colab')
        colab.files=types.SimpleNamespace(upload=lambda:{source.name:source.read_bytes()},download=lambda p:downloaded.append(Path(p)))
        sys.modules['google.colab']=colab
        state={}
        for index,cell in enumerate(nb['cells']):
            if cell['cell_type']!='code': continue
            code=''.join(cell['source']).replace("Path('/content/re-junte')",f'Path({str(target)!r})').replace("MODO = 'github'","MODO = 'zip'")
            exec(compile(code,f'ReJunte.ipynb:celda-{index}','exec'),state)
        expected=3 if json.loads((target/'config/evento.json').read_text()).get('url_publica') else 2
        assert len(downloaded)==expected
        assert all(path.exists() for path in downloaded)
        before=(target/'config/invitados.csv').read_bytes()
        subprocess.run([sys.executable,str(target/'scripts/build.py')],cwd=target,check=True)
        assert (target/'config/invitados.csv').read_bytes()==before
        with zipfile.ZipFile(target/'exports/re-junte-SITIO-PAGES.zip') as archive:
            assert 'index.html' in archive.namelist()
        # Repetir preparación conserva cambios locales sin volver a importar el ZIP.
        config=target/'config/evento.json'
        config_before=config.read_bytes()
        first=next(c for c in nb['cells'] if c['cell_type']=='code')
        code=''.join(first['source']).replace("Path('/content/re-junte')",f'Path({str(target)!r})')
        exec(compile(code,'preparacion-repetida','exec'),state)
        assert config.read_bytes()==config_before
        import preview
        port_a=state['puerto']
        port_b=preview.start(target)
        assert port_a != port_b
        preview.stop()
        print('OK: todas las celdas Python, importación ZIP, exportación, preservación de IDs, preparación repetida y reinicio del servidor temporal.')
        print('Límite: simulación de files.upload/download; no se ejecutó la interfaz ni el proxy real de Colab, ni el montaje de Drive.')

if __name__=='__main__': run()
