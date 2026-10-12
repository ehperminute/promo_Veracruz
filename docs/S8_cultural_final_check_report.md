# S8 — Final cultural heritage and activity audit (12 October 2026)

## Decision

**Do not use `culture_history=1` from S4 for marketing segmentation.** Keep it untouched for reproducibility of S4 clustering until a deliberate upstream revision is approved. Instead use `S8_cultural_activity_catalog_v2.csv`, whose unit of interpretation is a *named heritage feature or prospective visitor activity*.

## What 'real heritage' means here

Three things must not be conflated:

1. **Heritage established**: an identifiable physical site or living tradition backed by an appropriate source (e.g., INAH or UNESCO).
2. **Visitor-facing experience**: evidence exists for a visit, museum, public historic district, or event; official site listings may supply visitor information. This still does not prove access at a chosen future date.
3. **Marketable activity**: after checking timing, geographic attribution, consent where applicable, access, and availability, a specific promise can be made in campaign creative.

Heritage is more than an official UNESCO designation: named festivals, local traditions, crafts and buildings may be genuine even without international registration. Conversely, **a town having a church or commemorative monument does not establish a distinctive visitor activity**.

## Exact audit tally (55 destinations)

| Evidence class | Destinations | Permitted interpretation |
|---|---:|---|
| Primary INAH source with visitor information | 7 | Named archaeological site / museum exists and INAH publishes how to visit. Check updates before advertising. |
| Primary UNESCO + INAH evidence for Papantla | 1 | Archaeology and living heritage established; no assumption that ceremonies or workshops are bookable. |
| UNESCO historic district in Tlacotalpan | 1 | A documented public historic urban landscape; private buildings and guided tours unverified. |
| Tlapacoyan nearby-access case | 1 | Cuajilote/Vega de la Peña are geographically in Atzalan according to INAH; do not map as local Tlapacoyan attractions. |
| Named tradition, schedule not verified | 24 | Research lead; no claim an event will take place on a specified campaign date. |
| Named cultural feature, visitor access not verified | 20 | Research lead; no claim of opening, museum visit, tour or experience. |
| Named site from prior project data, no current visitor check | 1 | Existence lead; do not claim visitor access. |

These are **evidence classes, not a percentage of culturally rich places**, and the 55-row source is a staged evidence audit, not an exhaustive national heritage inventory.

## Strong primary-source examples

- **Papantla:** INAH El Tajín visit listing: https://lugares.inah.gob.mx/es/node/5407 ; UNESCO Voladores: https://ich.unesco.org/es/RL/la-ceremonia-ritual-de-los-voladores-00175 ; UNESCO Center for Indigenous Arts: https://ich.unesco.org/es/01377?id=13 . Distinguish cultural safeguarding and performance permissions from tourism sales.
- **Tlacotalpan:** UNESCO World Heritage, historic monuments zone: https://whc.unesco.org/en/list/862/ . Appropriate for walking/architecture interest, not an assumed guided tour.
- **Castillo de Teayo:** INAH archaeological site and museum: https://lugares.inah.gob.mx/es/node/4378 ; https://lugares.inah.gob.mx/es/node/5301 .
- **Actopan:** Quiahuiztlán, explicitly in Actopan: https://lugares.inah.gob.mx/es/node/5368 .
- **Santiago Tuxtla:** Tres Zapotes site and museum: https://lugares.inah.gob.mx/es/node/4480 ; https://lugares.inah.gob.mx/es/node/4321 .
- **Texistepec:** San Lorenzo Tenochtitlán: https://lugares.inah.gob.mx/es/node/5383 .
- **Úrsulo Galván:** Cempoala: https://lugares.inah.gob.mx/es/node/4379 .
- **Vega de Alatorre:** Las Higueras archaeological site and museum: https://lugares.inah.gob.mx/es/node/5714 ; https://lugares.inah.gob.mx/es/node/4320 .
- **Atzalan:** Cuajilote and Vega de la Peña, geographically in Atzalan but listed using Tlapacoyan as access/municipal reference: https://lugares.inah.gob.mx/es/node/4391 ; https://lugares.inah.gob.mx/es/node/4483 .

## How this should feed marketing

Use **specific experience labels**, not a single culture binary flag. Suggested matching attributes include archaeology, museums, vernacular architecture, festivals, living traditions, traditional craftmaking, and historical sites. An audience interested in archaeology can be matched to verified archaeological sites; an audience interested in festivals can match only to specific festivals with their published dates verified separately. A cultural feature never automatically implies a purchasable tour.

**Safe immediate S8 use:** introduce the primary-source heritage options to audiences interested in archaeology, architecture and living heritage, using truthful destination descriptions and links to official sites. **Not yet safe:** naming an itinerary, promising opening or reservations, or running a date-specific event advertisement for unverified festivals.

## Known gaps after this final check

- Individual primary-source checks are still missing for many locally named festivities, small museums, craft workshops and monuments. The prior audit often points to a state destination directory, which is not evidence of current programming.
- Dates, visitor hours and public access can change after source publication. Confirm immediately before a real promotion.
- UNESCO heritage recognition is **not** visitor capacity, consent to commercialize rituals, or permission to publish images.
- The audit includes one useful geographic correction (Atzalan/Tlapacoyan). Municipal attribution should be validated for other shared areas before campaign mapping.
- The previous summary claiming “all 55 have cultural evidence” is **not** equivalent to “all 55 have promotion-ready cultural activities.” Only nine are independently grounded in the stronger visitor-facing primary-source checks in this round.

## Reproducible S8 data contract

Input: previous `S8_culture_55_final_evidence_review.csv` (55 row exploratory findings) plus named INAH/UNESCO URLs above.
Output: `S8_cultural_activity_catalog_v2.csv` (55 rows; `destination`, `cultural_feature`, `activity_type`, `evidence_level`, `source_urls`, `claim_for_marketing`, etc.).

The export does **not** alter S4's features or S7 optimization. This is an **S8-specific evidence layer**. The newly confirmed sites can be used in an interest-to-activity match; the rest are conservatively marked as leads rather than converted into absent culture or verified offers.
