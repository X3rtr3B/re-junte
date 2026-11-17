"""Pruebas reales opcionales. Requiere Playwright y Chromium solo en desarrollo."""
import argparse
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json
import re
import sys
import tempfile
from threading import Thread
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[1]
WIDTHS=[320,375,390,430,768,1024,1440]

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*_): pass

def run(executable='/usr/bin/chromium'):
    results=[]
    reports=ROOT/'reports'
    shots=reports/'screenshots'
    shots.mkdir(parents=True,exist_ok=True)
    data=json.loads((ROOT/'docs/data.js').read_text().removeprefix('window.REJUNTE = ').strip().removesuffix(';'))
    def done(label):
        results.append(label)
        print('OK:',label,flush=True)
    def no_overflow(page):
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'),page.evaluate('({width:innerWidth,actual:document.documentElement.scrollWidth})')
    def capture(page,name):
        page.screenshot(path=str(shots/name.replace('.png','.jpg')),full_page=True,animations='disabled',type='jpeg',quality=82)
    with tempfile.TemporaryDirectory() as directory:
        (Path(directory)/'re-junte').symlink_to(ROOT/'docs',target_is_directory=True)
        server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=directory))
        Thread(target=server.serve_forever,daemon=True).start()
        base=f'http://127.0.0.1:{server.server_port}/re-junte/'
        try:
            with sync_playwright() as p:
                browser=p.chromium.launch(executable_path=executable,headless=True,args=['--no-sandbox'])
                context=browser.new_context(viewport={'width':1440,'height':1000})
                page=context.new_page()
                page.set_default_timeout(7000)
                errors=[]
                requests=[]
                page.on('request',lambda request:requests.append(request.method))
                page.on('pageerror',lambda error:errors.append(str(error)))
                page.goto(base)
                expect(page.locator('.guest-button')).to_have_count(3)
                assert page.locator('.guest-button').all_text_contents()==['Camila↗','Mateo↗','Sofía↗']
                expect(page.locator('#video-panel')).to_be_hidden()
                done('Acceso general; selector con nombres sin apodos y video oculto')
                page.get_by_role('button',name='Camila',exact=True).focus()
                page.keyboard.press('Enter')
                expect(page.locator('#invitation')).to_be_visible()
                expect(page.locator('#guest-name')).to_have_text('Camila')
                expect(page.locator('#guest-alias')).to_have_text('la Macha')
                expect(page.locator('#guest-obligation')).to_have_text('obligada')
                assert '/re-junte/?i='+data['invitados'][0]['id'] in page.url
                assert page.evaluate('document.activeElement.id')=='invite-title'
                done('Selección por teclado, URL bajo /re-junte/ y foco en invitación')
                text=' '.join(page.locator('.invitation-grid').inner_text().split())
                paragraphs=[
                    'Camila, alias la Macha, estás cordialmente obligada a asistir al reencuentro de quienes alguna vez compartimos crisis académicas y probablemente demasiadas horas juntos, al punto de ya no querer volver a vernos (al menos no en el futuro inmediato).',
                    'Carnal, considerando los antecedentes académicos, la antigüedad de la amistad y la ausencia de reuniones colectivas desde 2023, ya toca un junte como corresponde.',
                    'Que quieras asistir o no, no interesa. Y si faltas, deberás enviar tu aporte para tres bebidas espirituosas o pagar medio kilo de asado por cada uno de los que sí estaremos allí.',
                    'Reserva la fecha desde ahora.',
                    'El resto de los detalles vendrá después.',
                    'Nos volvemos a reunir.',
                    'La presente notificación tiene carácter vinculante y podrá ser utilizada como evidencia de que usted fue debidamente informado/a.'
                ]
                position=0
                for paragraph in paragraphs:
                    found=text.index(paragraph,position)
                    position=found+len(paragraph)
                assert page.locator('.actions button').count()==2
                done('Texto aprobado completo y en orden; exactamente dos acciones finales')
                for width in WIDTHS:
                    page.set_viewport_size({'width':width,'height':900})
                    no_overflow(page)
                    capture(page,f'invitacion-{width}.png')
                    page.locator('#change-guest').click()
                    no_overflow(page)
                    capture(page,f'selector-{width}.png')
                    page.get_by_role('button',name='Camila',exact=True).click()
                done('Siete anchuras: 320, 375, 390, 430, 768, 1024 y 1440; 14 capturas sin overflow')
                page.set_viewport_size({'width':390,'height':844})
                page.locator('#accept').click()
                expect(page.locator('#response-title')).to_have_text('DESTINO ACEPTADO')
                expect(page.locator('#response-body')).to_contain_text('Su disposición a cumplir con sus obligaciones sociales ha sido debidamente reconocida.')
                expect(page.locator('#response-body')).to_contain_text('Nos vemos en Tarija.')
                for _ in range(4):
                    page.keyboard.press('Tab')
                    assert page.evaluate('document.activeElement === document.body || document.querySelector("dialog").contains(document.activeElement)')
                capture(page,'destino-390.png')
                page.keyboard.press('Escape')
                expect(page.locator('#response-dialog')).not_to_be_visible()
                assert page.evaluate('document.activeElement.id')=='accept'
                done('Aceptación, diálogo modal, Tab, Escape y restauración del foco')
                page.locator('#negotiate').click()
                expect(page.locator('#response-title')).to_have_text('IMPUGNACIÓN DENEGADA')
                for text in ['El comité ha considerado que su recurso carece de fundamentos.','Motivo: La última reunión colectiva data de 2023.','Resolución: Preséntese el 28 de enero de 2027.','Contra esta resolución no procede recurso alguno.']:
                    expect(page.locator('#response-body')).to_contain_text(text)
                capture(page,'denegada-390.png')
                page.get_by_role('button',name='ENTENDIDO, NI MODO').click()
                assert page.evaluate('document.activeElement.id')=='negotiate'
                done('Negociación, resolución completa, cierre y foco')
                page.locator('#change-guest').click()
                page.get_by_role('button',name='Mateo',exact=True).click()
                expect(page.locator('#guest-obligation')).to_have_text('obligado')
                page.go_back()
                expect(page.locator('#selector')).to_be_visible()
                page.go_back()
                expect(page.locator('#guest-name')).to_have_text('Camila')
                page.go_forward()
                expect(page.locator('#selector')).to_be_visible()
                page.go_forward()
                expect(page.locator('#guest-name')).to_have_text('Mateo')
                done('Cambio de nombre y navegación Atrás/Adelante con popstate')
                for guest in data['invitados']:
                    page.goto(base+'?i='+guest['id'])
                    expect(page.locator('#guest-name')).to_have_text(guest['nombre'])
                    expect(page.locator('#guest-alias')).to_have_text(' '.join(filter(None,[guest['articulo_alias'],guest['apodo']])))
                done('Los tres enlaces individuales, tildes y concordancia explícita')
                page.goto(base+'?i=no-existe')
                expect(page.locator('#notice')).to_be_visible()
                expect(page.locator('#selector')).to_be_visible()
                page.get_by_role('button',name='Sofía',exact=True).click()
                expect(page.locator('#notice')).to_be_hidden()
                done('Identificador inválido recuperable sin pantalla vacía')
                page.emulate_media(reduced_motion='reduce')
                page.locator('#accept').click()
                assert page.locator('#confetti i').count()==0
                assert page.locator('.dialog-paper').evaluate('el=>getComputedStyle(el).animationName')=='none'
                page.keyboard.press('Escape')
                page.emulate_media(reduced_motion='no-preference')
                done('prefers-reduced-motion: sin confeti ni animación')
                altered=json.loads(json.dumps(data))
                altered['invitados'][0].update(nombre='<img src=x onerror="window.injected=1">',apodo='Apodo muy largo '*20,articulo_alias='')
                altered['invitados'] += [dict(id=f'long_list_token_{i:08d}',nombre=f'Invitado {i}',apodo='Alias',articulo_alias='',forma_obligacion='obligado') for i in range(50)]
                page.route('**/data.js',lambda route:route.fulfill(content_type='application/javascript',body='window.REJUNTE = '+json.dumps(altered)+';'))
                page.goto(base+'?i='+altered['invitados'][0]['id'])
                assert page.locator('#guest-name img').count()==0
                assert page.evaluate('window.injected') is None
                no_overflow(page)
                page.locator('#change-guest').click()
                expect(page.locator('#search-wrap')).to_be_visible()
                page.locator('#guest-search').fill('Invitado 49')
                expect(page.locator('.guest-button')).to_have_count(1)
                page.locator('#guest-search').fill('nombre inexistente')
                expect(page.locator('#no-results')).to_be_visible()
                done('Inserción segura, apodo largo sin artículo y buscador con 53 invitados')
                page.unroute('**/data.js')
                page.route('**/assets/decorations/compadres.svg',lambda route:route.abort())
                page.goto(base)
                page.get_by_role('button',name='Camila',exact=True).click()
                expect(page.locator('#invitation')).to_be_visible()
                page.unroute('**/assets/decorations/compadres.svg')
                done('Recurso decorativo fallido: contenido y selección disponibles')
                video_data=json.loads(json.dumps(data));video_data['evento']['video_habilitado']=True
                page.route('**/data.js',lambda route:route.fulfill(content_type='application/javascript',body='window.REJUNTE = '+json.dumps(video_data)+';'))
                page.goto(base+'?i='+data['invitados'][0]['id'])
                expect(page.locator('#video-panel')).to_be_visible()
                assert page.locator('video').evaluate('el=>el.paused && !el.autoplay && el.controls')
                page.locator('video').evaluate('el=>el.load()')
                page.locator('video').evaluate('el=>el.play().catch(()=>{})')
                expect(page.locator('#video-error')).to_be_visible()
                page.locator('#skip-video').click()
                assert page.evaluate('document.activeElement.id')=='antecedents'
                page.locator('#accept').click()
                expect(page.locator('#response-title')).to_have_text('DESTINO ACEPTADO')
                done('Video habilitado pero ausente: controles, error tolerado y omisión')
                assert not errors,errors
                assert not context.cookies()
                assert all(method=='GET' for method in requests)
                assert page.evaluate('localStorage.length + sessionStorage.length')==0
                done('Sin errores JavaScript ni cookies propias durante las interacciones')
                browser.close()
        finally:
            server.shutdown();server.server_close()
    report={'navegador':'Chromium headless / Playwright','grupos_verificados':len(results),'anchuras':WIDTHS,'resultados':results,'capturas':sorted(p.name for p in shots.glob('*.jpg'))}
    (reports/'browser-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(results)} grupos OK; {len(report["capturas"])} capturas.',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chromium',default='/usr/bin/chromium')
    run(parser.parse_args().chromium)
