#!/usr/bin/env python3
"""Idempotent additive upgrade of existing trip-gallery examples, not user stories."""
from pathlib import Path
import re
import shutil
import sys

repo = Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
site = repo / 'site'
source = Path(__file__).resolve().parent / 'site'
page = site / 'viajes.html'
core = site / 'js/trip-journal-core.js'
if not page.exists() or not core.exists() or not (site/'data/community_trips.json').exists():
    raise SystemExit('Requires the installed travel journal and community-gallery release. Nothing changed.')
for rel in ['data/trip_examples.json','js/trip-gallery.js','js/trip-example-budget.js','css/trip-example-budget.css']:
    dest = site / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source / rel, dest)
text = page.read_text(encoding='utf-8')
# Keep existing assets and version existing gallery with a new suffix to invalidate browser cache.
text,n=re.subn(r'<script defer src="js/trip-gallery\.js(?:\?v=[^"]*)?"></script>',
               '<script defer src="js/trip-gallery.js?v=samplephotos2"></script>',text,count=1)
if n!=1:raise SystemExit('Could not locate gallery script in viajes.html. Assets copied; journal markup unchanged.')
if 'js/trip-example-budget.js' not in text:
    text=text.replace('</head>','<link rel="stylesheet" href="css/trip-example-budget.css?v=samplephotos2">\n<script defer src="js/trip-example-budget.js?v=samplephotos2"></script>\n</head>',1)
page.write_text(text,encoding='utf-8')
print('Installed: 4 example trip photos and 4 illustrative expense breakdowns; traveler story data preserved.')
