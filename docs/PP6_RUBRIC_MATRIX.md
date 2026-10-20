# PP6 — requirements recovered from the ORIGINAL academic PDFs

**Status:** original requirements located; NOT waiting for the user to re-upload them.

Primary source: *Copia de PROBLEMA PROTOT-PICO 5-- LCDN-2026-2.pdf* (24 pages), especially pp. 3–8. Course materials: Data Mining syllabus, Stochastic Models syllabus, Operations Research didactic plan, Big Data syllabus, and Digital Marketing introductory presentation.

**Distinction:** An experiment reproducing successfully does not certify the academic submission. A negative result can satisfy experimental rigor but still leave marketing integration undone.

## The 11 original rubric criteria (100%)

| Criterion | Weight | Verified project evidence | Remaining decision / work |
|---|---:|---|---|
| Problem formulation | 8% | Research question in integrated report; distinguish documented tourism offer from measured demand | Clarify how promotion addresses the stated redistribution problem without claiming unmeasured saturation |
| Big Data storage | 12% | Source registry; SQLite; ETL; checksum records | Explain architecture, storage/scale trade-offs and responsible handling; do not claim distributed processing without running it |
| Data Mining | 12% | Source-backed activity discovery; historical clustering and association tests | Present mining methods/interpretation and why unstable segments are not deployed |
| Machine Learning | 12% | Paired forecast model/baseline comparison (52 cases) | Justify model selection and metrics; explicitly address weak improvement vs rolling mean and the limited geography |
| Stochastic Models | 10% | Forecast-error intervals and 2026 Markov holdout | Link uncertainty to decision scenarios; avoid ungrounded visitor/capacity probabilities |
| Operations Research | 12% | Six-place MILP 47 activity types; evidence and infrastructure sensitivity | Fully state objective, constraints and solver results; costs assumed, capacity not measured |
| Digital Marketing | 8% | Proposed creatives and 24-cell test plan | Complete buyer persona/branding, channel allocation and an honest implementation/evaluation plan |
| Interdisciplinary integration | 10% | Pipeline results and integrated narrative | Demonstrate explicit dependencies: evidence → mining/ML/uncertainty → OR → campaign decisions |
| Solution/impact | 8% | Portfolio trade-offs | Avoid unverified redistribution or environmental-impact claims; compare feasible scenarios and limits |
| Technical communication | 4% | Existing 8-page bilingual report draft | Expand to suggested **30–40 pages excluding appendices**, with specified sections and artifacts |
| Colloquium | 4% | No demonstrated completed final deck in current validation | Prepare presentation <=15 minutes; assign participation and technical defense |

## Minimum final products explicitly required (PP pp. 3–6)

1. **Campaign:** data justification, market audience and buyer persona, branding, selected channels, creatives, implementation on chosen channels, allocated budget, and impact indicators. A proposed test plan is NOT evidence of a paid campaign.
2. **Technical report:** suggested 30–40 pages excluding annexes, covering all 23 sections in `docs/pp6/original_rubric_spec.json`.
3. **Technical evidence:** database, dictionary, code, models, notebooks, queries, diagrams, figures, simulation and optimization outputs, and documentation.
4. **Colloquium:** <=15-minute integrated defense, all participants involved; avoid six unrelated class presentations.

## Gate decisions (do not ask for already-uploaded PDFs)

- `S9_RUBRIC_SPEC`: **PASS** once the local machine-readable specification passes internal consistency checks.
- `S9_RUBRIC_SUBMISSIONS`: **IN_PROGRESS**, not **BLOCKED_BY_MISSING_PDFS**. Work is to reconcile and produce campaign, complete report, products, presentation.
- `CAMPAIGN_LIVE_VALIDATION`: **EXTERNAL_LIMITATION**. No invented analytics, media spend, visitor flow or carrying-capacity measurement.

## Next automated work sequence

1. Audit every final deliverable section against source-backed results, classify *present / partial / missing / externally unverifiable*.
2. Reuse validated current database and experiments without re-ingesting legacy datasets.
3. Prioritize marketing branding/buyer-persona and budget/channel plan, integrated impact and scenario arguments; mark hypotheses clearly.
4. Assemble 30–40-page final technical report and evidence annexes; create integrated <=15-minute colloquium deck.
5. Check each output against rubric and revise within bounded attempts; record genuinely missing measurements without inventing values.
