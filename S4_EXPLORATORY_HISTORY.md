# S4 Exploratory History — Veracruz Tourism Intelligence

Status: archived exploratory work, not active analytical evidence.

## Purpose
Preserve superseded S4 experiments so future chats can recover why approaches were abandoned without treating their outputs as current results.

## 1. Legacy K-Means destination clustering
Earlier clustering used K-Means on mixed numeric/binary/region features and exported k=15 and k=17 memberships. Those values were exploratory choices, not statistically selected optima. The same diagnostics showed k=2 had the highest silhouette under that particular feature representation.

Why superseded:
- binary and mixed variables were awkward for Euclidean K-Means;
- k=15/k=17 produced singleton fragmentation;
- old product-count features came from a 75-product subset instead of the full official catalogue;
- several destination profiles were under-coded or inconsistently coded.

## 2. Revised Veracruz character clustering
Current preferred local approach:
- reviewed destination-character variables;
- Gower distance;
- PAM / k-medoids;
- k searched across a range;
- diagnostics include silhouette, cluster sizes, singleton count, medoid similarity and ambiguous memberships.

Direct demand is excluded from tourism-character clustering.

## 3. National structural clustering experiment
A national benchmark set was built from structured nationwide variables such as lodging, tourism-service establishments, tourism GDP and tourism specialization.

Result:
- the national structural space was dominated by a continuum of tourism/service scale;
- the strongest coarse split was roughly smaller vs larger tourism structures;
- forcing many clusters did not produce a convincing natural typology.

Decision:
- do not use national structural clustering as a substantive result;
- retain structural Gower distances for nearest-neighbour / analogue benchmarking.

## 4. National character clustering experiment
A second national experiment used variables closer to the Veracruz character schema.

Result:
- silhouette improved continuously as k increased;
- there was no stable natural stopping point;
- extra clusters mainly split increasingly specific combinations of binary characteristics.

Decision:
- do not present a national destination typology as if a natural number of clusters had been discovered;
- use the nationally comparable character variables for nearest-neighbour analogue searches instead.

## 5. Current national role
National data are retained as an external benchmarking layer, not as a replacement for the Veracruz typology.

For a Veracruz destination we can report:
1. local Veracruz tourism-character cluster/profile;
2. nearest national character analogues on common comparable variables;
3. nearest national structural/economic analogues as a second perspective.

These analogues support interpretation and comparison. They do not prove equal tourist behaviour, equal demand, causal transferability of strategies, or route feasibility.

## 6. Reporting recommendation
Main report:
- report the final Veracruz clustering;
- use national analogue benchmarking only where it helps interpret priority destinations;
- optionally note that exploratory national clustering did not reveal a sufficiently clear natural typology, so nearest-neighbour benchmarking was preferred.

Appendix/repository:
- keep this file and legacy diagnostics for transparency;
- do not use superseded outputs as active inputs.
