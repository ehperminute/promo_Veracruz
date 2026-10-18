#!/usr/bin/env python3
"""Publish a bounded regional OSM road graph and eligible attraction snaps for browser Dijkstra."""
import csv, gzip, json, math, os, sys
from pathlib import Path
from route_network import km_between

def main(graph_path, csv_path, output_path, max_snap=2.0):
    with gzip.open(graph_path, 'rt', encoding='utf-8') as f:
        graph=json.load(f)
    coords=graph['coords']; adj=graph['adj']; order=list(coords)
    ids={node:i for i,node in enumerate(order)}
    if len(order)<2 or len(order)>350_000:
        raise RuntimeError(f'Unsafe graph size ({len(order)} nodes); choose a smaller regional bbox')
    positions=[[round(coords[n][1],6),round(coords[n][0],6)] for n in order]
    edges=[[[ids[k],w] for k,w in adj.get(n,{}).items()] for n in order]
    bounds=graph['metadata']['bbox']; south,west,north,east=bounds
    with open(csv_path, encoding='utf-8-sig', newline='') as f:
        rows=list(csv.DictReader(f))
    sites=[]
    for r in rows:
        try:lat,lon=float(r['lat']),float(r['lon'])
        except (KeyError,TypeError,ValueError):continue
        if not (south<=lat<=north and west<=lon<=east):continue
        nearest=min(((km_between((lat,lon),(p[1],p[0])),i) for i,p in enumerate(positions)),default=None)
        if nearest is None or nearest[0]>max_snap:continue
        sites.append({'id':r['id'],'name':r['name'],'at':[round(lon,6),round(lat,6)],
            'node':nearest[1],'snap_km':round(nearest[0],3),'icon':r.get('icon','📍')})
    if len(sites)<2:raise RuntimeError('Fewer than two attractions snap to this regional graph; increase bbox or verify coordinates')
    payload={'version':1,'units':'km','region':'Xalapa–Coatepec–Xico','bbox':bounds,
         'limitations':'Shortest simplified OSM road distance; NO turn restrictions, ETA, traffic or entrance verification.',
         'positions':positions,'edges':edges,'sites':sites}
    output_path.parent.mkdir(parents=True,exist_ok=True)
    tmp=output_path.with_name(output_path.name+'.tmp')
    with tmp.open('w',encoding='utf-8') as f:
        json.dump(payload,f,ensure_ascii=False,separators=(',',':'))
    size=tmp.stat().st_size
    if size>35_000_000:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f'Browser graph is {size/1e6:.1f}MB; reduce regional bbox before publishing')
    os.replace(tmp,output_path)
    print(f'Browser graph exported: {len(positions):,} road nodes, {sum(map(len,edges)):,} directed arcs, {len(sites)} selectable attractions; {size/1e6:.2f} MB')
    print('Saved:',output_path)
    return payload

if __name__=='__main__':
    if len(sys.argv)!=4:
        raise SystemExit('Usage: python export_browser_graph.py ROADS.json.gz site/data/attractions.csv site/data/routes/xalapa_network.json')
    main(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]))
