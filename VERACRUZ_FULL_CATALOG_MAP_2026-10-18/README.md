# Veracruz full catalog map — October 18, 2026

This is one bulk integration, **not** a promise that every catalog record has exact coordinates. It uses the latest recovered research master and the existing (editable) attraction CSV.

## Install in your existing Codespaces repository

Upload this ZIP to the repository root and run:

```bash
unzip -o VERACRUZ_FULL_CATALOG_MAP_2026-10-18.zip
python VERACRUZ_FULL_CATALOG_MAP_2026-10-18/install_full_catalog.py .
```

Refresh the Codespaces preview. A running `python -m http.server` normally needs no restart unless Codespaces has suspended the process.

## What is visible

- **35 individual mapped geographic features**: preserves all 24 previously mapped attractions and adds 11 published site-level geographic points. These are **not certified visitor entrances**.
- **Full searchable research catalog**: 49 original named-place rows, 151 additional place/event lead records (often municipality-level), and 295 published tourism-product cards. The original Spanish titles and links are retained.
- Search for any named place, tradition, activity or marketed tour in the **existing search box**; select a result to open the sidebar. If there is only a municipality reference, the map can center on that approximate municipality position, and the guide explicitly says it is **not an attraction pin**. Where no reliable locality is known, the record is searchable but *not* pinned.
- The right-panel **Complete research catalog** button opens the whole inventory, with category filtering. Empty/unconfirmed original website descriptions are not replaced with invented text.
- 11 new source-linked features: Xalapa anthropology museum, Castillo de Teayo archaeological pyramid, Cuyuxquihui archaeological site, Las Higueras archaeological zone, Museo El Lencero, Fortaleza de San Carlos de Perote, Macuiltépetl Ecological Park, Playa de Villa Rica, Playa de La Mancha, Sótano de Popocatl (area only), and Cascada El Tucán.

### Editing later

`site/data/attractions.csv` is still the canonical CSV for individually mapped sites. Add or edit entries there; run `python tools/build_attractions.py .` to regenerate `site/data/attractions.geojson`.

`site/data/tourism_catalog.csv` is the editable **source lead and tourism product index**, including precision status. After changes run `python tools/build_catalog_index.py .` to rebuild its JSON. These records don't become attraction map pins without verified coordinates.

### Provenance / limitations

- Counts represent **source records**, not unique places. The 49 place names can overlap with the 151 leads and 295 tourism products; some leads combine more than one place or festival.
- The original 49-place table doesn't have exact coordinates, so the patch does not invent them. The 151 leads have approximate municipality reference points only, where indicated. The 295 products can span multiple municipalities. Thus **not every source record is geolocated**.
- Map data use approximate municipality centers for broad geographic context, and published individual site coordinates where available. Site coordinates are not automatically routing entrances.
- No old S4 dataset was used; source is the recovered PP3 SQLite file. No user data in GitHub is overwritten except the attraction presentation files (with backups) and the addition of eleven new rows to your existing attraction CSV.
- Source-only entries provide available original titles / reference links; they aren't all finished tourist articles with photographs.
- MapLibre marker rendering and Codespaces/browser caching still need checking on the user's live preview; JS syntax and installation can be tested offline.
