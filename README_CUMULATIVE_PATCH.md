# Veracruz — parche acumulativo del sitio (revisión del 11 de octubre de 2026)

**El parche NO está instalado ni publicado en GitHub.** Está basado en el último volcado completo del repositorio disponible en esta conversación (`ehperminute-promo_veracruz-8a5edab282632443.txt`), con los cambios anteriores de etiquetas, galería y actividades reunidos. Si alguien modificó los mismos archivos después del volcado, revisar los cambios antes de sobreescribir.

## Qué incluye

- **21 imágenes reales con identificación de lugar y metadatos de créditos**, servidas remotamente desde Wikimedia Commons (los JPEG no están dentro del ZIP).
- **114 descripciones/nombres de atractivos cotejados con fichas turísticas oficiales**, repartidos en 28 destinos. Los 89 aún no revisados individualmente se conservan como investigación, NO se publican en la interfaz.
- **60 registros de actividades concretas** (52 del piloto anterior y 8 de la investigación adicional), distribuidos en 37 destinos, con enlace a las fuentes.
- Búsqueda por nombre de localidad, actividad o atractivo, con o sin acentos.
- Etiquetas de grupos en EN/ES/JA y panel didáctico previo. **Las 12 asignaciones de clúster no cambian**.
- Traducción de los títulos y advertencias de la interfaz (los nombres de atractivos y de actividades mantienen la terminología de las fuentes en español).
- Comprobaciones automáticas y el documento `docs/WEBSITE_CONTENT_UPDATE_2026_10_11.md`.

### Archivos principales

`site/index.html`, `site/js/app.js`, `site/css/styles.css`, `site/i18n/{en,es,ja}.json`, `site/data/destinations.json`, `scripts/web/export_destinations.py`, `data/reference/cluster_display_labels.csv`, `data/reference/destination_photo_manifest.csv`, `data/evidence/*`, `tests/test_site_content_20261011.py`.

## Instalación en un Codespace

**Antes:** entrar al directorio raíz del proyecto y revisar `git status --short`; guardar/confirmar primero cualquier archivo modificado por el equipo.

1. Subir este ZIP al directorio raíz del repositorio.
2. Revisar `unzip -l PP1_VERACRUZ_WEB_CUMULATIVE_2026_10_11.zip`.
3. Extraer: `unzip -o PP1_VERACRUZ_WEB_CUMULATIVE_2026_10_11.zip -d .`.
4. Reconstruir la página: `python scripts/web/export_destinations.py`.
5. Verificar: `python -m pytest tests/test_site_content_20261011.py -q` y `node --check site/js/app.js`.
6. Inspeccionar `git diff --stat` y la página con vista previa de GitHub Pages antes de hacer commit.

**Precaución**: `unzip -o` sobreescribe archivos con el mismo nombre. Si existen ediciones recientes en `site/js/app.js` o el script de exportación, combinar esos archivos en vez de pisarlos automáticamente.

## Limitaciones conocidas

- Las **21 URL de archivos Commons existen y tienen atribución**. Los enlaces de entrega remota de fotografías no se han probado en un navegador con acceso completo a la red; la página oculta la imagen si no carga. Las otras 34 fichas quedan sin foto, no con imágenes falsas.
- No hay evidencia de que cada actividad continúe operativa o tenga reserva disponible. El usuario debe consultar la fuente correspondiente.
- La **etiqueta Adventure que ve el turista** usa actividades efectivamente listadas, mientras que `model_themes` conserva las características históricas usadas para explicar el clustering. No mezclar estos datos.
- Los datos no afirman ocupación o saturación turística a nivel municipal; los clústeres siguen siendo exploratorios.
- Este ZIP reúne el contenido visible del sitio, NO promueve los modelos experimentales A/B/C a producción y NO modifica S5.
