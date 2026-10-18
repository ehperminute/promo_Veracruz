# Veracruz map — geographic labels and visitor-first guides

Adds geographic names to map markers (collision-aware, shown progressively with zoom; always shown on hover/focus/selection). Adds a source-linked, visitor-friendly layout to all 216 experience guides. The 216 short introductions are **editorial scaffolding**, not a claim that all 216 guides have been independently written or translated; source-specific paragraphs appear where the evidence allows. Four commonly shown experiences have custom English/Spanish copy, including Playa Muñecos and Finca San Felipe. Sources remain visible under an expandable section. No opening hours, prices, or attraction coordinates are invented.

Existing `map_guide_notes.json`, restored source material, photo manifest, municipality coordinate GeoJSON and SQLite database are left intact. The new `map_editorial_notes.json` is a separate presentation-only file. The existing original-source addon remains supported.

## Installation

Extract archive in repository root of `promo_Veracruz`, then run:

```bash
python install.py
```

The installer checks SHA-256 hashes of the current JS/CSS to avoid destroying unexpected changes, and backs up modified files. The homepage loads versioned CSS/JS so mobile browsers do not retain old assets. A Ctrl+Shift+R or private tab can help refresh a stale session.

If it refuses due to a mismatch, do not overwrite files manually; the current site code needs to be merged.

## Reality check

Markers represent **municipality reference coordinates** and the labels are **municipality names**, not verified attraction entrance points. The website should not promise that snorkeling or any other activity is possible at the marker coordinate. Complete location-specific guide articles and photos still need source-specific review; this patch focuses on real titles, readable navigation and honest copy.
