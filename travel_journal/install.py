#!/usr/bin/env python3
"""Small additive GitHub Pages installer; preserves current site and source datasets."""
from pathlib import Path
import shutil
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
SITE = ROOT/'site'
INDEX = SITE/'index.html'
SRC=Path(__file__).resolve().parent/'site'
if not INDEX.exists():
    raise SystemExit('Run at your repo root; missing site/index.html')
for rel in ['viajes.html','js/trip-journal-core.js','js/trip-journal.js','js/trip-journal-bridge.js','css/trip-journal.css']:
    dest=SITE/rel
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(SRC/rel,dest)
html=INDEX.read_text(encoding='utf8')
marker='<!-- VERACRUZ-TRIP-JOURNAL-V1 -->'
if marker not in html:
    if '</body>' not in html:raise SystemExit('Unexpected index: no </body>')
    block=marker+'\n<script defer src="js/trip-journal-core.js?v=1"></script>\n<script defer src="js/trip-journal-bridge.js?v=1"></script>\n'
    html=html.replace('</body>',block+'</body>',1)
    # Static navigation also works when the map is unavailable.
    if '</nav>' in html:
        html=html.replace('</nav>','<a href="viajes.html">Viajes compartidos / Shared trips</a>\n</nav>',1)
    INDEX.write_text(html,encoding='utf8')
print('Trip journal installed. No data collection service or public user records created.')
