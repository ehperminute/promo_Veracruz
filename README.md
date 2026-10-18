# Veracruz map — navigation + visitor guides (18 Oct 2026)

## Apply on existing Codespaces repository

This is an ADDITIVE PATCH based on `VERACRUZ_MAP_EXPERIENCE_INTERACTION_UPDATE_2026-10-17.zip`.
It keeps `site/index.html`, the Planner, `site/data/map_points.geojson` and all SQLite/research sources unchanged.

In `promo_Veracruz` repository root:

```bash
cp site/js/map-explorer.js site/js/map-explorer.js.before-guides
cp site/css/map-explorer.css site/css/map-explorer.css.before-guides
unzip -o VERACRUZ_MAP_REGIONS_GUIDES_NAV_2026-10-18.zip
```

Reload homepage (Ctrl+Shift+R). If using local server, launch from the repository root:

```bash
python -m http.server 8000 --directory site
```

Rollback frontend files (leaves new supplemental JSON harmless):

```bash
cp site/js/map-explorer.js.before-guides site/js/map-explorer.js
cp site/css/map-explorer.css.before-guides site/css/map-explorer.css
```

## Included changes

* Theme > official tourism region > municipality > activity guide navigation.
* Breadcrumb trail and Back/Forward buttons. Regional dropdown zooms the map to that region.
* More readable EN/ES activity names, with best-effort English fallbacks under Japanese UI (no false claim of complete Japanese translation).
* Source-linked mini guides. There are 216 documented municipality/activity pairs; 55 have source-backed original Spanish phrases suitable for a brief excerpt. Others explicitly say the original descriptive text is missing.
* A photo manifest with **2 source-checked examples** only: Quiahuiztlán for Actopan archaeology and El Tajín for Papantla archaeology. Photo credits link to Wikimedia Commons. Images are remote HTTPS; require internet access.
* Condensed municipal-coordinate notice rather than the old repetitive disclaimer.
* Existing current map experience color coding and clustering preserved, no road-route optimizer included.

## Data and validation

* `site/data/map_regions.json`: sourced 7 tourism regions and **all 212 municipalities** (name correspondence checked; no omissions or duplicates), from the official portal `https://veracruz.mx/region.php?id=1` through `id=7`.
* `site/data/map_guide_notes.json`: read-only derivation from the latest recovered SQLite `VERACRUZ_PP3_SOURCE_FIRST_EVIDENCE_REPAIR_AND_OR_SENSITIVITY_2026-10-17` database. Does not add claims.
* `site/data/map_photos.json`: curated, explicitly credited; never auto-match arbitrary stock images to places.
* Original 295 official web-card description texts remain unavailable in the recovered database. We **do not** invent them.
* Municipality coordinates remain flagged approximate/unverified. Region membership does not make attraction locations precise.

## Tests completed

Node `--check` succeeds; data JSON valid; automated Chromium UI smoke test passed theme + region filtering, municipality drill-down, guide open, Back, Forward, with no browser JS errors. Full MapLibre tile and remote Wikimedia image rendering could not be tested in the restricted browser environment; verify those in Codespaces.

## Source photographs and licenses

* Quiahuiztlán (Actopan), photo by Adam Jones, CC BY-SA 2.0, https://commons.wikimedia.org/wiki/File:Quiahuiztlan_Archaeological_Site_-_Veracruz_-_Mexico_-_05_(16057710431).jpg
* El Tajín (Papantla), photo by JEAFotoarte75, CC BY-SA 4.0, https://commons.wikimedia.org/wiki/File:El_Taj%C3%ADn_zona_arqueol%C3%B3gica_precolombina_35_Papantla_de_Olarte,_Veracruz,_M%C3%A9xico.jpg

## Next research/data enrichment work (not in this patch)

Verify and geolocate named attractions individually. Recover remaining original descriptions, photographs, practical details (hours, tickets, accessibility, seasonality) per entry from authoritative sources. No fabricated travel-time estimates.
