# Veracruz tourism experience catalog: impact assessment

Review date: 2026-10-12 (project local date). Source: official Veracruz *¿Qué hacer en Veracruz? Catálogo de Experiencias Turísticas 2025*, 66 uploaded two-page spreads, print pages 1–131 (including cover/front matter). Uploaded as seven PDFs.

## Source characteristics
- The catalog's table of contents lists 28 experience **categories**, not 28 individual tours or a verified count of 619 distinct purchasable experiences.
- Many category sections combine promotional prose, municipality lists, named tourism providers (occasionally social handles/contact details), terrestrial/air travel estimates, and photographs.
- The cover indicates service providers with an RNT registration valid for the catalog's publication; this does not establish their registration or operational status today.
- Prose about a broad area, operator departure city, route, or thematic category must not be treated as proof of an activity occurring inside every listed municipality. Current route times, scheduled flights, operator prices, availability, environmental permissions and current registration status are not established.

## Stage-by-stage impact
| Stage | Recommended effect | Not supported by the catalog |
|---|---|---|
| S0–S3 data engineering | Register full original catalog and page provenance; stage canonical activity/provider/municipality many-to-many tables; reconcile place aliases and source dates | Demand, hotel room-night occupancy, tourist volume |
| S4 mining | Independent activity-level profiles and product co-occurrence; audit overly broad historic theme flags; evaluate changes to clustering before adopting | Treat new provider counts as visitor demand or silently change existing 12-cluster results |
| S5 ML | Possible future explanatory features only if historical snapshots, timing and consistent coverage can be established; otherwise descriptive context | Backfill annual tourism demand or monthly 2016–2024 features from a 2025 snapshot (look-ahead leakage) |
| S6 uncertainty | Add uncertainty provenance regarding availability and provider evidence; not numerical calibration data | Calibrate forecast residuals or generate probability distributions from provider listings |
| S7 OR | Possibly define availability/experience eligibility and geographic connectivity proxies after verification; test sensitivity on the *same* objective | Advertiser ROI, actual 5,000 MXN media costs, capacity/seasonality from static provider listings |
| S8 marketing | Major improvement: map audience interest -> named activity -> place -> provider; build segment-specific messages with confidence and current verification checks | Actual audience conversion, demand or viral sharing, live reservability |
| S9 website & report | Searchable evidence-backed experiences, source citations, methodology and limits; differentiate from static government catalog through analysis and campaign plan | Repost the entire catalog uncredited or imply it is freshly validated |

## Specific examples (source PDF pagination)
- Artisan activity: Naolinco shoemaking; artisanal craft description and providers, catalog print pp. 8–11.
- Birdwatching: Catemaco, San Andrés Tuxtla, Actopan, Puente Nacional with named providers, pp. 12–15.
- Canyoning: Teocelo, Xico, San Andrés Tuxtla and Jalcomulco with providers, pp. 28–31.
- Kayak: Zongolica, San Andrés Tuxtla, Atoyac, Veracruz, Alvarado, Tamiahua, Boca del Río and Amatlán de los Reyes, pp. 66–69.
- Spirit/wellness: Coatepec, Jalcomulco, Catemaco, Xico, Úrsulo Galván, Papantla, San Rafael and Soteapan, pp. 102–105.
- Archaeology: catalog narrative explicitly places Cempoala in Úrsulo Galván and Quiahuiztlán in Actopan, pp. 128–129; **do not assign San Lorenzo museum access to Catemaco merely because it is listed in the broader section**.

## Immediate actions, before changing the model
1. Preserve the 2025 catalog as a frozen raw source; source-register seven segments with original printed page references (or reconstruct a single source PDF with stable hash).
2. Extract one **record per specific activity × municipality × provider**, preserving catalog category and page; allow multiple provider records for the same activity.
3. Categorize evidence: activity explicitly tied to municipality; municipality-only category association; regional prose; operator departure location. Don't combine these automatically.
4. Match new records to the 55 curated destinations; log municipalities outside the current 55 as coverage gaps, not automatically new candidate destinations.
5. Compare new and prior S4/S8 evidence by source, name and municipality to avoid double-counting; flag contradictions for manual review.
6. Run prospective S8 matching and coverage counts; rerun S4 clustering/S7 only as a labeled sensitivity experiment with user approval if it changes the model's meanings.
7. Update teacher/progress reports with a short *new data source under incorporation* addendum; do not rewrite S5/S6 numerical results.

## Source risks to retain explicitly
1. Provider listing is a statement in a 2025 publication, not proof of current offering, prices or RNT validation.
2. Travel-time/flight listings in the catalog are illustrative, not validated live routes.
3. Ecological or cultural participation (e.g., turtle releases, ceremonies) may require permissions, community consent and season-specific checks.
4. The national and official 619-activities figures reported elsewhere must not be substituted for a deduplicated count extracted from these exact PDF pages.
5. Event, attraction, tour and accommodation should be different entity types, not interchangeable activities.
