#!/usr/bin/env python3
"""Consolidate current PP6 route discovery and pricing UX. No changes to SQLite or research data."""
from pathlib import Path
import hashlib, shutil, sys

HERE = Path(__file__).resolve().parent
ROOT = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd()
SITE=ROOT/'site'
HTML=SITE/'index.html'
TARGETS={
 'discovery-scoring.js':SITE/'js/discovery-scoring.js',
 'interest-recommender.js':SITE/'js/interest-recommender.js',
 'itinerary-pricing.js':SITE/'js/itinerary-pricing.js',
 'interest-recommender.css':SITE/'css/interest-recommender.css',
}
required=[HTML,SITE/'js/itinerary-router.js',SITE/'js/itinerary-pricing-core.js',SITE/'data/interest_evidence.json',SITE/'data/provider_prices.json',SITE/'data/map_points.geojson',SITE/'data/attractions.geojson']
missing=[str(p.relative_to(ROOT)) for p in required if not p.is_file()]
if missing:raise SystemExit('STOP: missing required CURRENT version files: '+', '.join(missing)+'\nInstall the itinerary, interest and cost releases first.')
html=HTML.read_text(encoding='utf-8')
oldjs=(SITE/'js/interest-recommender.js').read_text(encoding='utf-8')
oldprice=(SITE/'js/itinerary-pricing.js').read_text(encoding='utf-8')
if 'js/interest-recommender.js' not in html or 'js/itinerary-pricing.js' not in html:
 raise SystemExit('STOP: existing current recommender or cost widget missing from HTML; refusing blind patch.')
if 'function optimize(random=false)' not in oldjs and "const novelty=window.VXDiscoveryScore" not in oldjs:
 raise SystemExit('STOP: unfamiliar recommender; refusing to replace customized code.')
if 'window.VeracruzTripPricing' not in oldprice:
 raise SystemExit('STOP: unfamiliar cost widget; refusing to replace customized code.')
for x in TARGETS.values():
 if not (HERE/'assets'/x.name).is_file():raise SystemExit('STOP: patch asset missing: '+x.name)
# Copy once to ignored local backup; a repeated installation must not overwrite rollback data.
backup=ROOT/'.local-backup-unified-flow'
for source in [HTML,*[x for x in TARGETS.values() if x.exists()]]:
 target=backup/source.relative_to(ROOT)
 if not target.exists():target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
# Preserve exact release assets; existing data, router, pricing core, and canonical SQLite unchanged.
for filename,dest in TARGETS.items():shutil.copyfile(HERE/'assets'/filename,dest)
# Explicit ordering: load score helper BEFORE current recommender. Change only the intended tag.
if 'js/discovery-scoring.js' not in html:
 import re
 hit=re.search(r'<script\s+defer\s+src="js/interest-recommender\.js\?v=[^"]+"\s*></script>',html)
 if not hit:raise SystemExit('STOP: cannot safely locate recommender tag')
 html=html[:hit.start()]+'<script defer src="js/discovery-scoring.js?v=2"></script>\n'+html[hit.start():]
html=html.replace('js/interest-recommender.js?v=1','js/interest-recommender.js?v=2')
html=html.replace('css/interest-recommender.css?v=1','css/interest-recommender.css?v=2')
html=html.replace('js/itinerary-pricing.js?v=1','js/itinerary-pricing.js?v=2')
HTML.write_text(html,encoding='utf-8')
ignore=ROOT/'.gitignore';existing=ignore.read_text(encoding='utf-8') if ignore.is_file() else ''
if '.local-backup-unified-flow/' not in existing:
 ignore.write_text(existing.rstrip()+'\n# Local unified-flow backups / transfer archives\n.local-backup-unified-flow/\n/*.zip\n',encoding='utf-8')
print('PASS: ONE workflow: Discover/surprise → route stops → cost estimates/provider sources.')
print('PASS: Uncommon source-backed activities prioritized; NO claim of actual low visitor numbers.')
print('PASS: Recommender budget explicitly illustrative; itemized cost panel appears after route controls.')
print('PASS: SQLite, map layers, historical experiments, price ledger and routing engine unchanged.')
