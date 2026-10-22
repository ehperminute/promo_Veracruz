#!/usr/bin/env python3
"""Conservative audit for Veracruz repo; never deletes or rewrites files.
Optionally moves only UNTRACKED timestamped backup directories OUTSIDE the repository.
"""
import argparse, hashlib, json, os, re, shutil, subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

BACKUP_PATTERN=re.compile(r'^(?:\.before[-_]|\.backup[-_]|\.local-backup[-_]|\.local-site-backup[-_]|veracruz_map_final_backup_)[\w.-]+$')
LEGACY_PATTERN=re.compile(r'^(?:VERACRUZ_(?:ROUTE|MAP|OVERPASS|BROWSER_ROUTE|FULL_CATALOG|GEOFABRIK)_|veracruz_(?:guide_route_fix|attractions_v2_patch|all_descriptions_patch)|patch$)',re.I)

def git_tracked(repo, subpath):
    if not (repo/'.git').exists():return None
    p=subprocess.run(['git','ls-files','--',str(subpath.relative_to(repo))],cwd=repo,capture_output=True,text=True)
    if p.returncode:return None
    return bool(p.stdout.strip())

def size_of(path):
    if path.is_file():return path.stat().st_size
    total=0
    for root,dirs,files in os.walk(path):
        dirs[:]=[d for d in dirs if d!='.git']
        for filename in files:
            try:total+=(Path(root)/filename).stat().st_size
            except OSError:pass
    return total

def main():
    ap=argparse.ArgumentParser(description='Non-destructive repository hygiene audit, plus optional quarantine of untracked timestamped backups.')
    ap.add_argument('repo',nargs='?',default='.')
    ap.add_argument('--quarantine-untracked-backups',action='store_true',help='Move only untracked timestamped backup directories outside the repo (never tracked files).')
    args=ap.parse_args();repo=Path(args.repo).resolve()
    if not (repo/'site/index.html').exists():raise SystemExit('Not a Veracruz repository root')
    roots=[]
    for item in repo.iterdir():
        if item.name=='.git':continue
        kind='snapshot_backup' if BACKUP_PATTERN.match(item.name) else 'historical_patch_or_experiment' if LEGACY_PATTERN.match(item.name) else 'active_or_unclassified'
        roots.append({'path':item.name,'bytes':size_of(item),'kind':kind,'tracked':git_tracked(repo,item)})
    roots.sort(key=lambda x:x['bytes'],reverse=True)
    # checksum duplicate files >= 0.5 MB; report only, never infer safe deletion from equal bytes.
    same=defaultdict(list)
    for folder in [repo/'data',repo/'site',repo/'outputs',repo/'VERACRUZ_GEOGRAPHY_COURSE_RESULTS_2026-10-18',repo/'veracruz_all_descriptions_patch']:
        if not folder.is_dir():continue
        for root,dirs,files in os.walk(folder):
            dirs[:]=[d for d in dirs if d not in {'__pycache__','.git'}]
            for fn in files:
                path=Path(root)/fn
                try:sz=path.stat().st_size
                except OSError:continue
                if sz<500_000 or sz>150_000_000:continue
                h=hashlib.sha256()
                try:
                    with open(path,'rb') as f:
                        while block:=f.read(4*1024*1024):h.update(block)
                    same[(sz,h.hexdigest())].append(str(path.relative_to(repo)))
                except OSError:continue
    duplicates=[{'size':size,'sha256':digest,'paths':names} for (size,digest),names in same.items() if len(names)>1]
    report={'generated_utc':datetime.now(timezone.utc).isoformat(),'repo':str(repo),'top_level':roots,
            'backup_candidates':[x for x in roots if x['kind']=='snapshot_backup'],
            'historical_patch_candidates':[x for x in roots if x['kind']=='historical_patch_or_experiment'],
            'exact_duplicates':duplicates,
            'policy':'No deletion of canonical DB, site, raw sources, tests, results or Git history. Classifications are candidates for human review, not proof of redundancy.'}
    out=repo.parent/(repo.name+'_cleanup_audit.json');out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('AUDIT:',out)
    print('Largest root entries:')
    for x in roots[:18]:print(f" {x['bytes']/2**20:8.1f} MiB  {x['path']:58s} {x['kind']}  git-tracked={x['tracked']}")
    print('Timestamped backups:',len(report['backup_candidates']),'exact duplicate groups:',len(duplicates))
    if args.quarantine_untracked_backups:
        outside=repo.parent/(repo.name+'_untracked_backups_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
        candidates=[x for x in report['backup_candidates'] if x['tracked'] is False]
        if candidates:
            outside.mkdir(exist_ok=False)
            for c in candidates:
                src=repo/c['path'];dest=outside/c['path'];shutil.move(str(src),str(dest))
                print('MOVED UNTRACKED BACKUP:',src,'->',dest)
        else:print('No untracked backups eligible for automatic quarantine (tracked/unknown items left alone).')

if __name__=='__main__':main()
