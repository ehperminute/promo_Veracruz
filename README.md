# Veracruz — travel journal and expense-sharing pilot

## Purpose
Travelers can record stops and spending from an actual trip, voluntarily share a link with others, and reopen mapped stops in the existing itinerary planner. A traveler may list a purchased service, food, or item, a business name if desired, the approximate travel month, and the **total paid by the group in MXN**.

This is separate from the approved **provider offers** and from editable budget **scenarios**. Traveler-reported expenses are not live service prices. No shared trip is used as research data automatically.

## What is included
- `travel_journal/site/viajes.html`: self-contained ES/EN/JA travel journal UI
- `travel_journal/site/js/trip-journal-core.js`: pure trip validation, calculation and URL encoding
- `travel_journal/site/js/trip-journal.js`: editor, read-only shared view, local draft persistence
- `travel_journal/site/js/trip-journal-bridge.js`: link from the existing routing panel
- `travel_journal/site/css/trip-journal.css`: responsive styling
- `travel_journal/install.py`: additive and repeatable installation
- `travel_journal/tests/test_core.js`: regression checks
- `academic/`: two revised Word documents using the feature as a limited pilot, **not** claiming a collected user dataset

## Install in Codespaces
Copy this release ZIP into the **root** of `/workspaces/promo_Veracruz`, then run:

```bash
cd /workspaces/promo_Veracruz
unzip -o VERACRUZ_TRAVEL_JOURNAL_MVP_2026-10-25.zip
python travel_journal/install.py .
node travel_journal/tests/test_core.js
python -m http.server 8100 -d site
```

Open port 8100, use the itinerary planner to select stops, then click **Compartir ruta y gastos / Share route and spending**. Or open `/viajes.html` directly to create a travel journal manually.

To deploy after checking, commit **only the installed website source files**, not this ZIP.

## Usage
1. Add stops from the current route (or enter them manually).
2. Enter traveler count and approximate **month/year**, not the exact travel day.
3. Add purchases or services and the total **MXN amount paid by the group**.
4. Review all text for personal information, check the consent acknowledgement and copy the link.
5. Recipients can view the shared trip read-only or create an editable copy. If stops have the map's stable IDs, a button opens that itinerary in the planner.

## Storage and privacy
- A private draft is saved **in your own browser** via `localStorage`.
- Sharing encodes trip content in the **URL fragment** (after `#`); no backend, registration, or public feed.
- Anyone with the shared link can read the included information. The user is warned not to enter personal contact details, identifiable receipts, precise dates or home addresses.
- Content is rendered as text. The sharing UI requires acknowledgement.
- This version does not upload photos/videos or solicit traveler accounts; those would require moderation, consent and storage.

## Boundaries
- Up to 12 stops and 40 expense entries per link.
- Amounts reflect what travelers chose to disclose; omissions are normal, so totals mean **recorded expenditure**, not a complete quote.
- There is no public searchable trip gallery yet and no central collection of price observations. A moderated publication workflow would be a separate later step.
- Works on a static GitHub Pages site without a server. Browser state and copied links are the persistent medium.

## Tests / acceptance
The following have been executed on an extracted repository snapshot:
- Installer run twice without duplicate navigation or scripts.
- JavaScript syntax and Node test suite; Unicode roundtrip, sums, per-person totals, route IDs, invalid amounts, 12-stop cap, and month-only dates.
- Isolated Chromium interactions: adding stops and expenses, consent-gated sharing, receiving read-only links, making an editable copy, English switch, and dynamic itinerary button.
- HTML-like note text displayed without executing any HTML.
- Both revised academic DOCX files rendered and checked; report 37 pages, campaign 8 pages. Existing experimental source data unchanged.

**Live browser deployment on your particular GitHub Pages URL is not verified by these local tests.**
