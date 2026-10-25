#!/usr/bin/env python3
"""Safely archive untracked root ZIPs; tracked ZIPs are never moved."""
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
import shutil
p=argparse.ArgumentParser()
p.add_argument('repo',nargs='?',default='.')
p.add_argument('--archive',action='store_true')
args=p.parse_args()
repo=Path(args.repo).resolve()
if not (repo/'.git').exists():raise SystemExit('Not a Git working tree. No changes made.')
r=subprocess.run(['git','ls-files','--cached','-z'],cwd=repo,stdout=subprocess.PIPE,check=True)
tracked={x.decode('utf-8','surrogateescape') for x in r.stdout.split(b'\0') if x}
files=sorted(x for x in repo.glob('*.zip') if x.is_file() and x.name not in tracked)
print(f'{len(files)} untracked root-level ZIPs ({sum(x.stat().st_size for x in files)/1048576:.1f} MiB)')
for x in files: print(' ',x.name)
if not args.archive:
 print('DRY RUN: use --archive to move only these files outside the repository.')
else:
 dest=repo.parent/('promo_Veracruz_archived_ZIPs_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
 dest.mkdir(exist_ok=True)
 for x in files:shutil.move(str(x),str(dest/x.name))
 print('Moved to:',dest)
print('Preserved: tracked files, research data, .git, and all non-root archives.')
