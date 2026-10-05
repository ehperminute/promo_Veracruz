# Data sources

The working destination profile integrates official/public tourism and economic evidence.

## Current small reproducible inputs

### `destination_master_v1.csv`
Destination-level profile with tourism themes, official-offer indicators, INAH/DataTur coverage, DENUE service counts and tourism-GDP context.

### `tourism_products_sample_v1.csv`
75 tourism products and the municipalities associated with each product. It supports association-rule mining of **offer relationships**, not tourist behavior.

## Large external inputs

See `data/external/README.md`.

## Evidence boundaries

- DataTur: hotel-center context only where coverage exists.
- INAH: attraction-level archaeological visitors.
- DENUE: establishments/services, not carrying capacity.
- Product associations: co-occurrence in official products, not co-visitation.
