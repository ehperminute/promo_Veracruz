# Activity collections with representative documentary photographs

**Purpose:** replace the old 78 isolated activity cards with **eight sections, each containing at least two activities**. Retains **all 78 types, all 216 accepted municipality/activity relationships**, the specific activity descriptions, municipality add-to-route actions, and source links. No statistical clusters are reintroduced.

The original category `scenic_transport` has only one activity; it is presented under **Aventura terrestre y recorridos** so that no group contains a single orphan card.

A representative **Wikimedia Commons photograph** is linked for each section. Each picture shows a documented example of its theme, **not** necessarily all activities nor all municipalities underneath it. Each card shows a source/credit link. The original 78 generic SVG files are not used by this section; keep them until the cleanup audit is reviewed.

## Install in Codespaces

From repository root, extract this release ZIP and run:

```sh
python grouped_activity_cleanup/install.py .
node --check site/js/activity-groups.js
python -m http.server 8110 -d site
```

Open port 8110 and test search for `globos`, expand the activity row, add a municipality, and use **Ver en mapa**. Repeat in ES, EN, JA. The remote images require network access; a neutral non-photographic background appears if a remote file fails.

For provenance, `site/data/activity_sections.json` records the Commons file page, photographer/author, stated license, and what the photo actually shows. Photos are not in SQLite BLOBs: GitHub Pages uses browser-compatible public URLs, while the canonical data and evidence remain in SQLite.

## Limits and editorial checks

- The nine older “activity family” labels are used solely for navigation (eight visible sections after grouping), **not** the obsolete cluster model.
- Some photographs document examples of Veracruz crafts **photographed elsewhere**; this is disclosed in the photo caption.
- Do not claim these photos represent individual venues, currently available tours, or current commercial offers.
- Before public release, inspect all eight images and their credits in the live browser. This installer does not independently test Commons' live availability.
