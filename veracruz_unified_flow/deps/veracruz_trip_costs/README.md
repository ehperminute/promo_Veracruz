# Veracruz itinerary trip-cost estimator — source-aware pilot

This release adds a **collapsible cost estimator within the existing road itinerary**; it does NOT overwrite the project database or replace the research pipeline.

## Install (from promo_Veracruz root, after interest recommender + current route planner)

```bash
unzip -o VERACRUZ_TRIP_COST_ESTIMATOR_2026-10-22.zip
python veracruz_trip_costs/install.py .
node veracruz_trip_costs/tests/test_core.js
node --check site/js/itinerary-pricing.js
python -m http.server 8100 -d site
```

Open the forwarded 8100 port and refresh. Add **Coatepec** as a stop. Open **Estimate trip costs / Estimar costos** under the itinerary; select *Tour Museo del Café*. With two travelers this makes the source-listed component MXN 180, not a complete trip total. Choose two nights, fuel price, consumption, and calculate the road route if the routing API responds. Add Catemaco to compare published room rates. **You must select offerings explicitly.**

## Data and calculation rules

- `site/data/provider_prices.json` is derived from the **46 rows** of `verified_prices.csv`, retaining original source link, date, advertised amount, unit, restrictions and provider. It is commercial reference data, not a rewrite of the canonical research database.
- Listings attach by **exact normalized municipality name** when a user's selected stops specify a municipality. This is a provisional geographic association, not proof a service covers a specific attraction. Regional or circuit listings (21 records) are available as source-linked references, never silently matched or included in the total.
- Offers with unconfirmed price unit cannot be totaled. Hotel rooms are calculated as `price × rooms × nights`; admission and activities usually use `price × visitors`, subject to recorded group minimums and an illustrated 16% VAT addition when the record explicitly says “IVA adicional.” Some package fares assume double occupancy. **Conditions/eligibility must be confirmed with each operator.**
- Transport fuel cost = **actual route km × fuel MXN/L ÷ vehicle km/L**. Km are **not** inferred from straight lines. If the routing demo server fails, the traveler may enter a road distance from an independent directions provider; source is labeled manual. Tolls, meals, alternative lodging and other expenses are user estimates, not current market quotes. No default real-world prices are invented.
- The estimated subtotal is only **selected advertised services + entered assumptions**. Unpriced hotel, meals, tolls or attractions are listed separately. Provider services do not imply paid arrangements, confirmed inventory, capacity or booking authorization. Cost sharing/published references are not transactions.
- To avoid obvious double counting, a separately entered room estimate is suppressed when a published room rate is selected. Selecting overlapping packages/entrances still triggers an explicit warning; package inclusion rules must be checked before use.
- The interest-based recommender's original budget cap remains an **assumption-only candidate filter**, independent of this detailed estimator. A recommendation within that earlier cap does *not* establish a real trip within budget. Reconcile the two after real operator coverage improves.

## Acceptance criteria and limits

1. At least one city without a price record shows *unpriced*, not `MXN 0`.
2. Coatepec, Catemaco and Jalcomulco price listings appear when that city is added; regional offers remain **references only**.
3. Adding/removing/reordering stops changes the offers and clears old route-distance estimates.
4. Successful road-route responses populate km automatically; a failed API never fabricates distance.
5. A published room is not counted in addition to manual lodging estimates.
6. The source, conditions, unit and checked date are visible for every listing.
7. English, Spanish and Japanese labels display; content names remain as published.
8. No ZIP, prices, tests or backup are committed by accident; the ZIP is ignored by root `.gitignore` and the local backup is ignored.

**No live availability, reservations, transaction billing or full statewide price coverage is claimed.** This is a source-aware cost planner for the existing static website, with browser storage limited to the current session.
