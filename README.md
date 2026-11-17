# Re-junte 2027

Una convocatoria pseudojurídica para antiguos compañeros universitarios: **Compadres · 28 de enero de 2027 · Tarija, Bolivia**. Una sola web estática personaliza el texto, revela el apodo y permite aceptar el destino o intentar una negociación inevitablemente denegada.

**Operación principal: Google Colab.** Los invitados solo necesitan un navegador. El sitio publicado no depende de Python, Colab, Node.js, npm, cuentas ni un servidor propio.

[**Abrir ReJunte.ipynb en Colab**](https://colab.research.google.com/github/X3rtr3B/re-junte/blob/main/ReJunte.ipynb) · [Repositorio](https://github.com/X3rtr3B/re-junte) · [Configurar Pages](https://github.com/X3rtr3B/re-junte/settings/pages)

## Empezar desde cero

1. Abre el cuaderno mediante el enlace anterior. Usa Python 3 y hardware **Ninguno**.
2. Ejecuta las celdas en orden. La primera recupera la rama `main` en `/content/re-junte/`. También permite importar el ZIP **FUENTE**. No sobrescribe una carpeta existente.
3. Edita `config/evento.json` y `config/invitados.csv` desde Colab. Se incluyen tres identidades ficticias: Camila, Mateo y Sofía. La celda de invitados permite agregar y editar por ID sin cambiar enlaces.
4. Ejecuta construcción y validación. Abre la vista previa temporal y prueba los dos botones.
5. Exporta y descarga los ZIP. Guarda **FUENTE** antes de terminar la sesión. `/content/` se pierde entre sesiones.
6. Publica `docs/` siguiendo el procedimiento siguiente. Solo entonces configura la URL real y genera los enlaces personalizados.

El cuaderno no duplica el código web: llama a los scripts y copia los archivos editables de `src/`. Las ejecuciones posteriores conservan el diseño y los identificadores.

## Publicar en GitHub Pages

En el repositorio, abre **Settings → Pages** y selecciona:

```text
Source: Deploy from a branch
Branch: main
Folder: /docs
```

Guarda y espera a que GitHub indique que el despliegue está disponible. Abre la dirección que muestre GitHub y comprueba el selector. No se publica el notebook como si fuera el sitio.

La configuración inicial deja `url_publica` vacía. Cuando la dirección funcione, cópiala a ese campo, reconstruye y exporta. El proyecto puede vivir en `/re-junte/` o en otra ruta: todos los recursos locales usan rutas relativas y la navegación conserva la ruta base.

Para subir cambios desde Colab, descarga y extrae **re-junte-FUENTE.zip**. En GitHub usa **Add file → Upload files** para subir los archivos modificados a `main`, conservando su estructura. Compara primero la versión de GitHub para evitar sobrescribir cambios posteriores de otra sesión. Comprueba que `docs/.nojekyll` siga presente. No subas `exports/`, archivos temporales ni credenciales.

**Subir un ZIP al repositorio no publica su contenido: hay que extraerlo.** El ZIP **SITIO-PAGES** contiene `index.html` en la raíz para un alojamiento estático; si lo utilizas con la configuración anterior, su contenido debe quedar dentro de `docs/`.

No se ejecuta `git push` desde el cuaderno ni se requieren tokens para la publicación manual. Las herramientas de GitHub utilizadas para preparar este repositorio no habilitan por sí mismas el servicio Pages. El estado del despliegue debe comprobarse en GitHub.

## Archivos y responsabilidades

```text
ReJunte.ipynb                Operación en Colab, recuperación, edición y exportación
config/evento.json          Evento, URL pública, texto configurable, video y movimiento
config/invitados.csv        Identidades y correspondencia persistente de tokens
src/index.html             Estructura y texto aprobado
src/styles.css             Diseño, accesibilidad, adaptación y animaciones
src/app.js                 Selector, historial, personalización y diálogos
src/assets/                SVG originales, imagen social y fuente local con licencia
scripts/common.py          Modelo y validaciones compartidas
scripts/guests.py          Edición explícita por ID
scripts/build.py           Construcción y asignación de tokens nuevos
scripts/validate.py        Datos, UTF-8, recursos y sincronización
scripts/generate_links.py  CSV de enlaces con URL pública real
scripts/preview.py         Servidor temporal con puerto libre y cierre del anterior
scripts/export.py          ZIP de fuente y ZIP de sitio
tests/test_project.py     Pruebas Python sin dependencias adicionales
tests/browser_checks.py   Pruebas opcionales de Chromium mediante Playwright
tests/notebook_replay.py  Reproducción de celdas con carga y descarga simuladas
reports/                   Resultados y capturas de pruebas ejecutadas
docs/                     Sitio generado para Pages; no editar a mano
```

## Editar invitados y conservar enlaces

CSV UTF-8, con estas columnas exactas:

```csv
id,nombre,apodo,articulo_alias,forma_obligacion
,Camila,Macha,la,obligada
```

El ejemplo muestra una **fila nueva**. El CSV entregado ya contiene tokens aleatorios persistidos. Deja el ID vacío solamente al agregar una persona. `build.py` genera tokens URL-safe con `secrets.token_urlsafe(18)`, verifica su unicidad y guarda el CSV antes de generar el sitio. Los IDs existentes nunca se recalculan.

- El nombre y el apodo son obligatorios. El selector muestra únicamente el nombre; las flechas son decorativas.
- Usa `el`, `la`, `los`, `las` o un artículo vacío. Si se indica artículo, no lo repitas en el apodo.
- Configura `obligado` u `obligada` explícitamente. El sistema no infiere género a partir del nombre.
- Se rechazan IDs repetidos, columnas incompletas y duplicados de nombre + apodo. Personas diferentes pueden compartir nombre.
- Para cambiar datos, conserva el ID de la fila. No reutilices IDs eliminados. Para nombres que incluyan comas usa comillas CSV.
- **Guarda el CSV actualizado en GitHub o en el ZIP FUENTE antes de compartir enlaces.** Un ID generado solo en una sesión temporal se perderá al cerrar Colab si no guardas esa correspondencia.

Acceso general: la ruta pública del sitio. Acceso individual: la misma ruta seguida de `?i=TOKEN`. Un identificador inválido muestra un aviso y permite elegir un nombre. El botón de cambio de nombre y la marca regresan al selector. Atrás y Adelante funcionan mediante `popstate`.

Desde diez invitados aparece un buscador que también encuentra nombres sin escribir sus tildes.

## Configuración y mantenimiento

Los valores iniciales son `Re-junte`, `2027-01-28`, `Tarija`, `Bolivia`, `Compadres`, repositorio `re-junte`, URL pública vacía y video desactivado. El frontend formatea la fecha en español sin desplazarla por la zona horaria del navegador.

`texto` centraliza los párrafos configurables de la invitación. La cláusula de sanciones conserva énfasis editorial en el HTML; las respuestas están en JavaScript. Se entrega el texto aprobado completo. No lo cambies salvo que apruebes una nueva versión. No se han añadido horario, local, precio ni dirección no confirmados.

`opciones_visuales.animaciones` y `opciones_visuales.confeti` permiten desactivar movimiento y confeti. La preferencia `prefers-reduced-motion` se respeta siempre.

Para cambiar el diseño edita `src/`, nunca solo `docs/`. Reconstruye, valida, previsualiza, exporta y sube los cambios. Revisa un enlace antiguo después de publicar; tanto el ID como la ruta pública deben conservarse.

Los recursos decorativos se inspiran en canastas florales, cintas y papel recortado descritos en el brief. Son SVG originales, sin insignias oficiales. La tipografía Bricolage Grotesque se sirve localmente bajo SIL OFL; no se contacta con Google Fonts al abrir la invitación. El resto de los recursos no necesita descargas externas.

El coral se usa para titulares grandes y botones con tinta oscura; los párrafos y las etiquetas pequeñas usan combinaciones de mayor contraste. Los diálogos usan `<dialog>` nativo con fondo inerte, salida mediante Escape y restauración del foco. Las animaciones son breves y no bloquean el contenido.

### Video opcional

No existe un video por defecto. Añade `src/assets/video/invitacion.mp4` y subtítulos reales `subtitulos.vtt`, o configura otras rutas relativas dentro de `assets/video/`. Activa `video_habilitado` y reconstruye. Usa recursos con derechos de uso y subtítulos revisados.

El video tiene controles nativos, reproducción voluntaria, omisión y un mensaje de error si falla. Se pausa al cambiar de vista, abrir una respuesta o abandonar la pestaña. No es un requisito para leer la invitación. No hay música de fondo.

### Vista previa y recuperación

El servidor temporal de Python sirve `docs/`. Cada arranque cierra el servidor anterior y usa un puerto libre. `serve_kernel_port_as_iframe` lo muestra dentro de Colab cuando el entorno lo permite. Las restricciones del iframe pueden afectar el historial, el foco o el video: comprueba esos comportamientos en Pages si ocurre. La dirección temporal no sirve como enlace permanente.

Para una sesión nueva clona la última versión de GitHub o importa **FUENTE**. No se presupone persistencia en `/content/`. La copia opcional a Drive está desactivada; el montaje solicitará acceso solo si decides activarlo. No es necesario para ninguna función básica.

### Enlaces y vista previa social

`generate_links.py` requiere una URL HTTPS configurada sin credenciales, parámetros, fragmentos ni marcadores ficticios. Rechaza direcciones ilustrativas como `USUARIO.github.io` o `example.com`. Conserva Unicode en nombres y exporta un CSV UTF-8 con BOM, compatible con hojas de cálculo.

El generador no comprueba por red que una URL arbitraria exista: compruébala al publicarla. El archivo `enlaces_personalizados.csv` queda en `exports/` y no en el sitio. Los metadatos Open Graph son genéricos: al configurar la URL se añade la dirección absoluta de la imagen original `social.png`. Los servicios de mensajería deciden si muestran la vista previa y pueden mantener cachés. No hay metadatos personalizados por invitado.

## Privacidad y alcance de los botones

**Nombres, apodos y tokens son públicos.** El selector permite conocer la lista y `data.js` es descargable. Un token personaliza el contenido; no autentica a nadie ni hace privada la invitación. No incluyas datos sensibles, teléfonos ni domicilios.

«Acepto mi destino» muestra una respuesta en ese navegador y **no registra ni envía asistencia**. No hay backend, almacenamiento de confirmaciones, analítica, cookies, seguimiento propio ni credenciales. GitHub y el proveedor de alojamiento pueden conservar registros técnicos propios. La notificación y sus sanciones son bromas sin validez jurídica.

## Validación y desarrollo sin Colab

Estas mismas órdenes se ejecutan desde el cuaderno. Para un entorno de desarrollo con Python 3.10 o posterior:

```sh
python scripts/build.py
python scripts/validate.py
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/export.py
```

Para enlaces, después de publicar y configurar la dirección:

```sh
python scripts/generate_links.py
```

Las pruebas de navegador son opcionales para desarrollo; no son una dependencia de Colab ni de la aplicación. Con Playwright y Chromium disponibles:

```sh
pythontests/browser_checks.py --chromium /usr/bin/chromium
```

Se prueban selección real, enlaces, texto aprobado, historial, botones, foco, errores y las siete anchuras solicitadas. Las capturas y resultados se guardan en `reports/`. La validación estática no sustituye estas interacciones. Consulta [el informe de pruebas](reports/VERIFICACION.md) para distinguir lo ejecutado de los límites de la comprobación.

## Operaciones todavía externas

Sustituye los invitados ficticios por los reales cuando corresponda. El video sigue siendo opcional y debe aportarse si se quiere usar. La activación de GitHub Pages, su dirección pública y las pruebas del enlace remoto deben completarse y comprobarse desde la configuración de GitHub antes de distribuir invitaciones. El cuaderno no publica automáticamente.
