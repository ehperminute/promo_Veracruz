# Veracruz marker repair — diagnosed against your uploaded site files

This patch changes only:
- `site/js/map-explorer.js`
- `site/css/map-explorer.css`

It leaves `index.html`, `site/data/map_points.geojson`, all descriptions, photographs, region navigation, and SQLite files unchanged.

## Install in Codespaces

Upload `VERACRUZ_MARKERS_STABLE_FIX_2026-10-18.zip` into your `promo_Veracruz` repository root, then run:

```bash
unzip -o VERACRUZ_MARKERS_STABLE_FIX_2026-10-18.zip
python install_marker_repair.py
```

The installer verifies both existing files match your diagnostic upload and backs them up. It refuses to overwrite unexpected changes. No server restart is normally needed; hard-refresh the preview or open a private tab.

## What changed

The old marker overlay depended on `style.load` and native style layers, which are not rendering in your preview. This version uses `maplibregl.Marker` objects anchored to exact existing municipality reference coordinates. It does not depend on style-layer initialization. Themes appear as multicolor marker rings. Theme/activity filters, search, region selector, sidebar and navigation remain. Default is 61 evidence-linked municipalities; enable *All municipalities* to display all 212.

**Trade-off:** the 61 municipality markers appear individually at statewide zoom rather than as aggregated clusters. This is an intentionally simpler intermediate behavior to restore functionality and preserve multi-theme colors. We can revisit clustering once the points are reliably visible.

**Not claimed:** precise attraction geocoding or original description restoration. This patch does not edit those records.

## Test results and limitation

JavaScript syntax checked with Node. Offline Chromium test using a MapLibre API mock and the exact uploaded GeoJSON confirmed 212 constructed markers; 61 displayed initially; 22 matched the water filter; clicking Actopan opens its detail; switching to all municipalities displays 212; zero JS errors. MapLibre's remote basemap could not be loaded in this environment, so visual confirmation with the real renderer still needs the user's browser.

## Rollback

The installer prints the backup filename for each replaced file; copy backups back to their original names to undo this patch.
