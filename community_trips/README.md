# Veracruz — reusable trip stories and photographic submissions

This is an **additive update to the existing Travel Journal MVP**. It does not replace the municipality database, recommendations, the road router, supplier offers, cost estimator, or academic research.

## What you get

1. **Four clearly marked suggested trips** displayed above the journal, assembled from **current source-backed municipality–activity evidence**. They do not invent travelers, purchases or prices.
2. **Reusable itineraries**: view any template read-only or copy it into the existing journal and record your actual expenses.
3. **Photo and story submission interface** at `/enviar-viaje.html` with ES/EN/JA labels, a maximum of four photos, previews, optional captions, month-level dates, and optional consent for anonymized aggregated research. The image canvas strips EXIF/location metadata and re-encodes to WebP.
4. **Moderated public trip gallery**: reviewed submissions can be published by the administrator to `site/data/community_trips.json`, with photos under `site/media/community-trips/`.
5. **Optional private receiver**: a FastAPI pilot accepts submissions and stores them in a private SQLite queue, while public GitHub Pages stays static. Deploying a real receiver is a **separate step**; without it, users download a submission file and send it privately.
6. An executable **synthetic ingestion/aggregation benchmark** and architecture note for the Big Data course (not real visitor observations).

## Install (from `/workspaces/promo_Veracruz`)

The previously installed `travel_journal` should be in place. Extract this ZIP into the repo root, then:

```bash
python community_trips/install.py .
python -m unittest discover -s community_trips/tests -v
node --check site/js/trip-gallery.js
node --check site/js/trip-submission.js
python -m http.server 8110 -d site
```

Open `/viajes.html` for the examples and `/enviar-viaje.html` to submit a travel story. The second page reads the draft you created and saved in `/viajes.html` (same browser).

**Important:** Adding a story to the journal and downloading the submission file **does not publish it publicly**. The public catalog starts with zero contributed trips. The four examples are editorial suggestions, not customer testimonials.

## Moderation and manual publication

Download the JSON submitted from the form (or export it from the optional private receiver), review all fields/photos and confirm the uploader has rights. The administrator runs:

```bash
python community_trips/tools/publish_reviewed_trip.py /tmp/veracruz_trip_submission.json --site site --dry-run
python community_trips/tools/publish_reviewed_trip.py /tmp/veracruz_trip_submission.json --site site --approve --content-reviewed --rights-reviewed
```

The approval script validates the schema, re-encodes WebP photos without metadata, caps sizes, prevents duplicates, and publishes a source-marked `traveler_reported` record. Commit the generated **approved** public JSON and images—not private pending submissions.

## Optional automatic receiving backend (pilot, not yet deployed)

To accept submissions automatically you must run a separate backend. This package includes a basic FastAPI receiver storing pending submissions in private SQLite. It does **not** publish them automatically. Use it for demonstrations and local integration; do not expose it publicly without CAPTCHA, moderation operations, rate limiting at the edge, monitoring, secure authentication for administrators and documented deletion/retention.

```bash
python -m pip install fastapi uvicorn Pillow
VX_ALLOWED_ORIGIN=https://YOUR-USER.github.io \
VX_PRIVATE_SUBMISSION_DIR=/path/outside/public/site/.private_submissions \
VX_IP_HASH_SALT=replace-with-secret \
uvicorn community_trips.backend.app:app --host 127.0.0.1 --port 9000
```

Configure `site/data/trip_submission_config.json` with the actual public HTTPS endpoint; example:

```json
{"enabled":true,"endpoint":"https://your-secure-backend.example/api/trip-submissions"}
```

The public form will then show **Send submission automatically**. Upload still means *pending moderation*, not immediate publication.

For a local private queue, an admin can extract an item:

```bash
python community_trips/tools/export_pending.py SUBMISSION_ID --database /path/outside/public/site/.private_submissions/pending.sqlite --out /tmp/veracruz_trip_submission.json
```

## Media/privacy design

- Only JPEG/PNG/WebP image inputs. The browser exports metadata-free WebP thumbnails up to 1200px and the reviewer re-encodes them again.
- Photos never enter shared itinerary URLs; large binary objects live as static images only after approval.
- Public data contains a nickname **only if entered**; exact location histories, exact visit dates, contact information and backend IP hashes are not published.
- Consent for reuse of aggregate expenses in academic analytics is optional and separate from story-publication approval.
- Published self-reported expenses are **not supplier prices** and must not feed the commercial estimator as if verified. A sensible aggregation would require enough voluntary observations and bias/privacy checks first.

## What the package does not pretend to provide

There is no account login, social feed, photo/video hosting platform, booked tours, confirmed demand, observed price distribution, or deployed large-scale data architecture. The Big Data contribution is the **data design and demonstrable ingestion/validation pipeline**, with a synthetic performance experiment. It does not claim a cluster, petabyte throughput or actual traveler datasets.
