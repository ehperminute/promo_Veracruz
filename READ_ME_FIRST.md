# Optional PP1 interface experiment: experience gallery + algorithm lab

This is a **presentation-only prototype**. It does not change S4 clustering, destination records, labels, web exporter, data sources, or model results.

## What it does

1. Replaces the old *Overview* area with twelve large visual experience cards. Each card displays its localized cluster name, number of member destinations, three most frequently coded tourism themes, and example places. Clicking a group filters the existing destination catalog.
2. Simplifies tourist-facing destination detail dialogs: name, official tourism-region label, coded tourism themes, group description, other destinations in the same group, and a reminder that a group is not a route. It hides technical silhouette scores, medoid distances and structural analogues from the tourist dialog.
3. Replaces the generic *Data & Methods* area with an **optional, removable teaching lab**. Visitors/students can compare two destinations' nine indicators and reproduce the Gower-style distance. A second mini-example demonstrates the BUILD+SWAP PAM medoid selection on four real destination profiles, with k=2.
4. Keeps English, Spanish and Japanese strings. Does not add any dependency.

## Apply

Review the six `site/` files before overwriting anything. If you have changes made after the previous S4 web patch, merge them instead of overwriting them.

Extract this ZIP in the **root of `promo_Veracruz`**, preserving the `site/` subfolders. This patch contains:

- `site/index.html`
- `site/css/styles.css`
- `site/js/app.js`
- `site/i18n/en.json`, `es.json`, `ja.json`

The existing `site/data/destinations.json` continues to come from your normal `scripts/web/export_destinations.py` in the GitHub Pages workflow. **Do not replace the S4 exporter** with an older script.

Commit and push the files as usual. After GitHub Pages publishes, reload the site and check three things:

1. Twelve experience cards appear above the destination explorer; clicking one filters the destination list.
2. In the algorithm lab, comparing Catemaco with Calcahualco shows `2 / 6 = 0.333`.
3. Switch to Spanish and Japanese; both the gallery and lab should translate.

## Algorithm provenance

`data/reference/destination_reference.csv` is a **55-entry curated project reference**, not a complete official register of towns or a table automatically discovered from the 295 tourism-offering records. Destination themes were coded by the project from reviewed evidence. `data/reference/destination_profile_enrichment.csv` records reviewed S4 adjustments; `data/interim/destination_profiles_s4.csv` holds the resulting analytic profiles.

The site demonstrates the exact **nine features** in `scripts/mining/common.py`: eight asymmetric tourism-theme flags (shared absence ignored) and one symmetric `pueblo_magico` flag. The 4-place demonstration gives medoids `Calcahualco` and `Coatepec`, with total distance `0.533333...`. This matches the Python S4 `pam(...)` function on the same four profiles. **The published twelve groups** were calculated with the full set of 55 and k=12; the 4-place example does not reproduce that full clustering run.

## Scope / limitations

- The theme fields are **evidence-coded presence**, not 1–5 strength or confidence scales, and 0 is not verified absence.
- The visual symbols and colored borders are editorial decoration, not scientific measurements.
- The gallery is not evidence of low demand, uncrowded places or feasible travel routes.
- We verified the JSON export, JavaScript syntax, key translations, and the Gower/PAM example against the actual Python algorithm. A full automated browser navigation test was **blocked by the execution environment**, so the three visible checks above remain necessary after deployment.

The teaching lab is intended for the course prototype; it can be removed from the final tourist-facing site without affecting the catalog or clustering.
