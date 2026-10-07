# Milestone 1 final overlay v3

Copy/merge this archive at the repository root. It completes the two S3 outputs already required by the manifest/constitution: `demand_series.csv` and `origin_market_opportunity.csv`.

No new manual research is required. The origin-market reference contains only direct validated facts from the exact official DataTur `RES_2025_12.pdf` report; the normal pipeline remains offline and deterministic.

Then run:

```bash
python -m pip install -r requirements.txt
python scripts/data/run_data_pipeline.py --idempotence --test
```

Expected final status for the frozen 2026-10-06 project inputs:

- 13 local raw sources verified by SHA-256
- 1 exact fixed DataTur remote report registered
- 295 Veracruz tourism-product cards parsed
- 31 municipality entries parsed from the seven-region navigation
- 8 Pueblos Mágicos parsed from the manually browser-saved official page
- 6,900 DataTur center-month rows
- 324 Veracruz DataTur center-month rows
- 4,048 Veracruz INAH site-month rows
- 212 municipal infrastructure rows
- 75 project-v1 tourism-product selection rows grounded against frozen source cards
- 55 destination-master rows
- 4,372 canonical observed-demand rows
- 25 validated 2025 origin-market rows
- idempotence PASS
- 56 tests PASS

Acceptance/destructive rebuild:

```bash
rm -rf data/interim
rm -f \
  data/processed/destination_master.csv \
  data/processed/demand_series.csv \
  data/processed/origin_market_opportunity.csv \
  docs/DATA_SOURCES.md
python scripts/data/run_data_pipeline.py --idempotence --test
```

After extraction, remove old patch archives from the repository root (for example `promo_veracruz_milestone1_patch.zip`); they are delivery artifacts, not project inputs.
