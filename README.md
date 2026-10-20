# Veracruz tourism research — PP / PP6

This project investigates evidence-grounded tourism experiences, center-level demand, uncertainty, campaign allocation, and a proposed digital marketing campaign for Veracruz. The **latest source-restored SQLite evidence** is not equivalent to the historical 55-destination exploratory S4 catalog. Preserve both; do not promote historical S4 clusters to the current statewide tourism truth.

## Current research database

`data/recovered_source_descriptions/veracruz_pp3_master_with_originals.sqlite` is the source-restored working database for this second-pass audit. The 14-municipality typed review exists in the separate audited source database under `VERACRUZ_GEOGRAPHY_COURSE_RESULTS_2026-10-18/research/`. Missing source mentions mean *not documented*, not zero tourism. Tourism-product publication is not proof of current operation or visitor demand.

## Reproducibility

The historical full rebuild command is:

```bash
python scripts/data/run_data_pipeline.py --idempotence --test
```

**Missing DataTur coverage is missing measurement**, not low demand. Frozen DENUE/GDP archives and original catalog PDF snapshots must be present for a complete from-raw rebuild. An intentionally slim research transfer may contain the processed outputs but not those raw archives; treat the latter as an `INPUTS_UNAVAILABLE` check, not as a corrupted database.

The documented earlier frozen-input milestone recorded **56 Milestone-1 tests PASS**. That historical milestone does **not** certify the latest current database or current repository. Recovered sources and newer experiments require their own tests. Historical outputs include `data/processed/demand_series.csv` and `data/processed/origin_market_opportunity.csv`.

## Run the current stage-gated checks

```bash
python scripts/pp6/run_loop.py
```

See `docs/PP6_BLOCKERS.md` and the generated `outputs/pp6_loop/state.json` for the acceptance criteria, current gate results, retry counts, and externally blocked work. This process runs eligible checks automatically, without rewriting research or claiming scientific validity from a successful script exit. The website and map are excluded from automated writes.

## Scope and boundaries

- S4: use source-backed activity intersections; keep clustering exploratory.
- S5: forecast measured hotel-center occupancy only; compare the same dates and baselines.
- S6: estimate uncertainty with coverage and interval width; Markov prediction may perform no better than persistence.
- S7: the promotional placement costs are explicit **assumptions**, not verified prices or return on investment.
- S8: audiences, campaign cells, and advertisements are **proposals**, not observed campaign outcomes.
- S9: reports must be checked against the actual current assignment rubrics before submission.

Do not commit generated archives or overwrite the existing site with the historical 55-destination exporter without an explicit migration and current evidence QA.
