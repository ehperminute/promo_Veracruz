# Marketing segmentation — iteration 1

## What changed

The project now separates **domestic retention/remarketing** from **international acquisition**.

### Domestic side
The current project is already dominated by domestic demand evidence. For the marketing stage, the useful strategy is not to fabricate a detailed domestic demographic profile. Instead, the future campaign can use first-party behavior from people who:

- are currently travelling in Mexico;
- interacted with Veracruz content;
- viewed an itinerary or destination page;
- visited a destination and can be re-engaged for a later trip.

This makes domestic marketing primarily a **recommendation / remarketing** problem.

### International side
Foreign visitors require **pre-trip prospecting** because many will choose their Mexico itinerary before arrival.

The first public market table uses 2025 air entries to Mexico by country of residence. It does **not** claim that a large market automatically fits every Veracruz package.

The workflow is:

`country market -> package test -> measured response -> evidence-backed fit`

## Why we are not inventing country-level personas

INEGI's 2025 ETI metadata documents variables that would be ideal for this project: country of residence, cities visited, nights, purpose, package, spending, repeat visits and income. However, the record-level ETI base is restricted to the public.

INEGI's 2026 EVI public offer is broader and publishes aggregate information on residence, group characteristics, destination, stay, lodging/reservation, spending, repeat visits and related travel variables.

Therefore this iteration keeps two evidence levels separate:

1. **Country-level market size and growth** — observed.
2. **Aggregate international traveler profile** — observed but not country-specific.
3. **Country x Veracruz-package preference** — unknown and explicitly tested by campaign cells.

## Shortlist versus test matrix

`international_market_shortlist_v1.csv` is a broad screening list based only on observed market scale and recent growth. It is **not** a final advertising recommendation and does not yet include connectivity, language, media cost or destination fit.

`foreign_campaign_test_matrix_v1.csv` is intentionally smaller. It uses six markets for a first controlled experiment so that the project can learn market-package response without exploding into dozens of countries and creatives.

## Initial foreign experiment

Six source markets are used as a manageable first test set:

- United States
- Canada
- United Kingdom
- Argentina
- Spain
- Italy

Each is crossed with four Veracruz packages:

1. Papantla + Zozocolco — culture / archaeology / heritage / gastronomy
2. Catemaco + San Andrés Tuxtla — nature / adventure
3. Córdoba + Orizaba + Coscomatepec — coffee / gastronomy / mountains
4. Actopan + Úrsulo Galván + La Antigua — history / archaeology

This produces 24 controlled cells.

The purpose is not to spend equally on every cell forever. It is to learn which combinations produce qualified interest.

## What the ad algorithm is allowed to do

Within a defined market/package cell, an advertising platform may optimize delivery toward people more likely to interact or convert.

It should **not** decide the strategic question by itself. We preserve:

- country/market;
- package shown;
- creative;
- landing page;
- interaction and conversion metrics.

That means we can later learn:

`market -> package -> response`

instead of receiving one opaque campaign-wide conversion rate.

## Metrics

Primary:
- qualified landing-page rate

Secondary:
- click-through rate;
- itinerary-view rate;
- save/lead rate;
- cost per qualified visit.

A click alone is weak evidence. A visitor who reads the itinerary, opens a map, saves the package or submits a lead is substantially more informative.

## Sources

- DataTur / UPMRIP, 2024–2025 air entries by country of residence:
  https://datatur.sectur.gob.mx/Documentoscompartidos/upm/RES_2026_02.pdf
- SECTUR 2025 foreign-air-tourist age profile:
  https://www.gob.mx/sectur/articulos/sectur-mexico-recibe-mas-de-14-millones-de-turistas-extranjeros-en-2025-un-incremento-sostenido-respecto-a-anos-anteriores
- INEGI 2025 ETI metadata and access conditions:
  https://www.inegi.org.mx/rnm/index.php/catalog/1083
- INEGI EVI January 2026 public profile:
  https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2026/ViajInternales/evi2026_03.pdf
- INEGI 2026 EVI expanded thematic offer:
  https://www.inegi.org.mx/contenidos/programas/evi/doc/Actualizacion_EVI.pdf
