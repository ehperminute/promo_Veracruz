#!/usr/bin/env python3
"""Build the searchable, evidence-preserving catalogue from an editable CSV.
No missing attraction coordinates are invented.  Longitude/latitude 'reference' is only
used for navigation to an explicitly reported municipality, never to place an attraction marker.
"""
from pathlib import Path
import csv, json, sys, tempfile, os
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd()
src=ROOT/'site/data/tourism_catalog.csv'; dest=ROOT/'site/data/tourism_catalog.json'
required={'id','name','kind','municipality','municipality_id','source_url','activity','source_text_es','lat','lon','geographic_precision'}
if not src.is_file():raise SystemExit('Missing '+str(src))
with src.open(encoding='utf-8-sig',newline='') as f:
 reader=csv.DictReader(f)
 if not required.issubset(reader.fieldnames or []):raise SystemExit('Missing CSV columns: '+str(required-set(reader.fieldnames or [])))
 rows=list(reader)
ids=set()
for row in rows:
 if not row['id'].strip() or row['id'] in ids: raise SystemExit('Blank or duplicate record id: '+row['id'])
 ids.add(row['id'])
 if row['lat'] or row['lon']:
  if not row['lat'] or not row['lon']:raise SystemExit('Only one coordinate for '+row['id'])
  la,lo=float(row['lat']),float(row['lon'])
  if not (17.0<la<23.1 and -99.5<lo<-93.5):raise SystemExit('Coordinates outside Veracruz vicinity: '+row['id'])
  if row['geographic_precision'] not in ('municipality_reference','mapped_feature','verified_entrance'):
   raise SystemExit('Coordinate precision must be explicit: '+row['id'])
 if row['geographic_precision'] in ('mapped_feature','verified_entrance') and not (row['lat'] and row['lon']):
  raise SystemExit('Claimed mapped feature lacks coordinates: '+row['id'])
obj={'schema_version':1,'source':'Veracruz recovered PP3 source-first master: places, cultural_place_event_leads, catalog_product_cards','records':rows}
dest.parent.mkdir(parents=True,exist_ok=True)
fd,temp=tempfile.mkstemp(dir=dest.parent,prefix='.catalog_',suffix='.json')
try:
 with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump(obj,f,ensure_ascii=False,separators=(',',':'))
 os.replace(temp,dest)
finally:
 if os.path.exists(temp):os.unlink(temp)
print('Catalog indexed:',len(rows),'records | named places',sum(r['kind']=='named_place' for r in rows),'| evidence leads',sum(r['kind']=='place_event_lead' for r in rows),'| tourism products',sum(r['kind']=='tourism_product' for r in rows))
