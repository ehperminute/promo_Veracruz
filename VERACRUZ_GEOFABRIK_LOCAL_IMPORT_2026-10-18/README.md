# Veracruz map — offline bulk OSM importer (no Overpass)

## Why this package exists
The last `run_report.json` showed **0 successful tiles and 0 extracted locations**. Two Overpass APIs failed (500/502/timeout), and the resumable importer skipped the remaining areas. Running it repeatedly against those servers is not a productive approach.

This tool **does not contact Overpass**. Instead it downloads Geofabrik's single, published **Mexico `.osm.pbf` extract** (currently roughly 600–700 MB) and searches it **locally** for named museums, archaeological sites, waterfalls, beaches, viewpoints, caves, and other tagged tourist features. The data contains all Mexico, so it uses Veracruz municipality-reference proximity as a preliminary geographic screening step—not proof of administrative jurisdiction.

## Installation in Codespaces
Extract ZIP in the `promo_Veracruz` repository root:

```bash
unzip -o VERACRUZ_GEOFABRIK_LOCAL_IMPORT_2026-10-18.zip
python -m pip install osmium
python VERACRUZ_GEOFABRIK_LOCAL_IMPORT_2026-10-18/import_local_osm.py .
```

A running Codespaces with enough disk space and internet access is required. Processing the full Mexico extract will take time; there is no need to keep the website HTTP server running during the import. Geofabrik is the upstream provider: https://download.geofabrik.de/north-america/mexico.html

The download is resumable via `curl -C -`, and finished downloads are reused. The result JSON is cached in `.veracruz_osm_checkpoints/geofabrik_osm_candidates.json` so it can be inspected independently. A data-quality audit is created in `.veracruz_osm_checkpoints/geofabrik_audit.json`.

Already have Mexico `.osm.pbf`? Avoid downloading it again:

```bash
python VERACRUZ_GEOFABRIK_LOCAL_IMPORT_2026-10-18/import_local_osm.py . --pbf /path/to/mexico.osm.pbf
```

Want a research-only dry-run? Add `--no-apply`; it will create the candidate JSON without modifying the website.

## What changes

The existing site merger is bundled and re-used, which creates timestamped backups before it updates:

- `site/data/attractions.csv`
- `site/data/attractions.geojson`
- `site/js/map-attractions.js`
- `site/index.html`

The 35 hand-curated attractions are preserved. Source records in `site/data/tourism_catalog.csv` and the PP3 SQLite research database are never overwritten by this importer. OSM-derived points retain an OSM link and remain marked as research candidates, with no invented tourist descriptions, visitor entrances, or photographs. State-border membership and false duplicates still require review.

At statewide zoom, curated attractions stay visible while OSM candidate markers appear at closer zoom or in name search.

## Testing and limits

`test_offline.py` exercises node/way/relation extraction, name/type filtering, and coarse Veracruz geographic screening using simulated OSM objects. The bundled `finalize_map.py` was separately tested with simulated OSM query results. **Neither test verifies an actual full `.osm.pbf` run**, since Geofabrik downloads and `pip` are inaccessible in the authoring environment. If the install fails, save terminal output; do not keep trying Overpass.

OSM source is available under Open Database License (ODbL). Retain OpenStreetMap attribution on the site and audit extracted data before presenting candidate places as authoritative.
