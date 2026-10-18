#!/usr/bin/env python3
"""Non-destructive bulk Veracruz catalog integration for an existing promo_Veracruz site.
Adds sourced mapped attractions and indexes ALL recovered reference records.
No research tables, homepage sections, or municipality files are overwritten.
"""
from pathlib import Path
from datetime import datetime, timezone
import csv, json, re, shutil, sys, tempfile
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd().resolve()
SRC=Path(__file__).resolve().parent
SITE=ROOT/'site'; INDEX=SITE/'index.html'; DATA=SITE/'data'
CSV=DATA/'attractions.csv'; GEO=DATA/'attractions.geojson'
ADD=SRC/'assets/attractions_additions.csv'
TARGETS={
 SITE/'js/map-attractions.js':SRC/'assets/map-attractions.js',
 SITE/'css/map-attractions.css':SRC/'assets/map-attractions.css',
 DATA/'tourism_catalog.csv':SRC/'assets/tourism_catalog.csv',
 DATA/'tourism_catalog.json':SRC/'assets/tourism_catalog.json',
 ROOT/'tools/build_catalog_index.py':SRC/'tools/build_catalog_index.py',
}
def error(msg):raise SystemExit('STOP: '+msg+' — No changes made.')
for p in [INDEX,CSV,GEO,SITE/'js/map-explorer.js',ADD,*TARGETS.values()]:
 if not p.is_file():error('Missing required file: '+str(p))
html=INDEX.read_text(encoding='utf-8')
if not re.search(r'<script\b[^>]*src=["\']js/map-attractions\.js',html):error('Install the editable attractions patch first: index.html does not load map-attractions.js')
if 'window.__vx_attraction_map' not in (SITE/'js/map-explorer.js').read_text(encoding='utf-8'):
 error('Expected base map global unavailable; share the current map files before modifying it')
with CSV.open(encoding='utf-8-sig',newline='') as f:
 reader=csv.DictReader(f);colnames=reader.fieldnames;original=list(reader)
with ADD.open(encoding='utf-8-sig',newline='') as f:
 reader=csv.DictReader(f)
 if reader.fieldnames!=colnames:error('Existing attraction CSV columns differ from patch; preserve current data and request a merge')
 additions=list(reader)
existingids={r['id'] for r in original}; existingnames={r['name'].casefold() for r in original}
new=[r for r in additions if r['id'] not in existingids and r['name'].casefold() not in existingnames]
merged=original+new
try:
 for r in merged:
  la,lo=float(r['lat']),float(r['lon'])
  assert 17.2<=la<=22.6 and -99.3<=lo<=-93.2
  assert r['id'] and r['name'] and r['source_url'].startswith('https://')
  assert r['status'] in {'mapped_site','mapped_area','entrance_verified'}
  assert r['icon'] in {'🏛️','🏰','🌊','💧','🌿','☕','🎨','🏖️','🌸','🗿','🏞️','🐦','⛵','🎭'}
  assert not r['photo_url'] or (r['photo_credit'] and r['photo_source_url'])
 assert len({r['id'] for r in merged})==len(merged)
except (ValueError,AssertionError) as e:error('Cannot validate merged attraction data: '+str(e))
fc={'type':'FeatureCollection','name':'Veracruz named geographic features, not necessarily entrances','features':[
 {'type':'Feature','id':r['id'],'geometry':{'type':'Point','coordinates':[float(r['lon']),float(r['lat'])]},'properties':{**{k:v for k,v in r.items() if k not in ['lat','lon']},'mapping_status':r['status'],'attraction_name_original':r['name']}} for r in merged]}
with (SRC/'assets/tourism_catalog.json').open(encoding='utf-8') as f:
 cat=json.load(f)
if len(cat['records'])!=495:error('Catalog manifest does not contain expected 495 recovered source records')
newhtml=re.sub(r'(src=["\']js/map-attractions\.js)(?:\?[^"\']*)?(["\'])',r'\g<1>?v=20261018-fullcatalog1\2',html)
newhtml=re.sub(r'(href=["\']css/map-attractions\.css)(?:\?[^"\']*)?(["\'])',r'\g<1>?v=20261018-fullcatalog1\2',newhtml)
changes={p:source.read_bytes() for p,source in TARGETS.items() if not p.is_file() or p.read_bytes()!=source.read_bytes()}
if new:
 from io import StringIO
 s=StringIO();w=csv.DictWriter(s,fieldnames=colnames,lineterminator='\n');w.writeheader();w.writerows(merged)
 changes[CSV]=('\ufeff'+s.getvalue()).encode('utf-8')
 changes[GEO]=(json.dumps(fc,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
if newhtml!=html:changes[INDEX]=newhtml.encode('utf-8')
if not changes:
 print('Already installed. Existing data unchanged. Mapped attractions:',len(merged),'Catalog records:',len(cat['records']))
 sys.exit(0)
backup=SITE/('.full-catalog-backup-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f'))
backup.mkdir(parents=True,exist_ok=False)
for dst in changes:
 if dst.exists():
  safe=backup/dst.relative_to(ROOT);safe.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,safe)
for dst,value in changes.items():
 dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(value)
print('SUCCESS:',len(merged),'real coordinate markers (',len(new),'new ) +',len(cat['records']),'source records indexed.')
print('Backup:',backup)
print('Existing municipality records, research SQLite, and current descriptions preserved.')
print('Open the homepage and search for Castillo de Teayo, Cuyuxquihui, Finca Siete Lunas, etc.')
