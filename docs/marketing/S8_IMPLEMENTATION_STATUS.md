# S8 — Activity-first campaign evidence, implementation v0.1

Date: 12 October 2026. This is the first **reproducible S8 stage**, not the final advertising strategy.

## Decision logic

Start with candidate audience interests supported at category level by external published tourism studies; then find **named, source-linked tourist activities** in Veracruz; then intersect these offerings with the **actual S7 destination/season selections**. No use of `theme_culture_history` (all 55 were flagged in S4) as a marketing segmentation variable. Do not replace missing evidence with absence of culture or demand.

The script generates `outputs/marketing/s8_activity_audience_matches_100k.csv` using three repository inputs:

- `outputs/or/s7_calendar_budget_100000.csv`: selected destinations, periods and assumed cost, from S7 MILP.
- `data/reference/S8_cultural_activity_catalog_v2.csv`: verified heritage and conservatively classified leads. Only `PRIMARY_SOURCE*` classes become preliminary heritage matches.
- `data/reference/S8_destination_activity_audit.csv`: named, source-linked adventure examples (not verified bookable).

The audience labels are **hypotheses about interests**, not empirically measured market segments, conversion propensities, or geographic/demographic targets. A source establishing the existence of an archaeological site cannot establish its current opening hours. Adventure activity records require access, provider, safety, and season checks before a real advertisement.

## External audience / creative evidence (not demand for Veracruz)

1. Booking.com Travel Predictions 2025, survey of 27,713 travelers across 33 markets; exploratory travel motivations: https://www.booking.com/articles/travelpredictions2025.html .
2. Expedia Group Traveler Value Index 2025, >11,000 travelers from 11 markets; social media as travel inspiration: https://www.expedia.com/newsroom/travel-priorities-reinvented-expedia-groups-2025-traveler-value-index-signals-a-shift-in-consumer-priorities/ .
3. Expedia Group Advertising travel content research (2025); stated video influence: https://www.expedia.com/newsroom/expedia-group-advertising-travel-content-research/ .

These studies suggest topics/media to **test**, not guaranteed audience conversion or verified preferences for individual Veracruz destinations. Do not copy global survey percentages into simulated campaign performance.

## Budget rule

S7's MXN $5,000 is a hypothetical **destination-period promotion budget**. S8 does **not** allocate a second independent MXN $5,000 to every activity row. Multiple rows may describe alternative messages for the same selected placement. No channel allocation or media quotations are claimed at this stage.

## Gaps and next steps

- Expand comparable named source-linked activities beyond the adventure and primary-source heritage slices: local cuisine/coffee, ecological experiences, beaches, museums/arts/crafts; official product-card data and S4 attraction evidence should be normalized at activity level, not promoted solely from category flags.
- Add source-level verification and trip timing for each activity; research operating schedule, access, safety, and actual existence of providers where relevant.
- Complete origin-market shortlisting with geography/access and appropriate external market-specific preference data. The national foreign-air arrivals table is **not** evidence of travel to Veracruz.
- Define channel tests and KPIs (reach, CTR, landing-page engagement, qualified inquiries) without inventing benchmarks or ROI. Validate creative claims before real use.
- Rebuild S8 output for all four S7 budgets once input files are confirmed and versioned; add automated tests and dependency integration.

## Rebuild

`python scripts/marketing/build_s8_activity_matches.py`

This patch is **additive**. It does not change S4 clusters, S5/S6 models, S7 objective/constraints, or the static website. The output records are transparent candidate matches, not a statistically fitted recommendation model.
