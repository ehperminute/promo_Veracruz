# Veracruz · estabilización del diario y alineación académica

Una sola entrega que contiene:
- Reparación del botón **Ver ruta / View itinerary** para enlaces `#trip=` y `#draft=` desde la misma página `viajes.html`, más actualización de caché.
- Uniformidad visual y persistencia de la selección ES/EN/JA en `index.html`, `viajes.html`, `enviar-viaje.html`, `proveedores.html` y `planner.html` cuando existan.
- Limpieza **segura y voluntaria** de ZIPs de transferencia no rastreados mediante `archive_zips.py`.
- Informe, campaña y coloquio actualizados con la galería de rutas, diario de gastos y formulario de relatos/fotografías.
- Matriz de funcionalidades realmente implementadas, probadas y propuestas.

## Instalación desde el root de `promo_Veracruz`

```bash
unzip -o VERACRUZ_STABILITY_AND_SUBMISSION_2026-10-25.zip
python veracruz_stability_20261025/patch/install.py .
python veracruz_stability_20261025/tests/verify_site.py .
node --check site/js/trip-journal.js
node --check site/js/trip-gallery.js
python -m http.server 8110 -d site
```

En port 8110, abrir `viajes.html` y pulsar **Ver ruta** en la primera tarjeta; el diario debe mostrar **Coatepec → Xico → Jalcomulco**. Pulsar la segunda tarjeta; el diario debe cambiar a otra ruta sin recargar la página. Cambiar a EN y visitar `enviar-viaje.html` y `proveedores.html`, y comprobar que se conserva el idioma.

**Este ZIP no debe subirse a GitHub.** Extraer el contenido, probar, revisar `git status -sb`, después confirmar y subir los archivos necesarios.

## Limpieza segura de ZIPs

```bash
python veracruz_stability_20261025/patch/archive_zips.py .
python veracruz_stability_20261025/patch/archive_zips.py . --archive
```

El primer comando solo muestra archivos elegibles; el segundo mueve exclusivamente ZIPs **no rastreados de la raíz** a un directorio hermano externo. No toca carpetas `data/`, bases SQLite, paquetes de origen bajo subdirectorios ni historia Git. Si hay ZIPs rastreados, auditar antes de quitarlos mediante Git.

## Cuenta de usuario

**No** añadir login todavía. La edición local y el intercambio por enlace funcionan sin cuentas; los relatos públicos tienen su propia aprobación. Las cuentas solo se justificarían para sincronización privada y almacenamiento de identidad en un backend seguro.

## Límite de verificación

Se realizaron pruebas locales de análisis sintáctico, instalación idempotente, decodificación de la URL aportada y cambios consecutivos `#trip=` en un navegador en memoria. La ejecución de páginas locales por HTTP está bloqueada en el navegador de pruebas de este entorno; el Codespace sigue siendo el lugar para verificar el enlace en una URL real.
