#!/usr/bin/env python3
"""Bulk POI import from Geofabrik Mexico OSM PBF, with no Overpass dependency.

Conservatively discovers named features; coordinates represent mapped OSM features,
NOT verified entrances, and municipality proximity does NOT prove state membership.
Creates an offline Overpass-shaped results JSON and uses the existing map merger.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
URL = 'https://download.geofabrik.de/north-america/mexico-latest.osm.pbf'
TAGSETS = {
    'tourism': {'attraction','museum','gallery','viewpoint','zoo','theme_park'},
    'historic': {'archaeological_site','castle','fort','ruins'},
    'natural': {'waterfall','cave_entrance','beach','spring'},
    'waterway': {'waterfall'},
    'leisure': {'nature_reserve'},
}

def eligible(tags):
    return bool(tags.get('name')) and any(tags.get(k) in vals for k,vals in TAGSETS.items())

def close_to_seeds(lat,lon,seeds,km=35):
    if not (17.2 <= lat <= 22.5 and -99.4 <= lon <= -93.1):return False
    c=math.cos(math.radians(lat))
    return any(((lat-slat)*111.2)**2+((lon-slon)*111.2*c)**2 <= km*km for slon,slat in seeds)

def load_seeds(filename):
    data=json.loads(filename.read_text(encoding='utf-8'))
    seeds=[]
    for f in data.get('features',[]):
        try:
            lon,lat=map(float,f['geometry']['coordinates'])
            if math.isfinite(lon) and math.isfinite(lat):seeds.append((lon,lat))
        except (ValueError,TypeError,KeyError): pass
    if len(seeds)<200:raise RuntimeError('Expected >=200 municipality reference points; dataset appears incomplete.')
    return seeds

def parse_pbf(filename, seeds):
    try:import osmium
    except ImportError as exc:raise RuntimeError('Install PBF reader first: python -m pip install osmium') from exc
    print('Pass 1/3: scanning OSM features (no network calls)…',flush=True)
    selected_nodes=[]; selected_ways={}; selected_relations={}; rel_way_refs=set(); rel_node_refs=set()

    class Discover(osmium.SimpleHandler):
        def node(self,n):
            t=dict(n.tags)
            if not eligible(t) or not n.location.valid():return
            lat,lon=n.location.lat,n.location.lon
            if close_to_seeds(lat,lon,seeds):
                selected_nodes.append({'type':'node','id':n.id,'lat':lat,'lon':lon,'tags':t})
        def way(self,w):
            t=dict(w.tags)
            if not eligible(t):return
            selected_ways[w.id]=(t,[r.ref for r in w.nodes])
        def relation(self,r):
            t=dict(r.tags)
            if not eligible(t):return
            members=[(m.type,m.ref) for m in r.members]
            selected_relations[r.id]=(t,members)
            for typ,oid in members:
                if typ=='w':rel_way_refs.add(oid)
                elif typ=='n':rel_node_refs.add(oid)

    Discover().apply_file(str(filename))
    print(f'  Candidate nodes {len(selected_nodes)}, ways {len(selected_ways)}, relations {len(selected_relations)}',flush=True)
    if rel_way_refs:
        print('Pass 2/3: resolving member ways for relation geometry…',flush=True)
        class RelationWays(osmium.SimpleHandler):
            def way(self,w):
                if w.id in rel_way_refs and w.id not in selected_ways:
                    selected_ways[w.id]=(None,[n.ref for n in w.nodes])
        RelationWays().apply_file(str(filename))
    required=rel_node_refs.copy()
    for _,refs in selected_ways.values():required.update(refs)
    node_coords={}
    print(f'Pass 3/3: resolving {len(required)} referenced vertices…',flush=True)
    class ReadCoords(osmium.SimpleHandler):
        def node(self,n):
            if n.id not in required or not n.location.valid():return
            node_coords[n.id]=(n.location.lat,n.location.lon)
    ReadCoords().apply_file(str(filename))
    def center_refs(refs):
        pts=[node_coords[i] for i in refs if i in node_coords]
        if not pts:return None
        return {'lat':sum(p[0] for p in pts)/len(pts),'lon':sum(p[1] for p in pts)/len(pts)}
    results=selected_nodes[:];way_center={}
    for oid,(tags,refs) in selected_ways.items():
        center=center_refs(refs)
        if center:way_center[oid]=center
        if tags and center and close_to_seeds(center['lat'],center['lon'],seeds):
            results.append({'type':'way','id':oid,'center':center,'tags':tags})
    for oid,(tags,members) in selected_relations.items():
        pts=[]
        for kind,ref in members:
            if kind=='w' and ref in way_center:pts.append(way_center[ref])
            elif kind=='n' and ref in node_coords:
                lat,lon=node_coords[ref];pts.append({'lat':lat,'lon':lon})
        if pts:
            center={'lat':sum(p['lat'] for p in pts)/len(pts), 'lon':sum(p['lon'] for p in pts)/len(pts)}
            if close_to_seeds(center['lat'],center['lon'],seeds):
                results.append({'type':'relation','id':oid,'center':center,'tags':tags})
    print(f'Named geographic candidates near Veracruz municipalities: {len(results)}',flush=True)
    return results

def download(path):
    path.parent.mkdir(parents=True,exist_ok=True)
    receipt=path.with_suffix(path.suffix+'.complete')
    if path.exists() and receipt.exists() and receipt.read_text().strip()==str(path.stat().st_size):
        print(f'Using completed local extract: {path} ({path.stat().st_size//1_000_000} MB)')
        return
    print('Downloading Mexico OSM extract (~600-700 MB), resumable; may take a while.')
    print('Source:',URL,flush=True)
    cp=subprocess.run(['curl','--fail','--location','--retry','3','--continue-at','-','--output',str(path),URL])
    if cp.returncode:raise RuntimeError('Download failed. Rerun the command later to resume; site is unchanged.')
    if path.stat().st_size<300_000_000:raise RuntimeError('Downloaded file unexpectedly small. Site unchanged.')
    receipt.write_text(str(path.stat().st_size))

def main():
    p=argparse.ArgumentParser()
    p.add_argument('root',nargs='?',default='.')
    p.add_argument('--pbf',help='Already downloaded Mexico .osm.pbf (skips download)')
    p.add_argument('--no-apply',action='store_true',help='Create candidates and audit without modifying website')
    a=p.parse_args()
    root=Path(a.root).resolve()
    for file in ('site/data/map_points.geojson','site/data/attractions.csv','site/data/attractions.geojson','site/data/tourism_catalog.csv','site/js/map-attractions.js'):
        if not (root/file).is_file():raise RuntimeError(f'Missing {root/file}; install latest full catalog patch first.')
    pbf=Path(a.pbf).expanduser().resolve() if a.pbf else root/'.veracruz_osm_checkpoints'/'mexico-latest.osm.pbf'
    if not a.pbf:download(pbf)
    if not pbf.is_file():raise RuntimeError('PBF not found: '+str(pbf))
    seeds=load_seeds(root/'site/data/map_points.geojson')
    results=parse_pbf(pbf,seeds)
    cache=root/'.veracruz_osm_checkpoints';cache.mkdir(exist_ok=True)
    output=cache/'geofabrik_osm_candidates.json'
    output.write_text(json.dumps({'elements':results},ensure_ascii=False),encoding='utf-8')
    report=cache/'geofabrik_audit.json'
    report.write_text(json.dumps({'candidate_features':len(results),'dataset_source':URL,'precision':'mapped OSM feature; NOT visitor entrance','state_membership':'approximate proximity only; requires manual geographic validation','output':str(output)},indent=2),encoding='utf-8')
    print('Candidates saved:',output,'— audit:',report,flush=True)
    if not results:raise RuntimeError('Zero geographically plausible POIs; current website unchanged.')
    if a.no_apply:print('Dry run complete; website untouched.');return
    cp=subprocess.run([sys.executable,str(HERE/'finalize_map.py'),str(root),'--osm-json',str(output)])
    if cp.returncode:raise RuntimeError('Existing map merge rejected candidates; website should be unchanged, candidates saved.')
    print('Bulk import complete. Original curated attractions and PP3 master database preserved.')

if __name__=='__main__':
    try:main()
    except Exception as e:print('STOP:',e,file=sys.stderr);sys.exit(1)
