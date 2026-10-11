# S5 — Hotel occupancy forecasting (Veracruz PP)

## Goal
Forecast **next month's hotel occupancy percentage** separately for the three DataTur reporting centers, not tourist visits for the other destinations.

## Installation and run
Copy `scripts/run_s5.py` and `tests/test_s5.py` into the existing PP repository, retaining their folders. From the repository root:

```bash
python -m pip install pandas numpy scikit-learn pytest
python scripts/run_s5.py --input data/interim/datatur_veracruz_monthly.csv
python -m pytest tests/test_s5.py -q
```

If the column identifying the DataTur center differs from the supported candidates, use:

```bash
python scripts/run_s5.py --center-col YOUR_ACTUAL_CENTER_COLUMN
```

The script reads the existing S2 interim CSV, which must already have been generated. It never substitutes made-up occupancy data. The tests use synthetic data **only** to test code behavior.

## Outputs
- `outputs/ml/s5_backtest_predictions.csv`: observed versus predicted occupancy in 2023–2024, per model and center.
- `outputs/ml/s5_backtest_metrics.csv`: MAE, RMSE, bias in occupancy percentage points.
- `outputs/ml/s5_next_month_forecasts.csv`: predictions for the month immediately following the last data month (likely January 2025, not October 2026).
- `outputs/ml/s5_metadata.json`: scope, train/test details, winner and limitations.

## Method
Models: previous month, same month last year, historical average of same calendar month, Ridge regression, Random Forest. Lags and seasonal features are computed only from months strictly preceding each prediction. For each month in 2023–2024, training expands to the preceding month; evaluate genuine chronological out-of-sample errors. Select lowest-MAE model for each center. Fixed hyperparameters avoid tuning against test months.

## Interpretation cautions
The statistical series describes registered hotel occupancy at defined hotel centers, not tourist volume throughout Veracruz. No destination-level demand is imputed. There is no reliable projection from 2024 straight to October 2026. The 2025 projection is a historical one-step demonstration until more current DataTur observations are ingested. S6 may subsequently use stored out-of-sample residuals for uncertainty experiments.

## S5 status
Implementation provided and synthetic tests verified; **real-data backtest must be run against the project's S2 CSV before reporting numerical accuracy**.
