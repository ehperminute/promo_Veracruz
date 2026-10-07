# Reference and curation rules

Version: 2026-10-06-v3

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
- `data/raw/veracruz_pueblos_magicos_2026-10-06_manual.html`

`prepare_veracruz_web_reference.py` parses local snapshots only; normal pipeline runs do not require the network.

The automated Pueblos Mágicos snapshot returned a **Radware CAPTCHA page** to Codespaces and is retained unchanged as evidence of the failed fetch. The manually browser-saved official page is the preferred parser input. The products-page Pueblos Mágicos menu remains a tested fallback if that manual snapshot is unavailable or invalid.

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

## `origin_market_2025_validated.csv`

Contains only direct 2024-2025 country-of-residence counts, 2025 shares, and source-reported growth from the fixed official DataTur report `RES_2025_12.pdf`. The report states that 2025 values were validated by the source in August 2026.

This reference table deliberately contains **no marketing tier, targeting phase, persona, or campaign decision**. It is a small structured source transcription with the exact report URL retained on every row. `prepare_origin_markets.py` validates ranks, arithmetic, source URL, and official control totals before writing `data/processed/origin_market_opportunity.csv`.

The figures describe foreign air-entry events to Mexico by country of residence. They are not Veracruz visitor counts.

## `source_registry.csv`

Contains the source identifier, institution, URL, snapshot/version date, release/coverage note, project role, verification metadata, and `storage_mode`.

- `local_raw`: immutable files in `data/raw/`; SHA-256 is recalculated and must match.
- `remote_fixed`: an exact fixed official report URL used to ground a small version-controlled reference extract. It is not fetched during normal pipeline runs, so the pipeline remains offline and deterministic.

`build_source_registry.py` verifies all local raw hashes, records fixed remote sources without silently downloading them, writes `data/interim/source_registry_resolved.csv`, and regenerates `docs/DATA_SOURCES.md`.

## Change rule

Changes to reference rows must be reviewable in Git. Measured data must never be manually inserted into reference files merely to reproduce an older output.
