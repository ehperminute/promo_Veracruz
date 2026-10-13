# Veracruz — Catálogo de Experiencias Turísticas 2025: extraction package

Source: seven user-supplied PDF slices spanning **66 PDF spread-pages** (printed pages approximately 0–131). The document cover describes listed providers as having **Registro Nacional de Turismo (RNT) vigente at publication**, not guaranteed current registration or open bookings in October 2026.

## Contents

- `catalog_full_text_pages.csv`: **all text extracted from every one of the 66 pages**, with original slice filename, page number and experience section. This is the comprehensive source-preserving extraction, including prose, access descriptions, contacts, and places that do not fit table parsing.
- `catalog_all_text_blocks.csv`: **all 1,175 text blocks**, with original page and bounding coordinates to reconstruct ambiguous tables. This is the authoritative intermediate representation for further review.
- `catalog_sections.csv`: table of contents of 32 section starts and page spans (some headings merge different experiential categories).
- `catalog_municipality_rows.csv`: **128 automatically parsed municipality–section mentions**. Both the original geographic text and adjacent table-column text are retained. `municipality_raw` should NOT be treated as a cleaned municipality ID without review.
- `catalog_provider_contacts.csv`: **275 provider/contact text blocks**, NOT 275 unique companies. Some are repeated in multiple sections and may be overflow fragments. A provider's appearance within a section is not proof of availability at each listed town.
- `extract_catalog.py`: reproducible source-to-tables extractor (PyMuPDF / `fitz`). Adjust source glob/path for repository use.

## Data quality and limits

All textual content recoverable from the PDFs has been preserved in page and block tables. The municipality table is **not yet an exhaustive, manually reconciled destination–activity–provider database**. Nonstandard layout means that table records on pages **19, 25, 29, 45, 50** and some continued pages require review. Raw text from these pages is present. PDF images, including embedded photographs and pictorial maps, are not semantically inventoried; the original PDFs remain authoritative for visuals.

No inferred visitor demand, bookings, ROI, current opening hours, current operator availability or true journey duration is produced. Some listed towns are not among the project's 55 existing destination candidates. Geographic references for departure cities and provider operators must not be mistaken for activity coordinates.

## Recommended storage

Original seven PDFs: `data/raw/veracruz/experiences_2025/` (unchanged).
Section register and parsing rules: `data/reference/`.
Machine text and raw extracted table rows: `data/interim/catalog_experiences_2025/`.
Script: `scripts/data/extract_catalog_experiences_2025.py`.

**Next verification gate:** review geographic identifiers, parse provider associations and repeated listings using original blocks/spread images, and compare records with the existing 55-destination/activity tables. No S4/S7 changes were made.
