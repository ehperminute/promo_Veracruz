# Veracruz BLOB media patch

This patch adds **image BLOB columns** directly to the canonical SQLite database and fills them with **generated representative images** for:

- all rows in `municipalities`
- all rows in `activities`

It does **not** scrape or embed source photos. Instead, it creates clean placeholder/hero PNG images that are good enough for the planner, cards and activity descriptions right now. Later, you can replace them with extracted catalog images or licensed photographs.

## What gets added

### `municipalities`
- `hero_image_blob` BLOB
- `hero_image_mime` TEXT
- `hero_image_kind` TEXT
- `hero_image_note` TEXT
- `hero_image_updated_at` TEXT

### `activities`
- `illustration_blob` BLOB
- `illustration_mime` TEXT
- `illustration_kind` TEXT
- `illustration_note` TEXT
- `illustration_updated_at` TEXT

## Run it

Use your canonical DB, for example:

```bash
python veracruz_blob_media_patch/add_blob_media.py \
  data/recovered_source_descriptions/veracruz_pp3_master_with_originals.sqlite
```

Verify coverage:

```bash
python veracruz_blob_media_patch/verify_blob_media.py \
  data/recovered_source_descriptions/veracruz_pp3_master_with_originals.sqlite
```

Optional: export the blobs back into files so the website can reference them more easily:

```bash
python veracruz_blob_media_patch/export_blob_media.py \
  data/recovered_source_descriptions/veracruz_pp3_master_with_originals.sqlite \
  site/assets/db_images
```

## Recommendation

For the **database**, BLOB columns are fine if you really want a self-contained media store.

For the **website**, I still recommend exporting the BLOBs to static PNG files and pointing the UI at those files, because browsers do not naturally query SQLite BLOBs in a static GitHub Pages setup.

## Important limitation

These images are **representational generated placeholders**, not verified photographs of the municipality or activity.
They solve the current "empty / imageless" UI problem, but they should be described honestly in the report.
