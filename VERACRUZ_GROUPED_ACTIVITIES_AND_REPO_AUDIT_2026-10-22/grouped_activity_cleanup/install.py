#!/usr/bin/env python3
"""Idempotently install current-data grouped photo activity explorer; do not touch DB."""
import argparse, json, re, shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent

def apply(repo):
    repo=repo.resolve()
    site=repo/'site';index=site/'index.html'
    evidence=site/'data/interest_evidence.json'
    if not index.exists() or not evidence.exists():
        raise SystemExit('Expected current static Veracruz site/data/interest_evidence.json')
    live=json.loads(evidence.read_text(encoding='utf8'))
    grouped=json.loads((HERE/'site/data/activity_sections.json').read_text(encoding='utf8'))
    current={(r['municipality_id'],r['feature_id']) for r in live['records']}
    frozen={(m['municipality_id'],a['feature_id']) for s in grouped['sections'] for a in s['activities'] for m in a['municipalities']}
    if len(live['records'])!=216 or current!=frozen:
        raise SystemExit('Source evidence changed: refuse to overwrite with stale activity sections. Rebuild sections from the latest data.')
    for rel in ('js/activity-groups.js','css/activity-groups.css','data/activity_sections.json'):
        target=site/rel;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(HERE/'site'/rel,target)
    text=index.read_text(encoding='utf8')
    # Remove only obsolete 78-card tags; do not remove our own tags on a reinstall.
    text=re.sub(r'<script\b[^>]*src="js/activity-explorer\.js[^>]*></script>', '',text)
    text=re.sub(r'<link\b[^>]*href="css/activity-explorer\.css[^>]*>', '',text)
    if 'id="vx-activities"' not in text:
        marker='<section id="veracruz-map-section"'
        if marker not in text:raise SystemExit('Expected map section is missing: do not modify HTML automatically.')
        text=text.replace(marker,'<section id="vx-activities" aria-label="Experiencias documentadas en Veracruz"></section>\n        '+marker,1)
    if 'id="nav-activities"' not in text:
        pattern='<a href="#veracruz-map-section"'
        if pattern in text:text=text.replace(pattern,'<a href="#vx-activities" id="nav-activities">Actividades</a>\n      '+pattern,1)
    if 'css/activity-groups.css' not in text:
        text=text.replace('</head>','  <link rel="stylesheet" href="css/activity-groups.css?v=2">\n</head>',1)
    if 'js/activity-groups.js' not in text:
        text=text.replace('</body>','  <script defer src="js/activity-groups.js?v=2"></script>\n</body>',1)
    index.write_text(text,encoding='utf8')
    print('Installed 8 activity sections (78 types, 216 evidence links) and curated Commons photographs.')
    print('Preserved old activity script, research files, SQLite and route-planner internals.')
    print('Remote Commons images require an Internet connection in the browser.')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('repo',nargs='?',default='.');args=ap.parse_args();apply(Path(args.repo))
