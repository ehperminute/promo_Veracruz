# Veracruz — compatible original-description recovery (October 18, 2026)

This **replaces the failed exact-code matching installer**. The previous script stopped because `site/js/map-explorer.js` did not contain one expected comment. This version **never modifies or replaces `map-explorer.js`**. Instead, it adds a small separate guide extension to the existing homepage.

## Use in your Codespaces repository

1. Upload `VERACRUZ_RECOVER_ALL_DESCRIPTIONS_COMPAT_FIX_2026-10-18.zip` to the root of `promo_Veracruz`.
2. In the Codespaces terminal, from that root:

```bash
unzip -o VERACRUZ_RECOVER_ALL_DESCRIPTIONS_COMPAT_FIX_2026-10-18.zip
python -m pip install -r veracruz_all_descriptions_patch/requirements_descriptions.txt
python veracruz_all_descriptions_patch/restore_descriptions_and_guides.py .
```

This automatically fetches the tourism-products webpage if the exact historical snapshot is unavailable. If you have `data/raw/veracruz_productos_2026-10-06.html`, use:

```bash
python veracruz_all_descriptions_patch/restore_descriptions_and_guides.py . --html data/raw/veracruz_productos_2026-10-06.html
```

After `SUCCESS`, reload the site (a browser hard refresh may be necessary), choose a municipality, and select a tourism activity. For activities linked to original website products, a **Original tourism listings / Fichas originales** section will appear with actual Spanish source excerpts and links.

## What this changes

- Saves the **full recovered original Spanish text of 295 website product listings** in a **separate local copy** of the researched master: `data/recovered_source_descriptions/veracruz_pp3_master_with_originals.sqlite`.
- Publishes short excerpts and source links in `site/data/map_guide_notes.json` for activity guides linked to these products.
- Adds `site/js/veracruz-guide-originals-addon.js`, `site/css/veracruz-guide-originals.css` and their two references in `site/index.html`.
- Backs up each existing website file before changing it; will not overwrite your source database or `site/js/map-explorer.js`.
- Leaves MapLibre markers, routes, map style, existing sidebar and website translation code untouched.

**Important distinctions:** This restoration has **295 original website products**, which are not the same as the **216 municipality–activity map entries**. We verified the crosswalk in an offline simulation: 157 map entries have a directly linked product; 59 depend on PDF-catalog or other evidence. The interface displays original Spanish excerpts where available, not invented English/Japanese translations. A single product can cover multiple municipalities. For all 295 entries, restoration succeeds only if the actual HTML contents match the complete inventory, otherwise it fails and leaves site files unchanged.

## Verification and limits

The patch was tested using a simulated 295-entry HTML page, a mock site with a **different version** of `map-explorer.js`, and browser rendering in Chromium using mocked static data. **Those are not live source descriptions.** We cannot confirm the real 295-text recovery until Codespaces runs the scraper against the real website or the historical snapshot. The installer reports an explicit failure if it cannot verify the source material. We haven't run it against your current Codespaces files, so visual behavior there still requires checking.

Re-running after a successful restoration uses the stored complete recovered database without fetching the site again. Original snapshots and audit files are saved under `data/recovered_source_descriptions/restoration_audit/`.
