# Acceptance checks performed

- Core trip journal Node regression: **PASS** (roundtrip, expenses, date constraints and stop references).
- Community publication Python unit tests: **4 PASS** (route templates, review/publish WebP, duplicate prevention, invalid dates, invalid values/media).
- Repeated community installer: **PASS**, no duplicate script or section.
- JS syntax validation: **PASS** for `trip-gallery.js` and `trip-submission.js`.
- Isolated Chromium gallery test: **PASS**, four editorial routes and one **test-only** approved trip showing an image (test record not included in the release).
- Isolated Chromium submission test: **PASS**, three-stop draft → English form → photo upload/preview → caption → separate research consent → downloadable WebP-based JSON.
- Optional FastAPI receiver TestClient: **PASS**, status 202 for valid and repeated payload (idempotent); 422 for invalid payload.
- Reviewer CLI test: **PASS**, test-only private file → approved gallery record plus metadata-stripped public image.
- Synthetic metadata benchmark: **500,000 generated expenditure rows** processed on local SQLite; results were a technical workload, **not tourist observations**.

## Tests that require your deployment

- Live website HTTP headers, caching and ES/EN/JA transitions on GitHub Pages.
- A real serverless receiving URL and protection against automated abuse (not configured in this package).
- Administrator approval of a real consenting user's story and photograph rights.
- Public availability and persistent storage for automatic submissions. GitHub Pages alone cannot provide this.
