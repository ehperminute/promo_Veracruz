# Veracruz — final map consolidation / freeze (18 October 2026)

This is the **last planned map patch before resuming the Data Science project**. It expands the existing attraction layer using individually mapped and named OpenStreetMap points. It does *not* claim that every Veracruz tourist site has been found, that every source record is an attraction, or that a mapped point is an accessible entrance.

## Requirements

- Your existing `promo_Veracruz` repository with the October 18 **Full Catalog Map** update already installed (`site/data/attractions.csv`, `site/data/tourism_catalog.csv`, `site/data/attractions.geojson`, `site/js/map-attractions.js`).
- Python 3 (standard library only), internet access from Codespaces for the one-time OSM query.
- Run from the repository root.

## One final installation

1. Upload `VERACRUZ_MAP_FINAL_FREEZE_2026-10-18.zip` to the repository root.
2. Run:

```bash
unzip -o VERACRUZ_MAP_FINAL_FREEZE_2026-10-18.zip
python VERACRUZ_MAP_FINAL_FREEZE_2026-10-18/finalize_map.py .
```

**The online step can take several minutes.** This is a one-time request to a public Overpass service, not a background service. If the provider is busy or denies the request, the script exits before changing any site files. Don't repeatedly hammer public servers; the current map remains usable with its existing pinned attractions.

3. Reload the page. Codespaces may need its HTTP server restarted *only if the Codespace suspended*.
4. **Search** for any newly mapped name or zoom to approximately level 9 to see additional OSM attraction pins. At statewide zoom, the original curated pins stay visible and the much larger OSM collection is hidden to avoid a carpet of symbols. The 495 previously recovered source records stay searchable as before.
5. When satisfied, commit changes:

```bash
git add site/data/attractions.csv site/data/attractions.geojson site/data/osm_geocoding_audit.json site/js/map-attractions.js site/index.html
git commit -m "Freeze Veracruz attraction map and bulk OSM geocoding"
```

## What is imported, and what is not

- Imports named OSM nodes, ways and relations tagged as tourist attractions, museums, galleries, archaeological sites, castles/forts, ruins, waterfalls, beaches, caves, springs, viewpoints and nature reserves **within the mapped Veracruz state boundary**.
- A close duplicate with the same name as one of your manually curated attractions is skipped. Your edited descriptions, photos, icons, research database and the 495 source records are preserved.
- OSM points not matched to our original catalog are labeled `OpenStreetMap — additional mapped place (review)`. They are **not independently verified against a second source**. They may refer to broad sites rather than entrances.
- Does **not** invent opening times, fees, entrances, images, tours, descriptions or route metrics. OSM credits and URLs are saved in the CSV. Approximate geographical extent remains explicit (`mapped_area`).
- The map's full editorial content remains unfinished where original source text or photos haven't been recovered. This script is a bulk coordinate-enrichment and final UI-stabilization step, not a completed regional tourism encyclopedia.

## Editing a location in the future

Modify one row in `site/data/attractions.csv`, then run:

```bash
python tools/build_attractions.py .
```

No new map patch is required. Edits to the researched master SQLite are not part of this command.

## Audit and rollback

- An audit is written to `site/data/osm_geocoding_audit.json` listing all OSM records imported and duplicates skipped, the import date, and source.
- Backups of the modified CSV, GeoJSON, JS, and HTML are placed in the repository root under `veracruz_map_final_backup_<UTC timestamp>/`.
- If the request fails, no site files are overwritten. If the display regresses after a successful import, restore those backed-up files.
- The importer accepts `--osm-json <local Overpass JSON file>` for repeatable offline testing without another web request.

## Why the precise number of attractions cannot be predicted in advance

OSM is a volunteer-maintained map, so its quantity and quality of named tourist features vary, and there can be duplicates or missing metadata. The script prints the **actual count after import**. It does not equate the original 495 research rows with 495 separate physical attractions. Source tags and georeferences should be verified before using these points as driving destinations.

## Project resumes after this

Freeze the site, then begin OR with a **tiny graph you implement yourself**, Dijkstra's algorithm using loops and dictionaries, a NetworkX validation, then road-network routing between verified visitor access points. Do not wait for every photo to be finished before returning to the analytical work.
