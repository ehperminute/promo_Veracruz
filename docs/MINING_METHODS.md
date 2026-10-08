# S4 data-mining methodology — mixed destination profiles

## Why the earlier clustering was discarded

The earlier K-Means experiments are retained only as historical development artifacts. They mixed several different questions (destination character, infrastructure scale and official region) inside Euclidean feature space and produced contradictory-looking values of `k`. They are **not** used as evidence in the current S4 results.

The revised method follows the mixed-data logic used in tourism clustering research: represent heterogeneous destination characteristics with a suitable mixed-data distance, then cluster around real observations (medoids) rather than artificial Euclidean centroids.

Relevant methodological precedents:

- Sertkan, Neidhardt & Werthner, *What is the “Personality” of a tourism destination?*, Information Technology & Tourism. The study uses **Gower distance + PAM/k-medoids** for mixed binary/continuous destination attributes and evaluates alternative `k` values with silhouette: https://link.springer.com/article/10.1007/s40558-018-0135-6
- D'Urso et al., mixed tourist segmentation in *Social Indicators Research*. The study discusses Gower-type mixed-data dissimilarity and medoid-based clustering because mixed segmentation variables are not naturally represented by arithmetic means: https://link.springer.com/article/10.1007/s11205-020-02537-y

These studies guide the **method**, not the substantive conclusions for Veracruz.

## 1. Profile audit before clustering

S4 first builds `data/interim/destination_profiles_s4.csv` from the current 55-row `destination_master.csv` and the full mechanically parsed official product page.

Two corrections matter:

1. The frozen official Veracruz product page contains **295 product cards**. The old 75-row `tourism_products.csv` is only a coursework selection. S4 therefore counts/analyses all 295 cards while retaining the 75-row table solely for earlier-course reproducibility.
2. Carrillo Puerto was genuinely under-described: its region remained `Por verificar` and only archaeology was coded. Current official Veracruz pages support Altas Montañas, historical/cultural evidence and gastronomy.
3. A targeted review of Xalapa, La Antigua and Poza Rica found two additional coding corrections: La Antigua has explicit beach/coast and nature-tourism evidence, while Poza Rica is described in tourism-specific sources primarily as an urban/petroleum-history and cultural gateway rather than a nature-tourism destination. Xalapa's existing nature/culture/gastronomy/urban profile remained supported.

All reviewed corrections are explicit in `data/reference/destination_profile_enrichment.csv`.

The audit output `outputs/mining/audit/destination_profile_gaps.csv` flags documentation/measurement gaps. A gap is **not** interpreted as low tourism.

## 2. Main destination-character clustering

The main clustering asks:

> **Which destinations have similar tourism character/profile?**

It uses only:

- `pueblo_magico`;
- beach/coast;
- nature;
- culture/history;
- archaeology;
- adventure;
- gastronomy/coffee;
- wellness/spiritual;
- urban services.

### Deliberately excluded

- **Direct demand** (`DataTur` arrivals/occupancy and INAH visitor counts): demand must not define profile similarity.
- **Official tourism region**: including it would partly force the discovered clusters to reproduce an existing administrative/tourism grouping. Region is used afterward to interpret clusters.
- **Product-card count**: the number of official cards is useful offer/visibility evidence but is partly a catalogue/promotion effect, not an intrinsic tourism-character trait. It remains in the audit and cluster descriptions, but not in the clustering distance.
- **DENUE/PIB infrastructure scale**: kept for cluster description and the separate structural-analog analysis below rather than allowed to swamp the tourism-character segmentation.

## 3. Distance: Gower-style mixed dissimilarity

The eight tourism themes are treated as **asymmetric binary variables**. A shared positive theme contributes similarity; a mismatch contributes dissimilarity; a shared zero is ignored. This is important because `0` means “not positively evidenced in the reviewed profile,” and two destinations should not become similar merely because the project lacks evidence for the same theme.

`pueblo_magico` is treated as a symmetric known binary designation.

The resulting distance is bounded from 0 (identical on comparable profile evidence) toward 1 (maximally different).

## 4. Clustering: PAM / k-medoids

`Partitioning Around Medoids (PAM)` is used instead of K-Means. Each cluster is represented by an **actual Veracruz destination (the medoid)** rather than a synthetic arithmetic centroid.

The script evaluates **k=2 through k=20**.

For each `k` it reports:

- average silhouette;
- total PAM dissimilarity;
- smallest/largest/median cluster size;
- number of singleton clusters.

Current result:

| k | silhouette | smallest cluster | singletons |
|---:|---:|---:|---:|
| 10 | 0.560 | 3 | 0 |
| 11 | 0.594 | 2 | 0 |
| **12** | **0.637** | **2** | **0** |
| 13 | 0.655 | 1 | 1 |
| 14 | 0.684 | 1 | 1 |
| 15 | 0.731 | 1 | 1 |
| 17 | 0.732 | 1 | 3 |
| 20 | 0.770 | 1 | 6 |

Silhouette keeps increasing when the algorithm is allowed to isolate increasingly specific profiles. For that reason the largest silhouette is **not** accepted blindly. The current rule selects the highest-silhouette solution with **no singleton clusters**, which is **k=12** after the targeted profile corrections.

This is a working analytical segmentation, not a claim that Veracruz possesses exactly 12 objectively real tourism types. The fact that a few plausible profile corrections changed the recommended solution from 13 to 12 is itself a reason to report the clustering as exploratory/analytical rather than a discovered natural law.

## 5. Cluster similarity and ambiguous assignments

`cluster_medoid_similarity.csv` compares every pair of cluster medoids using the same Gower distance. This makes it visible when two selected clusters remain close rather than pretending every cluster is completely distinct.

`destination_silhouettes.csv` reports each destination's silhouette value. Borderline destinations are intentionally exposed. After the targeted review, Xalapa sits almost exactly on a cluster boundary, while La Antigua and Poza Rica have mildly negative silhouettes. These are deliberately exposed as borderline cases rather than hidden or forced into a stronger interpretation.

`feature_sensitivity.csv` removes each profile feature in turn and recomputes the partition. The largest changes currently come from adventure, archaeology, nature, gastronomy and Pueblo Mágico status; culture/history and wellness/spiritual have little effect on the current partition because they do not differentiate many profiles at this resolution.

## 6. Structural analog similarity is a separate analysis

Finding a destination with similar **tourism character** is not identical to finding a structurally comparable destination.

`undermeasured_anchor_similarity.csv` therefore uses a broader Gower distance containing:

- all 295-card product count;
- lodging;
- food/beverage establishments;
- recreation proxy;
- agencies/tours/events;
- tourist transport;
- tourism GDP and tourism share where available;
- INAH archaeological inventory count;
- Pueblo Mágico and theme evidence.

Missing numerical values are ignored pairwise rather than imputed with a fabricated median.

These are **structural analogs only**. Similarity does not prove the target has the same tourism demand and does not imply geographic route feasibility.

## 7. Product association mining

All **295 official product cards** are treated as offer transactions. Municipality-pair support, confidence and lift therefore mean:

> destinations appearing together in the official tourism offer.

They are **not tourist itineraries**, co-visitation records or observed travel movements.

## 8. What S4 does not do

- Clusters are **not geographic routes**.
- Missing DataTur coverage is not low demand.
- INAH visits are not total municipal tourism.
- DENUE is infrastructure/service structure, not carrying capacity.
- No live campaign behaviour is inferred.
- Historical `_v1` result files are not inputs to current S4 results.
