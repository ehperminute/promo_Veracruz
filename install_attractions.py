#!/usr/bin/env python3
"""Add attraction markers and attraction search to the existing Veracruz homepage.
Does not alter the municipality data, tourism descriptions or project database.
Run from promo_Veracruz repo root after extracting the zip.
"""
from pathlib import Path
from datetime import datetime
import re, sys, shutil, json, hashlib
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd().resolve()
HERE=Path(__file__).resolve().parent
INDEX=ROOT/'site/index.html'
JS=ROOT/'site/js/map-explorer.js'
TARGETS={
  ROOT/'site/js/map-attractions.js':HERE/'assets/js/map-attractions.js',
  ROOT/'site/css/map-attractions.css':HERE/'assets/css/map-attractions.css',
  ROOT/'site/data/attractions_batch1.geojson':HERE/'assets/data/attractions_batch1.geojson',
}

def fail(message): raise SystemExit('STOP (no files changed): '+message)
if not INDEX.is_file() or not JS.is_file():fail('Run in the promo_Veracruz repository root, with site/index.html and site/js/map-explorer.js present.')
for dest,src in TARGETS.items():
    if not src.is_file():fail('Missing patch asset: '+str(src))
    if dest.exists() and dest.read_bytes()!=src.read_bytes():fail('Existing custom file differs; preserve it and request a merge: '+str(dest))
fc=json.loads((HERE/'assets/data/attractions_batch1.geojson').read_text(encoding='utf-8'))
if len(fc.get('features',[]))!=18:fail('Attraction GeoJSON must contain 18 researched points.')
if not all(any(f['properties']['attraction_name_original']==name for f in fc['features']) for name in ('El Tajín','Quiahuiztlán')):fail('Missing critical attraction names.')
original=JS.read_text(encoding='utf-8')
if 'window.__vx_attraction_map = mapObject;' not in original:
    anchor='if(mapObject){'
    if original.count(anchor)<1 or not re.search(r'const\s+mapObject\s*=',original):fail('Cannot find existing MapLibre object. JS unchanged; request a merge.')
    revised=original.replace(anchor,'window.__vx_attraction_map = mapObject;\n'+anchor,1)
else: revised=original
html=INDEX.read_text(encoding='utf-8')
if '</body>' not in html:fail('index.html has no closing </body>.')
# The latest map code executes as a deferred script: insert this after the base map script.
if not re.search(r'<script\b[^>]*src=["\']js/map-explorer\.js(?:\?[^"\']*)?["\']',html):fail('Homepage does not reference js/map-explorer.js. No files changed.')
newhtml=html
if 'map-attractions.js' not in newhtml:
    snippet='\n<link rel="stylesheet" href="css/map-attractions.css?v=20261018-a1">\n<script defer src="js/map-attractions.js?v=20261018-a1"></script>\n'
    newhtml=newhtml.replace('</body>',snippet+'</body>',1)
# Refresh the main map JS path when making the one-time map-instance exposure change.
if revised!=original:
    newhtml=re.sub(r'(?<=src=")js/map-explorer\.js(?:\?[^"\s]*)?(?=")','js/map-explorer.js?v=20261018-attractions-v1',newhtml)
    newhtml=re.sub(r"(?<=src=')js/map-explorer\.js(?:\?[^'\s]*)?(?=')",'js/map-explorer.js?v=20261018-attractions-v1',newhtml)
if revised==original and newhtml==html and all(dest.exists() for dest in TARGETS):
    print('Already installed: attraction layer and search.');sys.exit(0)
backup=ROOT/('site/.before-attractions-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True,exist_ok=True)
if revised!=original:
    shutil.copy2(JS,backup/'map-explorer.js')
    JS.write_text(revised,encoding='utf-8')
if newhtml!=html:
    shutil.copy2(INDEX,backup/'index.html')
    INDEX.write_text(newhtml,encoding='utf-8')
for dest,src in TARGETS.items():
    if not dest.exists():
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,dest)
print('SUCCESS: installed 18 attraction locations + search into the existing Veracruz map.')
print('Try "El Tajín" or "Quiahuiztlán" in the map search box, or use the Mapped attractions list.')
print('Backup:',backup)
print('The municipality GeoJSON, original tourist descriptions, and SQLite database were not changed.')
