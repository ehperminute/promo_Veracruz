# Veracruz Tourism Intelligence

Small reproducible repository for the Veracruz tourism data-science project.

## Goal

Use current public/official tourism and economic data to compare destinations, identify structurally similar or undermeasured places, inspect tourism-product associations, and support later territorial and campaign decisions.

This repository is intentionally a **current project**, not an archive of every earlier iteration.

## Repository structure

```text
.
├── README.md
├── requirements.txt
├── data/
│   ├── processed/
│   │   ├── destination_master_v1.csv
│   │   ├── tourism_products_sample_v1.csv
│   │   └── undermeasured_candidates.csv        # generated
│   └── external/
│       └── README.md
├── scripts/
│   ├── build_candidates.py
│   ├── cluster_destinations.py
│   ├── mine_product_associations.py
│   └── run_pipeline.py
├── notebooks/
│   ├── 00_data_overview.ipynb
│   └── 01_results_overview.ipynb
├── outputs/
│   ├── associations/                           # generated
│   ├── clustering/                             # generated
│   ├── ml/
│   │   └── ml_evaluation_regression_linear_v1.csv
│   └── territorial/
│       └── territorial_shortlist_v1.csv
├── docs/
│   ├── DATA_SOURCES.md
│   ├── METHODOLOGY.md
│   └── LIMITATIONS.md
└── tests/
    └── test_smoke.py
```

## Run

```bash
python -m pip install -r requirements.txt
python scripts/run_pipeline.py
```

The pipeline rebuilds the candidate list, clustering outputs, and association rules from the small processed datasets included here.

## What is deliberately not in GitHub

Large raw DENUE, INAH, DataTur and PIB downloads are not duplicated in the repository. Their sources and expected roles are documented in `data/external/README.md` and `docs/DATA_SOURCES.md`.

## Interpretation rules

- Missing DataTur coverage does **not** mean low tourism demand.
- INAH visitor counts measure archaeological attractions, not total municipal tourism.
- DENUE establishments describe economic/tourism structure, not ecological carrying capacity.
- Synthetic/future campaign behavior is not treated as observed tourist evidence.
- Clusters are analytical groupings, not automatically viable travel routes.
