#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone
import shutil,re
ROOT=Path('.').resolve()
HERE=Path(__file__).resolve().parent
site=ROOT/'site'
js=site/'js/route-planner.js'
css=site/'css/route-planner.css'
html=site/'index.html'
for f in (js,css,html):
    if not f.is_file(): raise SystemExit(f'STOP: missing {f}. Nothing changed.')
original=js.read_text(encoding='utf-8')
if "vxr-route-site-pin" not in original or "function dijkstra(begin,end)" not in original:
    raise SystemExit('STOP: unexpected route planner version. No changes made.')
# Don't overwrite another version silently. Exact earlier patch text or already hotfixed.
if "dataset.routeSiteId=site.id" not in original and "function setPicking(kind)" not in original:
    raise SystemExit('STOP: unrecognized marker selection code. No changes made.')
s=html.read_text(encoding='utf-8')
version='20261018-route-click-fix-1'
for typ in ('js','css'):
    pattern=rf'((?:src|href)=[\"\'])(?:{typ}/route-planner\.{typ})(?:\?[^\"\']*)?([\"\'])'
    new,count=re.subn(pattern,lambda m:m.group(1)+typ+'/route-planner.'+typ+'?v='+version+m.group(2),s,count=1)
    if count!=1: raise SystemExit(f'STOP: route-planner.{typ} reference missing. No changes made.')
    s=new
b=ROOT/('.backup-route-click-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
b.mkdir(parents=True,exist_ok=False)
for f in (js,css,html):
    target=b/f.relative_to(ROOT)
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(f,target)
shutil.copy2(HERE/'route-planner.js',js)
shutil.copy2(HERE/'route-planner.css',css)
html.write_text(s,encoding='utf-8')
print('Route click-capture and label density fixed. Backup:',b)
print('Refresh site. No road network rebuild required.')
