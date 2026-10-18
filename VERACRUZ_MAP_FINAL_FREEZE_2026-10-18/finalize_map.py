#!/usr/bin/env python3
"""One-time geographic enrichment for the existing Veracruz tourism website.

Reads real named OpenStreetMap attractions through one Overpass request, preserves
existing site catalogue, writes independently sourced map points + audit.
Does NOT claim that POIs are necessarily in the PP3 catalogue, or that coordinates
are visitor entrances.  Designed to be executed in Codespaces, which has internet.
"""
from __future__ import annotations
import argparse
import csv
import io
import json
import math
import re
import shutil
import sys
import time
import unicodedata
import urllib.request
import urllib.parse
import urllib.error
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
OVERPASS_URLS=("https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter")
QUERY='''[out:json][timeout:140];
area["ISO3166-2"="MX-VER"]["admin_level"="4"]->.ver;
(
  nwr(area.ver)["name"]["tourism"~"^(attraction|museum|gallery|viewpoint|zoo|theme_park)$"];
  nwr(area.ver)["name"]["historic"~"^(archaeological_site|castle|fort|ruins)$"];
  nwr(area.ver)["name"]["natural"~"^(waterfall|cave_entrance|beach|spring)$"];
  nwr(area.ver)["name"]["waterway"="waterfall"];
  nwr(area.ver)["name"]["leisure"="nature_reserve"];
);
out center tags;'''
FIELDS=['id','name','lat','lon','type','icon','status','source_url','source_provider','municipality','description_en','description_es','details_en','details_es','visit_note_en','visit_note_es','photo_url','photo_credit','photo_source_url']
ICON={'archaeological_site':('Archaeological site','🏛️'), 'museum':('Museum','🏛️'), 'gallery':('Gallery','🎨'), 'waterfall':('Waterfall','💧'), 'beach':('Beach','🏖️'), 'cave_entrance':('Cave','🏞️'), 'nature_reserve':('Nature reserve','🌿'), 'spring':('Spring','💧'), 'viewpoint':('Viewpoint','🏞️'), 'castle':('Historic site','🏰'), 'fort':('Historic site','🏰'), 'ruins':('Ruins','🏛️'), 'zoo':('Zoo','🌿'), 'theme_park':('Attraction','🎭'), 'attraction':('Attraction','🌿')}

def normalized(s):
    s=unicodedata.normalize('NFKD',str(s).casefold())
    s=''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+',' ',s).strip()

def coords(row):
    raw=(row.get('center') or row)
    try: return float(raw['lat']),float(raw['lon'])
    except (KeyError, TypeError, ValueError):return None

def haversine_km(a,b):
    la1,lo1=a; la2,lo2=b; p1,p2=map(math.radians,(la1,la2)); dlat=p2-p1; dlon=math.radians(lo2-lo1)
    return 6371*2*math.asin(math.sqrt(math.sin(dlat/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dlon/2)**2))

def classify(tags):
    for key in ('historic','natural','waterway','tourism','leisure'):
        val=tags.get(key)
        if key=='waterway' and val=='waterfall':return ICON['waterfall'], 'mapped_area'
        if key=='leisure' and val=='nature_reserve':return ICON['nature_reserve'],'mapped_area'
        if val in ICON:
            return ICON[val], ('mapped_area' if val in {'beach','nature_reserve','waterfall','spring','cave_entrance'} else 'mapped_site')
    return None

def fetch_once():
    data=urllib.parse.urlencode({'data':QUERY}).encode('utf-8')
    errors=[]
    for url in OVERPASS_URLS:
        req=urllib.request.Request(url,data=data,headers={'User-Agent':'VeracruzEducationalTourismProject/1.0 (one-time geographic research; OpenStreetMap attribution)', 'Accept':'application/json'})
        try:
            print('Requesting named tourist places from:',url,flush=True)
            with urllib.request.urlopen(req,timeout=165) as response:
                raw=response.read(28_000_000)
                if response.read(1):raise ValueError('Overpass result exceeds 28 MB limit')
                result=json.loads(raw)
            if not isinstance(result.get('elements'),list) or not result['elements']:
                raise ValueError('Overpass returned no named locations (area unavailable or empty).')
            return result,url
        except (OSError, urllib.error.URLError, ValueError, json.JSONDecodeError) as e:
            errors.append(f'{url}: {e}')
    raise RuntimeError('Overpass query could not complete. No website files modified.\n'+'\n'.join(errors))

def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if reader.fieldnames!=FIELDS:
            raise RuntimeError(f'Unexpected CSV schema: {path}. Refusing to overwrite custom edits.')
        return list(reader)

def to_bytes(rows):
    mem=io.StringIO();wr=csv.DictWriter(mem,fieldnames=FIELDS,lineterminator='\n');wr.writeheader();wr.writerows(rows)
    return ('\ufeff'+mem.getvalue()).encode('utf-8')

def build(rows, items, catalog_names):
    # Cleanly replace previous OSM-sourced import on repeat runs, but never remove original curated rows.
    curated=[r for r in rows if not r['id'].startswith('OSM-')]
    existing={normalized(r['name']):[] for r in curated}
    for r in curated:
        existing.setdefault(normalized(r['name']),[]).append((float(r['lat']),float(r['lon'])))
    seen_osm=set();additions=[];log=[]
    for e in items:
        osm_type=e.get('type');osm_id=e.get('id');tags=e.get('tags') or {}
        if osm_type not in {'node','way','relation'} or not isinstance(osm_id,int):continue
        name=(tags.get('name:es') or tags.get('name') or '').strip()
        pos=coords(e);typ=classify(tags)
        if not name or not pos or not typ:continue
        lat,lon=pos
        # guard against an incorrect area match or impossible geometry
        if not 17.2<=lat<=22.5 or not -99.4<=lon<=-93.1:continue
        norm=normalized(name);key=(osm_type,osm_id)
        if not norm or key in seen_osm:continue
        seen_osm.add(key)
        tagkind,status=typ;kind,icon=tagkind
        published=norm in catalog_names
        # Exact source-name + <=1.5 km duplicate; same-name places in other towns can coexist.
        if any(haversine_km(pos,x)<1.5 for x in existing.get(norm,[])):
            log.append({'name':name,'action':'already_curated','source':f'https://www.openstreetmap.org/{osm_type}/{osm_id}'});continue
        if any(normalized(r['name'])==norm and haversine_km(pos,(float(r['lat']),float(r['lon'])))<1.5 for r in additions):
            log.append({'name':name,'action':'duplicate_OSM','source':f'https://www.openstreetmap.org/{osm_type}/{osm_id}'});continue
        provider='OpenStreetMap — name matched to PP3 catalog' if published else 'OpenStreetMap — additional mapped place (review)'
        additions.append(dict.fromkeys(FIELDS,''))
        r=additions[-1]
        r.update({'id':f'OSM-{osm_type}-{osm_id}','name':name,'lat':str(lat),'lon':str(lon),
                  'type':kind,'icon':icon,'status':status,
                  'source_url':f'https://www.openstreetmap.org/{osm_type}/{osm_id}',
                  'source_provider':provider,
                  'municipality':(tags.get('addr:city') or tags.get('addr:municipality') or ''),
                  # Do not manufacture brochures, admissions, photographs or exact entrances.
                  'visit_note_en':'Attraction coordinates are mapped by OpenStreetMap; visitor entrances and current access are not verified.',
                  'visit_note_es':'Ubicación cartografiada en OpenStreetMap; entrada de visitantes y acceso vigente sin verificar.'})
        log.append({'name':name,'action':'catalog_name_match' if published else 'OSM_added_unmatched','source':r['source_url']})
    # Catalogue-matching attractions appear first in GeoJSON and search results; all are genuine OSM mapped objects.
    additions.sort(key=lambda r:(0 if 'name matched' in r['source_provider'] else 1,normalized(r['name'])))
    return curated+additions,log

def csv_to_geojson(rows):
    features=[]
    for r in rows:
        la,lo=float(r['lat']),float(r['lon'])
        if not(math.isfinite(la) and math.isfinite(lo) and 17.2<=la<=22.6 and -99.4<=lo<=-93.1):raise ValueError('Invalid location '+r['name'])
        p={k:v for k,v in r.items() if k not in ('lat','lon')};p['mapping_status']=r['status'];p['attraction_name_original']=r['name']
        features.append({'type':'Feature','id':r['id'],'geometry':{'type':'Point','coordinates':[lo,la]},'properties':p})
    return json.dumps({'type':'FeatureCollection','name':'Veracruz tourist attractions; OSMap site coordinates are NOT necessarily entrances','features':features},ensure_ascii=False,indent=2).encode('utf-8')

def patch_map_js(src):
    # Keep named/OFFICIAL points displayed statewide. OSM discovery appears only after zooming,
    # or when searched, to prevent statewide visual overload. Never manipulate MapLibre position/transform.
    old="markers.push({el:e,id:entry.id});"
    new="markers.push({el:e,id:entry.id,osm:entry.id.startsWith('MAP-OSM-'),name:normal(p.name)});"
    src=src.replace(old,new,1) if old in src else src
    old="const zoomLabels=()=>{const z=map.getZoom();markers.forEach(m=>m.el.classList.toggle('vxa-labels-on',z>=9.2||m.id===active));};"
    new="""const zoomLabels=()=>{const z=map.getZoom(),q=normal(search.value);markers.forEach(m=>{
 m.el.classList.toggle('vxa-labels-on',z>=9.2||m.id===active||(q&&m.name.includes(q)));
 if(m.osm)m.el.style.display=(z>=9.0||m.id===active||(q&&m.name.includes(q)))?'':'none';
});};"""
    if old in src:src=src.replace(old,new,1)
    elif new not in src:raise RuntimeError('Current map JS differs from the known version; no changes made. See README.')
    needle="search.addEventListener('input',()=>{paging=65;guide.hidden=true;render();});"
    if needle in src:src=src.replace(needle,"search.addEventListener('input',()=>{paging=65;guide.hidden=true;render();zoomLabels();});",1)
    return src

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('root',nargs='?',default='.',help='promo_Veracruz repository root')
    parser.add_argument('--osm-json',help='Offline Overpass response for test/recovery; default fetches once')
    args=parser.parse_args();root=Path(args.root).resolve();site=root/'site';data=site/'data'
    csvfile=data/'attractions.csv';geo=data/'attractions.geojson';js=site/'js/map-attractions.js';catalog=data/'tourism_catalog.csv'
    for path in (csvfile,geo,js,catalog):
        if not path.exists():raise RuntimeError('Missing '+str(path)+'; install the last full catalog patch first.')
    rows=read_csv(csvfile)
    known_js=js.read_text(encoding='utf-8')
    patched_js=patch_map_js(known_js)
    with catalog.open(encoding='utf-8-sig',newline='') as f: catalogrows=list(csv.DictReader(f))
    if not len(catalogrows)>=495:raise RuntimeError('Current tourism catalog appears incomplete; refusing to proceed.')
    catalog_names={normalized(r['name']) for r in catalogrows if r.get('kind') in ('named_place','place_event_lead') and normalized(r['name'])}
    if args.osm_json:
        obj=json.loads(Path(args.osm_json).read_text(encoding='utf-8'));endpoint='offline_json'
    else:obj,endpoint=fetch_once()
    if not isinstance(obj.get('elements'),list) or len(obj['elements'])<1:
        raise RuntimeError('No usable OpenStreetMap objects. Nothing changed.')
    out,review=build(rows,obj['elements'],catalog_names)
    osm_count=sum(r['id'].startswith('OSM-') for r in out)
    if osm_count<1:raise RuntimeError('No new geolocated named attractions found; no changes made.')
    newcsv=to_bytes(out);newgeo=csv_to_geojson(out)
    html=site/'index.html'
    if not html.exists():raise RuntimeError('Missing homepage index.html')
    page=html.read_text(encoding='utf-8')
    import re as regex
    versioned=regex.sub(r'(src=[\"\']js/map-attractions\.js)(?:\?[^\"\']*)?([\"\'])',r'\g<1>?v=20261018-finalfreeze\2',page)
    if versioned==page and '20261018-finalfreeze' not in page:raise RuntimeError('Map attractions script not linked on homepage; stopping.')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    backup=root/('veracruz_map_final_backup_'+stamp)
    backup.mkdir(exist_ok=False)
    for p in [csvfile,geo,js,html]:
        d=backup/p.relative_to(root);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d)
    audit=data/'osm_geocoding_audit.json'
    audit_payload={'retrieved_utc':stamp,'endpoint':endpoint,'records_in_osm_response':len(obj['elements']),
         'previous_curated_pins':len([r for r in rows if not r['id'].startswith('OSM-')]),
         'new_osm_pins':osm_count,'catalog_matching_name_pins':sum('name matched' in r['source_provider'] for r in out),
         'notes':'OSM mapped features are candidate destinations. Their source coordinates are NOT guaranteed entrance/parking locations. Original research catalogue remains unchanged.',
         'review':review}
    # Stage all data before any changes.
    targets={csvfile:newcsv,geo:newgeo,js:patched_js.encode('utf-8'),html:versioned.encode('utf-8'),audit:json.dumps(audit_payload,ensure_ascii=False,indent=2).encode('utf-8')}
    for p,content in targets.items():
        tmp=p.with_name(p.name+'.tmp-veracruz');tmp.write_bytes(content)
    for p in targets:
        p.with_name(p.name+'.tmp-veracruz').replace(p)
    print('\nVERACRUZ MAP DATA UPDATED')
    print('Existing editorial pins:',len([r for r in rows if not r['id'].startswith('OSM-')]))
    print('Additional named POIs mapped from OSM:',osm_count)
    print('Total mapped attraction objects:',len(out))
    print('Research catalog source records kept:',len(catalogrows))
    print('Audit:',audit)
    print('Rollback copy:',backup)
    print('At statewide zoom, original curated markers remain; OSM pins appear at zoom >= 9 or when searched.')
    print('No changes to the PP3 research database. No new descriptions/photos fabricated.')

if __name__=='__main__':
    try:main()
    except Exception as e:
        print('STOP — map files not changed: '+str(e),file=sys.stderr);sys.exit(1)
