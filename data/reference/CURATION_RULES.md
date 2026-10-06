# Reference curation rules

Version: 2026-10-06-v1

This directory contains **version-controlled project reference inputs**. They are not measured demand, DENUE counts, or model outputs. They encode reviewed mappings and categorical interpretations needed to join official sources into the project universe.

## `destination_reference.csv`

One row per destination in the 55-destination project universe.

### Directly source-backed fields

- `destination`, `municipio`: project destination and municipality key.
- `region_turistica_preliminar`: reviewed mapping against the frozen Veracruz tourism-region page. `Por verificar` is retained where the mapping was not confidently established.
- `pueblo_magico`: direct indicator from the frozen official Pueblos Mágicos page.
- `oferta_turistica_oficial_web`, `productos_en_extracto_local_n`, `productos_ejemplo`: curated extraction from the frozen official Veracruz tourism-products page.
- `inah_inventory_sites`: reviewed mapping from destination to INAH archaeological-site inventory names.
- `inah_series_sites`: **exact `recinto` values** used to map the INAH visitor time series to a destination.
- `datatur_center`: reviewed mapping from a destination to an exact DataTur tourism-center name. A DataTur center can cover more than one municipality; this is context, not municipal demand.
- `datatur_scope_note`: records that interpretation explicitly.

### Interpretive theme fields

The following are project-coded categorical features, not official government classification fields:

- `tourism_tags`
- `theme_beach_coast`
- `theme_nature`
- `theme_culture_history`
- `theme_archaeology`
- `theme_adventure`
- `theme_gastronomy_coffee`
- `theme_wellness_spiritual`
- `theme_urban_services`

A theme is coded `1` when the frozen official tourism offer/region description or the reviewed destination evidence explicitly supports that theme. Otherwise it is `0`. These fields describe offer/profile, not demand.

### Provenance fields

Every row points to the frozen local snapshots or structured raw files used for review. The frozen HTML snapshots are:

- `data/raw/veracruz_productos_2026-10-06.html`
- `data/raw/veracruz_regiones_2026-10-06.html`
- `data/raw/veracruz_pueblos_magicos_2026-10-06.html`

The INAH and DataTur raw files are also referenced directly.

### Prohibited content

`destination_reference.csv` must **not** contain measured/derived quantities such as:

- annual visitor totals;
- DataTur arrivals/occupancy;
- DENUE establishment counts;
- tourism GDP;
- cluster labels;
- model predictions;
- marketing outcomes.

Those are regenerated downstream.

## `tourism_products.csv`

One row per reviewed official tourism product, with the municipalities associated with that product. This is a curated representation of the **official offer** and can support offer-association mining later. It does not represent tourist co-visitation.

## Change rule

Changes to reference rows should be reviewable as ordinary Git diffs. If a theme, mapping, or destination universe changes, the reason should be documented in the commit/decision log. Measured data must never be manually inserted here to make a downstream result match an older artifact.
