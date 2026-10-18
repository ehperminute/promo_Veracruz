#!/usr/bin/env python3
"""One-time regional road-graph preparation + additive homepage route planner."""
from pathlib import Path
from datetime import datetime,timezone
import argparse, importlib.util, json, re, shutil, sys

HERE=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser(description='Integrate Xalapa regional browser-side Dijkstra into existing Veracruz map')
    parser.add_argument('root',nargs='?',default='.',help='promo_Veracruz repository root')
    parser.add_argument('--graph',help='Use an existing prebuilt road graph (.json.gz), instead of rebuilding from PBF')
    args=parser.parse_args();root=Path(args.root).resolve();site=root/'site'
    html=site/'index.html';attractions=site/'data/attractions.csv';mapjs=site/'js/map-explorer.js'
    for p in (html,attractions,mapjs):
        if not p.is_file():raise SystemExit('STOP — missing required existing-site file: '+str(p))
    old_html=html.read_text(encoding='utf-8')
    if not re.search(r'<script\b[^>]*src=["\']js/map-explorer\.js',old_html):
        raise SystemExit('STOP — homepage map script not found. No website modifications made.')
    if 'window.__vx_attraction_map' not in mapjs.read_text(encoding='utf-8'):
        raise SystemExit('STOP — map instance is not exposed by installed map version. No modifications made.')
    spec=importlib.util.spec_from_file_location('vxexport',HERE/'export_browser_graph.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    graph=Path(args.graph).resolve() if args.graph else root/'data/processed/xalapa_roads.json.gz'
    if not graph.exists():
        pbf=root/'.veracruz_osm_checkpoints/mexico-latest.osm.pbf'
        if not pbf.is_file():raise SystemExit('STOP — Mexico PBF was not found at '+str(pbf)+'; no files changed.')
        from route_network import build_graph
        print('ONE-TIME ROAD DATA PREPARATION: this may take minutes; not a browser route search.',flush=True)
        build_graph(pbf,(19.36,-97.09,19.63,-96.82),graph)
    else:
        print('Reusing existing regional graph:',graph,flush=True)
    output=site/'data/routes/xalapa_network.json'
    tmp=output.with_name(output.name+'.new')
    try:mod.main(graph,attractions,tmp)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise
    if not json.loads(tmp.read_text(encoding='utf-8')).get('sites'):
        tmp.unlink(missing_ok=True);raise SystemExit('STOP — no selectable attractions in this region')
    js=site/'js/route-planner.js';css=site/'css/route-planner.css'
    existing=old_html
    if 'route-planner.js' not in existing:
        if '</body>' not in existing:tmp.unlink(missing_ok=True);raise SystemExit('STOP — no closing body tag in homepage')
        existing=existing.replace('</body>','<script defer src="js/route-planner.js?v=20261018-or1"></script>\n</body>',1)
    if 'route-planner.css' not in existing:
        css_tag='<link rel="stylesheet" href="css/route-planner.css?v=20261018-or1">\n'
        existing=existing.replace('</head>',css_tag+'</head>',1) if '</head>' in existing else css_tag+existing
    backup=root/('.before-route-planner-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    backup.mkdir(parents=True,exist_ok=False)
    for p in (html,js,css,output):
        if p.exists():
            dest=backup/p.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    for src,dst in ((HERE/'assets/route-planner.js',js),(HERE/'assets/route-planner.css',css)):
        dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
    output.parent.mkdir(parents=True,exist_ok=True);tmp.replace(output)
    if existing!=old_html:html.write_text(existing,encoding='utf-8')
    print('SUCCESS: Plan a route appears in the current homepage map sidebar.')
    print('Select regional attractions, calculate routes in the browser; no backend required.')
    print('Map/description databases unchanged. Backup:',backup)

if __name__=='__main__':main()
