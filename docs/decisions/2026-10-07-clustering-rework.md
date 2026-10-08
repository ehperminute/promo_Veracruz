# Clustering rework decision log — 2026-10-07

## Status

Current decision. Earlier K-Means k=15/k=17 outputs are retained only as historical exploratory artifacts and are not active evidence.

## Why the method changed

The destination-character variables are primarily binary/categorical. K-Means with Euclidean centroids was therefore a poor primary representation and different feature matrices produced apparently contradictory values of k. The active S4 method uses Gower-style mixed dissimilarity and PAM/k-medoids, which represents each cluster with a real destination.

## Data corrections made before/after the rework

- S4 uses all 295 mechanically parsed official tourism-product cards for offer coverage/associations; the 75-row table remains a coursework subset only.
- Carrillo Puerto: region and cultural/gastronomic profile repaired from official sources.
- La Antigua: beach/coast and nature evidence added from official tourism sources.
- Poza Rica: nature flag reset to *not positively evidenced* after destination-specific tourism review; general ecosystem description is not enough to assert a nature-tourism profile.
- Xalapa: targeted review confirmed the existing nature/culture/gastronomy/urban profile.

## Current selection rule

Evaluate k=2..20 with PAM/Gower and choose the highest average silhouette among solutions with no singleton clusters. Interpretability and per-destination silhouettes are then reviewed.

After the targeted profile review the current frozen-data working solution is k=12 with average silhouette ≈0.637 and no singleton clusters. This is a working segmentation, not a claim that exactly 12 natural tourism types objectively exist.

## How to report the history

The final report should not narrate every failed patch. It should state briefly that an initial Euclidean K-Means exploration was superseded after a mixed-data/profile audit, and present the final Gower/PAM method. Detailed iteration history belongs in Git and this decision log or an appendix.
