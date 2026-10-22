# Evidence for the academic submission — travel cost and provider comparison

## Research problem and functional response

The original tourism dataset documents attractions and specific activities but **does not contain a verified live inventory of provider tariffs or hotel room availability**. The static travel-planning website adds a separate, auditable pricing ledger. Its purpose is to make some itinerary costs visible without confusing missing prices with free services or claiming bookings are available.

The commercial reference ledger dated 2026-10-21 has **46 advertised entries**: 25 tied to exactly one of five documented municipalities (Catemaco 8, Coatepec 4, Jalcomulco 9, Papantla 2, Veracruz 2), and 21 regional or circuit offers without validated local pickup/itinerary correspondence. Consequently published-price coverage is **5/212 municipality reference points (2.36%)**, not statewide. Three listings are classified as directly totalable under their advertised unit, 24 conditional on restrictions, and 19 have unknown units and are reference only. No availability is confirmed. All provider offers retain source URL, date and terms.

For a selected itinerary, the consumer can choose only locally mapped references with a known pricing unit. The estimated cost includes per-person activity prices and per-room nightly rates with indicated minimum-group or room-capacity adjustments; separate user-provided lodging assumptions are suppressed if a room price (or package with lodging) is selected. The routing provider's travel distance (if received) supports an illustrative fuel calculation, `fuel cost = road_km / km_per_liter * MXN_per_liter`, with the user's fuel price and vehicle efficiency. No distance is invented if routing fails. Tolls, meals, miscellaneous expenses and unlisted hotels remain user-entered assumptions or unknowns. The interface displays a subtotal and a list of unresolved items and restrictions, never a complete guaranteed trip quote.

## Application to the PP6 research and marketing campaign

The feature supports **information-based discovery**: a user can select interests, generate a source-backed destination suggestion, arrange the road itinerary and review partial known costs with links to providers. This operationalizes the campaign proposition without assuming commission contracts, a reservation system or observed tourist behavior. The academic budget optimizer (assumed MXN 5,000 per campaign placement) remains distinct from the tourist cost estimator; their financial variables must never be pooled.

The price-coverage result exposes a significant constraint on the project's stated accessibility and economic feasibility. No empirical claim about tourist expenditure, price competitiveness, value for money or conversion rate can be justified for the 207 municipalities without direct local prices. Future studies could measure provider-price completeness, source staleness, user task completion, and referrals to operators. Those are **proposed measures**, not observed outcomes. The website is a prototype of campaign delivery, not evidence of paid advertising, sales uplift, redistributed visitation or sustainable carrying capacity.

## Reproduction

- Source ledger: `veracruz_trip_costs/assets/verified_prices.csv` (46 advertised listings, sources and checks recorded).
- Published static dataset: `site/data/provider_prices.json` (sha256 traced to source ledger).
- Engine: `site/js/itinerary-pricing-core.js`.
- UI: `site/js/itinerary-pricing.js`.
- Tests: `node veracruz_trip_costs/tests/test_core.js` and `python veracruz_trip_costs/tests/validate_release.py .`.
- Coverage: `outputs/pricing/price_coverage_audit.json` (derived; not new tourism records).

For the article, include a concise table of cost category, variable, source, unit and limitation; move the 46-row inventory to an annex. Cite the individual provider website and observation date for examples; do not substitute generic tourism-sector references for actual prices. Do not describe estimates as verified expenses, confirmed reservations or statewide price coverage.
