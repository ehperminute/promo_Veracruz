# Installing the S8 first implementation

Extract at repository root, retaining paths. It adds `scripts/marketing/`, `data/reference/`, and `docs/marketing/` and **does not overwrite the website or S7 model**. The new S8 script reads the existing `outputs/or/s7_calendar_budget_100000.csv` produced by the installed S7 optimizer.

Run: `python scripts/run_s7_framework.py` (if needed to regenerate the S7 calendar), then `python scripts/marketing/build_s8_activity_matches.py`.

The bundled reference inputs are snapshots of the cultural and adventure research collected on 12 October 2026. Review `docs/marketing/S8_IMPLEMENTATION_STATUS.md` before using the output for a campaign; these are explicitly hypotheses and proposed experiences, not verified bookings or actual campaign results.
