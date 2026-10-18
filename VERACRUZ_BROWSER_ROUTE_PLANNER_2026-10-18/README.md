# Veracruz: browser-side regional route planning (OR)

**What this actually does:** Adds a **Plan a route** section to the map sidebar of the current GitHub Pages homepage. Visitors select a start, finish, and optional intermediate attractions within the Xalapa–Coatepec–Xico test region. JavaScript runs Dijkstra *in their browser* on a prepared road graph, draws an actual graph-following polyline on the MapLibre map and reports road distance. They can also add candidates near that path. No new hosting service, API key, or JavaScript work is needed.

## Install (one command, after unzipping)

From the `promo_Veracruz` repository root, after your separate national attraction extraction has finished:

```bash
unzip -o VERACRUZ_BROWSER_ROUTE_PLANNER_2026-10-18.zip
python VERACRUZ_BROWSER_ROUTE_PLANNER_2026-10-18/install.py .
```

The installer finds `.veracruz_osm_checkpoints/mexico-latest.osm.pbf`. If needed, it makes a **regional** graph under `data/processed/xalapa_roads.json.gz` (one-time CPU-intensive operation; may take minutes). It then exports `site/data/routes/xalapa_network.json`, which the browser uses for fast route queries. The GeoJSON pins, attraction CSV, tourism catalog and previous map code are not changed. The only homepage edit is a CSS/script reference; dedicated JS and CSS files are added. Backups are created.

If you already ran the previous Python OR road-graph builder, the installer reuses `data/processed/xalapa_roads.json.gz` without rescanning the Mexico PBF.

Your static HTTP server works; just refresh the page. In the map's right sidebar, find **Plan a route** / **Planear ruta**. Select an origin, destination, optional intermediate stops and click **Find shortest road route**. A blue line should follow the road graph; orange dots mark your selected attraction locations. Near-route suggestions are based on *straight-line proximity to the road polyline*, **not** verified detour driving time.

**Important constraints:** This is a regional prototype only. It optimizes **approximate road distance**, not driving time. OSM road data are simplified (some access restrictions, lane turns, closures and vehicle rules aren't modeled). Attraction points have not been verified as vehicle entrances. The line is not turn-by-turn navigation. Do not use it for safety-critical driving.

If the site says that routing data could not be loaded, check that `site/data/routes/xalapa_network.json` exists and that you are viewing the site through HTTP rather than `file://`. Use browser DevTools console/network panel to check failed requests.

To revert, restore `site/index.html` from the latest `.before-route-planner-*` backup and remove `site/js/route-planner.js`, `site/css/route-planner.css`. Keep `site/data/routes/xalapa_network.json` if you want to preserve the prepared dataset.

**Git:** Keep the raw Mexico PBF outside Git. The regional browser graph may be committed if it stays small; the installer enforces a 35 MB limit. Verify `git status` before committing.

## Algorithm

The browser uses a binary min-heap Dijkstra and retains the predecessor chain to reconstruct the road polyline. For multiple stops it solves each leg in selected order, rather than optimizing stop order (that is a later orienteering/TSP-style problem). `export_browser_graph.py` converts the Python road graph to indexed arrays; you can inspect and modify the Python exporter without touching the homepage.
