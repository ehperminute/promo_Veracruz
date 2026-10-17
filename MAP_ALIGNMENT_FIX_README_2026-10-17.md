# Veracruz map marker alignment fix — 2026-10-17

This patch addresses visible marker drift/misalignment in the existing integrated MapLibre map without changing the recovered tourism catalog, municipality coordinates, SQLite database, homepage HTML, or campaign planner.

## Install in GitHub Codespaces

Place `VERACRUZ_MAP_MARKER_ALIGNMENT_FIX_2026-10-17.zip` in the root of the `promo_Veracruz` repository (same directory as `site/`). From that directory, run:

```bash
unzip -o VERACRUZ_MAP_MARKER_ALIGNMENT_FIX_2026-10-17.zip
```

Reload the preview with a hard refresh (Ctrl+Shift+R). If you are running a Python preview server, leave it running; JavaScript and CSS files are loaded on the next refresh.

**Only two website files are replaced**:

- `site/js/map-explorer.js`
- `site/css/map-explorer.css`

**No catalog file is in this ZIP.** `site/data/map_points.geojson` and `veracruz_pp3_master.sqlite` are not changed.

## Changes

- Replaced HTML-positioned location markers and custom screen-space clustering with MapLibre-native GeoJSON map layers and clustering. Marker and basemap positions now share the map's own rendering pipeline.
- Colored rings display all evidenced experience categories for each municipality.
- Disabled scroll-wheel zoom on the embedded homepage map (use +/- controls or pinch on a touch screen).
- Removed scrollIntoView calls that unintentionally moved the whole webpage when a location was selected.
- ResizeObserver tells MapLibre to adjust when the embedded map container changes size.
- Scoped protection from global responsive `canvas` max-width/max-height CSS rules.

## How to check

1. Open the homepage map and locate one documented municipality.
2. Scroll the webpage: the basemap and marker should remain geographically aligned, and page scrolling should not zoom the map.
3. Pan or use +/- to zoom the map: markers must stay attached to their places.
4. Filter by experience, search, and toggle all 212 municipality reference points; both the list and map should update.
5. Click a single icon or cluster: the destination detail or zoom should open.

**Geographic accuracy warning:** The current GeoJSON contains third-party, approximate municipality reference coordinates, not exact attraction coordinates or independently verified municipal seats. This patch fixes marker rendering but does not resolve any underlying coordinate inaccuracies. Review individual problematic municipalities separately against authoritative geographic data.

## Revert

With Git: `git restore site/js/map-explorer.js site/css/map-explorer.css` (before committing this patch). Or restore the two files from your last working commit or backup.
