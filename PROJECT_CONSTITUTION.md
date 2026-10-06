# PROJECT_CONSTITUTION.md
Version: 1.0
Status: PROPOSED — becomes FROZEN on user approval
Owner: User
Change authority: USER ONLY
Project: Veracruz Tourism Intelligence / Semester Project

---

## 1. Purpose

This project is one coherent semester-long Data Science system focused on tourism in Veracruz.

Its purpose is to integrate official/public tourism data, describe uneven measurement and demand, identify relevant destination patterns, forecast observed demand where valid, represent uncertainty, evaluate territorial and operational feasibility, and translate those results into a proposed digital-marketing strategy.

The project is not a collection of unrelated course exercises. Each course contributes one stage or analytical lens to the same pipeline.

---

## 2. Non-negotiable principles

1. Every active result must be reproducible from upstream data and code.
2. No historical result CSV, old shortlist, old cluster assignment, or prior model output may be used as an input to the active pipeline.
3. Frozen raw-source snapshots are legitimate inputs; derived artifacts are always regenerated.
4. Missing DataTur coverage means missing measurement, not low demand.
5. INAH visitor counts measure visits to archaeological attractions, not total municipal tourism.
6. DENUE describes tourism/service structure, not ecological carrying capacity.
7. Association rules built from tourism products describe offer co-occurrence, not tourist travel histories.
8. Clusters describe analytical similarity; they do not automatically define viable geographic routes.
9. Synthetic data may be used only for demonstrations explicitly labeled synthetic. Synthetic data may never support claims about actual tourists, destinations, demand, or campaign performance.
10. There is no live campaign, hosted booking platform, cookie collection, or real conversion dataset in the semester project unless the user later explicitly changes scope.
11. Buyer personas and targeting profiles are proposed marketing representations unless supported by observed evidence.
12. National destinations outside Veracruz may be used only as analytical/reference examples when needed. They are not campaign conquest targets. Current campaign recommendations remain Veracruz-focused.
13. Code, reports, notebooks, and submissions must all describe the same pipeline and the same assumptions.
14. Structural simplification must never remove an active stage or break data lineage.
15. The assistant may propose changes to this constitution but may not modify it without explicit user authorization.

---

## 3. Canonical end-to-end flow

```text
S0  SOURCE REGISTRY / FROZEN RAW DATA
    DataTur
    INAH
    DENUE
    tourism GDP
    official Veracruz tourism products / regions / Pueblos Mágicos
    international origin-market statistics
            ↓
S1  INGESTION + CLEANING
    normalize formats, dates, names, municipalities, categories
            ↓
S2  CURATED INTERIM TABLES
    DataTur monthly fact
    INAH monthly fact
    municipal tourism infrastructure mart
    official tourism-product table
            ↓
S3  INTEGRATED ANALYSIS TABLES
    destination master
    demand time series
    market opportunity tables
            ↓
S4  DATA MINING / DESCRIPTIVE ANALYTICS
    clustering
    similarity
    product associations
    candidate detection
            ↓
S5  MACHINE LEARNING
    forecast observed demand
    compare against baselines
    evaluate out-of-sample
            ↓
S6  STOCHASTIC / UNCERTAINTY
    residual distributions
    scenarios
    prediction / uncertainty ranges
            ↓
S7  TERRITORIAL + OPERATIONS RESEARCH
    feasibility
    constraints
    package/resource/budget optimization
            ↓
S8  MARKETING
    tourist/origin-market segmentation from available evidence
    segment × Veracruz-product matching
    buyer personas as labeled hypotheses
    proposed campaign messages / channels / KPIs
            ↓
S9  FINAL SUBMISSION / PORTFOLIO
    conclusions
    limitations
    reproducibility
    course-specific deliverables
```

A hypothetical post-deployment feedback loop may be documented conceptually, but it is outside the active semester pipeline unless the user explicitly changes scope.

---

## 4. Data status classes

Every dataset in the project must belong to exactly one of these classes.

### RAW
Frozen snapshot of an original source. Never edited manually.

### REFERENCE
Small curated project knowledge that is not naturally produced by a raw-data transformation, such as manually reviewed destination-theme labels or explicit source mappings. Every row/field must retain provenance.

### INTERIM
Mechanically generated cleaned/aggregated tables between raw and final analytical tables.

### PROCESSED
Analysis-ready canonical tables consumed by multiple downstream stages.

### OUTPUT
Generated analytical/model result. Must never become a silent upstream input unless the constitution explicitly defines that downstream dependency.

### PROPOSAL
Marketing copy, persona, campaign matrix, or hypothetical implementation design. Not empirical evidence.

### SYNTHETIC
Artificial data for demonstration/testing only. Always labeled and isolated.

---

## 5. Canonical repository structure

```text
promo_veracruz/
├── PROJECT_CONSTITUTION.md
├── PIPELINE_MANIFEST.yaml
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/
│   │   ├── datatur/
│   │   ├── inah/
│   │   ├── denue/
│   │   ├── pib/
│   │   └── markets/
│   ├── reference/
│   ├── interim/
│   ├── processed/
│   └── synthetic/
│
├── scripts/
│   ├── data/
│   ├── mining/
│   ├── ml/
│   ├── stochastic/
│   ├── optimization/
│   ├── marketing/
│   └── run_pipeline.py
│
├── notebooks/
│   ├── exploration/
│   └── presentation/
│
├── outputs/
│   ├── mining/
│   ├── ml/
│   ├── stochastic/
│   ├── optimization/
│   └── marketing/
│
├── docs/
│   ├── DATA_SOURCES.md
│   ├── DATA_DICTIONARY.md
│   ├── DATA_FLOW.md
│   ├── METHODOLOGY.md
│   ├── LIMITATIONS.md
│   └── decisions/
│
├── submissions/
│   ├── big_data/
│   ├── data_mining/
│   ├── machine_learning/
│   ├── stochastic_models/
│   ├── operations_research/
│   └── digital_marketing/
│
└── tests/
```

`archive/` is not part of the active logical system. Development backups may exist outside the repository, but old results must not appear in the active pipeline.

---

## 6. Stage contracts

### S0 — Source registry

Inputs:
- official/public source URLs or user-provided original files

Required output:
- exact frozen raw snapshot or exact retrievable version
- source institution
- retrieval date/version
- checksum when practical
- source description

Prohibited:
- altering raw files
- replacing a source silently

### S1 — Ingestion and cleaning

Inputs:
- S0 raw files

Outputs:
- cleaned/interim tables only

Required:
- deterministic scripts
- no manual spreadsheet edits hidden from the pipeline
- explicit normalization rules

### S2 — Curated interim tables

Required tables include, where data support them:
- DataTur tourism-center/month fact
- INAH Veracruz site/month fact
- municipal infrastructure/tourism-economy mart
- tourism-product/municipality table

These are produced from S0/S1, not copied from historical results.

### S3 — Integrated tables

Canonical core tables:
- `destination_master`
- observed demand time series
- origin-market opportunity data
- supporting reference tables

The destination master combines structural evidence and source-backed destination attributes. It must not encode unobserved demand as zero.

### S4 — Data Mining

Permitted analyses:
- clustering / similarity
- association analysis of official tourism products
- destination candidate detection
- descriptive concentration / segmentation

Required:
- feature list documented
- direct demand excluded from similarity models when doing so would cause leakage
- cluster diagnostics
- interpretation limitations

### S5 — Machine Learning

Purpose:
- model observed demand where time-series evidence exists

Required:
- time-aware train/test or walk-forward validation
- baseline comparison
- MAE/RMSE and other justified metrics
- predictions generated from current processed data

Prohibited:
- using old prediction CSVs as current inputs
- treating models for observed anchors as proof of demand for unmeasured destinations

### S6 — Stochastic / uncertainty

Inputs:
- current S5 predictions/residuals and current observed data

Outputs:
- uncertainty ranges/scenarios used downstream

Required:
- assumptions documented
- stochastic parameters derived from current data or explicitly justified

### S7 — Territorial / Operations Research

Inputs:
- current structural data
- current demand/uncertainty outputs
- current geographic/feasibility constraints

Outputs:
- current shortlist / allocation / optimized decision

Prohibited:
- hard-coding an old shortlist as the answer
- assuming cluster membership alone implies route feasibility

### S8 — Marketing

Inputs:
- current destination/package results
- current market evidence
- externally sourced tourist-profile evidence when available

Outputs:
- target segment hypotheses
- Veracruz package matches
- buyer personas labeled as constructed
- proposed creatives/channels/KPIs

No live campaign outcomes are claimed.

### S9 — Final deliverables

Every report/presentation/submission must be generated from or reconciled with the current pipeline.

Course-specific submissions may emphasize different stages, but must not contradict the canonical system.

---

## 7. Course integration

### Big Data
Data architecture, heterogeneous source ingestion, storage/processing rationale, scalable data flow.

### Data Mining
Association rules, clustering, similarity, pattern discovery, segmentation logic.

### Machine Learning
Observed-demand forecasting and predictive evaluation.

### Stochastic Models
Uncertainty, probabilistic demand scenarios, risk representation.

### Operations Research
Optimization and constrained decision-making using current model outputs.

### Digital Marketing
Evidence-based segmentation, Veracruz-product matching, campaign proposal, KPIs.

No course creates a disconnected mini-project.

---

## 8. Change-control protocol

Once approved by the user, this document is FROZEN.

A structural change requires:

```text
CHANGE REQUEST
1. Proposed change
2. Reason
3. Files/stages affected
4. Downstream consequences
5. Migration plan
6. User approval
```

Without explicit user approval:
- stage order cannot change;
- active stages cannot be removed;
- meaning of a data class cannot change;
- empirical/synthetic boundary cannot change;
- project scope cannot expand into a live campaign;
- downstream stages cannot start consuming historical outputs.

Normal implementation changes do NOT require constitutional approval when they preserve the contracts above, for example:
- bug fixes;
- refactoring a script without changing inputs/outputs;
- adding tests;
- replacing a model with a better validated model inside the same S5 contract;
- adding a new official source without changing the project's logic.

---

## 9. Assistant operating rules

Before changing code or documents, the assistant must:

1. Identify the affected stage.
2. Check this constitution.
3. Identify upstream inputs and downstream dependents.
4. Modify the minimum necessary files.
5. Rerun affected tests/pipeline stages.
6. Report exactly what changed.
7. Never silently rewrite architecture.
8. Never delete a stage because it is inconvenient.
9. Never promote an old artifact into an active input.
10. Ask for user authorization only when a constitutional/structural change is genuinely required.

---

## 10. Definition of done

The semester project is structurally complete when:

```text
raw/reference data
        ↓ reproducible scripts
interim/processed tables
        ↓ reproducible analyses
mining + ML + stochastic + OR + marketing outputs
        ↓
course submissions and final portfolio
```

can be explained from left to right without unexplained jumps, hidden historical results, or synthetic evidence presented as real.

---

END OF PROPOSED PROJECT CONSTITUTION v1.0
