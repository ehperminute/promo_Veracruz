#!/usr/bin/env python3
"""Safe, version-aware repair for map markers; leaves catalog and data alone."""
from pathlib import Path
from datetime import datetime
import hashlib, shutil, sys
HERE=Path(__file__).resolve().parent
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd().resolve()
FILES=[
  ("site/js/map-explorer.js", "73bd717fef93ef9dcddeefd832847f4f6d87cb33a3833f254668ab65f1664bcd", "a1457bccc18923128a1824d4ca97a92e535dfda6976227460bdb3ab11b6ca24a"),
  ("site/css/map-explorer.css", "f172ec537a336bfc75110619c08b2e8562e812ef62cb821e3136b4ceaf4847e5", "881ecc353de32a7f8aa3135498fc01de5fb6e86eda5239b4f55cec63e01370e3"),
]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
  pending=[]
  for name,before,after in FILES:
    dst=ROOT/name;src=HERE/'patch'/name
    if not dst.is_file():sys.exit(f"ERROR: Missing {dst}; run from the promo_Veracruz root.")
    actual=sha(dst)
    if actual==after:continue
    if actual!=before:sys.exit(f"ERROR: {name} changed since your diagnostic upload. No files changed. Send the newest file instead of overwriting your edits.")
    if sha(src)!=after:sys.exit(f"ERROR: patch archive damaged: {name}.")
    pending.append((dst,src))
  if not pending:
    print('Marker fix already installed; no changes.');return
  ts=datetime.now().strftime('%Y%m%d_%H%M%S')
  for dst,src in pending:
    backup=dst.with_name(dst.name+'.before-marker-repair-'+ts)
    shutil.copy2(dst,backup);shutil.copy2(src,dst)
    print(f'Updated {dst}; backup: {backup.name}')
  print('DONE: geographic markers now use MapLibre Marker objects. Data and guides were not modified.')
  print('Refresh your site (and try a private tab if the previous JS is cached).')
if __name__=='__main__':main()
