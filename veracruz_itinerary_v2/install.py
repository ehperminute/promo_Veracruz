#!/usr/bin/env python3
"""Replace BOTH competing route widgets with one UI; keep data and old source scripts untouched."""
import re, shutil
from pathlib import Path

root=Path(__file__).resolve().parents[1]
site=root/'site'; page=site/'index.html'
assert page.is_file(),f'Not a repo with site/index.html: {root}'
text=page.read_text(encoding='utf-8')
if 'js/itinerary-router.js' in text:
    print('Already installed: no changes to index.html')
else:
    shutil.copy2(page,site/'index.html.before-itinerary-v2')
    # Unhook legacy 5.6 MB regional planner and the four-dropdown pilot. Preserve source files.
    text,n1=re.subn(r'<script\b[^>]*\bsrc=["\'][^"\']*\bjs/route-planner\.js[^"\']*["\'][^>]*>\s*</script>', '',text)
    text,n2=re.subn(r'<script\b[^>]*\bsrc=["\'][^"\']*\bjs/statewide-route\.js[^"\']*["\'][^>]*>\s*</script>', '',text)
    text=re.sub(r'<link\b[^>]*\bhref=["\'][^"\']*\bcss/(?:route-planner|statewide-route)\.css[^"\']*["\'][^>]*>', '',text)
    if n1!=1:
        print('NOTE: regional route script not found exactly once; found',n1)
    if n2!=1:
        print('NOTE: prior statewide preview script not found exactly once; found',n2)
    assert '</head>' in text and '</body>' in text
    text=text.replace('</head>','<link rel="stylesheet" href="css/itinerary-router.css?v=2">\n</head>',1)
    text=text.replace('</body>','<script defer src="js/itinerary-router.js?v=2"></script>\n</body>',1)
    page.write_text(text,encoding='utf-8')
# Give existing attraction markers an exact ID so two equally named attractions
# in different municipalities cannot be confused during map selection.
markers=site/'js/map-attractions.js'
if markers.is_file():
    m=markers.read_text(encoding='utf-8')
    anchor='e.title=p.name;'
    if 'e.dataset.vxPlaceId' not in m and anchor in m:
        shutil.copy2(markers,site/'js/map-attractions.js.before-itinerary-v2')
        markers.write_text(m.replace(anchor,anchor+'e.dataset.vxPlaceId=String(p.id||f.id);',1),encoding='utf-8')
        print('Tagged existing attraction marker elements with stable IDs (tourism data unchanged).')
    elif 'e.dataset.vxPlaceId' not in m:
        print('NOTE: attraction marker source layout changed. Name-based fallback only.')
for fn,folder in [('itinerary-router.js','js'),('itinerary-router.css','css')]:
    target=site/folder/fn;target.parent.mkdir(exist_ok=True,parents=True)
    shutil.copy2(Path(__file__).parent/'assets'/fn,target)
print('Installed unified planner. Previous regional graph and routing scripts remain on disk, but are no longer loaded.')
print('Run: python -m http.server 8000 -d site')
print('If inline OSRM fails, the itinerary can still open driving directions for all points in Google Maps.')
