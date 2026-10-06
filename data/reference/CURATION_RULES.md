# Reference and curation rules

Version: 2026-10-06-v2

This directory contains **version-controlled project reference inputs**. Reference data are neither measured demand nor model outputs. They hold explicit code lists, reviewed mappings, and interpretive categories needed to transform frozen raw sources reproducibly.

## Raw vs reference vs generated

- `data/raw/`: exact frozen source snapshots. Never manually edited.
- `data/reference/`: explicit project rules or reviewed selections. Changes are ordinary Git diffs.
- `data/interim/`: generated outputs from raw + reference.
- `data/processed/`: canonical analysis-ready tables.

A rule that changes the analytical meaning of a variable must not exist only as a Python constant.

## `denue_activity_groups.csv`

Defines the SCIAN rules used to build municipal service/infrastructure variables.

Each row contains:

- `metric`: generated project variable;
- `match_type`: `exact` or `prefix`;
- `code`: SCIAN code or prefix;
- `description`: human-readable activity meaning.

`prepare_infrastructure.py` reads this file directly. This makes the tourism proxies inspectable without reading Python source.

## PIB workbook fields

The municipal PIB parser uses the official municipality key and validates the workbook headers before reading 2022 values. It expects the `PIB_Municipal` sheet to contain:

- `Clave de municipio`;
- `PIB Municipal 2022 (I)`;
- `PIB Turístico Municipal 2022 (J)`;
- `Participación en % del Turismo en el municipio (J/I)`.

The script fails rather than silently reading different columns if the workbook layout changes.

## Frozen Veracruz HTML

The local proof-of-concept snapshots are:

- `data/raw/veracruz_productos_2026-10-06.html`
- `data/raw/veracruz_regiones_2026-10-06.html`
- `data/raw/veracruz_pueblos_magicos_2026-10-06.html`

`prepare_veracruz_web_reference.py` parses local snapshots only; normal pipeline runs do not require the network.

The Pueblos Mágicos gob.mx snapshot returned a **Radware CAPTCHA page** to Codespaces. It is retained unchanged as evidence of what the fetch returned. For the current proof of concept, the parser transparently falls back to the Pueblos Mágicos menu embedded in the frozen official `veracruz_productos_2026-10-06.html` page. The generated table records that fallback explicitly.

The products snapshot currently yields the full set of product cards mechanically. The seven-region navigation menu is also parsed mechanically and retains the municipality identifiers exposed in the source URL.

## `tourism_products.csv`

This is the **75-product project-v1 analytical selection** used by the existing coursework, not a claim that the official website contains only 75 products.

The full frozen page is parsed first. `prepare_tourism_products.py` then verifies every selected row against a source card with the same municipality set and a closely matching title, and records the matched source-card index/title in the generated interim table.

This preserves the existing project scope while making its source grounding testable. A later decision may explicitly replace the 75-product selection with the full parsed offer; that would be a data-scope change, not a hidden parser change.

## `destination_reference.csv`

One row per destination in the 55-destination project universe.

### Direct/source-backed and reviewed fields

- `destination`, `municipio`, `clave_municipio`: project destination/municipality identity.
- `region_turistica_preliminar`: reviewed tourism-region mapping; parser-derived navigation mappings are used as validation where the frozen page exposes the municipality directly. `Por verificar` remains where unresolved.
- `pueblo_magico`: checked against the mechanically extracted Pueblos Mágicos list.
- `oferta_turistica_oficial_web`, `productos_en_extracto_local_n`, `productos_ejemplo`: project-v1 offer-selection fields, grounded in `tourism_products.csv`.
- `inah_inventory_sites`: reviewed mapping to INAH archaeological inventory names.
- `inah_series_sites`: exact `recinto` strings used to map the INAH visitor series.
- `datatur_center`: explicit mapping from destination to an exact DataTur center; a center may cover more than one municipality.
- `datatur_scope_note`: records that interpretation.

### Interpretive theme fields

These are project-coded categories, not official government classification fields:

- `tourism_tags`
- `theme_beach_coast`
- `theme_nature`
- `theme_culture_history`
- `theme_archaeology`
- `theme_adventure`
- `theme_gastronomy_coffee`
- `theme_wellness_spiritual`
- `theme_urban_services`

A theme is coded `1` when reviewed destination evidence supports that theme. These fields describe offer/profile, not demand.

### Prohibited content

`destination_reference.csv` must not contain derived/measured quantities such as annual visitor totals, DataTur arrivals/occupancy, DENUE counts, tourism GDP, cluster labels, predictions, or campaign outcomes. Those are regenerated downstream.

## `source_registry.csv`

Contains the expected raw filename, institution, URL, snapshot date, release/coverage note, project role, and expected SHA-256 checksum.

`build_source_registry.py` recalculates every hash, fails on any mismatch or missing file, writes `data/interim/source_registry_resolved.csv`, and regenerates `docs/DATA_SOURCES.md`.

## Change rule

Changes to reference rows must be reviewable in Git. Measured data must never be manually inserted into reference files merely to reproduce an older output.
