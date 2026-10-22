# Veracruz · interest-based route discovery + Big Data benchmark

**One additive release**, designed for the current V2 city/attraction routing site. It does not replace the research database, the MapLibre map or the routing engine.

## Install in Codespaces

Place this ZIP in the repository root. From the repository root:

```bash
unzip -o VERACRUZ_INTEREST_AND_SCALE_RELEASE_2026-10-21.zip
python veracruz_interest_bigdata/install.py .
python scripts/bigdata_benchmark.py
python -m unittest discover -s veracruz_interest_bigdata/tests -p 'test_core.py' -v
python -m http.server 8100 -d site
```

Open forwarded port 8100. Hard-refresh. Expand **Find destinations by interests · Surprise me / Por intereses** within the existing road-trip planner; select themes and optionally specific activities. The app shows matches and source links. Click **Use these stops in my route** to populate the ordinary itinerary and calculate its road route separately. The map shows numbered orange selected-stop pins. The existing external directions fallback is preserved.

The Python installer is idempotent. It only writes:

- `site/js/interest-recommender.js`
- `site/css/interest-recommender.css`
- `site/data/interest_evidence.json` (derived from current read-only SQLite)
- `scripts/interest/export_interest_evidence.py`
- `scripts/bigdata_benchmark.py`
- additive `<link>` and `<script>` tags to `site/index.html`
- a small event signal in `site/js/itinerary-router.js` so the numbered map pins update when stops change

The SQLite source is **never rewritten**. Historical 55-destination data is never read. The export preserves all 216 accepted positive municipality/activity links, 61 municipalities and 78 specific activity types, including records whose original-text support is not yet recorded (shown as such in the structured data). The separate reviewed 14-municipality evidence remains separate, not silently coerced into the strict activity matrix.

## Rules and limitations

- The user **declares** interests. The interface does not infer actual market preferences, demographic segments or tourist behavior.
- Suggestions enumerate combinations of 1–3 municipalities within a *pruned pool of at most 19 candidates*, scoring documented activity matches, source-text support and approximate proximity. **This is bounded search, not a globally exact state-level MILP**. The separate academic six-municipality MILP remains unchanged.
- The search radius and proximity penalty are based on **great-circle distance**, not roads. A provider-based road calculation occurs only afterward in the normal itinerary panel; current routing can still fail if external services do.
- The planning budget is `user-set transport allowance + number of suggested stops × user-set allowance per stop`. It is an assumption for illustrating constraints, **NOT a calculated tour price**, and excludes actual room rates, fuel, admissions, meals and other unknown costs. The planner must not claim a trip fits an actual financial budget.
- `Surprise me` uses random candidate diversification from documented options. It isn't a learned recommendation model, and missing evidence isn't evidence an activity does not exist.
- Municipality reference points are approximate and not guaranteed accessible vehicle entrances. Provider availability, opening hours and bookings are unverified.

## Measured Big Data processing experiment

`scripts/bigdata_benchmark.py` reads the actual 31,147-row `data/raw/Base70centros.csv` in streaming batches of 4,000 rows and creates temporary SQLite tables. It benchmarks original records and clearly labeled **synthetic replicas** at 8×, 16× and 64× (up to **1,993,408 rows**, approximately **116 MB** SQLite on the measured machine). For this temporary ingestion-only workload the script disables SQLite journal and synchronous durability; its ingest speeds must not be treated as production write throughput. Each run compares full scans against indexed aggregation by reporting center/month, verifying that all totals scale exactly and indexes do not alter results. The script writes `outputs/bigdata/data_processing_benchmark.json`.

The included `benchmark_reference.json` is from our current analysis environment: at 64×, 6.40 seconds to ingest, 0.143 seconds for an aggregate scan, 0.078 seconds for its indexed form. These timings are not performance promises for Codespaces. Replicas are a **stress test**, not extra real tourist observations. No Spark/Hadoop cluster, parallel execution, fault tolerance or streaming source is proven. For a stricter Big Data course demonstration, the next honest exercise would be partitioned processing of the actual archived OSM extract under a measured workload and comparison with an appropriate execution engine.

## Research and submission status

The revised technical-report draft documents these two new experiments in their natural sections. The study still needs a final review of the actual campaign implementation, source-to-claim links in the submitted media and the 15-minute colloquium rehearsal. A website or simulation is **not** evidence of measured tour bookings, uplift in tourist flows or destination carrying capacity. A report covering a discipline by name is not automatically proof that every course competence has been demonstrated.

Browser-based UI tests were executed locally with a headless Chromium fixture that mocked map-service responses; they did **not** test a successful live OSRM road route. The browser test file is supplied for reproducibility but requires Playwright and a local Chromium executable; the stdlib `test_core.py` has no such dependency.
