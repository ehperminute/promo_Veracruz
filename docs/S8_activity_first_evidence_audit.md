# S8 — Activity-first audience matching: evidence audit (12 Oct 2026)

## Decision
**Start with travel motivations and specific activities, then identify destinations able to offer them, then intersect with S7's selected destinations and campaign periods.** Do not infer audience demographics or country from a destination's cluster. This is an audit and research base, **not** a final segmentation or a validated advertisement plan.

## What the repository actually contains

Sources reviewed: `destination_profiles_s4.csv` (55 destinations, 50 columns), the consolidated adventure-activity evidence table embedded in the supplied repository digest, and `s7_calendar_budget_100000.csv` from the S7 reproduction. A companion `S8_destination_activity_audit.csv` joins these sources by destination name and flags the MXN 100,000 scenario.

| Destination profile flag | Flagged destinations / 55 | Limit |
|---|---:|---|
| Coast / beach | 11 | Presence category, not a named or accessible beach activity |
| Nature | 46 | Too broad to infer birdwatching, hiking or guides |
| Culture / history | 55 | No discriminatory power as a filter; use specific attractions, events or products |
| Archaeology | 11 | Site-level INAH evidence may support more precise matching |
| Adventure | 19 | Flagging and published activity evidence do not perfectly coincide |
| Gastronomy / coffee | 44 | Not a documented inventory of individual tastings, classes, plantations or restaurants |
| Wellness / spirituality | 1 | Insufficient coverage for confident location-level matching |
| Urban services | 9 | Service capacity is not a traveler motivation by itself |

The activity evidence contains **67 records**, of which **52 have `incluir_preview=1`**, covering **29 distinct destinations**. A preview flag means the project judged the named activity publishable with its evidence and caveat; it does **not** confirm current schedules, availability, access, or safety. In the S7 MXN 100,000 plan, **14 of 20 destinations** have at least one of these named preview activity records. The remaining six may offer activities from other categories, but cannot be assigned an *adventure-activity* message from this particular table alone.

**Critical discrepancy:** the 19 broad `theme_adventure` flags are modeling codes from S4, while the consolidated activity table documents specific activities in 29 destinations; these are different definitions and should not be collapsed or silently overwritten. The flag for culture/history is present in all 55, so matching travelers on that flag alone would give almost no ranking power.

## Evidence for potential audiences (outside research)

Research is not Veracruz-specific unless stated. Findings below support *interests* or *information channels*, not measurable demand for particular Veracruz destinations. Links are provided for checking source methodology.

| Interest or behavior | Evidence and population | Use in S8 | Evidence boundary |
|---|---|---|---|
| Nature, unconventional experiences, wellness / adventure | [Booking.com Travel Predictions 2025](https://www.booking.com/articles/travelpredictions2025.html): 27,713 prospective travelers surveyed online in 33 markets, July–August 2024; reports preferences for nature-based, meaningful and adventure/wellness experiences | Motivate nature/adventure creative hypotheses | Aggregated responses do not tell us which specific Veracruz activities or nationalities will convert |
| Specific adventure-tour activity demand | [ATTA 2025 industry research](https://learn.adventuretravel.biz/research/2025-adventure-travel-trends-insights-state-of-the-adventure-travel-industry): survey of adventure tour operators about 2024 operations and 2025 trends | Identify activity vocabulary, client motivations and operator-side validation questions | Operators are not a representative random sample of all tourists; detail may require report access |
| Culinary motivation and food/coffee | [World Food Travel Association Food Travel Monitor 2026](https://www.worldfoodtravel.org/2026-food-travel-monitor): survey fielded April–May 2026 in China, France, Germany, Mexico, UK, US; average importance of food and drink when choosing destination was reported as 8.2/10 | Supports exploring authentic food, producer visits and coffee-related offers | Aggregate score cannot be attributed to a country or Veracruz; full cross-tabs should be checked before demographic claims |
| Cultural/archaeological heritage | [UK Participation Survey 2024–25](https://www.gov.uk/government/statistics/participation-survey-2024-25-annual-publication/main-report-for-the-participation-survey-april-2024-to-march-2025): 65% of adults engaged physically with heritage in England over previous 12 months | Shows heritage engagement is a measurable motivation and offers example of survey definitions | **Not** international travel intention or specific demand for Mexican archaeological sites |
| Coastal holidays | [Beach.com US beach survey 2025](https://www.beach.com/trends/survey-americans-plan-to-spend-31-percent-more-on-travel/): surveyed 1,007 US adults, January 2025; cleanliness, sandy shore and weather identified as important; US beaches preferred by a majority | Suggests concrete experience and amenity questions for beach messaging | Preference for domestic beaches may argue **against** assuming strong US demand for Veracruz coastal trips |
| Digital discovery / channels | [Expedia Traveler Value Index 2025](https://partner.expediagroup.com/en-us/resources/research-insights/2025-traveler-value-index): over 11,000 consumers in 11 markets; social platforms prominent for inspiration | Supports testing social content alongside search / destination guides | Does not establish campaign conversions or ad effectiveness in Veracruz |
| Culinary subtypes | [Morning Consult 2025](https://pro.morningconsult.com/analysis/culinary-tourism-research-foodies): 2,201 US adults surveyed March 12–13, 2025; culinary travelers differ in preference for casual eateries and when they plan meals | Distinguish food discovery, local eateries, and prebooked cooking tours | US sample; specific activity percentages require full article/table verification |

## Activity-first matching rules

1. **Audience interest → named activity**: e.g. river rafting, coffee tasting, archaeology visit, kayaking, historical walking tour; use externally sourced preferences or mark as a hypothesis. Do not convert preference for *nature* directly into preference for *rafting*.
2. **Activity → local evidence**: require named attraction/product, destination, source URL and evidence status. Keep source date and geographic caveats. `theme_*` presence alone is insufficient to claim a specific activity.
3. **Destination → S7 selection and period**: intersect the activity table with actual S7 calendar rows. A destination not selected in a given budget is not silently added to that optimized scenario; it can be an alternative to discuss or a reason to revisit S7 later.
4. **Season → practical feasibility**: investigate operating schedules, rainfall/weather, regional transport, opening dates, protected-area permits and operator availability *before* final seasonal ad content. S5 occupancy forecasting covers only three DataTur hotel centers; do not project it onto every municipality.
5. **Market → feasibility and channel**: choose country/language based on accessible transport, research on travel behavior, communication feasibility and eventual conversion evidence. A global survey result is not automatically a Mexico/US/Canada preference percentage.
6. **Evidence labels**: `observed_research`, `documented_local_activity`, `hypothesis`, `not_yet_verified`, and `excluded_due_to_geographic_ambiguity`. No synthetic ranking scores disguised as real demand.

## Preliminary activity-led candidate messages (illustrations, not approved campaign allocations)

| Interest group | Named local activity examples from reviewed evidence | Example locations in the source table | Next check |
|---|---|---|---|
| River / outdoor adventure | Rafting; rappelling; mountain biking | Jalcomulco, Actopan, Tlapacoyan | Current operators, rainy-season restrictions, safety/access |
| Water and mangrove experiences | Kayak in lagoon/mangrove; paddle surf | Coatzacoalcos, Tamiahua | Current availability and protected-area access |
| Mountain trails and vertical activities | Canyoning; highland hiking; downhill cycling | Perote, Xico, Coscomatepec | Named routes, providers, season/weather |
| Culture / archaeological interpretation | **Not sufficiently represented in the adventure table** | Papantla, Castillo de Teayo are candidate *site-level* checks, not certified matches from this table | Join INAH site inventory and attraction records |
| Food / coffee experiences | **Not sufficiently represented as specific activities in current reviewed table** | Coatepec is a candidate for targeted verification, not a certified tasting-tour offer | Catalog specific coffee tours, farms, tastings, producers |
| Coastal leisure | **Beach tag alone is insufficient** | Tecolutla, Veracruz coast as candidate places only | Identify beaches, services, cleanliness/accessibility, season |
| Wellness / spirituality | **Insufficient location/activity coverage** | Do not select places from generic labels | Find individual, non-stereotyped, verifiable products |

## Gaps before final S8 campaign design

**Blocking for precise matching:** specific local activity/product records for archaeology, food/coffee, cultural interpretation, coastal recreation and wellness; current operating/access evidence for adventure experiences; year/season feasibility for selected destinations. The existing 295 official tourism product cards and 114 source-reviewed attractions should be parsed or reused where available instead of repeating web research from zero.

**Blocking for country-level audience claims:** comparable country-specific cross-tabs of motivations; practical route/access and cost research; demand for Veracruz, where observable. Booking.com and WFTA include Mexico and selected foreign markets in their studies, but pooled findings cannot be assigned to those markets without subgroup results.

**Blocking for an executable media budget:** actual indicative ad-channel cost data (clearly dated and contextual), selection of conversion goals, website instrumentation plan. S7's MXN 5,000 placement cost is a hypothetical OR unit, **not** the price of Instagram advertisements.

## Recommended next technical artifact

Build one canonical `activity_evidence` table from the repository's official product cards, attraction evidence, and existing adventure source audit, with destination, named activity, category, URL, geographic confidence, evidence date, current-operation status, and season constraints. Then perform the interest → activity → location → S7 intersection without changing S7 allocations. The matching can be done with pandas; no new machine-learning model is required.
