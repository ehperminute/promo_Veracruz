# Veracruz route planner — usability fix, 18 October 2026

This is an **interface-only** update to the browser-side Xalapa–Coatepec–Xico route planner. It does not modify the OSM-derived road graph, attraction catalog, coordinate data, tourism descriptions, or original map engine.

## Install

From `promo_Veracruz` repository root:

```bash
unzip -o VERACRUZ_ROUTE_USABILITY_FIX_2026-10-18.zip
python VERACRUZ_ROUTE_USABILITY_FIX_2026-10-18/install.py .
```

Then hard-refresh the site. The installer creates a timestamped `.before-route-ui-...` backup with previous HTML, JS and CSS.

## Use

1. Find **Plan a route** in the right panel.
2. Click **Choose start on map**, then click the first eligible attraction pin. The planner switches to **Choose destination** automatically. Click the second attraction pin. Or type part of their names in the search boxes; only up to seven matches are shown at once.
3. Click **Find shortest road route**. The route appears in blue with numbered stops. The road distance appears prominently **on the map and in the right panel**. Time is a rough *illustration assuming an average 30–50 km/h*, **not a validated ETA**.
4. Add intermediate attractions by searching **Find an optional stop** and clicking **Add stop**, or click **Choose stop on map** and tap an attraction pin. Reorder stops with the up/down buttons.
5. To reopen regular attraction guides, simply click map pins when none of the three **Choose ... on map** buttons is active. After destination selection this returns to normal automatically.

The route graph still covers **only Xalapa–Coatepec–Xico**. Clicking a mapped attraction outside that available regional graph displays a visible warning; it cannot be used as a driving stop until regional coverage expands. No live traffic, driving speeds, turn restrictions or verified visitor entrances are available.

## Recover if something breaks

The terminal prints a backup directory. Copy its `site/js/route-planner.js`, `site/css/route-planner.css` and `site/index.html` back to the corresponding `site` paths. The installer refuses to overwrite unknown route-planner versions.
