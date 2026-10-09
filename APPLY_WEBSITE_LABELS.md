# PP1 website cluster labels — review patch

This patch **does not change the clustering model, group assignments, source data, or other analytical scripts**. It changes the website's **source of displayed destination features** to the already-refined S4 profile table and replaces public `Cluster N` labels with editable editorial names.

## Included files

- `scripts/web/export_destinations.py`: now exports the refined `data/interim/destination_profiles_s4.csv` values and adds multilingual names and short descriptions; detects missing/reassigned clusters.
- `data/reference/cluster_display_labels.csv`: 12 provisional editorial names and descriptions in English, Spanish and Japanese, with representative destination checks.
- `site/js/app.js`: named experience groups in the filter, cards and destination details. Cluster ID remains visible in the details.
- `site/css/styles.css`: badges accommodate names of varying length.
- `site/i18n/en.json`, `es.json`, `ja.json`: accompanying localization and methodological warning.
- `site/index.html`: cache-bust updated assets to version 5.
- `tests/test_web_export.py`: verifies output vs S4 themes, ID coverage, multilingual labels, and the known S4 corrections.
- `docs/CLUSTER_LABELS.md`: explains provenance and editing.

## How to apply

1. Review names in `data/reference/cluster_display_labels.csv`. These are proposals, not official brands.
2. Extract this ZIP into your Git repository root **preserving its folder structure**, overwriting only the included site/export files.
3. Run `python scripts/web/export_destinations.py` (or let the GitHub Pages workflow run it).
4. Optional check: `python -m pytest -q tests/test_web_export.py`.
5. Commit and push to `main`. The existing GitHub Pages workflow will deploy the updated website on its next run.

The exporter reads the S4 profile CSV, which itself comes from the S0–S3 source/data pipeline. It does **not** mean the analytical workflow skips S3. If clustering is rerun and a group representative changes, the exporter deliberately stops and asks for the labels to be reviewed.

**Interpretation:** names describe **similar tourism characteristics**. They do not prove that all destinations in a group are part of one geographic route, that the destinations are uncrowded, or that tourists have matching preferences.
