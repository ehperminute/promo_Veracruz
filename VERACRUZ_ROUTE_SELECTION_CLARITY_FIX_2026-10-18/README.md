# Veracruz regional route selector — targeted correction

The map planner now uses **one** “Select places on map” button. It reveals gold markers for attractions actually supported by the prepared Xalapa–Coatepec–Xico road graph. Tap one for start, then another for destination; it moves to the destination phase automatically. Subsequent optional stops can be added by turning map-selection mode on again or via search. Other tourism markers remain available for guides, but cannot be routed until the road graph is expanded.

Road distance is displayed after Dijkstra calculates it. The previous 30–50 km/h travel-time guess is removed because road speeds and entrances have not been verified.

## Install in promo_Veracruz root

```bash
unzip -o VERACRUZ_ROUTE_SELECTION_CLARITY_FIX_2026-10-18.zip
python VERACRUZ_ROUTE_SELECTION_CLARITY_FIX_2026-10-18/install.py .
```

Backups automatically created. Changes only `site/js/route-planner.js`, `site/css/route-planner.css`, and their versioned references in `site/index.html`. Existing road graph, tourism data and map explorer remain untouched.

If installation says `STOP — different route planner version`, do not force overwrite: attach the current `site/js/route-planner.js` and `site/index.html` to ChatGPT. The patch is built against the previous `VERACRUZ_ROUTE_USABILITY_FIX`.

The routing algorithm still finds a distance-minimizing path over the current regional OSM graph, not a traffic-aware route. It assumes your selected stop order; it does not optimize that order.
