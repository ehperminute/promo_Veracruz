# S5 — Test on the new 2025–July 2026 DataTur reports

Extract this archive **at the existing repository root** (`promo_Veracruz/`), merging directories.

Run from the repository root:

```bash
python scripts/evaluate_s5_new_data.py
```

Requires the existing `data/interim/datatur_veracruz_monthly.csv` (2016–2024) and Python packages pandas, numpy, scikit-learn. If `outputs/ml/s5_rf_tuning_test_metrics.csv` is present, the script reuses the previously selected tuned-forest hyperparameters; otherwise `tuned_forest` is a duplicate of the original forest and **must not be interpreted as tuned**. Copy in the previous tuning metrics CSV if needed.

Outputs (new filenames; does not overwrite existing S5 results):
- `outputs/ml/s5_new_period_predictions.csv`: individual observations and predictions
- `outputs/ml/s5_new_period_metrics.csv`: error by center/year/model and aggregate
- `outputs/ml/s5_new_period_metadata.json`: assumptions, counts and limitations

Missing 2025 Sep–Dec Veracruz–Boca del Río reports are not imputed as target values. When a lag is missing, the feature receives a training-only median rather than pretending that the missing month's occupancy was observed. The `last_month` comparison is omitted if that observation was not published. Models are refit before every test month using only earlier target observations; for reproducibility, the 2023–2024 original comparison remains separate.

**Interpretation caveat:** Comparing overall model MAE to last-month MAE is not apples-to-apples if different numbers of rows were scored. Compare the models on common dates when interpreting performance, especially for Veracruz–Boca del Río.
