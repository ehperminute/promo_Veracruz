# PP6 blocker register — executable second-pass audit

This register refers to the **current researched project state**, including the already reviewed 14-municipality material. It does not propose additional collection or reintroduce the 55-profile pilot as the authoritative dataset.

| ID | Scope | Evidence | Resolution and gate | Status |
|---|---|---|---|---|
| B01 | Full frozen raw rebuild | Six DENUE/GDP ZIPs were intentionally excluded from the compact transfer; original large catalog PDFs also excluded. Recovered SQLite and archived HTML still available. | `S0_FULL_RAW_REBUILD`: record missing source files, do not fabricate or retry until inputs available; independent stages continue. | BLOCKED only for full from-raw rebuild |
| B02 | Root documentation | `README.md` was blank | Restore truthful current commands/limitations; `test_repository_docs.py` | FIXED |
| B03 | Marketing output location | The authored 24-cell matrix exists at `docs/marketing/foreign_campaign_test_matrix_v1.csv` while test expected an `outputs/marketing/` copy | `scripts/marketing/export_foreign_campaign_matrix.py` validates/exports exact source; `test_international_markets.py` | FIXED |
| B04 | Historical site exporter test | Test asserted historical model themes = public display themes; exporter deliberately places source-supported `adventure` at end | Test `model_themes` separately and public-theme rule; no website change | FIXED |
| B05 | Pipeline orchestration | `scripts/run_pipeline.py` stops at old S4 and must not overwrite recovered source data | `scripts/pp6/run_loop.py` drives independent source-backed PP6 gates with persistent state and bounded retries | ADDED |
| B06 | S5 validity | Difference among unpaired historical samples; paired forest advantage over 3-month baseline near zero | Paired 52-case evaluation reproduced, retain research result; no public model superiority claim | RESEARCH PASSED, DEPLOYMENT HELD |
| B07 | Sparse / unsupported segmentation | Legacy cluster groups have no demonstrated user utility for statewide activity discovery | Evidence-backed exact interest matches; retain historical clusters as exploratory only | RESOLVED BY DESIGN |
| B08 | S6 claims | Coverage and interval width differ markedly by reporting center; Markov no better than persistence | Reproduce independent Markov experiment from matching 53-row DataTur observations; 8/20, equal to persistence; do not generalize statewide | RESEARCH PASSED, DEPLOYMENT HELD |
| B09 | S7 business feasibility | Promotion price assumption MXN 5,000 each; no measured ROI, capacity or access validation | Reproduce 47-type six-municipality MILP; sensitivity with archived text support; label scenario assumptions | RESEARCH PASSED WITH LIMITS |
| B10 | S8 validity | Advertising and opening hours not measured; one campaign activity pair lacks recorded original-text support | Source-linked evidence ledger and controlled proposal matrix; deployment requires actual verification | ANALYTICAL PROPOSAL, LIVE DEPLOYMENT BLOCKED |
| B11 | Rubric and deliverable verification | Original 2026-2 PP and the original UCA course documents have been located in the earlier PP conversation; 11 rubric criteria and required final products are recorded | `docs/pp6/original_rubric_spec.json` + `docs/PP6_RUBRIC_MATRIX.md`; finish 30–40-page report, campaign, reproducible evidence and <=15-min colloquium | RUBRIC SPEC PASS / SUBMISSIONS IN PROGRESS |
| B12 | Automated restart beyond response | Standard ChatGPT session does not self-run between turns | Repo-side runner can execute on demand/CI; writes `outputs/pp6_loop/state.json` and `CHECKPOINT.md`, so the next session resumes from observed outputs | LOCAL RUNNER READY; NO BACKGROUND TASK CLAIM |

## Rules of the loop
1. For each eligible stage, execute a command, inspect acceptance evidence, and persist the outcome.
2. Retry command failures no more than `--max-attempts` (default 2); deterministic scientific gaps cannot be repaired by blind retries.
3. Advance independent stages even if a separate source/release gate is blocked.
4. Record `BLOCKED` for genuinely absent inputs, `FAILED` for failed computation, `RESEARCH_PASS` for valid negative experimental results, `PASS_WITH_LIMITS` for constrained proposals, and `PASS` for validated reproducibility checks.
5. Do not write `site/`, replace databases, manufacture data, change objectives to chase favorable metrics, or claim live availability.
6. Keep checkpoint logs in `outputs/pp6_loop/`, and review them before integrating to the website.
