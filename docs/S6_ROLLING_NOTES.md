# S6 follow-up: rolling-calibration comparison

Run from repository root:

`python scripts/compare_s6_rolling.py`

Inputs: `outputs/ml/s5_rf_tuning_test_predictions.csv` and `outputs/ml/s5_new_period_predictions.csv`.
Outputs: `outputs/stochastic/s6_rolling_comparison_metrics.csv` and `outputs/stochastic/s6_rolling_comparison_predictions.csv`.

Four methods estimate a symmetric interval radius from preceding absolute out-of-sample errors per city: a fixed 2023–24 window, the last 12, the last 24, or all past errors. Each 2025–26 observation is used to update rolling windows only **after** its interval was evaluated. Radius is a rank-based 90% empirical conformal quantile; these time-series intervals are **not guaranteed** to attain 90% coverage. In finite samples, 12- and 24-error calibrations can be sensitive to a single large error.

Interpretation: In 2025–26, rolling-12 achieved 17/19 for Coatzacoalcos but its Xalapa intervals became very wide. These candidate calibration rules were compared on the same recent test interval and any selection based on their scores must be marked exploratory; another future evaluation period is needed to confirm generalization. Do not rewrite original S6 reports or call 2025–26 performance unbiased evidence for a newly selected method.
