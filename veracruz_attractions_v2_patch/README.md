# Veracruz — editable attraction catalog and sidebar guides (v2)

This is an **upgrade** for the previously installed `VERACRUZ_ATTRACTIONS_ON_MAP_2026-10-18.zip`, not a new standalone page. It does not change `site/js/map-explorer.js`, its original municipality data, or the SQLite research database.

## Install from the repository root (Codespaces)

```bash
unzip -o VERACRUZ_ATTRACTIONS_GUIDES_EDITABLE_2026-10-18.zip
python veracruz_attractions_v2_patch/install_attractions_v2.py .
```

Refresh your existing homepage in the browser. The running Python HTTP server normally does **not** need a restart.

## What changes

- **24** geolocated named attraction records: preserves all 18 previously mapped sites and adds **six source-linked records** (Museo de Arte del Estado de Veracruz, Cuajilote, Vega de la Peña, Jardín de las Esculturas, Museo del Café, Cascada Naolinco).
- **One editable CSV**: `site/data/attractions.csv`. You can open it with spreadsheet software to change an attraction's name, coordinates, icon, type, municipality, English/Spanish description, practical notes, photo URL and credit, and source.
- **Map generation**: `site/data/attractions.geojson` generated from that CSV. It is the file the browser reads. The original `attractions_batch1.geojson` remains untouched, but is no longer the active attraction layer.
- **Separate concerns**: clicking a marker opens the full travel guide in the **right sidebar**; the popup stays short (name + button to view guide). Photos appear when a Wikimedia Commons URL is supplied.
- Original coordinates still distinguish general-area points and site-level points; **no verified road entrances are claimed**.

## How to edit / add a location

1. Edit **one row** in `site/data/attractions.csv`. For a new attraction, duplicate a row, set a *new unique* `id`, its `name`, `lat`, `lon`, and verified `source_url`. Use an existing icon emoji such as `🏛️`, `💧`, `🌊`, `🌿`, `🏰`, `🎨`, `☕`.
2. For an image, fill `photo_url` (direct HTTPS image), `photo_credit` (photographer + license), and `photo_source_url` (photograph's source page). Leave all three blank if you have no verified photo.
3. From the repository root run:

   ```bash
   python tools/build_attractions.py .
   ```
4. Refresh the map. The importer validates latitude/longitude, unique IDs, known icons, source links, and image attribution; if validation fails, it **does not replace** the old GeoJSON.

You do **not** need to change JavaScript each time a destination or description is added. You must rebuild the GeoJSON after editing the CSV. It is compatible with static GitHub Pages; no backend needed.

## Important limitations

- These are **24 confirmed mapped features or locations**, not all tourism products. The source research contains 49 named-place candidates, **31 of which were unresolved** in the first audit. Six additional sourced sites were added in this update; many broad or ambiguous candidates are still unresolved.
- The research master also has **295 tourism-product cards**, many of which describe *tours*, *routes*, or *regions*, rather than uniquely geolocatable attractions. They should not all become arbitrary map pins.
- Editorial descriptions are a short first pass, mostly English and Spanish. The sidebar retains the original geographic source links. A Japanese tourist-article translation pass is still outstanding.
- **Six licensed Commons photo URLs** are supplied. They require access to Wikimedia Commons in your browser and may be blocked by external networks. The interface hides a broken image instead of replacing it with stock photography.
- This package does **not** claim 24 verified visitor entrances and cannot yet be used for final road routing.

The installer takes backups under `site/.attractions-backup-YYYYMMDD-HHMMSS/` of all overwritten files. Running twice should be a no-op.
