#!/usr/bin/env python3
"""Validate the editable attraction CSV and export GeoJSON consumed by the existing map.
No network access. Does not alter the original research database.
"""
import csv,json,math,sys
from pathlib import Path
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
SOURCE=ROOT/'site/data/attractions.csv'
DEST=ROOT/'site/data/attractions.geojson'
COLUMNS=['id','name','lat','lon','type','icon','status','source_url','source_provider','municipality','description_en','description_es','details_en','details_es','visit_note_en','visit_note_es','photo_url','photo_credit','photo_source_url']
ALLOWED_ICONS={'🏛️','🏰','🌊','💧','🌿','☕','🎨','🏖️','🌸','🗿','🏞️','🐦','⛵','🎭'}
ALLOWED_STATUSES={'mapped_site','mapped_area','entrance_verified'}

def build():
    if not SOURCE.is_file(): raise ValueError(f'Missing {SOURCE}')
    rows=[]; errors=[]; ids=set()
    with SOURCE.open(encoding='utf-8-sig',newline='') as file:
        reader=csv.DictReader(file)
        if reader.fieldnames!=COLUMNS: raise ValueError(f'CSV columns changed. Expected: {", ".join(COLUMNS)}')
        for line,r in enumerate(reader,start=2):
            try:
                p={k:(v or '').strip() for k,v in r.items()}
                if not p['id'] or p['id'] in ids: raise ValueError('empty or duplicate id')
                ids.add(p['id'])
                if not p['name']: raise ValueError('missing name')
                lat,lon=float(p['lat']),float(p['lon'])
                if not math.isfinite(lat) or not math.isfinite(lon) or not(17.2<=lat<=22.6 and -99.3<=lon<=-93.2): raise ValueError('coordinates outside approximate Veracruz range')
                if p['status'] not in ALLOWED_STATUSES: raise ValueError('invalid status')
                if p['icon'] not in ALLOWED_ICONS: raise ValueError('icon outside approved list')
                if not p['source_url'].startswith('https://'): raise ValueError('source_url must be https')
                for k in ('photo_url','photo_source_url'):
                    if p[k] and not p[k].startswith('https://'): raise ValueError(f'{k} must be https')
                if p['photo_url'] and (not p['photo_credit'] or not p['photo_source_url']): raise ValueError('photo requires credit and Commons source')
                props={k:v for k,v in p.items() if k not in ('lat','lon')}
                props['attraction_name_original']=p['name']
                props['mapping_status']=p['status']
                rows.append({'type':'Feature','id':p['id'],'geometry':{'type':'Point','coordinates':[lon,lat]},'properties':props})
            except (ValueError,TypeError) as e: errors.append(f'Row {line}: {e}')
    if errors: raise ValueError('\n'.join(errors))
    if not rows: raise ValueError('No attractions')
    fc={'type':'FeatureCollection','name':'Veracruz named attraction catalog: site/area coordinates, not always entrances','features':rows}
    DEST.parent.mkdir(parents=True,exist_ok=True)
    temporary=DEST.with_suffix('.geojson.tmp')
    temporary.write_text(json.dumps(fc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    temporary.replace(DEST)
    print(f'OK: {len(rows)} named attractions written to {DEST}. No research database modified.')
    return len(rows)
if __name__=='__main__':
    try: build()
    except Exception as exc: print('STOP: '+str(exc),file=sys.stderr);sys.exit(1)
