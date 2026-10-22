#!/usr/bin/env python3
"""Add one itemized trip cost estimator to the current itinerary panel.
Safe: does not modify tourism SQLite, canonical evidence, map point data, or historical results.
"""
from __future__ import annotations
import csv, hashlib, json, shutil, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd()
SITE=ROOT/'site';INDEX=SITE/'index.html';ROUTER=SITE/'js/itinerary-router.js'
LEDGER=HERE/'assets/verified_prices.csv'
if not INDEX.is_file() or not ROUTER.is_file():
    raise SystemExit('STOP: install from the promo_Veracruz root after the current itinerary planner is installed.')
if not (SITE/'data/attractions.geojson').is_file() or not (SITE/'data/map_points.geojson').is_file():
    raise SystemExit('STOP: latest map data not found; refusing to install on an obsolete snapshot.')
html=INDEX.read_text(encoding='utf-8');router=ROUTER.read_text(encoding='utf-8')
if 'window.VeracruzItineraryV2' not in router:
    raise SystemExit('STOP: itinerary API not recognized; do not overwrite your router.')
# Verify before any writing; never silently patch a different routing-engine version.
if 'vxw:route-calculated' not in router and 'currentRoute=geom;drawRoute();' not in router:
    raise SystemExit('STOP: route geometry hook missing. Please provide site/js/itinerary-router.js for review.')
if 'vxw:route-cleared' not in router and "summary.textContent='';}" not in router:
    raise SystemExit('STOP: route clearing hook missing.')
if '</body>' not in html or '</head>' not in html:
    raise SystemExit('STOP: homepage HTML does not have expected tags.')
with LEDGER.open(encoding='utf-8-sig',newline='') as f:
    rows=list(csv.DictReader(f))
required={'municipality_or_area','provider','offering','price_mxn','unit','source_url','can_auto_total','checked_at'}
if not rows or not required.issubset(rows[0]):raise SystemExit('STOP: ledger schema error.')
for r in rows:
    amount=float(r['price_mxn'])
    if not 0<=amount<=1e8:raise SystemExit('STOP: bad ledger amount')
    if not r['source_url'].startswith('https://'):raise SystemExit('STOP: unpublished/invalid price source '+r['offering'])
    r['price_mxn']=amount
pfile=SITE/'data/provider_prices.json'
manifest={'scope':'Published-source prices; not current availability or quotes',
          'dataset_kind':'commercial_reference_only_not_canonical_activity_database',
          'price_count':len(rows),'source_checked_at':'2026-10-21',
          'sha256_ledger':hashlib.sha256(LEDGER.read_bytes()).hexdigest(),'entries':rows}
# Preserve a narrowly scoped local rollback once; do not re-create backups on every reinstall.
backup=ROOT/'.local-backup-trip-costs'
for source,relative in [(INDEX,'site/index.html'),(ROUTER,'site/js/itinerary-router.js')]:
 target=backup/relative
 if not target.exists():target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
if 'vxw:route-cleared' not in router:
    router=router.replace("summary.textContent='';}","summary.textContent='';document.dispatchEvent(new CustomEvent('vxw:route-cleared'));}",1)
if 'vxw:route-calculated' not in router:
    router=router.replace('currentRoute=geom;drawRoute();',"currentRoute=geom;drawRoute();document.dispatchEvent(new CustomEvent('vxw:route-calculated',{detail:{distanceMeters:route.distance,durationSeconds:route.duration}}));",1)
ROUTER.write_text(router,encoding='utf-8')
for name,dest in [
 ('itinerary-pricing-core.js',SITE/'js/itinerary-pricing-core.js'),
 ('itinerary-pricing.js',SITE/'js/itinerary-pricing.js'),
 ('itinerary-pricing.css',SITE/'css/itinerary-pricing.css')]:
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(HERE/'assets'/name,dest)
pfile.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if 'js/itinerary-pricing.js' not in html:
    html=html.replace('</head>','<link rel="stylesheet" href="css/itinerary-pricing.css?v=1">\n</head>',1)
    html=html.replace('</body>',('<script defer src="js/itinerary-pricing-core.js?v=1"></script>\n'
                                '<script defer src="js/itinerary-pricing.js?v=1"></script>\n</body>'),1)
INDEX.write_text(html,encoding='utf-8')
ignore=ROOT/'.gitignore';old=ignore.read_text(encoding='utf-8') if ignore.exists() else ''
if '.local-backup-trip-costs/' not in old:
    ignore.write_text(old.rstrip()+'\n.local-backup-trip-costs/\n',encoding='utf-8')
print(f'PASS: connected {len(rows)} source-linked listings to the existing itinerary.')
print('PASS: provider citations, conditional prices, road distance event, unknown costs and user inputs.')
print('PASS: canonical SQLite and historical research data not modified.')
print('Test: node veracruz_trip_costs/tests/test_core.js')
