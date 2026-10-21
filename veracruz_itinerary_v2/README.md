# Veracruz unified itinerary planner v2 (replacement for both old routing widgets)

This is a UI replacement for the *installed* statewide preview and the older Xalapa-only planner. It does not edit tourism data, project ML, OR, or the map features.

## Install (from repository root in Codespaces)

```bash
unzip -o VERACRUZ_ITINERARY_ROUTER_V2.zip
python veracruz_itinerary_v2/install.py
python -m http.server 8000 -d site
```

Open the forwarded port; do a **hard refresh** to bypass old JavaScript cache. The site should have ONE panel named **Plan your road trip** (ES: *Planear un recorrido vial*) and a **Show planner** button on the map.

- Add attractions with the searchable name field (no native dropdown), or press **Add points on map** and tap attraction pins or any map location.
- Add up to 12 points; move each stop with the ↑ and ↓ buttons and remove with ×.
- Click **Calculate road route**. The purple road geometry draws only if the external OSRM API returns a valid result. No straight-line approximation is substituted for a failed request.
- **Open road directions** always constructs usable Google Maps URLs (the itinerary is split into multiple overlapping route links if needed, because Google Maps mobile URLs support only 3 intermediate waypoints).

## Test examples

1. Search for `Cascada de Texolo`; add. Search `Palacio de Hierro`; add. Click **Calculate road route**. If the public demo works, a line follows actual roads; otherwise the error is explicit and **Open road directions** remains clickable.
2. Enable **Add points on map**, click an attraction pin and then any road area, then disable mode. Verify two new stops appear.
3. Add at least five stops, reorder two, remove one, and confirm that external links update to the current order. With 7+ stops, multiple directions parts are provided rather than silently dropping stops on mobile.
4. In the mobile browser, verify that there is no four-dropdown form and only one planner.

## Technical boundaries

Two OSRM public demo endpoints are attempted on an explicit click (`routing.openstreetmap.de/routed-car`, then `router.project-osrm.org` after a failed request). Both have reasonable-use limits and **neither guarantees uptime or CORS reachability**. This environment did **not** have network access to validate the live response. For production use, configure `window.VX_ROUTING_BASE_URL` with a properly permitted OSRM-compatible routing service, or host OSRM. The fallback opens Google Maps' public driving-directions URL; it does not require provider integration.

Custom points are map coordinates, not verified vehicle entrances. Road travel time excludes live traffic. Routes include all selected stops in their listed order; no automatic TSP optimization. Map basemap roads were already statewide; this change is a route-planning UI and fallback, not a statewide self-hosted road engine.

## Undo

```bash
cp site/index.html.before-itinerary-v2 site/index.html
# If the backup exists, restore marker-renderer logic as well:
[ ! -f site/js/map-attractions.js.before-itinerary-v2 ] || cp site/js/map-attractions.js.before-itinerary-v2 site/js/map-attractions.js
```

The previous standalone scripts stay on disk for comparison. The installer adds one stable identifier to each existing mapped attraction marker; no source data, descriptions or coordinates are changed. Do **not** delete or commit transfer ZIPs.

## Stop criterion

If the inline route fails in your real browser, inspect the displayed HTTP/timeout message. The external Google Maps directions must still work. If *that* also fails, hide this feature and submit the evidence map without claiming functional statewide routing; do not generate more cosmetic patches.
