# Destination profile gap audit

## Purpose

Before rerunning clustering, the project checked whether apparently unusual destinations were actually unusual or merely poorly documented. The current audit keeps all 55 destinations and separates three different ideas:

1. **offer-catalogue coverage** — whether the destination appears in the frozen 295-card official product catalogue;
2. **profile evidence** — reviewed tourism-character themes;
3. **measurement coverage** — whether DataTur/INAH/GDP variables happen to exist.

None of these is individually equivalent to tourism importance.

## What changed

### Full official product catalogue

`veracruz_productos_2026-10-06.html` mechanically yields **295 product cards**. Earlier work used a manually selected 75-product subset for coursework. That subset remains available, but it is no longer used as if it were the complete tourism offer.

Examples of the difference:

- Soteapan: 0 appearances in the old 75-selection → **7** cards in the full catalogue.
- Tlalnelhuayocan: 0 → **4**.
- Calcahualco: 0 → **1**.
- Chinameca: 0 → **1**.
- Jáltipan: 0 → **1**.

The full card descriptions are also useful qualitative evidence for the final report. For example, Soteapan products explicitly describe Popoluca culture and gastronomy, ecotourism, botanical/silence trails, aquatic activities, temazcal/traditional medicine and rappel.

### Carrillo Puerto

Carrillo Puerto was the clearest genuine profile gap. The old profile had `Por verificar` as its region and only archaeology as a positive theme.

Reviewed official evidence now supports:

- **Altas Montañas** region — official regional page: https://www.veracruz.mx/region.php?id=5
- **culture/history** — the official destination page documents the pre-Hispanic province of Cuauhtochco, historical buildings, traditions and music;
- **archaeology** — already present in the project profile;
- **gastronomy** — the official page has a dedicated local-food section.

Destination source: https://www.veracruz.mx/destino.php?Municipio=31

The correction is stored separately and visibly in `data/reference/destination_profile_enrichment.csv` rather than hidden inside Python.

## Remaining medium-priority gaps

After the Carrillo correction, **no destination is high-priority/unusable for the profile clustering**. Six remain medium-priority for future enrichment:

- Carrillo Puerto — no card in the 295-product catalogue and no municipal tourism-GDP value, but now has enough profile evidence to remain in clustering.
- Calcahualco — one official product card and strong theme evidence, but no municipal tourism-GDP value / INAH inventory in the current tables.
- Chinameca — one official product-card appearance and two current theme categories; no tourism-GDP value.
- Las Choapas — no product-card appearance; official destination material nevertheless documents ecosystems, traditions/music, gastronomy and a natural recreation site.
- Soteapan — seven official product cards but incomplete economic/INAH coverage; this is a **measurement gap**, not an offer gap.
- Tlalnelhuayocan — four official product cards and three themes, but incomplete economic/INAH coverage.

Supporting research notes and URLs are stored in `data/reference/destination_profile_sources.csv`.

## Decision on exclusions

No destination is removed at this stage.

A destination will be excluded from profile clustering only if its tourism character remains too unresolved to make pairwise comparison meaningful. Missing demand, missing GDP, or absence from the product catalogue alone is **not** sufficient reason for exclusion.

If later research still leaves a few destinations inadequately described, reducing the clustering universe to roughly 50 destinations is methodologically acceptable as long as the exclusions and reasons are explicit and the destinations remain in the canonical 55-row master table.


## Targeted review: Xalapa, La Antigua and Poza Rica

A follow-up review was triggered by per-destination silhouettes rather than by a desire to improve the global clustering score. The objective was to check whether unusual assignments reflected real profile ambiguity or coding gaps.

### Xalapa

Current coding remains supported. Official state and municipal tourism material describes Xalapa as simultaneously urban/cultural and nature-oriented, with museums, parks, Macuiltépetl, El Haya, the Jardín Botánico Clavijero and local gastronomy. No profile theme was changed.

### La Antigua

The profile was under-coded. Official tourism material explicitly documents Playa de Chalchihuecan and the Río Huitzilapan with riverside/mangrove vegetation and boat, swimming, fishing, rafting and kayak activities. `theme_beach_coast` and `theme_nature` were therefore changed from 0 to 1.

### Poza Rica de Hidalgo

The earlier `theme_nature=1` was based on general municipal ecosystem context rather than destination-specific nature-tourism evidence. Current SECTUR descriptions present Poza Rica primarily through petroleum history, civic/cultural attractions, events and its role as a gateway to nearby Totonacapan attractions. Because S4 zero means *not positively evidenced* rather than *proven absent*, `theme_nature` was changed to 0.

### Effect on clustering

These corrections slightly reduce the headline silhouette but improve semantic validity. The recommended singleton-free PAM solution changes from k=13 (≈0.694 before the targeted review) to **k=12 (≈0.637)**. This is not treated as a regression to optimize away: accurate profiles take priority over maximizing an internal validation score. Xalapa, La Antigua and Poza Rica remain borderline cases, suggesting that the eight broad tourism themes do not fully capture every urban/historical destination distinction.
