# PP3 consolidated evidence update — 2026-10-15

This package reconstructs the **2026-10-14 frozen source-rebuild tables contained in the uploaded repository text dump** and integrates the final 19 candidate cultural/event records (7 municipalities). It is a data layer only: no site, S4 clustering, S5/S6 or planner outputs are overwritten.

## Files
- `data/reference/pp3_2026_10_15/municipality_profiles_212_updated.csv`: 212 municipal rows, with the earlier activity codes retained and named events appended.
- `data/reference/pp3_2026_10_15/named_place_event_heritage_leads_updated.csv`: older 132 source-linked records plus 19 final records.
- `data/reference/pp3_2026_10_15/final_cultural_patch.csv`: final 19 records as obtained in the prior turn.
- `data/reference/pp3_2026_10_15/source_rebuild_snapshot/`: 48 original 2026-10-14 CSV, MD and JSON text files extracted from the uploaded repository text dump, preserved unchanged.

## Cautions
- Earlier mentioned 183/212 research coverage **cannot be reconstructed from this uploaded dump**; the 2026-10-14 tables are the latest complete source-linked version available here.
- The 19 leads refer to festivities/traditions, not verified current tour products; calendar dates are historical/descriptive, not 2026 availability.
- `observed_specific_activity_count` is NOT increased by festival leads. Missing activity remains unknown rather than false/zero demand.
- This source snapshot may not contain more recent intermittent research performed elsewhere.
- `source_rebuild_snapshot` represents previously **derived** frozen tables, not immutable original government source files. Preserve original government sources already in your repository.
- No cluster membership or validation result was regenerated in this package.

## Usage
Extract at repository root, preserving directories. Inspect `municipality_profiles_212_updated.csv`. These are the **new PP3 source tables**; do not overwrite `data/interim/destination_profiles_s4.csv` or call the old 55-profile results updated. Next S4 work should create a *separate, versioned feature builder*, select a defensible set of direct activity candidates, compare with existing 55-place PAM baseline, and keep events/context separate from active tourism products.
