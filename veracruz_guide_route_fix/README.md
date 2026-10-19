# Veracruz guide-first sidebar + route actions

This patch was constructed against the `veracruz_site_current.zip` attached on October 18/19.

From the root of `promo_Veracruz`, extract the ZIP and run:

```bash
python veracruz_guide_route_fix/install.py .
```

Then refresh the website. No server restart or road graph rebuild is needed.

Changes:
- Attraction guide appears first in the right panel rather than below the route planner.
- Buttons for **Start here / Finish here / Add stop** appear only if a mapped attraction is in the existing regional routing graph. These activate the existing route planner, no new routing API or hosting.
- A compact photograph preview appears in the map only where the existing data has a photo URL. It does not invent images, and is hidden on narrow screens.
- Guide closes and the existing route planner reappears when route action selected or Back clicked.

The patch makes dated backups of `site/index.html`, `site/js/map-attractions.js`, and `site/js/route-planner.js`. It does not alter CSV, SQLite, GeoJSON, or road networks. Re-running the installer does nothing.

**Limitations:** Regional routing still only covers Xalapa/Coatepec/Xico, and only existing six photo URLs can display image previews. The route chooser uses site identifiers and names already in the regional graph. This does not research new descriptions or calculate popularity.
