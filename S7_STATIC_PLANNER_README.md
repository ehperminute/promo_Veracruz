# S7 planner: static Python results

Extract into the project root, allowing the included files to overwrite the current `site/` equivalents. Existing site resources not present in this ZIP stay untouched.

- `site/planner.html`: precomputed annual-scenario viewer.
- `site/js/planner_static.js`: display/filter/translate only; **no optimizer in browser**.
- `site/data/s7_precomputed.json`: four annual MILP output scenarios from `scripts/run_s7_framework.py` (MXN 30k, 60k, 100k, 200k).
- Site homepage navigation and EN/ES/JA translations from prior patch.

**Crucial:** Seasonal filtering does NOT optimize a season-specific budget. The annual budget applies to the full year, while the table and current-view spending show just one season. The model assumes MXN 5,000 per placement; this is not a real media price or expected return.

For more budgets, rerun the Python optimizer locally and rebuild this JSON export before publishing. No JavaScript optimization solver is used. If viewing locally, use `python -m http.server 8000 --directory site`, then browse http://localhost:8000/planner.html; `file://` may block JSON loading.

The source result files came from the earlier S7 framework archive and have not been independently re-solved in this patch.
