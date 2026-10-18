# Veracruz: visible road route repair

This is a **targeted correction** for the browser route planner from October 18. It does NOT rebuild roads, redownload OpenStreetMap data, or touch tourist descriptions.

**Issue:** The old planner calculated a route and zoomed even when MapLibre rejected/dropped its custom layer. A caught map-layer error was immediately overwritten by a misleading ready message.

**Fix:** The route is now drawn as a blue, white-outlined geographic SVG overlay attached directly to the map container. MapLibre's `project()` method converts each road coordinate to its on-screen location. Map pan, zoom, and resize events redraw the route. Chosen stops have numbered orange circles. Failure to render becomes a visible message instead of silent success.

From the `promo_Veracruz` repository root:

```bash
unzip -o VERACRUZ_ROUTE_DRAWING_FIX_2026-10-18.zip
python VERACRUZ_ROUTE_DRAWING_FIX_2026-10-18/install_fix.py .
```

Hard-refresh the site. Select **two distinct attractions** in Plan a route and click **Find shortest road route**. You should see a **blue line with white outline** following the calculated road graph, **numbered orange stops**, and a road-distance result. The line should stay aligned when zooming.

If it fails, the sidebar now displays an error. Send that error rather than reinstalling the other map patches. You can inspect the console for `[Veracruz Dijkstra]` or `[Veracruz routing SVG]`.

Limitations: regional Xalapa–Coatepec–Xico graph only, road *distance* not driving time, attraction entrances not validated, no live traffic. This is a visualization fix, not a change to routing validity.

To roll back, restore `site/js/route-planner.js` and `site/index.html` from the `.before-visible-route-...` directory printed by the installer.
