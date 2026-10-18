#!/usr/bin/env python3
"""Resume-friendly geographic OSM research, compatible with Veracruz final map installer.

Splits the statewide query into small bboxes near known Veracruz municipalities,
caches each successful response, and delegates final CSV/GeoJSON merge to the
previously shipped, tested finalize_map.py. No edit to research SQLite.

IMPORTANT: bounds are research windows, not a legal state polygon. Imported OSM
records remain flagged as unverified candidates, never certified entrances.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError

HERE=Path(__file__).resolve().parent
ENDPOINTS=(
    'https://overpass.private.coffee/api/interpreter',
    'https://overpass-api.de/api/interpreter',
)
# Latitude/longitude boundaries for the *research grid*, not the state's outline.
WEST, SOUTH, CELL = -99.5, 17.0, 1.0
HEADERS={'User-Agent':'VeracruzAcademicTourismProject/1.1 (bounded one-time OpenStreetMap research)', 'Accept':'application/json'}
TAG_QUERY='''[out:json][timeout:50][bbox:{bbox}];
(
  nwr["name"]["tourism"~"^(attraction|museum|gallery|viewpoint|zoo|theme_park)$"];
  nwr["name"]["historic"~"^(archaeological_site|castle|fort|ruins)$"];
  nwr["name"]["natural"~"^(waterfall|cave_entrance|beach|spring)$"];
  nwr["name"]["waterway"="waterfall"];
  nwr["name"]["leisure"="nature_reserve"];
);
out center tags;'''

def grid(geojson_path, attraction_path):
    with geojson_path.open(encoding='utf-8') as f:d=json.load(f)
    if len(d.get('features',[])) < 200:
        raise RuntimeError('Expected the current 212 municipality coordinates; found too few.')
    seeds=[]
    for feat in d['features']:
        try:
            lon,lat=feat['geometry']['coordinates']
            if -99.5<=lon<=-93.0 and 17.0<=lat<=22.7:seeds.append((float(lon),float(lat)))
        except (KeyError,TypeError,ValueError):pass
    # Also include known attraction pins to cover coastlines and distant landmarks.
    if attraction_path.exists():
        with attraction_path.open(encoding='utf-8') as f: a=json.load(f)
        for feat in a.get('features',[]):
            try:
                lon,lat=feat['geometry']['coordinates']
                if -99.5<=lon<=-93.0 and 17.0<=lat<=22.7:seeds.append((float(lon),float(lat)))
            except (KeyError,TypeError,ValueError):pass
    tiles=set()
    for lon,lat in seeds:
        for dx in (-.14,.14):
            for dy in (-.14,.14):
                x=math.floor((lon+dx-WEST)/CELL)
                y=math.floor((lat+dy-SOUTH)/CELL)
                if 0<=x<=7 and 0<=y<=6:tiles.add((y,x))
    return sorted(tiles),seeds

def box(tile):
    y,x=tile
    s=SOUTH+CELL*y; w=WEST+CELL*x
    return f'{s:.4f},{w:.4f},{s+CELL:.4f},{w+CELL:.4f}'

def query(tile):return TAG_QUERY.format(bbox=box(tile))

def cache_key(tile):return f'tile_{tile[0]:02d}_{tile[1]:02d}'

def validate_response(obj):
    if not isinstance(obj,dict) or not isinstance(obj.get('elements'),list):
        raise ValueError('Overpass did not return a valid elements array.')
    # A valid empty response is okay in a low-density tile.
    for e in obj['elements']:
        if not isinstance(e,dict):raise ValueError('Malformed geographic object in response')
    return obj

def fetch_tile(tile):
    payload=urllib.parse.urlencode({'data':query(tile)}).encode('utf-8')
    errors=[]
    for endpoint in ENDPOINTS:
        try:
            req=urllib.request.Request(endpoint,data=payload,headers=HEADERS)
            with urllib.request.urlopen(req,timeout=70) as res:
                content=res.read(12_000_001)
                if len(content)>12_000_000:raise RuntimeError('Oversized response')
                obj=validate_response(json.loads(content))
            return obj,endpoint
        except (HTTPError,URLError,TimeoutError,ValueError,RuntimeError,OSError,json.JSONDecodeError) as ex:
            errors.append(f'{endpoint}: {type(ex).__name__}: {ex}')
    raise RuntimeError('; '.join(errors))

def nearest_distance(lat,lon,seeds):
    """Approximate shortest distance to recorded municipality reference/attraction point.
    This is only a coarse filter to reduce neighboring-state records, NOT proof
    of administrative boundary membership.
    """
    best=1e9
    c=math.cos(math.radians(lat))
    for x,y in seeds:
        d=((lat-y)*111.2)**2+((lon-x)*111.2*c)**2
        if d<best:best=d
    return math.sqrt(best)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('root',nargs='?',default='.',help='promo_Veracruz root directory')
    ap.add_argument('--offline',action='store_true',help='Only use existing cached response files; never contact servers')
    ap.add_argument('--cache-dir',help='Override checkpoint directory for tests')
    args=ap.parse_args()
    root=Path(args.root).resolve()
    site=root/'site';data=site/'data'
    required=(data/'map_points.geojson',data/'attractions.csv',data/'attractions.geojson',site/'js/map-attractions.js',data/'tourism_catalog.csv')
    for p in required:
        if not p.is_file():raise RuntimeError(f'Missing {p}. Make sure you are in the promo_Veracruz root.')
    old=HERE/'finalize_map.py'
    if not old.is_file():
        raise RuntimeError('The bundled finalize_map.py is missing; extract the entire fix ZIP.')
    cache=Path(args.cache_dir) if args.cache_dir else root/'.veracruz_osm_checkpoints'
    cache.mkdir(parents=True,exist_ok=True)
    tiles,seeds=grid(data/'map_points.geojson',data/'attractions.geojson')
    print(f'Split Veracruz research into {len(tiles)} smaller map areas; successes are cached.',flush=True)
    successes=[]; fail=[]; consecutive_failures=0
    for i,tile in enumerate(tiles,1):
        file=cache/(cache_key(tile)+'.json')
        if file.exists():
            try:validate_response(json.loads(file.read_text(encoding='utf-8')))
            except (ValueError,KeyError,json.JSONDecodeError):
                print(f'  Invalid cached file {file}; will try again.')
                file.unlink()
        if not file.exists() and not args.offline and consecutive_failures>=2:
            fail.append({'tile':cache_key(tile),'box':box(tile),'reason':'Deferred: services failed in two consecutive areas; avoid overwhelming public servers'})
            continue
        if not file.exists() and not args.offline:
            print(f'[{i}/{len(tiles)}] Fetching {box(tile)}',flush=True)
            try:
                obj,endpoint=fetch_tile(tile)
                tmp=file.with_suffix('.tmp')
                tmp.write_text(json.dumps(obj,ensure_ascii=False),encoding='utf-8')
                tmp.replace(file)
                print(f'    Saved {len(obj["elements"])} OSM objects from {endpoint}',flush=True)
                consecutive_failures=0
                time.sleep(1.5)  # Be polite to donated public infrastructure.
            except Exception as ex:
                consecutive_failures+=1
                fail.append({'tile':cache_key(tile),'box':box(tile),'reason':str(ex)})
                print('    Not available; will leave this tile pending (cached others are safe).',flush=True)
        if file.exists():successes.append(file)
        elif args.offline:fail.append({'tile':cache_key(tile),'box':box(tile),'reason':'Not cached'})
    # Only call the already-tested site writer after successful results exist.
    elements={};rejected=0
    for filename in successes:
        obj=validate_response(json.loads(filename.read_text(encoding='utf-8')))
        for e in obj['elements']:
            typ=e.get('type');oid=e.get('id')
            if typ not in ('node','way','relation') or not isinstance(oid,int):continue
            pos=e.get('center') or e
            try:lat=float(pos['lat']);lon=float(pos['lon'])
            except (KeyError,ValueError,TypeError):continue
            # Bounding-box research can include neighboring states. This conservative
            # proximity filter reduces cross-border pins, but all remain review-only.
            if nearest_distance(lat,lon,seeds)>35:
                rejected+=1;continue
            elements[(typ,oid)]=e
    state={
        'searched_areas':len(tiles), 'cached_successes':len(successes),
        'unresolved_areas':fail, 'unique_osm_objects':len(elements),
        'rejected_far_from_known_veracruz_references':rejected,
        'location_warning':'Nearest-municipality proximity is NOT a state boundary proof; individual visitor entrances and jurisdiction need review.'
    }
    (cache/'run_report.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
    if not elements:
        print('No usable geographic results yet. Current website untouched. See checkpoint report:',cache/'run_report.json')
        return 2
    combined=cache/'combined_results.json'
    combined.write_text(json.dumps({'elements':list(elements.values())},ensure_ascii=False),encoding='utf-8')
    print(f'Applying {len(elements)} unique geographic records from {len(successes)}/{len(tiles)} areas.',flush=True)
    cp=subprocess.run([sys.executable,str(old),str(root),'--osm-json',str(combined)],check=False)
    if cp.returncode:
        print('Site merge rejected the data. Existing site should be unchanged. Cached research is safe.',file=sys.stderr)
        return cp.returncode
    if fail:print(f'PARTIAL: {len(fail)} map areas still unavailable. A later rerun will retry ONLY those areas.',flush=True)
    else:print('COMPLETE: all selected geographic research areas processed.',flush=True)
    print('Checkpoint/audit:',cache/'run_report.json')
    return 0

if __name__=='__main__':
    try:sys.exit(main())
    except Exception as e:
        print(f'STOP: {e}',file=sys.stderr);sys.exit(1)
