#!/usr/bin/env python3
"""Idempotently install activity explorer into an existing static Veracruz site."""
import argparse
import shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent

def install(repo: Path):
    repo=repo.resolve()
    site=repo/'site'
    htmlfile=site/'index.html'
    if not htmlfile.exists() or not (site/'data/interest_evidence.json').exists():
        raise SystemExit('Missing Veracruz site or evidence export. Install the unified current site first.')
    for rel in ['js/activity-explorer.js','css/activity-explorer.css','data/activity_cards.json']:
        src=HERE/'site'/rel
        dest=site/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,dest)
    target=site/'assets/activity-illustrations'
    target.mkdir(parents=True,exist_ok=True)
    for file in (HERE/'site/assets/activity-illustrations').glob('*.svg'):
        shutil.copy2(file,target/file.name)
    html=htmlfile.read_text(encoding='utf-8')
    style='<link rel="stylesheet" href="css/activity-explorer.css?v=1">'
    script='<script defer src="js/activity-explorer.js?v=1"></script>'
    main_marker='<section id="veracruz-map-section"'
    if style not in html:
        html=html.replace('</head>',f'  {style}\n</head>',1)
    if script not in html:
        html=html.replace('</body>',f'  {script}\n</body>',1)
    if 'id="vx-activities"' not in html:
        if main_marker not in html:
            raise SystemExit('Cannot locate current map section; site layout differs from tested version.')
        html=html.replace(main_marker,'<section id="vx-activities" aria-label="Documented Veracruz activities"></section>\n\n        '+main_marker,1)
    if 'id="nav-activities"' not in html:
        i=html.find('<a href="#veracruz-map-section"')
        if i>=0:
            html=html[:i]+'<a href="#vx-activities" id="nav-activities">Actividades / Activities</a>\n      '+html[i:]
    htmlfile.write_text(html,encoding='utf-8')
    print('Installed 78 individual activity cards on homepage; no cluster code re-enabled.')
    print('Content: 216 strict documented municipality/activity links; generated illustrations + three source-linked sample photographs.')
    print('Note: media is shown from static assets; SQLite BLOBs do not auto-render on GitHub Pages.')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('repo',nargs='?',default='.')
    install(Path(parser.parse_args().repo))
if __name__=='__main__':main()
