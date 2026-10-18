#!/usr/bin/env python3
"""Safe UI patch, generated from the latest marker repair and no data changes."""
from pathlib import Path
from datetime import datetime
import hashlib, shutil, re, sys
HERE=Path(__file__).resolve().parent
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd().resolve()
FILES=[('js/map-explorer.js', 'a1457bccc18923128a1824d4ca97a92e535dfda6976227460bdb3ab11b6ca24a', '2a9ec78342a4d8bfcb1f1b4988105024dd79b2d5e6a0d95b772a5f329e8a357e'), ('css/map-explorer.css', '881ecc353de32a7f8aa3135498fc01de5fb6e86eda5239b4f55cec63e01370e3', '32d2c47e70480bd7bb0ba356acb647cabd94ecd7d4a28e07891059decae19903')]
STAMP='20261018-visible-markers-v1'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    changes=[]
    for name,old,new in FILES:
        dst=ROOT/'site'/name
        src=HERE/'patch'/'site'/name
        if not dst.is_file() or not src.is_file(): sys.exit('Missing map file: '+str(dst))
        if sha(src)!=new:sys.exit('Patch archive checksum mismatch: '+name)
        actual=sha(dst)
        if actual==new:continue
        if actual!=old:sys.exit('STOP: '+name+' differs from the latest marker patch; no changes made. Send the current files rather than overwrite newer work.')
        changes.append((dst,src))
    html=ROOT/'site/index.html'
    if not html.is_file():sys.exit('site/index.html missing')
    original=html.read_text(encoding='utf-8')
    updated=original
    for asset in ('css/map-explorer.css','js/map-explorer.js'):
        pattern=r'(?P<before>(?:href|src)=["\']'+re.escape(asset)+r')(?P<query>\?[^"\']*)?(?P<after>["\'])'
        updated,n=re.subn(pattern,lambda m:m.group('before')+'?v='+STAMP+m.group('after'),updated)
        if n<1:sys.exit('No site reference for '+asset+'; no files changed')
    if not changes and updated==original:
        print('Already installed. Nothing changed.');return
    tag=datetime.now().strftime('%Y%m%d_%H%M%S')
    for dst,src in changes:
        backup=dst.with_name(dst.name+'.before-marker-ui-'+tag)
        shutil.copy2(dst,backup);shutil.copy2(src,dst)
        print('Updated '+str(dst))
    if updated!=original:
        backup=html.with_name('index.before-marker-ui-'+tag+'.html')
        shutil.copy2(html,backup);html.write_text(updated,encoding='utf-8')
        print('Updated index.html asset versions to avoid stale cached styles')
    print('Done. No catalog, coordinates or recovered descriptions changed.')
if __name__=='__main__':main()
