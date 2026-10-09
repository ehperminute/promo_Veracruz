# S4 experience-group names: evidence and editorial decisions

## Status, scope, and interpretation

The project currently clusters 55 selected Veracruz destinations into **12 similarity groups** using mixed tourism-character variables, Gower distance, and PAM (k-medoids). This file explains the **proposed public names** in `data/reference/cluster_display_labels.csv`. These are **editorial labels**, not classifications published by Veracruz's tourism authority, inferred customer segments, verified tour routes, ecological-capacity assessments, or statements about a destination's popularity.

The clusters cross official administrative tourism regions. Consequently, official names such as *Altas Montañas*, *Totonacapan*, or *Los Tuxtlas* cannot simply be applied as cluster labels. The name must fit the **shared variables among the actual cluster members**. The percentages below come from `outputs/mining/clustering/cluster_profiles.csv` in this repository snapshot, not from surveys of visitors.

| Internal ID | Proposed Spanish display name | Group and example members | Specific justification from the current S4 output | Qualification |
|---|---|---|---|---|
| 1 | **Paisajes y Sabores** | 8; Acajete, Xalapa, Pánuco, Tempoal | All 8 are coded for nature, culture/history and gastronomy/coffee; none for archaeology or adventure. | Members span several regions; no geographic route is implied. |
| 2 | **Aventuras del Pasado** | 3; Actopan, Carrillo Puerto, Úrsulo Galván | All 3 are coded for archaeology, culture/history and gastronomy; 2 of 3 additionally have adventure. | Adventure is not a trait of every member. |
| 3 | **Tesoros Arqueológicos** | 5; Atzalan, Castillo de Teayo, Misantla, Papantla, Vega de Alatorre | All 5 have archaeology, nature, culture/history and gastronomy; 4 of 5 are in the Totonacapan tourism region. | The label describes attractions, not their visitor counts. |
| 4 | **Ciudades y Costa Viva** | 5; Alvarado, Boca del Río, Poza Rica de Hidalgo, Tuxpan, Veracruz | All 5 have culture/history and gastronomy; 4 of 5 are coded coastal and 4 of 5 have urban services. | Poza Rica is not treated as a beach destination. |
| 5 | **Aventuras entre Paisajes** | 12; Calcahualco, Catemaco, Jalcomulco, Perote, Zongolica | All 12 have nature, adventure and culture/history; membership crosses mountain, inland and Los Tuxtlas areas. | Not a connected itinerary; some theme codings are broad. |
| 6 | **Playas y Naturaleza Viva** | 4; Cazones de Herrera, Nautla, Tamiahua, Tecolutla | All 4 are coded for beach/coast, nature, culture/history and gastronomy. | No claim of low occupancy, safe swimming or visitor capacity. |
| 7 | **Naturaleza con Raíces** | 4; Chinameca, Jáltipan, Las Choapas, Soteapan | All 4 have nature and culture/history; none are coded for beaches, adventure or gastronomy/coffee in the final model feature set. All belong to the Olmeca tourism region. | "Raíces" is evocative editorial language, not proof of a particular shared ancient civilization or tourism route. |
| 8 | **Pueblos Mágicos con Sabor** | 3; Coatepec, Naolinco, Zozocolco de Hidalgo | All 3 are designated Pueblos Mágicos and coded for nature, culture/history and gastronomy. | The three towns do not form an automatically validated itinerary. |
| 9 | **Ciudades del Sur** | 2; Coatzacoalcos, Minatitlán | Both have urban services, nature and culture/history; both are in the Olmeca tourism region. | Doesn't claim that visitors will choose them for identical activities. |
| 10 | **Montañas Mágicas** | 4; Coscomatepec, Córdoba, Orizaba, Xico | All 4 are Pueblos Mágicos and coded for adventure, nature, culture/history and gastronomy; 3 are in *Altas Montañas*. | Xico belongs to another official tourism region; "mountains" is a shared tourism character rather than a formal region label. |
| 11 | **Huellas Ancestrales del Sur** | 3; Jesús Carranza, Santiago Tuxtla, Texistepec | All 3 are coded for archaeology, nature and culture/history; destinations lie in southern Veracruz/Los Tuxtlas. | "Ancestral" denotes archaeological heritage, not an assertion that every local site has identical history. |
| 12 | **Tradiciones que se Saborean** | 2; Puente Nacional, Tlacotalpan | Both are coded for culture/history and gastronomy; neither for nature, beaches or adventure in the final model features. | The two places are not automatically one tour route. |

### How the names reach the page

1. `data/processed/destination_master.csv` remains the S3 integrated source table.
2. `scripts/mining/build_destination_profiles.py` generates `data/interim/destination_profiles_s4.csv`, applying the reviewed S4 tourism-character enrichments.
3. S4 clustering generates `outputs/mining/clustering/cluster_membership.csv` and `cluster_profiles.csv`.
4. `data/reference/cluster_display_labels.csv` stores the reviewed editorial names and descriptions in Spanish, English, and Japanese, keyed by cluster number and expected medoid.
5. `scripts/web/export_destinations.py` joins the **refined S4 profiles**, membership, diagnostics and editorial labels; it writes `site/data/destinations.json`.
6. The site displays localized names in the filter, cards and destination detail dialog, while retaining the numerical group ID for technical reference.

**This patch does not rerun or change the PAM model.** It changes presentation and corrects the web export source for destination-character themes. The export checks that cluster IDs are complete and that each representative medoid still matches the editorial labels. If membership changes after later reclustering, the names also need human review, even if the medoid happens to stay the same.

### Review and validation

```bash
python scripts/web/export_destinations.py
python -m pytest -q tests/test_web_export.py
```

The original repository's GitHub Pages workflow regenerates the JSON before publication. The underlying demand analysis, S3 evidence, and upcoming S5–S8 stages remain separate and unchanged.
