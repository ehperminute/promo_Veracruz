# Veracruz PP — geographic verification + four-course analytical results

This is **one consolidated project handoff**, not a replacement for the recovered tourism database.

## What's completed
- Audit of all 26 physical sites/areas from the reviewed 14-municipality extension (`geographic_audit_26.csv`).
- 10 separately geolocated features, of which **3 were already mapped**; **7 new site/area markers** in `new_verified_map_sites.csv`.
- 16 unresolved geographic identities remain documented. Rejected ambiguous place matches are not put on the map. No visitor entrances have been verified.
- Reproducible Monte Carlo experiment (5,000 draws at each of 4 budgets, using the latest 61 evidence-supported municipalities), report and CSV results.
- Ready-to-edit Spanish academic report linking **Minería de Datos, Investigación de Operaciones, Métodos Estocásticos and Mercadotecnia Digital** (DOCX and Markdown).

## Apply map update (optional, when you next use Codespaces)

From the root of `promo_Veracruz`:

```bash
unzip -o VERACRUZ_GEOGRAPHY_COURSE_RESULTS_2026-10-18.zip
python VERACRUZ_GEOGRAPHY_COURSE_RESULTS_2026-10-18/install_verified_points.py .
```

Refresh your published local site. The installer changes **only** `site/data/attractions.csv` and `site/data/attractions.geojson`; makes backups; and is safe to run twice. It requires both files already present to avoid erasing prior map points. It doesn't modify scripts, stylesheets, the SQLite database, or any existing attraction descriptions.

**Important:** `mapped_site` or `mapped_area` labels are geographic feature locations, **NOT verified entrances or routing stops**. In particular, the Balneario El Rincón de las Doncellas record is mapped to the **lake** feature, and the public marker is labelled accordingly; this isn't a verified entrance to the balneario.

## How to reproduce the experiment

```bash
python VERACRUZ_GEOGRAPHY_COURSE_RESULTS_2026-10-18/reproduce_monte_carlo.py \
 VERACRUZ_GEOGRAPHY_COURSE_RESULTS_2026-10-18/research/veracruz_master_with_verified_evidence.sqlite \
 ./reproduced_results
```

Outputs: `monte_carlo_draws.csv` and `monte_carlo_summary.csv`. Only Python standard library required. Randomized benchmark is uniform selection of eligible municipalities, **not actual tourist demand probability**. MX$5,000 per promotional municipality is a teaching assumption.

## File inventory

- `VERACRUZ_REPORTE_INTEGRADOR_RESULTADOS.docx` — report for courses, with actual results and limitations.
- `REPORT_INTEGRADOR.md` — editable source narrative.
- `geographic_audit_26.csv` — all 26 records with exact audit status and geographic source where available.
- `new_verified_map_sites.csv` / `.geojson` — only seven new points with map-ready source references and location warning.
- `install_verified_points.py` — safe idempotent merge.
- `monte_carlo_summary.csv` / `monte_carlo_draws.csv` — reproducible random-selection results.
- `reproduce_monte_carlo.py` — independent rerun against snapshot `research/veracruz_master_with_verified_evidence.sqlite`.
- `research/OR_EVIDENCE_SENSITIVITY_REPORT.md` — earlier exact strategy comparison, as separate supporting evidence.

No further user-provided files are required to use the analytical results. The route-planner UI is outside this patch and remains unchanged.
