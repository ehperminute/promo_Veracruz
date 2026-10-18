#!/usr/bin/env python3
"""Install visitor-facing map names and source-first guide copy, conservatively."""
from pathlib import Path
from datetime import datetime
import hashlib,sys,shutil,re
HERE=Path(__file__).resolve().parent
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd().resolve()
BASE_HASHES={'site/js/map-explorer.js': '2a9ec78342a4d8bfcb1f1b4988105024dd79b2d5e6a0d95b772a5f329e8a357e', 'site/css/map-explorer.css': '32d2c47e70480bd7bb0ba356acb647cabd94ecd7d4a28e07891059decae19903'}
NEW_HASHES={'site/js/map-explorer.js': '6b62ca462411b08fd2400c3008be746483871987c7977fc2c6c3913837f8fad3', 'site/css/map-explorer.css': 'a9c928f4d0a8f988f344937741e57dad2f26dcd0ccfece2fea23ad046b8346a0', 'site/data/map_editorial_notes.json': '909870e30a1cdc98df3217f4234130cb8163dd02e97b75425bb4644883ec1ef5'}
FILES=['site/js/map-explorer.js', 'site/css/map-explorer.css', 'site/data/map_editorial_notes.json']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
  checks=[]
  for rel in FILES:
    src=HERE/'patch'/rel;dst=ROOT/rel
    if not src.exists():sys.exit('Missing patch asset: '+str(src))
    if sha(src)!=NEW_HASHES[rel]:sys.exit('Corrupted patch asset: '+rel)
    if rel not in BASE_HASHES:
      if dst.exists() and sha(dst)!=NEW_HASHES[rel]:sys.exit('Existing custom editorial data: '+str(dst)+'; not overwriting it.')
    elif not dst.is_file() or sha(dst) not in (BASE_HASHES[rel],NEW_HASHES[rel]):
      sys.exit('STOP: '+str(dst)+' differs from the latest map patch. No changes were made. Upload the current map JS/CSS for a safe merge.')
    checks.append((rel,src,dst))
  index=ROOT/'site/index.html'
  if not index.is_file():sys.exit('Missing site/index.html')
  html=index.read_text(encoding='utf8')
  updated=html
  for asset in ('css/map-explorer.css','js/map-explorer.js'):
    pattern=r'(?P<left>(?:href|src)=[\"\']'+re.escape(asset)+r')(?P<q>\?[^\"\']*)?(?P<right>[\"\'])'
    updated,n=re.subn(pattern,lambda m:m.group('left')+'?v=20261018-labels-guides-v1'+m.group('right'),updated)
    if n<1:sys.exit('Missing map asset reference in HTML: '+asset)
  if all(dst.exists() and sha(dst)==NEW_HASHES[rel] for rel,src,dst in checks) and html==updated:
    print('Already installed');return
  stamp=datetime.now().strftime('%Y%m%d-%H%M%S')
  backup=ROOT/('site/.before-tourist-guide-'+stamp)
  backup.mkdir()
  for rel,src,dst in checks:
    if dst.exists():shutil.copy2(dst,backup/dst.name)
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,dst)
  if updated!=html:
    shutil.copy2(index,backup/'index.html');index.write_text(updated,encoding='utf8')
  print('Installed map labels and visitor guides. Backup:',backup)
  print('No existing catalog, coordinates, photos, recovered descriptions or SQLite database was modified.')
if __name__=='__main__':main()
