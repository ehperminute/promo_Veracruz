# PP6 research / publication boundary — 2026-10-21

This is a status inventory, **not** a claim that the project is complete.

## What can be defended from reproducible records

- Tourism research: recovered source-linked SQLite, including documented specific municipality–activity relationships and original source descriptions. Recorded absence of an activity is not evidence the municipality lacks it.
- Data mining: activity-first retrieval is demonstrable. The old 55-destination / 12-cluster Gower/PAM representation is **historical and has not been validated as a current-catalog tourist segmentation**.
- ML: occupancy models were benchmarked. Small and reporting-center-limited samples, and weak improvement against simple baselines, do not justify statewide visitor predictions.
- Stochastic: rolling interval checks and the negative Markov comparison are research results, not campaign-response probability forecasts.
- OR: tested illustrative coverage optimization; 5,000 MXN per placement is a user-provided model assumption, not a verified advertising cost or evidence of actual tourist redistribution.
- Marketing: proposal and KPI measurement plan can be documented, but buyer-persona assumptions, provider arrangements, bookings, measured reach and visitor flows are not observed.

## Open research decisions (not web UI bugs)

1. Run and interpret a **current-catalog** pattern analysis on specific activities, with source coverage and sparsity/selection sensitivity. Do not revive 55-profile clusters as though they were current, or reduce specific experiences to broad thematic flags. If no robust associations emerge, document that negative result.
2. Reconcile the previously identified 2025 international-origin table discrepancy (11 country counts) before using market-size rankings or origin targeting in public claims. Do not infer traveler interests from arrival-country counts.
3. Complete a **claim-to-evidence trace** for the cross-disciplinary technical report and campaign. Ensure every numerical assertion points to a particular program/data/output, and distinguish inferred capacity from real destination carrying capacity.
4. Decide scope of optional analogue/foreign-preference hypotheses: report the existing holdout analogue experiment as exploratory; without suitable traveler-preference observations, mark preference extrapolation untestable rather than inventing it.
5. For commercial viability, actual price/availability and provider-to-service matching still require direct verification and partnerships. These are future data/business dependencies, not prerequisites for an honest academic prototype.

## Website product gate

- Home page must display only up-to-date, evidence-linked municipality and attraction discovery and an itinerary widget; no obsolete 55-profile/12-cluster claim.
- Tecolutla and all other mapped municipalities are selectable as **approximate municipality reference points**; the route builder also includes precisely mapped attractions.
- Public OSRM demo availability is not guaranteed; verify in a real browser, and do not label an external directions link an integrated booking/route engine.
- Historical coursework `planner.html` is explicitly archived and not linked from the home page. Old files are retained for audit, not the current product.
