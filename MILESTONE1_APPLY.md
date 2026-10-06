# Milestone 1 final overlay

Copy/merge this archive at the repository root. It contains one additional small raw source supplied by the user: `data/raw/veracruz_pueblos_magicos_2026-10-06_manual.html`. The large raw datasets are already committed in `data/raw/`.

Then run:

```bash
python -m pip install -r requirements.txt
python scripts/data/run_data_pipeline.py --idempotence --test
```

Expected final status for the frozen 2026-10-06 inputs:

- 13 raw sources verified by SHA-256
- 295 Veracruz tourism-product cards parsed
- 31 municipality entries parsed from the seven-region navigation
- 8 Pueblos Mágicos parsed from the manually browser-saved official SECTUR page; the failed CAPTCHA snapshot is preserved and the products-page menu remains a tested fallback
- 6,900 DataTur center-month rows
- 324 Veracruz DataTur center-month rows
- 4,048 Veracruz INAH site-month rows
- 212 municipal infrastructure rows
- 75 project-v1 tourism-product selection rows, each grounded against a frozen source card
- 55 destination-master rows
- idempotence PASS
- 44 tests PASS

Acceptance/destructive rebuild:

```bash
rm -rf data/interim
rm -f data/processed/destination_master.csv docs/DATA_SOURCES.md
python scripts/data/run_data_pipeline.py --idempotence --test
```

After extraction, remove old patch archives from the repository root (for example `promo_veracruz_milestone1_patch.zip`); they are delivery artifacts, not project inputs.
