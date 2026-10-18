# Veracruz PP — OR shortest-path baseline (real road network)

This is an **analytical project module**, not a website/UI patch and not a tutorial script. It reads the downloaded Mexico OpenStreetMap PBF locally, extracts a *regional* driving network, then runs our own priority-queue Dijkstra on that network. Results are written as GeoJSON for later visualization.

## Prerequisites

* The Mexico PBF already downloaded into `.veracruz_osm_checkpoints/mexico-latest.osm.pbf` by the previous importer.
* Python with the `osmium` library (already installed in Codespaces for the attraction importer).
* The current project's `site/data/attractions.csv`, **not** the obsolete S4 dataset.
* Do not run a second long OSM job simultaneously with the existing attraction extraction; wait for the previous job to complete or stop it deliberately.

## Install (from the `promo_Veracruz` repository root)

Extract the ZIP into the repository root, leaving the `tools/` folder intact. The file should be `tools/routing/route_network.py`. No overwrite of website or PP3 database.

## 1. Extract a regional graph

```bash
python tools/routing/route_network.py build \
  --pbf .veracruz_osm_checkpoints/mexico-latest.osm.pbf \
  --bbox 19.36 -97.09 19.63 -96.82 \
  --out data/processed/xalapa_roads.json.gz
```

Coordinates in `--bbox` are **south west north east**, covering the Xalapa–Coatepec–Xico test region. This streams the national file once; it is **preprocessing**, and can be slow. The graph is saved, so you don't repeat this step for every route request. If a `build` fails, no completed graph is overwritten.

## 2. Solve a real route between mapped attraction points

```bash
python tools/routing/route_network.py route \
  --graph data/processed/xalapa_roads.json.gz \
  --attractions site/data/attractions.csv \
  --from "Jardín de las Esculturas" \
  --to "Jardín Botánico F.J. Clavijero" \
  --out data/processed/route_xalapa.geojson
```

The tool prints total **road distance** (kilometers), closest-road-node offset at each end, explored node count, and output location. The GeoJSON contains a `LineString` over OSM road graph nodes plus the two selected attraction points. This is a distance-optimal route in a **simplified model**, *not* Google-Maps-equivalent car navigation. Attractions are not verified entrances; the route is snapped to nearby graph nodes, and distance from point to road should be reviewed. Traffic, turn restrictions, closures, speed and estimated travel time are **not** included.

If the snapping radius is exceeded (2 km by default), the program refuses to invent accessibility and explains the problem.

## 3. Next OR/stochastic steps

* Compare shortest network distance to a straight-line baseline (always report both and their limitations).
* Check simple connectivity, verify entrances / accessible vehicle access; use a smaller local bbox when needed.
* Add **travel-time weights** using carefully documented speed assumptions or verified data; distinguish shortest distance from shortest time.
* Run the algorithm against NetworkX and record agreement, search duration, graph size, number of expanded nodes.
* Then introduce multiple-stop tourist itinerary optimization and uncertainty in travel times.

## Tests

The self-contained synthetic test verifies Dijkstra against NetworkX, one-way links, private-road exclusion, route GeoJSON production, and unreachable destinations. Run with:

```bash
python -m unittest discover -s tools/routing/tests -v
```

An offline synthetic test cannot verify the real Mexico PBF, OSM source quality or the actual routes; the real build must be executed in Codespaces to produce data-grounded results.

## Git hygiene

The raw `.osm.pbf` file and other cache files belong under `.veracruz_osm_checkpoints/`, which should already be `.gitignore`d. If the regional graph grows unusually large, exclude it from Git too. Commit only the script, small validated route GeoJSON, and analytical report as appropriate.
