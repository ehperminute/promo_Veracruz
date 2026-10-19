#!/usr/bin/env python3
"""Non-destructive UI-only route planner upgrade for the existing Veracruz site."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import re
import shutil

HERE=Path(__file__).resolve().parent
VERSION='20261018-route-selection-final-v2'

def main():
    ap=argparse.ArgumentParser(description='Simplify regional map selection and remove fictitious travel-time range')
    ap.add_argument('repo',nargs='?',default='.',help='promo_Veracruz repository root')
    args=ap.parse_args()
    root=Path(args.repo).resolve()
    site=root/'site'
    js=site/'js/route-planner.js'
    css=site/'css/route-planner.css'
    index=site/'index.html'
    graph=site/'data/routes/xalapa_network.json'
    for p in (js,css,index,graph):
        if not p.is_file():
            raise SystemExit('STOP — existing route-planner file missing: '+str(p)+'\nNo files changed.')
    old=js.read_text(encoding='utf-8')
    if 'function dijkstra(begin,end)' not in old or ('vxr-geographic-overlay' not in old and 'Tap “Choose start on map”' not in old):
        raise SystemExit('STOP — different route planner version. No files changed. Please share site/js/route-planner.js.')
    html=index.read_text(encoding='utf-8')
    replacements={}
    for kind in ('js','css'):
        regexp=re.compile(r'(?P<before>(?:src|href)=[\'"])(?P<url>'+kind+r'/route-planner\.'+kind+r'(?:\?[^\'"]*)?)(?P<after>[\'"])')
        if len(regexp.findall(html))!=1:
            raise SystemExit('STOP — expected exactly one route-planner.'+kind+' asset in site/index.html; no changes made.')
        html=regexp.sub(lambda m:m.group('before')+kind+'/route-planner.'+kind+'?v='+VERSION+m.group('after'),html,count=1)
    # Validate the new files before saving backups or touching the site.
    for f in ('route-planner.js','route-planner.css'):
        if not (HERE/f).is_file() or (HERE/f).stat().st_size<1000:
            raise SystemExit('STOP — incomplete patch file: '+f)
    if not (HERE/'route-planner.js').read_text(encoding='utf-8').count('function dijkstra(begin,end)')==1:
        raise SystemExit('STOP — Dijkstra implementation missing in new JS')
    backup=root/('.before-route-ui-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    backup.mkdir(parents=True,exist_ok=False)
    for p in (js,css,index):
        dest=backup/p.relative_to(root)
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(p,dest)
    shutil.copy2(HERE/'route-planner.js',js)
    shutil.copy2(HERE/'route-planner.css',css)
    index.write_text(html,encoding='utf-8')
    print('SUCCESS — single guided map selection, route-only gold markers, distance-only results.')
    print('Refresh the site. You do not need to rebuild OSM data or restart an active server.')
    print('Road graph, attractions and tourism database untouched.')
    print('Backups:',backup)

if __name__=='__main__':main()
