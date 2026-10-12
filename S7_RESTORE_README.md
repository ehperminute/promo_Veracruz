# Restore the Veracruz S7 optimizer

This patch restores the **original** `scripts/run_s7_framework.py` and adds `tests/test_s7_reproducibility.py`. It **does not** overwrite your data, website, precomputed scenarios or existing stages. The optimizer reads current files in the repository.

## Install

1. Extract the ZIP at the root of the `promo_veracruz` repository, preserving `scripts/` and `tests/`.
2. In the Codespace terminal, from the repository root, run:

```bash
python -m pip install scipy
python -m pytest -q tests/test_s7_reproducibility.py
python scripts/run_s7_framework.py
```

The test recomputes all four budget scenarios and checks their exact `(destination, period)` pairs against the **current published** `site/data/s7_precomputed.json`. A mismatch fails the test, rather than silently replacing the site's scenarios.

The script generates `outputs/or/s7_calendar_budget_*.csv` and `outputs/or/s7_scenario_comparison.csv`. Inspect these, and only commit them if desired. It does **not** update the website JSON automatically. This stage remains separately runnable; `scripts/run_pipeline.py` still runs through S4.

## Dependencies and boundaries

- Inputs: `data/interim/destination_profiles_s4.csv`, `data/reference/datatur_veracruz_monthly_2025_2026.csv`.
- `scipy.optimize.milp` does binary integer optimization; requires `scipy` in addition to pandas/numpy.
- MXN 5,000 per destination-season, scores, 80% occupancy cutoff and per-region-season cap are **model assumptions**.
- The model maximizes diversity/coverage and readiness proxies; it does **not** estimate advertising ROI or causal increases in tourist demand.
- Scenario equality does not prove these assumptions are objectively best. Sensitivity analysis and academic justification remain pending.
