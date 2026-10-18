# Veracruz — Overpass 502/500 recovery (18 October 2026)

This is a **fix for the failed bulk importer**, not a new version of the tourism dataset.

## Cause

The previous script submitted **one expensive query for the entire state**. The two public Overpass endpoints responded with HTTP 502 and HTTP 500; neither indicates an error in your Codespaces or local data. Public servers can reject queries that require too many resources.

## Run from your `promo_Veracruz` repository root

```bash
unzip -o VERACRUZ_OVERPASS_RESUMABLE_FIX_2026-10-18.zip
python VERACRUZ_OVERPASS_RESUMABLE_FIX_2026-10-18/resume_osm_import.py .
```

The importer automatically:

1. Divides the existing geographic coverage into about **17 smaller bounding boxes** (the exact count depends on your current data).
2. Queries them **sequentially**, with modest resource limits and an alternate public endpoint.
3. Saves successful OSM results in `.veracruz_osm_checkpoints/`, so a Codespaces disconnect or provider failure won't erase progress.
4. After some successful responses, passes those results through the existing CSV/GeoJSON merge, preserving the original curated rows. Each run creates an automatic backup of any replaced site files.
5. Prints the real number of imported pins and which areas are still pending. It stops trying after two consecutive failed areas to respect the public services.

If the service becomes available again, running **the same command** resumes the pending geographic areas without repeating successful requests.

## What you should expect

- **If at least one area succeeds**, the website is updated with the successful geographic records. It reports `PARTIAL` when others remain pending. New OSM points become visible as you zoom in or search for them.
- **If all areas fail**, no website files are changed; inspect `.veracruz_osm_checkpoints/run_report.json`. This is not proof that the attractions don't exist.
- It can still take several minutes because responses depend on free, shared public servers.
- No guarantee of a complete state inventory: OSM may omit attractions, contain duplicates or include points from adjoining states. A coarse proximity check reduces cross-border errors but **does not prove** that every point is within Veracruz. Treat imported OSM entries as candidates requiring review; route entrances are not verified.
- Existing 35 curated pins, descriptions, research SQLite database, and 495 searchable catalog records remain intact.

### Freeze and resume project work

Once the importer is done (even if partial), you can commit the website and move back to Dijkstra / Operations Research. The map does not have to be a complete tourist encyclopedia to begin routing research.
