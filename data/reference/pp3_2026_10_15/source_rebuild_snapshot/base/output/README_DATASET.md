# Veracruz clean evidence layer — v1.0 | 2026-10-13

## What is delivered

This is a **source-linked, reproducible data layer** for the Veracruz tourism project, not another clustering result or live campaign. The supplied `catun_municipio.zip` contains INEGI's national AGEEML list. Only the 212 Veracruz municipalities are retained in the administrative frame; population/housing values are included as **reference data with unspecified measurement vintage in the CSV**, not current tourist capacity.

**All source material already supplied** was used where it can be reconciled: original repository digest with 295 official product cards and 212 infrastructure rows; the previous 212-municipality scope screening; the seven uploaded 2025 catalog PDF parts and frozen 66-page text; 128 ordinary + 58 unusual catalog municipality tables; previous 879 long-form S4/S8 evidence assertions (split by evidence type instead of copying 523 product mentions twice); 67 named adventure locations; 55 cultural feature leads; INAH inventory/site locations; targeted new official-source leads; and the 275 extracted provider directory blocks.

### Counts and their proper interpretation

| Measurement | Actual count | Meaning |
|---|---:|---|
| Veracruz municipalities | 212 | Exhaustive **administrative** reference, not list of 212 tourist destinations |
| Candidate municipalities | 98 | Historical 55 + 43 additional **research candidates**, not optimal cluster scope |
| Direct-offer/site evidence tier | 70 | Source screening, *not live-booking confirmation* |
| Contextual evidence tier | 26 | Events / map mention; further research needed |
| Insufficient evidence in screened sources | 116 | Unknown, **not no attractions** |
| Official product cards | 295 | Complete published card titles, not separate visitor activities |
| Card → municipality mentions | 541 | A route may mention many municipalities |
| Catalog municipality–chapter rows | 187 | 128 automatic + 58 prior recovered + **1 extra independently read: Herpetology at Los Reyes** |
| Providers' published directory blocks | 275 | Neither 275 unique operators nor verified provider–activity joins |
| Distinct INAH sites with source URLs | 10 | Physical site municipality; historic published opening status, not today |
| Named place/tradition mentions | 132 | Raw leads; some fields contain several names and are not split |
| Typed experience/cultural/heritage claims | 396 | Excludes duplicate product-card associations |
| Observed municipality–specific-activity tag pairs | 207 | At most an evidenced association; NOT unique tour inventory |
| Municipalities with at least one observed tag | 64 | Published / historical evidence, booking not verified |
| Candidate municipalities without specific tags | 34 | **Research gaps**, explicit in `research_gaps_no_specific_tag_98.csv` |
| Unmatched municipality references | 0 | Zero among the parsed source tables; does not imply verified physical site geography |

### File meanings

**Geography:** `municipalities_212.csv` is the canonical INEGI-keyed frame. `destination_candidates.csv` (98) retains both original and newly suggested places. `destination_activity_coverage_212.csv` retains unknowns. `candidate_experience_profiles.csv` and `READABLE_98_DESTINATIONS.md` provide human-readable coverage.

**Original tourism records:** `tourism_products_295.csv` (original card titles) and `tourism_product_municipality_links.csv` (not physical venue locations). `official_catalog_municipality_sections.csv` (source chapter plus page, municipality, type), `catalog_provider_directory_blocks.csv` (as-published contact blocks) and `inah_physical_site_register.csv` (10 original INAH URLs). Original page text is retained in `inputs/catalog_page_text_66.csv`.

**Typed evidence:** `destination_activity_and_heritage_evidence.csv` (claims, raw wording, source IDs and URL/file, status and location caveat), `named_places_events_and_attraction_leads.csv`, and `additional_official_source_leads.csv`. `activity_taxonomy.csv` maps raw source labels to derived codes **without overwriting the raw labels**. `municipality_observed_activity_links.csv` collapses multiple assertions to one municipality+activity pair while listing all underlying claim IDs.

**QA and reproducibility:** `research_gaps_no_specific_tag_98.csv`, `unresolved_geographies.csv`, `quality_exceptions.csv`, `source_manifest.csv`, `pdf_original_source_checksums.csv`, `validation_summary.json`. Build with `python build_clean_dataset.py` using the included frozen `inputs/` files. It uses only the Python standard library; PDFs not needed for *rebuilding the frozen CSV outputs*, but check their digests to independently verify page provenance.

### Important decisions

- The 55-destination limit is **not** used to discard legitimate source records; 98 is a research selection, and the remaining 114 municipalities stay visible.
- Municipality ≠ individual locality ≠ archaeological site ≠ tour provider's office. A catalog chapter can connect several municipalities and multiple operators without declaring who operates which specific experience.
- **Do not derive activities from tourism product titles**, even if a title sounds descriptive. Keep original titles separately.
- The original adventure/culture source labels remain intact. A canonical activity can use one umbrella code for truly overlapping synonyms (for example mountain hiking is a subtype of hiking) but the original descriptor stays in the source claim. Unspecified compound categories are not decomposed into unproven activities.
- Unknown values are not zeros. No room-night slack, municipal hotel occupancy, current provider availability, conversion rate, ROI, and no exhaustive 212-municipality tourism inventory can be inferred from this package.
- **No new clustering has been selected or run**; this fixes source preparation before modeling.

### What is still incomplete (explicit, not hidden)

1. **34 / 98 candidate municipalities** have no specific activity category qualifying under the current normalization, despite possible product/event/attraction leads. Investigate the list using their source links; don't mark them as non-tourist.
2. The claimed 619 state activities, 423 regional attractions, and community-tourism experiences are higher-level official totals. Individual records are **not entirely present** in the supplied files, so this package is not an exhaustive census of all possible experiences.
3. Operator contact blocks cannot be reliably joined to a given physical place/activity from layout alone. Their presence in the 2025 catalog doesn't prove October 2026 operations.
4. Explicit source status is retained for historical competitions, general plans, and cultural festivals; no claim of a current, regularly bookable activity follows from those leads.
5. The CSV source materials derive from previous local project outputs and audits, and previous researchers' links were not all reopened in this build. To publish claims externally, recheck the selected items for dates, geography, and provider availability.

### Repository placement (recommended; no remote repository was changed)

- `data/raw/inegi/`: original `catun_municipio.zip`
- `data/raw/veracruz/experiences_2025/`: original seven catalog PDF parts
- `data/interim/`: parsed cards, catalog tables, provider text and original claims (all preserved in `inputs/`)
- `data/processed/`: `municipalities_212.csv`, `destination_candidates.csv`, `destination_activity_and_heritage_evidence.csv`, `municipality_observed_activity_links.csv`, named places and coverage
- `docs/`: this README, readable profiles, QA exceptions
- `scripts/data/`: `build_clean_dataset.py`.

**Do not silently overwrite the existing S4 clustering or S7 planner.** Test a new S4 feature view only after reviewing which evidence statuses qualify for a present-day marketing profile and selecting a justifiable geographic universe.
