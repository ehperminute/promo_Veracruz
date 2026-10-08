# Current Project Status — Veracruz Tourism Intelligence

## S0–S3: data foundation
Completed and reproducible:
- source registry / frozen raw sources;
- cleaning and interim tables;
- destination master;
- observed demand series;
- origin-market opportunity table.

Interpretation boundaries:
- missing DataTur != low tourism;
- INAH visits are attraction visits, not total municipal demand;
- DENUE measures service/infrastructure structure, not carrying capacity;
- association rules represent co-occurrence in the official tourism offer, not tourist movement.

## S4: descriptive analytics / data mining
Current working components:
- Veracruz destination-character profiles;
- Gower + PAM local clustering;
- ambiguous-membership diagnostics;
- tourism-product association mining using the full parsed catalogue;
- candidate / analogue analysis;
- national character analogue benchmarking;
- national structural analogue benchmarking.

Superseded:
- legacy K-Means k=15/k=17 outputs as final segmentation;
- national structural clustering as a national typology;
- national character clustering as a national typology.

## What is still missing

### S5 — Machine learning
- forecast observed demand where reliable time series exist;
- time-aware validation / walk-forward testing;
- baseline comparison;
- MAE/RMSE and justified additional metrics;
- no extrapolation of observed-anchor demand into unmeasured destinations as fact.

### S6 — stochastic / uncertainty
- residual/error distributions from S5;
- uncertainty intervals or scenarios;
- assumptions documented.

### S7 — territorial + operations research
- geographic / feasibility constraints;
- current shortlist generated from current analysis;
- resource/budget/package optimization;
- cluster membership alone must not imply route feasibility.

### S8 — marketing
- current destination/package results;
- origin-market evidence;
- segment hypotheses;
- Veracruz package matching;
- buyer personas labeled as constructed hypotheses;
- proposed channels, creatives and KPIs;
- no fake live campaign results.

### S9 — final portfolio / submission
- reconciled final report;
- limitations;
- reproducibility / data lineage;
- course-specific deliverables consistent with the canonical project.

## Page / prototype
A page prototype can be designed now as a low-fidelity information architecture because the major data entities are known.

Suggested sections:
1. Veracruz overview / problem statement
2. Destination explorer
3. Destination character / local cluster
4. National analogues
5. Demand / seasonality where measured
6. Tourism-product relationships
7. Candidate packages / territorial decision layer
8. Market opportunity / marketing layer
9. Methods, sources and limitations

Sections 5–8 should be progressively populated as S5–S8 are completed.

## Recommended next order
1. Freeze S4 outputs and documentation.
2. Build a lightweight page prototype / information architecture if useful.
3. Continue with S5 machine learning.
4. S6 uncertainty.
5. S7 territorial / operations research.
6. S8 marketing.
7. Finalize the page/report in S9.
