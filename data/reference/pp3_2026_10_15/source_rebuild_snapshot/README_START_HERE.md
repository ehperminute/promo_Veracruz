# Veracruz — source-complete reassembly v2 (14 Oct 2026)

## Answer to the catalog question

**Yes: text from all seven original Catálogo de Experiencias Turísticas 2025 PDF slices was extracted.** The 66 full text pages and 1,175 positioned PDF text blocks were preserved. The earlier assistant was incorrect to describe the resulting municipality–activity registry as complete. Its *follow-on data modelling*, not text extraction, left named attractions, mixed composite categories, and uncertain source statuses underused.

This build **actually reassembles** the original preserved sources into an inspectable, typed source layer, checks the 187 municipality–catalog-section associations against the source PDFs, and additionally recovers named-place mentions from the catalog narrative. It does **not** pretend to be an exhaustive attraction census or invent bookable activities.

## Start with these five datasets

- `deliverables/UNIFIED_SOURCE_EVIDENCE_LEDGER.csv`: **1,087** searchable municipality-linked records, clearly typed as activities/source claims, product mentions, named places/events, or other official leads. **Not 1,087 activities.** Original source wording, provenance, and limitations retained.
- `deliverables/catalog_municipality_experience_associations.csv`: **187** original municipality × official 2025 catalog chapter records, with page and PDF part. A chapter may be broad or composite; it does not assert all specific subactivities at each place.
- `deliverables/catalog_full_text_pages_66.csv`: **the complete extracted source text for every one of 66 PDF spread pages**. Includes narratives, connectivity, captions, and directories; nothing omitted merely because it did not parse into a table.
- `deliverables/catalog_named_places_verbatim_matches.csv`: **70 occurrences of 36 distinct controlled named-place strings** found literally in the PDF text, with extracted source context and page. These are *literal mentions*, not 36 geolocated/verified tourist venues. The controlled keyword list is explicitly in the builder; it is not an exhaustive automated named-entity extraction.
- `deliverables/ALL_212_municipality_evidence_profiles.csv`: all official municipalities, old 55/research 98 flags, known chapter names, specific tags, leads, and products. A municipality with no current tag is explicitly **unknown, not no activity**.

Also useful: `evidence_based_municipality_activity_pairs.csv` (207 unique evidence-backed tag associations), `named_place_event_heritage_leads.csv` (132 older named leads), `official_tourism_products_295.csv`, `tourism_card_municipality_mentions.csv` (541), `catalog_provider_blocks.csv` (275 source directory text blocks, NOT verified unique operators), `catalog_source_text_blocks_1175.csv`, `PDF_TABLE_GEOGRAPHY_VERIFICATION.csv`, `VALIDATION.json`, and `TABLE_MANIFEST.csv`.

## What was actually verified

- 7 original uploaded catalog PDFs SHA-256 fingerprints match the previous source-inventory digests.
- Their **66 pages and 1,175 text blocks** are preserved.
- The **187** catalog municipality–chapter associations have correct municipality IDs and match their original chapter/PDF page.
- Page layout checking recovered **186** municipality names directly in the municipality-column text coordinates; one source entry uses shortened **Las Vigas** for official *Las Vigas de Ramírez*. This alias is recorded, not silently changed.
- **295 original products**, **541** product–municipality *mentions*, **396 typed evidence claims**, **132** originally reviewed named-place/event leads, and **212** reference municipalities are all included. The 98 research-candidate flag is retained for comparison and is **not a justified optimal count**.
- Reproducible CSV build uses standard-library Python; PDF coordinate verification additionally uses `fitz` (PyMuPDF). See `build_v2.py` and `verify_pdf_layout.py`.

## What remains unresolved (explicitly)

1. **34 of the 98 previously screened candidate municipalities** do not yet have an accepted detailed-activity tag under the *old conservative rules*. Some have events, place leads or published product mentions. Their absence from the derived tag list does not establish a lack of activities.
2. The 2025 PDF catalog is **not the entire state's attraction census**. The full narrative and captions still need systematic named-entity normalization and independent source triangulation. The 70 newly mined named-place appearances are candidates/links, not a complete machine-resolved geolocation inventory.
3. Provider blocks cannot safely be joined to every municipality or specific subactivity in a chapter. No 2026 opening hours, RNT validity or capacity is claimed.
4. Broad/composite chapters such as “Rafting, rápel y tirolesa” and “Entorno acuático” **must not** automatically be expanded into three or more independent activity tags per municipality. Detailed originals are retained, and these categories can be represented as a single published composite observation until disaggregated by more specific evidence.
5. INAH physical site municipality, tour-provider office municipality, and marketing itinerary municipality are separate concepts, not interchangeable. The official product cards were **not** relabelled as confirmed activities.
6. **No clustering is run or overwritten here.** This is a data-layer release. Silhouette is not a data-quality acceptance criterion, and the original S4/S7 campaign remains unchanged.

## Files and reproducibility

The package includes `base/` (frozen prior input package from the Oct 13 cleaned build), `catalog_extraction/` (previous full PDF text and positioned extraction), `build_v2.py`, `verify_pdf_layout.py`, and all generated `deliverables/` files.

```
python build_v2.py
python verify_pdf_layout.py --pdf-dir /path/to/the/seven/original/pdf/slices
```

The first command only needs the included frozen data; the second needs the seven separately supplied original PDFs. The package does not duplicate ~200MB of original PDF binaries. A new repository import should be done as **additive data/reference + data/interim + data/processed files after reviewing paths**, not by replacing the original project wholesale.
