#!/usr/bin/env python3
"""Idempotent, additive: requires the existing trip journal installed first."""
from pathlib import Path
import shutil, sys
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd()
site=root/'site'
src=Path(__file__).resolve().parent/'site'
page=site/'viajes.html'
if not page.exists() or not (site/'js/trip-journal-core.js').exists():
    raise SystemExit('Install the existing VERACRUZ_TRAVEL_JOURNAL_MVP first. Existing journal not found.')
files=['enviar-viaje.html','js/trip-gallery.js','js/trip-submission.js', 'css/trip-community.css','data/trip_examples.json']
for rel in files:
    dest=site/rel; dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src/rel,dest)
for rel in ['data/community_trips.json','data/trip_submission_config.json']:
    dest=site/rel;dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.exists():shutil.copyfile(src/rel,dest)
html=page.read_text(encoding='utf8')
marker='<!-- VX-COMMUNITY-TRIPS-V1 -->'
if marker not in html:
    if '</head>' not in html or '<main class="tj-main">' not in html:
        raise SystemExit('Unexpected journal markup')
    html=html.replace('</head>','<link rel="stylesheet" href="css/trip-community.css">\n<script defer src="js/trip-gallery.js"></script>\n</head>',1)
    html=html.replace('<main class="tj-main">','<main class="tj-main">\n'+marker+'\n<section id="vx-trip-gallery" aria-label="Rutas compartidas y de ejemplo"></section>',1)
    page.write_text(html,encoding='utf8')
print('Community trip gallery and submission interface installed; existing published stories preserved.')
