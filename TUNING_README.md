# S5 Random Forest hyperparameter tuning

Extract the archive **into the repository root**. The archive contains only `scripts/tune_s5.py` and this `TUNING_README.md`; it does not overwrite `run_s5.py`.

From the project root, run:

```bash
python scripts/tune_s5.py
```

The script takes `data/interim/datatur_veracruz_monthly.csv`, selecting hyperparameters based on **2021–2022** one-month-ahead errors (24 candidate settings per center, expanding training window), then re-evaluates the chosen model on **2023–2024**. It also reports the original forest configuration and the `last_month` baseline on those same 2023–2024 months.

Outputs:

- `outputs/ml/s5_rf_tuning_validation.csv` — each candidate's 2021–2022 MAE.
- `outputs/ml/s5_rf_tuning_test_predictions.csv` — monthly observations, predictions and errors for the final test.
- `outputs/ml/s5_rf_tuning_test_metrics.csv` — side-by-side 2023–2024 comparison and selected settings.

The test is *not* used for selecting settings. The tuning window includes pandemic recovery; a low validation MAE may not carry over into 2023–2024. Compare the tuned model with the original forest and `last_month` rather than assuming tuning improved it.
