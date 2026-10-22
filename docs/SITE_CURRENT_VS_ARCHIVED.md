# Current public website vs archived research (2026-10-21)

Current on the home page: `site/data/map_points.geojson` (212 approximate municipality references),
`site/data/attractions.geojson` (506 mapped attractions), `site/data/tourism_catalog.json` (documentary tourism records),
`site/js/map-explorer.js`, `site/js/map-attractions.js` and `site/js/itinerary-router.js`.
Do not confuse municipality centroids with verified entrances or driving destinations.

Historical, retained for research provenance but not presented as current home-page results:
`site/data/destinations.json`, `site/js/app.js`, old 55-profile Gower/PAM clustering,
`site/data/s7_precomputed.json`, old 8-theme / 55-destination campaign planner.
The direct `site/planner.html` is visibly marked **ARCHIVED** and removed from main navigation.
Historical clustering may appear in the academic methods as a negative or unstable experimental result,
never as the authoritative current catalog or a validated segmentation of tourists.

The **live road-routing service is not verified**, and municipality markers are approximate.
External driving directions are a separate provider integration, not an on-site booking or verified route.
This patch neither changes canonical databases nor validates an independent tourism-demand claim.

Rollback from repository root (only if you need the previous web view):
`cp .local-site-backup-before-v3/index.html site/index.html`
Other changed files can be copied back from the matching paths under `.local-site-backup-before-v3`.
