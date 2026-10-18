#!/usr/bin/env python3
"""Replace only the routing overlay code; leave map, road graph and tourism data intact."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,re,shutil

HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description='Repair visible route drawing on existing Veracruz map')
p.add_argument('root',nargs='?',default='.')
a=p.parse_args()
root=Path(a.root).resolve();js=root/'site/js/route-planner.js';html=root/'site/index.html';graph=root/'site/data/routes/xalapa_network.json'
for f in (js,html,graph):
    if not f.is_file():raise SystemExit('STOP: required existing file missing: '+str(f))
old=js.read_text(encoding='utf-8')
if 'function dijkstra(begin,end)' not in old or 'vx-browser-route' not in old and 'vxr-geographic-overlay' not in old:
    raise SystemExit('STOP: unexpected route planner version; no files changed. Please send site/js/route-planner.js.')
page=html.read_text(encoding='utf-8')
needle=re.compile(r'(?P<prefix>src=["\'])(?P<url>js/route-planner\.js(?:\?[^"\']*)?)(?P<suffix>["\'])')
if len(needle.findall(page))!=1:raise SystemExit('STOP: expected one route-planner.js link; no files changed.')
version='?v=20261018-route-svg-1'
new_page=needle.sub(lambda m:m.group('prefix')+'js/route-planner.js'+version+m.group('suffix'),page,count=1)
backup=root/('.before-visible-route-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
backup.mkdir()
for f in (js,html):
    dst=backup/f.relative_to(root);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dst)
shutil.copy2(HERE/'route-planner.js',js)
if page!=new_page:html.write_text(new_page,encoding='utf-8')
print('Route drawing fix installed. Restart NOT required. Hard-refresh the website.')
print('Road graph/database unchanged; rollback backup:',backup)
