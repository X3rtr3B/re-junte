# Verificación de Re-junte 2027

Ejecución: 16 de noviembre de 2026 (America/La_Paz), Python 3.12.14 y Chromium 156.0.8078.79 headless mediante Playwright. Se sirvió el sitio por HTTP bajo `/re-junte/`, reproduciendo la ruta de un proyecto de GitHub Pages.

## Resultados ejecutados

- **25 pruebas Python aprobadas.** CSV, campos obligatorios, duplicados, artículos, concordancia explícita, tokens URL-safe, colisiones aleatorias, persistencia de IDs, reconstrucciones byte a byte idénticas, generación de enlaces Unicode, rechazo de URLs ficticias, datos maliciosos serializados sin HTML ejecutable, tolerancia a video ausente, recursos, sincronización, ZIP y sintaxis del notebook. Salida completa: [python-results.txt](python-results.txt).
- **14 grupos de interacción aprobados en Chromium.** Selector; selección mediante Enter; URL personalizada y foco; contenido aprobado completo y en orden; exactamente dos acciones finales; diálogos de aceptación y negociación; cierre, Escape y foco restaurado; cambio de nombre; Atrás y Adelante; los tres enlaces individuales; ID inválido; movimiento reducido; apodo largo sin artículo; nombre con contenido similar a HTML mostrado como texto; buscador con 53 invitados; recurso decorativo fallido; video habilitado y ausente; omisión del video. Sin errores JavaScript, cookies propias, almacenamiento local ni peticiones distintas de GET. Detalle: [browser-results.json](browser-results.json).
- **Siete anchuras comprobadas:** 320, 375, 390, 430, 768, 1024 y 1440 px, tanto en selector como en invitación, sin desbordamiento horizontal. Se corrigió un desborde inicial de 4 px en el título del selector a 320 px. Hay 14 capturas de las vistas y dos de las respuestas en [screenshots/](screenshots/).
- **Validación estática aprobada:** datos sincronizados, UTF-8, IDs únicos y ocho referencias locales verificadas. Salida: [validation-results.txt](validation-results.txt).
- **Cuaderno reproducido:** se ejecutaron todas las celdas Python, importando un ZIP FUENTE en una carpeta temporal, mediante una API simulada de `files.upload` y `files.download`. La carga validó las rutas del ZIP; la ejecución reconstruyó, validó, ejecutó las 25 pruebas, previsualizó mediante servidor HTTP y exportó ambos ZIP. Repetir preparación conservó los datos; reiniciar la previsualización cerró el servidor anterior. Salida: [notebook-results.txt](notebook-results.txt). Reproducción: `python tests/notebook_replay.py`.
- **Recuperación desde GitHub comprobada:** después de publicar el commit `9b43477`, se clonó `main` en una carpeta temporal nueva y se ejecutaron todas las celdas Python del cuaderno, incluida construcción, validación, las 25 pruebas y exportación. La vista previa respondió HTTP 200 y el CSV conservó sus IDs. Salida: [github-recovery-results.txt](github-recovery-results.txt).
- **Contraste nominal:** siete combinaciones de la paleta cumplen los umbrales AA aplicables a texto normal o grande. Se oscureció la tinta del botón coral para superar 4.5:1. Cálculos: [contrast-results.json](contrast-results.json). Se inspeccionaron capturas móviles y de escritorio.

## Capturas de referencia

[Selector de escritorio](screenshots/selector-1440.jpg) · [Selector móvil](screenshots/selector-390.jpg) · [Invitación móvil](screenshots/invitacion-390.jpg) · [Aceptación](screenshots/destino-390.jpg) · [Negociación](screenshots/denegada-390.jpg).

## Límites y pendientes reales

No se ha ejecutado la interfaz de Google Colab, su proxy de iframe, la descarga real del navegador ni el montaje opcional de Drive. La reproducción comprueba el Python y los archivos, y usa una ruta temporal equivalente en lugar de `/content/re-junte/`. Se comprobaron por separado la recuperación desde ZIP y la clonación real desde GitHub; ninguna de ellas sustituye la comprobación de la interfaz de Colab. No se instalaron dependencias de ejecución para la operación en Colab.

No se han probado Safari, Firefox, un lector de pantalla físico, reproducción de un video real ni servicios de previsualización de mensajería. La prueba de Tab comprueba que el foco permanece en el diálogo o en el ciclo nativo del navegador; los controles del fondo son inertes por `showModal()`. El cálculo de contraste no sustituye una auditoría integral de accesibilidad y usa colores nominales sin la textura ligera.

La consulta HTTP a la dirección candidata de GitHub Pages devolvió 404 antes de subir esta implementación. GitHub Pages requiere su activación y una comprobación remota. `url_publica` permanece vacía, y la exportación actual entrega **cero enlaces definitivos**. No se afirma un despliegue ni una URL pública disponible. Los invitados son ficticios; no hay video. La aplicación no registra asistencia y sus tokens no aportan privacidad.
