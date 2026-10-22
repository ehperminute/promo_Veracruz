# Activity explorer — current Veracruz tourism evidence

**Purpose:** Reintroduce useful cards without reviving obsolete destination clusters.

The homepage gains a searchable, 9-category explorer of **78 specific activity types**, drawn exclusively from `site/data/interest_evidence.json` (216 strict municipality–activity evidence links across 61 municipalities). The archived 55-destination/12-cluster dataset is **not used**.

Each card includes an editorial description, a conceptual illustration (not a destination photo), documented municipality count, a list of named municipalities with source links, a direct **Add to itinerary** action, and **Show on map** which drives the existing `#vx-activity` filter. Three cards include documentary Wikimedia Commons photos already referenced by the existing attraction map (El Tajín, Cascada de Texolo, San Juan de Ulúa) with credits and source links. There are **no claims that all 212 municipalities have 78 documented activities**; the 212-municipality map remains separate.

## Install

Unzip the release into the repository root, then:

```bash
python veracruz_activity_explorer/install.py .
python veracruz_activity_explorer/tests/test_release.py
node --check site/js/activity-explorer.js
python -m http.server 8100 -d site
```

Open the forwarded Codespaces port. The cards appear **above the existing map**, including mobile. Try searching `telar`, filtering `Artesanías`, opening the places under `Taller de globos de papel`, and adding Zozocolco to the itinerary. Verify that `Ver en el mapa` activates that activity on the municipality map.

The installer is idempotent and does not edit the SQLite database. If you already installed the BLOB patch, this release does **not** remove its BLOB columns or overwrite their contents; it publishes browser-readable static illustrations separately.

**Still missing:** verified geographic photos for most municipalities, current operator access and published fees. Representational artwork is labeled as such and does not imply a real photographic depiction.

## Regeneration

If the source evidence export changes, **do not** reuse the cards blindly. Regenerate from a checked copy of the current site:

```bash
python veracruz_activity_explorer/build_data.py --site site
python veracruz_activity_explorer/tests/test_release.py
```

The current builder intentionally rejects evidence exports other than the tested 216-link version. A new research release requires reviewing the evidence contract.
