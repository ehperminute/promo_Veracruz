#!/usr/bin/env python3
"""Reversible homepage injection of precomputed MapLibre explorer.

The existing site's data files, descriptions, JavaScript app and planner are untouched.
Run with path to the repository whose homepage lives in site/index.html.
"""
from pathlib import Path
import argparse, re, shutil
ROOT = Path(__file__).resolve().parent
MARKER = 'id="veracruz-map-section"'

def install(repo: Path):
    site = repo/'site'
    index = site/'index.html'
    if not index.is_file():
        raise SystemExit(f'Cannot find {index}. Specify the root of the promo_Veracruz repository.')
    original = index.read_text(encoding='utf-8-sig')
    html=original
    if MARKER not in html and "id='veracruz-map-section'" not in html:
        # Prefer the destination explorer as anchor (no dependence on old data).
        candidates=[
          r'<section\b[^>]*\bid\s*=\s*["\']destinations["\'][^>]*>',
          r'<section\b[^>]*\bid\s*=\s*["\']destination-explorer["\'][^>]*>',
          r'<(?:section|div)\b[^>]*\bid\s*=\s*["\']destinations["\'][^>]*>',
          r'</main\s*>'
        ]
        anchor=None
        for pattern in candidates:
            m=re.search(pattern,html,re.I)
            if m: anchor=m;break
        if anchor is None:
            raise SystemExit('Could not locate the destination explorer/main anchor; NO changes made.')
        start=anchor.start()
        html=html[:start]+('<section id="veracruz-map-section" aria-label="Interactive Veracruz tourist experiences map"></section>\n\n')+html[start:]
    if 'css/map-explorer.css' not in html:
        match=re.search(r'</head\s*>',html,re.I)
        if not match:raise SystemExit('Missing </head> in site/index.html; NO changes made.')
        html=html[:match.start()]+'''<link rel="stylesheet" href="https://unpkg.com/maplibre-gl@5.6.2/dist/maplibre-gl.css">
<link rel="stylesheet" href="css/map-explorer.css">
'''+html[match.start():]
    if 'js/map-explorer.js' not in html:
        match=re.search(r'</body\s*>',html,re.I)
        if not match:raise SystemExit('Missing </body> in site/index.html; NO changes made.')
        html=html[:match.start()]+'''<script defer src="https://unpkg.com/maplibre-gl@5.6.2/dist/maplibre-gl.js"></script>
<script defer src="js/map-explorer.js"></script>
'''+html[match.start():]
    files=['css/map-explorer.css','js/map-explorer.js','data/map_points.geojson']
    for file in files:
        source=ROOT/'site'/file
        if not source.is_file():raise SystemExit(f'Missing patch asset {source}; NO changes made.')
    backup=index.with_name('index.before-map.html')
    if not backup.exists(): shutil.copy2(index,backup)
    for file in files:
        dest=site/file
        dest.parent.mkdir(parents=True,exist_ok=True)
        if (ROOT/'site'/file).resolve() != dest.resolve(): shutil.copy2(ROOT/'site'/file,dest)
    if html!=original:index.write_text(html,encoding='utf-8')
    print('SUCCESS: Map installed into',index)
    print('Existing homepage backup:',backup)
    print('Populated 212-municipality map: site/data/map_points.geojson')
    print('Existing destination catalog and planner were not edited.')

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('repo', nargs='?',type=Path,default=Path.cwd())
    args=ap.parse_args()
    install(args.repo.expanduser().resolve())
