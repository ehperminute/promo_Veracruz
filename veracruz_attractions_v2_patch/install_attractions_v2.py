#!/usr/bin/env python3
"""Idempotent, backup-first attraction overlay upgrade for existing Veracruz homepage."""
from pathlib import Path
from datetime import datetime,timezone
import shutil,re,sys,subprocess
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd().resolve()
HERE=Path(__file__).resolve().parent
SITE=ROOT/'site';INDEX=SITE/'index.html';BASEJS=SITE/'js/map-explorer.js'
TARGETS={
 SITE/'js/map-attractions.js':HERE/'assets/map-attractions.js',
 SITE/'css/map-attractions.css':HERE/'assets/map-attractions.css',
 SITE/'data/attractions.csv':HERE/'assets/attractions.csv',
 SITE/'data/attractions.geojson':HERE/'assets/attractions.geojson',
 ROOT/'tools/build_attractions.py':HERE/'tools/build_attractions.py',
}
def stop(why):raise SystemExit('STOP: '+why+' (no files changed)')
if not INDEX.is_file() or not BASEJS.is_file():stop('Run inside the promo_Veracruz repository root.')
for src in TARGETS.values():
 if not src.is_file():stop('Patch package incomplete: '+str(src))
s=INDEX.read_text(encoding='utf-8')
if '</body>' not in s:stop('index.html has no </body>')
if not re.search(r'<script\b[^>]*src=["\']js/map-explorer\.js',s):stop('Homepage does not load map-explorer.js')
# Existing installation must have exposed the MapLibre map instance. Do not patch unknown JS.
if 'window.__vx_attraction_map = mapObject;' not in BASEJS.read_text(encoding='utf-8'):
 stop('The existing base map has no __vx_attraction_map instance. Install the preceding attractions patch first, or share this file to merge.')
# Remove only the old attraction addon <script> and <link>, not other site tags.
new=re.sub(r'(?m)^\s*<script\b[^>]*src=["\']js/map-attractions\.js(?:\?[^"\']*)?["\'][^>]*></script>\s*\n?', '\n',s)
new=re.sub(r'(?m)^\s*<link\b[^>]*href=["\']css/map-attractions\.css(?:\?[^"\']*)?["\'][^>]*>\s*\n?', '\n',new)
insert='\n<link rel="stylesheet" href="css/map-attractions.css?v=20261018-v2">\n<script defer src="js/map-attractions.js?v=20261018-v2"></script>\n'
new=new.replace('</body>',insert+'</body>',1)
if new.count('js/map-attractions.js')!=1:stop('Attraction script duplication risk in homepage')
changes=[(p,src.read_bytes()) for p,src in TARGETS.items() if not p.is_file() or p.read_bytes()!=src.read_bytes()]
if new!=s:changes.append((INDEX,new.encode('utf-8')))
if not changes:
 print('Already up to date.');sys.exit(0)
backup=SITE/('.attractions-backup-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f'))
backup.mkdir(parents=True,exist_ok=False)
for dest,_ in changes:
 if dest.exists():
  saved=backup/dest.relative_to(ROOT)
  saved.parent.mkdir(parents=True,exist_ok=True)
  shutil.copy2(dest,saved)
for dest,content in changes:
 dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_bytes(content)
print('INSTALLED:',len(TARGETS),'attraction files; backup:',backup)
print('Now:',len(__import__('json').loads((SITE/'data/attractions.geojson').read_text())['features']),'named attraction markers.')
print('Edit site/data/attractions.csv and rebuild: python tools/build_attractions.py .')
