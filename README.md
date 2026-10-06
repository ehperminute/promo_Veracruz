# Veracruz Tourism Intelligence

Semester-long Data Science project for analyzing tourism evidence in Veracruz with a reproducible S0→S9 pipeline.

## Current stable milestone

Milestone 1 closes S0–S3:

- **S0 — Sources:** frozen DataTur, INAH, DENUE, tourism-GDP, and official Veracruz tourism-web snapshots with SHA-256 registry.
- **S1 — Ingestion/cleaning:** deterministic parsers and normalization scripts.
- **S2 — Curated interim tables:** DataTur month/center, INAH site/month, municipal infrastructure/economy, and tourism-product tables.
- **S3 — Integrated table:** `data/processed/destination_master.csv`.

Interpretation boundaries and stage contracts are defined in `PROJECT_CONSTITUTION.md`.

## Rebuild S0–S3

```bash
python -m pip install -r requirements.txt
python scripts/data/run_data_pipeline.py --idempotence --test
```

Expected frozen-input result:

- 13 raw sources verified
- 6,900 DataTur center-month rows
- 324 Veracruz DataTur rows
- 4,048 Veracruz INAH site-month rows
- 212 municipal infrastructure rows
- 75 selected tourism-product rows grounded in the frozen official web snapshot
- 55 destination-master rows
- idempotence PASS
- 44 Milestone-1 tests PASS

## Destructive reproducibility check

```bash
rm -rf data/interim
rm -f data/processed/destination_master.csv docs/DATA_SOURCES.md
python scripts/data/run_data_pipeline.py --idempotence --test
```

Generated/interim artifacts must return from raw/reference inputs plus code.

## Data classes

- `data/raw/`: immutable source snapshots.
- `data/reference/`: explicit mappings, curation rules, code groups, and source registry.
- `data/interim/`: mechanically generated cleaned/aggregated tables.
- `data/processed/`: canonical analysis-ready tables.
- `outputs/`: analytical/model results; not silent upstream inputs.

## Important interpretation rules

- Missing DataTur coverage is missing measurement, not low tourism demand.
- INAH counts are archaeological-site visits, not total municipal tourism.
- DENUE measures service/infrastructure structure, not ecological carrying capacity.
- Product association rules describe offer co-occurrence, not tourist movement.
- Clusters represent analytical similarity, not automatically viable routes.
- Synthetic or proposed campaign data are never treated as observed evidence.
