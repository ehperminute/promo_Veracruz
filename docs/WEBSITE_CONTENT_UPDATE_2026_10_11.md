# Sitio Veracruz — actualización acumulativa de contenido (2026-10-11)

## Alcance implementado

La actualización consolida **las etiquetas editoriales de 12 clústeres**, el atlas de grupos y panel didáctico previamente preparados, las actividades de aventura con fuente y las fichas con imágenes / atractivos nuevos. **No se ha cambiado la clasificación PAM, la matriz S4 original ni el número de clústeres.**

| Campo | Cobertura del sitio |
|---|---:|
| Destinos | 55 |
| Fotografías con archivo, autor y licencia identificados | 21 destinos |
| Sin fotografía identificada todavía | 34 destinos |
| Atractivos cotejados directamente contra fichas oficiales | 114 registros / 28 destinos |
| Actividades de aventura concretas en fichas | 60 registros / 37 destinos |
| Clústeres publicados (provisionales) | 12 (sin cambios) |
| Traducciones de la interfaz | Español, inglés, japonés |

## Significado de los datos

**Imágenes:** `data/reference/destination_photo_manifest.csv` contiene el nombre exacto de cada archivo de Wikimedia Commons, la imagen remota, la página de autoría, licencia y un pie de foto traducido. No se incluyen archivos JPG. La URL de Commons puede dejar de funcionar o tener restricciones externas; la interfaz oculta una imagen que falle. El hecho de que exista la página del archivo NO equivale a que el enlace de imagen haya sido probado en el sitio público.

**Atractivos:** se publican únicamente las 114 filas con `estado_cotejo_actual=TEXTO_RESPALDADO_EN_FUENTE_OFICIAL` de `data/evidence/s4_atractivos_fuentes_v2.csv`. Las 89 filas `PENDIENTE_COTEJO_INDIVIDUAL` permanecen para investigación y NO se muestran como verificadas. Se muestran nombre y fuente; las descripciones complementarias están en español, y solo se despliegan como párrafo en la interfaz española. Los nombres propios originales permanecen en los otros idiomas.

**Aventura:** se publican las filas marcadas para difusión en `data/evidence/s4_actividades_aventura_consolidadas.csv` más ocho entradas de la revisión posterior cuya procedencia se identifica en `data/evidence/s4_aventura_public_followup.csv`. Se excluyeron resultados sin municipio claro, eventos históricos usados como prueba de oferta actual y actividades meramente propuestas. Incluimos registros de un plan municipal histórico y una ruta comunitaria, con fuente; **no implican disponibilidad comercial, acceso libre ni servicio vigente**.

**Dos versiones del indicador Adventure:** `model_themes` conserva exactamente la matriz original utilizada en el modelo publicado; `themes` es la selección *editorial para el visitante*. En esta última, `adventure` aparece si y solo si tenemos al menos una actividad concreta publicada con fuente. Por eso hay 37 fichas con Adventure en el sitio, aunque el indicador original del modelo solo fuese 1 en 19 municipios. Esto **no es** un nuevo resultado de clustering: el sitio informa de más actividades, pero no reentrena PAM.

**Búsqueda:** además del nombre, busca por región, nombre de atractivo y actividad específica; ignora diferencias de tildes (por ejemplo, `rapel` busca `rápel`).

## Decisión metodológica

Se conservan los grupos de 12 del prototipo como **exploratorios**. La revisión de perfiles de S4, las tres pruebas de clustering posteriores y las correcciones propuestas pertenecen al historial experimental, no a los resultados oficiales publicados. No mezclar el indicador visual de Adventure con los nueve indicadores históricos de PAM.

## Comprobaciones

```
python scripts/web/export_destinations.py
python -m pytest tests/test_site_content_20261011.py -q
node --check site/js/app.js
```

Una prueba de navegador con HTML/CSS/JS y datos incrustados pasó: 55 fichas, 12 tarjetas de grupos, búsqueda `rafting`/`cascada`, apertura de Catemaco y cambios de idioma EN/ES/JA sin errores JS. La prueba de navegador se ejecutó con una representación local porque el entorno bloqueó acceso HTTP incluso a localhost. **La entrega de imágenes desde Commons al navegador público no se ha comprobado**.

## Pendiente / antes de publicación

- Revisar cambios de otros integrantes del repositorio antes de sustituir `site/js/app.js` o `scripts/web/export_destinations.py`.
- Abrir GitHub Pages y revisar al menos 5 fotos y créditos con internet normal.
- No actualizar `CURRENT_PROJECT_STATUS.md`, la clasificación S4 oficial ni el sitio con nuevos clústeres sin aceptar antes una solución.
- Completar fotografías de 34 destinos restantes progresivamente; no usar imágenes de municipios vecinos sin declararlo.
