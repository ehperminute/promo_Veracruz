#!/usr/bin/env python3
"""Safely append 7 independently mapped features to Veracruz site's editable attraction data.
NOT road entrances. Does not touch any SQLite/CSV source evidence, nor JS/CSS.
Usage: python VERACRUZ_GEOGRAPHY_COURSE_RESULTS_2026-10-18/install_verified_points.py .
"""
from pathlib import Path
import sys,csv,json,io,shutil,datetime,unicodedata,math
HERE=Path(__file__).resolve().parent
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd()
CSV=ROOT/'site/data/attractions.csv';GEO=ROOT/'site/data/attractions.geojson'
ADD=HERE/'new_verified_map_sites.csv'
def norm(x):return ''.join(c for c in unicodedata.normalize('NFKD',x.lower()) if not unicodedata.combining(c)).replace('"','').replace("'",'')
def near(a,b):
 lat1,lon1,lat2,lon2=map(float,[a['lat'],a['lon'],b['lat'],b['lon']]);return math.hypot((lat1-lat2)*111,(lon1-lon2)*106)<0.35

def main():
 if not CSV.is_file():raise RuntimeError(f'Expected editable catalog missing: {CSV}')
 with CSV.open(encoding='utf-8-sig',newline='') as f:
  rd=csv.DictReader(f);columns=rd.fieldnames;existing=list(rd)
 with ADD.open(encoding='utf-8-sig',newline='') as f: additional=list(csv.DictReader(f))
 if not columns or any(k not in columns for k in additional[0]):raise RuntimeError('Attraction CSV columns do not match this patch. No changes made.')
 if not GEO.is_file():
  raise RuntimeError('Existing GeoJSON file missing: '+str(GEO)+'; no changes made (prevents dropping earlier map points).')
 obj=json.loads(GEO.read_text(encoding='utf-8'))
 assert obj.get('type')=='FeatureCollection' and isinstance(obj.get('features'),list),'GeoJSON structure unexpected'
 present_ids={r['id'] for r in existing};features_ids={f.get('id') for f in obj['features']};added=[];skipped=[]
 for r in additional:
  if not(17.2<=float(r['lat'])<=22.6 and -99.3<=float(r['lon'])<=-93.2):raise RuntimeError('New coordinate outside plausible Veracruz bounds')
  matches=[e for e in existing if e['id']==r['id'] or (near(e,r) and (norm(e['name'])==norm(r['name']) or norm(e['name']) in norm(r['name']) or norm(r['name']) in norm(e['name'])))]
  if matches:skipped.append((r['name'],matches[0]['name']));continue
  if r['id'] in present_ids:raise RuntimeError('Unresolved duplicate id '+r['id'])
  added.append(r)
 # Existing geojson could be stale, compare consistency of known ids but do not discard data.
 for r in added:
  obj['features'].append({'type':'Feature','id':r['id'],'geometry':{'type':'Point','coordinates':[float(r['lon']),float(r['lat'])]},'properties':{k:v for k,v in r.items() if k not in ('lat','lon')}})
 if not added:
  print('ALREADY PRESENT — no records changed.');return
 buf=io.StringIO(newline='');wr=csv.DictWriter(buf,fieldnames=columns,lineterminator='\n');wr.writeheader();wr.writerows(existing+added)
 # Backups immediately before atomic replaces, no working database changed.
 stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
 for file in [CSV,GEO]:
  if file.exists():shutil.copy2(file,file.with_name(file.name+'.before-vx14-'+stamp))
 tmp=CSV.with_suffix('.csv.vx14.tmp');tmp.write_text(buf.getvalue(),encoding='utf-8-sig')
 tmp_geo=GEO.with_suffix('.geojson.vx14.tmp');tmp_geo.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 tmp.replace(CSV);tmp_geo.replace(GEO)
 print(f'OK: {len(added)} new attractions mapped; {len(skipped)} already present; prior catalog rows preserved.')
 print(f'Updated: {CSV} and {GEO}. Restart server NOT needed; reload browser.')
 print('IMPORTANT: These are mapped site/area reference points, not verified visitor entrances.')
if __name__=='__main__':
 try: main()
 except Exception as e:print('STOP — '+str(e),file=sys.stderr);sys.exit(1)
