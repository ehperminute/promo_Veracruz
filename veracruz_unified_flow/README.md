# Veracruz: single trip-planning flow (2026-10-22)

**Purpose:** Consolidate currently installed itinerary / interests / cost releases into one usable journey, without rewriting the university research or canonical tourism data.

**Install:** This is a **cumulative release** for the current municipal map and route planner. You do NOT need to install the earlier interest or price ZIP separately. From `/workspaces/promo_Veracruz`, unpack this ZIP and run:

```bash
python veracruz_unified_flow/setup.py .
node veracruz_unified_flow/tests/test_scoring.js
python veracruz_unified_flow/tests/verify_install.py .
node --check site/js/interest-recommender.js
python -m http.server 8100 -d site
```

Open forwarded port 8100 and hard refresh. The UI order is Discover (interests/Surprise me), Search/add/reorder stops and calculate road route, and then itemized provider prices and costs. The map and geographic markers remain from the existing site.

**What changed:** `Surprise me` no longer starts from municipalities with most activity links. It prefers **rare, specifically documented experiences**, source-backed proof, and family diversity, while penalizing excessive approximate geographic spread. It draws suggestions from the *existing* 216 links across 61 municipalities; no old 55-place segmentation, generic replacing of rafting/birdwatching/etc, or statistical tourist popularity claims. It explains the rare activity by name and shows how often that activity is documented across municipalities in *this catalog*. These counts are **not tourist visits or crowd sizes**. Community ceremonies and professional research expeditions are not auto-suggested without access authorization; their source records remain in the manual evidence catalog. Its random selection creates variation but cannot prove hidden-gem status. Original narratives are preserved in the research database.

**Cost limitation:** The interest-based budget is an *illustrative screening envelope* and is not the same as the route-cost estimate. After adding suggestions to the route, choose offered services and calculate the route to see the **partial itemized subtotal**. Published prices are dated, availability unverified, and unpriced fees remain unknown. Never equate assumed spending with actual itinerary affordability.

**External dependencies:** Live OSRM road calculation still requires a reliable provider. Two demo endpoints have no uptime guarantees; Google Maps directions remains a fallback. No reservation payment, operator contracts, live availability, local popularity data, or real tourist redistribution can be inferred from this patch.

**Local backup:** `.local-backup-unified-flow/` holds originals and is gitignored. No databases or raw data are changed. Reinstalling is idempotent. When reviewing changes use `git diff -- site/index.html site/js/interest-recommender.js site/js/itinerary-pricing.js`.

**Academic claims:** The optimized campaign placement ILP, attraction discovery and interactive approximate budget are separate methods. Do not claim this stochastic heuristic proves visitor redistribution or a measured market segment. Cite the study and test findings; do not invent positive ML outcomes.

**Browser acceptance:** Test Xalapa → Coatepec plus at least one lower-profile municipality. Verify: Surprise suggestions differ across several presses, explanations name real supported activities, selected route markers show numbered stops, prices change after each stop, missing prices remain unknown, live route failure preserves external directions, ES/EN/JA survive language switching, and mobile controls remain usable.
