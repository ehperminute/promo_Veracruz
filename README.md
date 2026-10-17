# Veracruz: populated map in existing homepage (17 October 2026)

This package **integrates the map inside the existing site's homepage** above the current destination explorer. It is **NOT** a new `map.html` page and does **NOT** alter the old explorer, your marketing campaign Planner, original catalog files, translations, or research database.

## Source recovered, not recreated

The populated map was generated from the attached **`VERACRUZ_PP3_SOURCE_FIRST_EVIDENCE_REPAIR_AND_OR_SENSITIVITY_2026-10-17(1).zip`** → `veracruz_pp3_master.sqlite` (SQLite SHA-256 `ceb935532c783c5eb8df5fd8abce5c975582fc3262e7d021f121d3a2496dda35`). This is newer than the statewide-OR and restored-description archives. Its input integrity check passed.

- All **212 municipalities** appear in the geographic export with an *approximate municipality reference point* each.
- The initial map shows **61 municipalities having at least one accepted documented activity**, covering **216 municipality–activity pair records** and **78 distinct activity features**. A checkbox reveals all **212**.
- The other **151** retain their place in the database; **lack of documented activities is not evidence of tourism absence**.
- Of the 216 pairs, **55** retain original-source passage support; **161** are source-linked summaries awaiting original text. The UI labels this difference for each activity.
- **295 official webpage product descriptions still have not been restored to their original wording** in this packaged master; do NOT treat paraphrases as originals. This export does not invent or substitute descriptions.
- Map pins show **municipality-scale approximate points**, **not** actual geographic coordinates of activities, attractions, festival venues, municipal boundaries, or road-network stops. Travel optimization requires additional geocoding and road travel times.

## Install in current repo (GitHub Pages)

Extract the ZIP, then from the extracted folder or anywhere in a terminal:

```
python install_map.py /path/to/promo_Veracruz
```

On Windows, for example:

```
py install_map.py C:\\Users\\you\\promo_Veracruz
```

The installer requires the existing `site/index.html` and inserts a map section immediately before the existing `destinations` section if present, otherwise before `</main>`. It creates `site/index.before-map.html` (once), and copies exactly **three** files into the site's existing tree:

- `site/data/map_points.geojson` — **populated** from recovered master;
- `site/js/map-explorer.js` — scoped MapLibre map, marker groups, filters, bilingual activity names, search, source links;
- `site/css/map-explorer.css` — scoped responsive map styling.

It links MapLibre's CSS/JS assets by CDN in `index.html`; no frontend build tooling is required. It does **not** overwrite `destinations.json`, `app.js`, i18n JSON, Python pipeline outputs, or the Planner. Re-running is idempotent (no duplicate map section or imports). No internet is required to install, but the map tiles and CDN require internet to render in the browser.

To test locally, from repo root:

```
python -m http.server 8000 --directory site
```

Open `http://localhost:8000`. Test filtering by *aventura* and *naturaleza*, switch ES/EN/JA using the existing language control, and click a municipality to see source-backed activities.

### Rollback

Restore `site/index.before-map.html` as `site/index.html`. Optionally delete the three `map-*` files and `data/map_points.geojson`. Your existing catalog never changes.

### Rebuilding the GeoJSON later

The build script is provided under `tools/export_map_geojson.py` and **only reads** the SQLite database. It does not need to run to install this patch. To regenerate after a reviewed database change:

```
python tools/export_map_geojson.py /path/to/veracruz_pp3_master.sqlite --output site/data/map_points.geojson
```

The exporter checks database integrity, and refuses a database with unexpected municipality or accepted-evidence counts. Update checks deliberately when your database evolves.

### Notes

- Markers use a green pin plus multiple colored activity-category dots. A municipality with three families of experiences shows all three colors; it is not forced into one primary category.
- At state zoom, nearby pins group into numbered bubbles; click to zoom into that group.
- The default filter emphasizes documented experience coverage. All other municipalities are still accessible.
- Basemap uses MapLibre GL JS with OpenStreetMap raster tiles for an educational prototype. For substantial public traffic, use a suitable compliant hosted tile service; do not assume OSM's free community tile server guarantees production capacity.
- You should commit the new site files after visual inspection and then deploy via your existing GitHub Pages workflow.
