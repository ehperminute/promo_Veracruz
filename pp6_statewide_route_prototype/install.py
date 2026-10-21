#!/usr/bin/env python3
"""Install only the statewide pilot router beside existing regional router; no data edits."""
import argparse, shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('repo',nargs='?',default='.');a=p.parse_args()
repo=Path(a.repo).resolve();src=Path(__file__).resolve().parent
page=repo/'site/index.html'
if not page.is_file():raise SystemExit('STOP: site/index.html not found. Pass repo root.')
body=page.read_text(encoding='utf-8')
marker='js/statewide-route.js'
if marker in body:
 print('Already installed. No changes made.');raise SystemExit(0)
needle='<script defer src="js/route-planner.js?v=20261018-guide-route-v1"></script>'
if body.count(needle)!=1:raise SystemExit('STOP: page route-planner script changed; no changes made. Inspect site/index.html.')
shutil.copy2(page,page.with_name('index.html.before-statewide-route'))
body=body.replace(needle,needle+'\n<script defer src="js/statewide-route.js?v=1"></script>')
body=body.replace('</head>','<link rel="stylesheet" href="css/statewide-route.css?v=1">\n</head>',1)
for sub,filename in [('js','statewide-route.js'),('css','statewide-route.css')]:
 target=repo/'site'/sub/filename;target.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(src/'assets'/filename,target)
page.write_text(body,encoding='utf-8')
print('INSTALLED: statewide routing preview; original regional planner and datasets untouched.')
print('TEST: serve site over HTTP and choose two attractions in the Statewide routes panel.')
print('NOTE: public OSRM is a noncommercial demo without availability guarantees; not a production backend.')
