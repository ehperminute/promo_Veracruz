#!/usr/bin/env python3
"""One-command, reversible installation: ensure evidence+price modules, then unify UX.
Never touch canonical SQLite or replace the map/router.
"""
from pathlib import Path
import subprocess, sys
HERE=Path(__file__).resolve().parent
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd()
SITE=ROOT/'site'
req=[SITE/'index.html',SITE/'js/itinerary-router.js',SITE/'data/map_points.geojson',SITE/'data/attractions.geojson',ROOT/'data/recovered_source_descriptions/veracruz_pp3_master_with_originals.sqlite']
missing=[str(p.relative_to(ROOT)) for p in req if not p.is_file()]
if missing:raise SystemExit('STOP: current route/map/canonical database prerequisites missing: '+', '.join(missing)+'\nDo NOT overwrite current research with the archived 55-place files.')
router=(SITE/'js/itinerary-router.js').read_text(encoding='utf-8')
if 'window.VeracruzItineraryV2' not in router:raise SystemExit('STOP: current route planner is not installed. Upgrade your route planner first.')
if not (SITE/'js/interest-recommender.js').exists() or not (SITE/'data/interest_evidence.json').exists():
 print('INSTALL: current source-backed interests from bundled dependency.')
 subprocess.run([sys.executable,str(HERE/'deps/veracruz_interest_bigdata/install.py'),str(ROOT)],check=True)
if not (SITE/'js/itinerary-pricing.js').exists() or not (SITE/'data/provider_prices.json').exists():
 print('INSTALL: current price reference module from bundled dependency.')
 subprocess.run([sys.executable,str(HERE/'deps/veracruz_trip_costs/install.py'),str(ROOT)],check=True)
subprocess.run([sys.executable,str(HERE/'install.py'),str(ROOT)],check=True)
subprocess.run([sys.executable,str(HERE/'tests/verify_install.py'),str(ROOT)],check=True)
print('DONE: unified flow installed; no previous interest or price ZIP needed separately.')
