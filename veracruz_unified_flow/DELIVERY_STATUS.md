# PP6 unified product — evidence and acceptance status (2026-10-22)

The intended public workflow is **Discover → select stops → calculate road route → inspect partial cost estimate → contact published providers**.

## Work completed in this release

- Replaced activity-count-biased Surprise-me ranking with bounded evidence-gated novelty selection. A feature occurring in one municipality **in the database** is described as uncommon **in the database**, not as a low-tourism site. The score rewards documented distinctive activities, variety and approximate proximity; randomization changes the candidates. Selection is limited to the 216-link / 61-municipality strict activity evidence set, even though the general map contains 212 municipalities and 506 attraction records. General map coverage must not be confused with verified specific activity availability.
- Clarified discovery's provisional budget allowance and kept the *separate* itemized cost estimator as the only source of calculated prices. Relocated the pricing panel **after** road-route controls. Published price sources are unconfirmed for availability; missing entries remain explicitly unknown.
- Kept the historical 55-place/12-cluster dataset archived, with canonical databases and regional routing algorithms unchanged.

## Gate assessment

| Gate | Current status | Proof/limit |
|---|---|---|
| Municipality and attraction selection | TESTED in simulated browser | 212 municipal references / 506 mapped attractions; locations can be approximate |
| Novelty recommender | TESTED in simulated browser | Novelty scores from source-backed activity records, not popularity |
| Source and price data | TESTED for integrity | 216 activity links, 46 price entries; 25 stop-linked in five municipalities |
| 2-person known-price calculation | TESTED in simulated browser | Two Coatepec museum admissions = MXN 180; partial price only |
| Router to fuel calculation | TESTED with mocked OSRM response | Distance emitted, fuel estimated only when inputs provided |
| Missing-price / outdated route state | TESTED in simulated browser | Unknown costs remain, previous distance cleared on route change |
| EN/ES/JA controls | TESTED in simulated browser | Browser UI text; provider-source text stays in original language |
| Full live road service | NOT VERIFIED | Public OSRM demo may fail; external directions fallback |
| Providers/bookings/payments | NOT PROVIDED | No contracts, availability APIs or transaction/billing system |
| Actual tourism popularity | NOT AVAILABLE STATEWIDE | Can't claim lesser-visited destinations, crowding reductions or demand redistribution |
| Academic rubric final certification | NOT COMPLETED | Citation audit, real campaign launch evidence/creatives, final report consistency remain |

## Release stop conditions

The site is a **travel discovery and planning prototype**. It must not claim reliable reservations, complete prices, statistically observed traveler preferences, proven reduced crowding, or business revenue.

Before public submission, complete one manual browser test with a municipality not in the old 55-place source; verify route preview or its external fallback, locale, one published price and an unpriced stop; confirm the homepage excludes obsolete public segmentation. For the report, distinguish the campaign-placement MILP from this heuristic recommendation; keep negative ML and association tests and cite the actual methods and data.
