# Veracruz — integrated attraction layer (batch 1)

This is an integration patch for the **existing `promo_Veracruz/site/index.html` map**. It adds 18 previously researched named attraction references from `VERACRUZ_ATTRACTION_GEOCODING_BATCH1_2026-10-18` directly to the page. It does not replace municipal maps, guide content, existing source datasets or the SQLite database.

## Install in Codespaces

Put the ZIP in the **root of `promo_Veracruz`** and run:

```bash
unzip -o VERACRUZ_ATTRACTIONS_ON_MAP_2026-10-18.zip
python install_attractions.py
```

With a local server already running, refresh the website (no server restart required). The installer makes a dated backup of `site/index.html` and the original `site/js/map-explorer.js` in `site/.before-attractions-.../`.

**Test:** Search `El Tajín` in the existing *Veracruz Explorer* search field. A separate **Attraction results** section appears in the right panel. Click `El Tajín`, or press Enter, to zoom to the site and open its source card. Search `Quiahuiztlán` or `Quiahuiztlan` to test accent-insensitive lookup. Expand **Mapped attractions · 18** in the right panel to browse all mapped attractions.

## What it adds

- `site/data/attractions_batch1.geojson` — the **18 source-linked geocoded attraction and geographic-area records** from the prior research batch.
- `site/js/map-attractions.js`, `site/css/map-attractions.css` — distinct attraction markers and their names, source popups and search integration.
- A tiny one-line expose of the existing MapLibre instance in `site/js/map-explorer.js`, so the addon uses the **same map**. One `<link>` and one `<script>` added to `site/index.html`.

**Important:** Attraction coordinates represent the mapped feature or general geographic area, **not verified entrances**. All batch-1 records say routing entrance NOT verified. Islands and large waterbodies are not drivable stops. This patch does not claim they are ready for Dijkstra road routing. The existing municipality source remains separate.

## Troubleshooting

If the map works but the attraction list reports unavailable, check the browser Console for `[Veracruz attractions]` errors and confirm that `site/data/attractions_batch1.geojson` is being served. The JS and CSS URLs are versioned to bypass stale caching. If the installer says STOP, it makes no changes and the existing JS file needs a merge; send that exact version instead of overwriting it manually.

## Offline tests completed

- Installer succeeds and a repeated run is a no-op.
- JavaScript passes `node --check`.
- Chromium test with a simulated MapLibre implementation: loads 18 records, resolves El Tajín on click, resolves `Quiahuiztlan` by Enter, flies to the correct coordinates and shows source cards. A real deployed MapLibre rendering test was not available here.
