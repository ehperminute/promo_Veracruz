# Veracruz map visible-marker and contextual-sidebar repair

This patch is designed specifically for the October 18 marker repair already installed in `promo_Veracruz`.
It changes **only** `site/js/map-explorer.js`, `site/css/map-explorer.css`, and asset query versions in `site/index.html`.
It does not change `map_points.geojson`, the tourism SQLite database, guides, descriptions, or the main destination explorer.

## Install

From repo root:

```bash
unzip -o VERACRUZ_MAP_VISIBLE_MARKERS_SIDEBAR_2026-10-18.zip
python install_map_ui.py
```

The installer verifies existing JS/CSS checksums, creates timestamped backups, and safely refuses to overwrite an unfamiliar version. Refresh the site afterward.

## Changes

1. Marker icons use divs with essential inline marker styling, eliminating default button appearance and avoiding reliance on cached marker CSS. They keep geographic MapLibre anchors, activity colors and filter selection.
2. Cache-busted CSS and JS references in index.html ensure compatible asset versions.
3. Contextual sidebar: municipalities within current view first, type names and named activities, explicitly labeled counts. Other places can be expanded without losing records.
4. Opening a place now shows its detail instead of simultaneously rendering a 61-place directory below it.

Markers still represent municipality reference coordinates; they are *not* precise geolocated attractions. Activity counts mean documented municipality–activity links, not count of attractions.

Testing note: JS syntax, sample GeoJSON integration and Chromium layout test performed with simulated MapLibre; we can't access your live Codespaces browser. The most direct cause indicated by screenshot is an unstyled browser-default button, plausibly from stale map CSS. There are no claims of verified live behavior.
