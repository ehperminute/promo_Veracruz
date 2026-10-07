# Veracruz Tourism Intelligence

Semester-long Data Science project for analyzing tourism evidence in Veracruz with a reproducible S0→S9 pipeline.

## Current stable milestone

Milestone 1 closes S0–S3:

- **S0 — Sources:** 13 immutable local raw snapshots plus one exact fixed official DataTur origin-market report registered with explicit provenance.
- **S1 — Ingestion/cleaning:** deterministic parsers and normalization scripts.
- **S2 — Curated interim tables:** DataTur month/center, INAH site/month, municipal infrastructure/economy, and tourism-product tables.
- **S3 — Canonical processed tables:**
  - `data/processed/destination_master.csv`
  - `data/processed/demand_series.csv`
  - `data/processed/origin_market_opportunity.csv`

Interpretation boundaries and stage contracts are defined in `PROJECT_CONSTITUTION.md`.

## What the two S3 support tables mean

`demand_series.csv` is a standardized time-series table for later ML/stochastic work. It keeps DataTur hotel-center arrivals and INAH archaeological-site visits as separate measurement scopes; they must not be summed or treated as the same kind of demand.

`origin_market_opportunity.csv` ranks the 25 leading countries of residence for foreign air-entry events to Mexico using DataTur's validated 2025 annual figures. It is national origin-market context for later marketing analysis, **not evidence of visits to Veracruz**. Marketing tiers/personas/campaign decisions are deliberately excluded from S3.

## Rebuild S0–S3

```bash
python -m pip install -r requirements.txt
python scripts/data/run_data_pipeline.py --idempotence --test
```

Expected frozen-input result:

- 13 local raw sources verified by SHA-256
- 1 fixed official remote report registered without making the normal pipeline network-dependent
- 295 Veracruz tourism-product cards parsed
- 31 municipality entries parsed from the seven-region navigation
- 8 Pueblos Mágicos parsed from the manually browser-saved official page
- 6,900 DataTur center-month rows
- 324 Veracruz DataTur rows
- 4,048 Veracruz INAH site-month rows
- 212 municipal infrastructure rows
- 75 selected tourism-product rows grounded in the frozen official web snapshot
- 55 destination-master rows
- 4,372 canonical observed-demand rows
- 25 validated 2025 origin-market rows
- idempotence PASS
- 56 Milestone-1 tests PASS

## Destructive reproducibility check

```bash
rm -rf data/interim
rm -f \
  data/processed/destination_master.csv \
  data/processed/demand_series.csv \
  data/processed/origin_market_opportunity.csv \
  docs/DATA_SOURCES.md
python scripts/data/run_data_pipeline.py --idempotence --test
```

Generated/interim artifacts must return from raw/reference inputs plus code.

## Data classes

- `data/raw/`: immutable source snapshots.
- `data/reference/`: explicit mappings, direct source extracts, curation rules, code groups, and source registry.
- `data/interim/`: mechanically generated cleaned/aggregated tables.
- `data/processed/`: canonical analysis-ready tables.
- `outputs/`: analytical/model results; not silent upstream inputs.

## Important interpretation rules

- Missing DataTur coverage is missing measurement, not low tourism demand.
- INAH counts are archaeological-site visits, not total municipal tourism.
- DENUE measures service/infrastructure structure, not ecological carrying capacity.
- Foreign origin-market counts describe air-entry events to Mexico, not Veracruz visits.
- Product association rules describe offer co-occurrence, not tourist movement.
- Clusters represent analytical similarity, not automatically viable routes.
- Synthetic or proposed campaign data are never treated as observed evidence.
