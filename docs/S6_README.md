# S6 — uncertainty of Veracruz hotel occupancy predictions

## One-command run

1. Extract this archive into the **project root** (merge `scripts/`, `tests/`, and `docs/`).
2. The input CSVs must already exist at:
   - `outputs/ml/s5_rf_tuning_test_predictions.csv` (2023–2024)
   - `outputs/ml/s5_new_period_predictions.csv` (2025–July 2026)
3. Run: `python scripts/run_s6.py`

If your CSVs are elsewhere: `python scripts/run_s6.py --old PATH_TO_OLD.csv --new PATH_TO_NEW.csv`.

## What it actually does

Take each city's *tuned Random Forest* prediction errors from an earlier period. Sort their absolute magnitudes and select a conservative empirical 90% quantile (without interpolation). Add/subtract that error margin to the next period's predictions, clipping at physical occupancy bounds of 0–100%. Then count how many real observations fall inside the intervals.

- **2024 retrospective check**: 2023 errors calibrate; 2024 checks coverage.
- **2025–July 2026 check**: 2023–2024 errors calibrate; 2025–2026 checks coverage.
- No missing monthly observations are invented.
- The model is not tuned using the newer evaluation outcomes. The S5 rolling forecaster may retrain on previously observed outcomes, as documented in S5.

**Outputs** in `outputs/stochastic/`:

- `s6_intervals.csv`: one lower/central/upper prediction per tested city/month; indicator for whether reality fell inside.
- `s6_coverage_metrics.csv`: error margin, number covered, observed coverage, average interval width.
- `s6_method.json`: method and limitations.

**Interpretation:** A claimed 90% interval is *not proved* reliable by this exercise. With only 12/24 calibration errors per city, observations that depend on time, changes in tourism patterns, and large jumps, nominal coverage assumptions may fail. Reporting observed coverage and interval widths is more honest than promising 90% probability for future months. This is empirical forecasting uncertainty for hotel centers, not tourist-demand estimates for any of the other destinations.
