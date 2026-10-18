# Veracruz — Attraction-level geocoding, first research batch (2026-10-18)

Source: recovered latest `veracruz_pp3_master.sqlite` (49 records in `places`). This is an **additive, unmerged audit**: it does not modify or replace the original database, website descriptions, or municipality GeoJSON.

- Named places in recovered master: **49**.
- Named records matched to published location objects: **18**.
- Still unresolved / ambiguous: **31**.
- Visitor entrances verified in this batch: **0**. Do **not** use these points directly as driving destinations yet.

## Files
- `named_places_coordinate_audit.csv`: ALL 49 original named-place records with blank coordinates preserved where uncertain.
- `mapped_attraction_coordinates.csv`: 18 records with source URL per row.
- `mapped_attraction_coordinates.geojson`: mapped points for a separate **attraction map layer** (longitude, latitude EPSG:4326).

## Geographic meaning
Published archaeological site coordinates, waterfall nodes, building reference points, beach/polygon representative coordinates, island and lake reference points have **different meanings**. `mapped_feature_type`, `visitor_entrance_verified`, and `road_routing_ready` expose this difference. A point coordinate does not guarantee entrance accuracy; even 6 decimal digits are not proof of meter-level positional precision.

The El Tajín INAH point is labeled as locality in its entry, not explicitly the ticket-gate point; verify the actual visitor access separately. Distinguish Salto de Eyipantla waterfall from the nearby village. Avoid routing to isolated islands or lake centroids. Isla de Sacrificios has restricted public access according to published geographic guidance.

## Next step before Dijkstra on actual roads
1. Obtain accessible entrance / dock / parking coordinates for a selected initial region (e.g. Xalapa–Xico, then Veracruz–Actopan).
2. Snap each **entrance** to a verified road/trail node; store entrance source, type of access and permissions.
3. Extract routable OSM road network offline and calculate travel-time-weighted paths. Keep abstract tourism/municipal coordinates out of turn-by-turn driving.

## Remaining records requiring more research
- San Miguel Aguasuelos
- Los Tuxtlas
- lagunas de Actopan
- La Mancha
- Chichicaxtle
- Villa Rica
- sunken vessel
- Mandinga
- Museo de Arte del Estado
- Puerto de Veracruz
- Finca Santa Martha
- river entering cave
- river headwaters
- Manglares de Mandinga
- Tamiahua estuaries
- Los Tuxtlas camp/beach
- Cerro de las Antenas / Fortín de las Flores
- Filobobos
- Sierra de Zongolica / Roca Partida / Cueva del Pirata
- Veracruz (multiple locations)
- Fincas de Fortín de las Flores y Córdoba
- Finca San Felipe
- Naolinco / Xico / Coatepec
- Pico de Orizaba / Cofre de Perote
- Zongolica / unspecified
- Sótano de Popocatl / unknown
- Atlahuitzia
- cloud forest
- Museo de la Orquídea
- unspecified Ramsar wetland
- Casa de Cortés / early church
