"""Servidor temporal reutilizable: importar y llamar start(root)."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from pathlib import Path
from common import ROOT

_server = None
_thread = None

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

def stop():
    global _server, _thread
    if _server:
        _server.shutdown()
        _server.server_close()
        _thread.join(timeout=3)
        _server = None
        _thread = None

def start(root=ROOT):
    global _server, _thread
    stop()
    docs = Path(root) / 'docs'
    if not (docs / 'index.html').exists():
        raise ValueError('Primero construye docs/.')
    _server = ThreadingHTTPServer(('0.0.0.0', 0), partial(QuietHandler, directory=str(docs)))
    _thread = Thread(target=_server.serve_forever, daemon=True)
    _thread.start()
    return _server.server_address[1]
