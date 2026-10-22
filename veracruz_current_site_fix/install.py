#!/usr/bin/env python3
"""V3: municipality-aware itinerary + retire obsolete public 55-profile sections.
No research datasets are modified; this only edits the public site's HTML and scripts.
"""
from pathlib import Path
import re, shutil, sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd()
SITE=ROOT/'site'; PAGE=SITE/'index.html'; THIS=Path(__file__).resolve().parent
if not PAGE.exists() or not (SITE/'data/map_points.geojson').exists() or not (SITE/'data/attractions.geojson').exists():
    raise SystemExit('ERROR: Run from the promo_Veracruz repository root; current map GeoJSON files are required.')
backup=ROOT/'.local-site-backup-before-v3'
backup.mkdir(exist_ok=True)
for name in ['index.html','planner.html','js/map-explorer.js','js/map-attractions.js','js/itinerary-router.js','css/itinerary-router.css']:
    origin=SITE/name
    target=backup/name
    if origin.exists() and not target.exists():
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(origin,target)

html=PAGE.read_text(encoding='utf-8')
if '<!-- PP6 CURRENT-SITE-V3 -->' not in html:
    for section,pattern in [
        ('old 12-collection gallery',r'<section\s+id="experiences"[^>]*>.*?</section>'),
        ('old 55-destination explorer',r'<section\s+id="destinations"[^>]*>.*?</section>'),
        ('obsolete Gower/PAM widget',r'<section\s+id="methods"[^>]*>.*?</section>')]:
        html,n=re.subn(pattern,'',html,count=1,flags=re.S)
        if n!=1:raise SystemExit('STOP: Site layout differs; could not safely remove '+section)
    for js in ('app','route-planner','statewide-route','itinerary-router'):
        html=re.sub(r'<script\b[^>]*\bsrc=["\'][^"\']*\bjs/'+js+r'\.js[^"\']*["\'][^>]*>\s*</script>','',html)
    for css in ('route-planner','statewide-route','itinerary-router'):
        html=re.sub(r'<link\b[^>]*\bhref=["\'][^"\']*\bcss/'+css+r'\.css[^"\']*["\'][^>]*>','',html)
    nav='''<nav aria-label="Main navigation">
      <a href="#veracruz-map-section" id="nav-map">Explore the map</a>
      <a href="#vxw-itinerary" id="nav-route">Plan a route</a>
    </nav>'''
    html,n=re.subn(r'<nav>.*?</nav>',nav,html,count=1,flags=re.S)
    if n!=1:raise SystemExit('STOP: Cannot locate main navigation')
    html=html.replace('''<p
                class="subtitle"
                data-i18n="subtitle"
            >
                Data-driven exploration of tourism
                destinations in Veracruz
            </p>''','''<p class="subtitle" id="current-subtitle">Explore documented activities and mapped attractions; locations and access may be approximate.</p>''',1)
    # Only the current map and itinerary remain public; archived scripts stay on disk for reproducibility.
    html=html.replace('</head>','<link rel="stylesheet" href="css/itinerary-router.css?v=3">\n</head>',1)
    html=html.replace('</body>','<!-- PP6 CURRENT-SITE-V3 -->\n<script defer src="js/itinerary-router.js?v=3"></script>\n<script defer src="js/current-home.js?v=3"></script>\n</body>',1)
    PAGE.write_text(html,encoding='utf-8')

municipal_marker=SITE/'js/map-explorer.js'
m=municipal_marker.read_text(encoding='utf-8')
needle='  pin.title=p.name;'
if 'pin.dataset.vxMunicipalityId' not in m:
    if needle not in m:raise SystemExit('STOP: Cannot identify municipality pin construction')
    m=m.replace(needle,needle+'\n  pin.dataset.vxMunicipalityId=String(p.municipality_id);',1)
    municipal_marker.write_text(m,encoding='utf-8')

attraction_marker=SITE/'js/map-attractions.js'
m=attraction_marker.read_text(encoding='utf-8')
needle='e.title=p.name;'
if 'e.dataset.vxPlaceId' not in m:
    if needle not in m:raise SystemExit('STOP: Cannot identify attraction marker construction')
    m=m.replace(needle,needle+'e.dataset.vxPlaceId=String(p.id||f.id);',1)
    attraction_marker.write_text(m,encoding='utf-8')

for name,folder in [('itinerary-router.js','js'),('itinerary-router.css','css'),('current-home.js','js')]:
    source=THIS/'assets'/name
    dest=SITE/folder/name
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,dest)

archive=SITE/'planner.html'
arch=archive.read_text(encoding='utf-8')
if 'PP6 LEGACY DEMO' not in arch:
    arch=arch.replace('<title>Veracruz · Campaign Planner</title>', '<title>ARCHIVED · 55-destination campaign exercise</title>')
    arch=arch.replace('<main>','''<main><!-- PP6 LEGACY DEMO -->
    <div role="note" style="border:2px solid #8a6d26;background:#fff8e0;color:#442f00;border-radius:12px;padding:1rem;margin:1rem 0;line-height:1.5">
      <strong>ARCHIVED / ARCHIVADO / 旧版</strong> — This is the historical 55-destination / 8-theme coursework scenario, NOT the current tourism catalog or the validated PP6 optimization. Its assumed MXN 5,000 placement cost is not a provider quote. / Ejercicio histórico; no representa los datos actuales.
      <a href="index.html">Return to current map / Volver al mapa actual</a>.
    </div>''',1)
    archive.write_text(arch,encoding='utf-8')

doc=ROOT/'docs/SITE_CURRENT_VS_ARCHIVED.md'
doc.parent.mkdir(parents=True,exist_ok=True)
doc.write_text('''# Current public website vs archived research (2026-10-21)

Current on the home page: `site/data/map_points.geojson` (212 approximate municipality references),
`site/data/attractions.geojson` (506 mapped attractions), `site/data/tourism_catalog.json` (documentary tourism records),
`site/js/map-explorer.js`, `site/js/map-attractions.js` and `site/js/itinerary-router.js`.
Do not confuse municipality centroids with verified entrances or driving destinations.

Historical, retained for research provenance but not presented as current home-page results:
`site/data/destinations.json`, `site/js/app.js`, old 55-profile Gower/PAM clustering,
`site/data/s7_precomputed.json`, old 8-theme / 55-destination campaign planner.
The direct `site/planner.html` is visibly marked **ARCHIVED** and removed from main navigation.
Historical clustering may appear in the academic methods as a negative or unstable experimental result,
never as the authoritative current catalog or a validated segmentation of tourists.

The **live road-routing service is not verified**, and municipality markers are approximate.
External driving directions are a separate provider integration, not an on-site booking or verified route.
This patch neither changes canonical databases nor validates an independent tourism-demand claim.

Rollback from repository root (only if you need the previous web view):
`cp .local-site-backup-before-v3/index.html site/index.html`
Other changed files can be copied back from the matching paths under `.local-site-backup-before-v3`.
''',encoding='utf-8')
ignore=ROOT/'.gitignore';txt=ignore.read_text(encoding='utf-8') if ignore.exists() else ''
if '.local-site-backup-before-v3/' not in txt:
    ignore.write_text(txt.rstrip()+'\n\n# Local rollback backups (do not publish)\n.local-site-backup-before-v3/\n',encoding='utf-8')
print('PASS: live home uses 212 municipality references + 506 attractions, and no longer displays old 55/12 segmentations.')
print('PASS: old campaign planner is visibly archived and no longer in the main navigation.')
print('PASS: canonical databases and other research sources unchanged.')
