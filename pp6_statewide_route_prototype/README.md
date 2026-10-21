# Veracruz statewide driving-route prototype (standalone, additive)

Built against the PP6 2026-10-20 `pp6_research.zip` snapshot. No changes to SQLite, attraction geojson, regional graph, website content, or deployed assets unless **you** install it.

## Install in Codespaces

```bash
unzip -o VERACRUZ_STATEWIDE_ROUTING_PILOT_2026-10-20.zip
python pp6_statewide_route_prototype/install.py .
python -m http.server 8000 -d site
```

Open the forwarded port and find **Rutas viales en Veracruz — prueba** under the original regional planner. Choose start, finish, optionally two intermediate stops, then click **Dibujar ruta vial**. The purple line follows the routing service's roads. The **Abrir indicaciones** link opens external driving directions as a fallback. On mobile the selection fields stack vertically.

## Boundaries and caveats

- Uses an **external** OSRM **demo server**, initiated by an explicit click, not by background bulk collection. At most one query per click with a short cooldown. Demo server has no uptime guarantee, and may restrict access. **Do not use this server as a commercial production backend.** Replace `window.VX_STATEWIDE_ROUTING_BASE` with a permitted compatible service or your own OSRM deployment for production.
- A mapped attraction coordinate is not necessarily a vehicle entrance. Road snapping, vehicle access, tolls and safety require verification. Route distance/duration is estimated without live traffic.
- This demonstration uses GeoJSON road geometries but does **not** optimize stop order; the route visits points in selected order.
- The existing browser-side Dijkstra regional planner is **preserved**, not discarded.
- Depends on Internet connectivity, OSM routing-service availability and OSM/MapLibre map. Google Maps Directions external fallback requires separate availability.
- Attribute OpenStreetMap contributors / OSRM; review tile-service attribution and usage conditions separately.
- Test routing across representative town and rural pairs to find graph gaps and false entrance points before academic claims. If the route cannot be found, say so rather than replacing it with a straight line.

## Why no giant road graph in GitHub Pages?

The old regional graph is 5.6 MB JSON, and the old exporter caps each client graph at 35 MB. A full state road graph may be much larger and expensive to download/route in the mobile browser. The static site can remain on GitHub Pages while a separate routing API returns only the geometry for each requested trip.

## Rollback

Restore `site/index.html` from `site/index.html.before-statewide-route`, then remove `site/js/statewide-route.js` and `site/css/statewide-route.css`. Nothing else changed.
