"""Idempotent install of the interest recommender, selected-stop highlighting and benchmark.
Never removes or overwrites the canonical database or previous source evidence.
"""
from __future__ import annotations
import argparse
import shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('root',nargs='?',default='.');args=p.parse_args()
root=Path(args.root).resolve()
html=root/'site/index.html';router=root/'site/js/itinerary-router.js'
assert html.is_file() and router.is_file(),'Install over an existing V2 itinerary site, not the old archive.'
for src,dest in [
 (HERE/'assets/interest-recommender.js',root/'site/js/interest-recommender.js'),
 (HERE/'assets/interest-recommender.css',root/'site/css/interest-recommender.css'),
 (HERE/'scripts/export_interest_evidence.py',root/'scripts/interest/export_interest_evidence.py'),
 (HERE/'scripts/bigdata_benchmark.py',root/'scripts/bigdata_benchmark.py')]:
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(src,dest)
text=html.read_text(encoding='utf-8')
stylesheet='<link rel="stylesheet" href="css/interest-recommender.css?v=1">'
script='<script defer src="js/interest-recommender.js?v=1"></script>'
if stylesheet not in text:text=text.replace('</head>',stylesheet+'\n</head>')
if script not in text:text=text.replace('</body>',script+'\n</body>')
html.write_text(text,encoding='utf-8')
code=router.read_text(encoding='utf-8')
anchor='function changed(){routeSeq++;'
if 'vxw:stops-changed' not in code:
    assert anchor in code,'Unexpected route-planner version; refusing to patch blind.'
    code=code.replace('renderStops();renderDirections();}\n  function add(',
      "renderStops();renderDirections();document.dispatchEvent(new CustomEvent('vxw:stops-changed'));}\n  function add(",1)
    code=code.replace('renderStops();renderDirections();setStatus(tx().ready);',
      "renderStops();renderDirections();document.dispatchEvent(new CustomEvent('vxw:stops-changed'));setStatus(tx().ready);",1)
    router.write_text(code,encoding='utf-8')
import subprocess,sys
subprocess.run([sys.executable,str(root/'scripts/interest/export_interest_evidence.py')],cwd=root,check=True)
print('PASS: interest recommender + numbered route markers, no changes to canonical SQLite.')
print('Optional Big Data benchmark: python scripts/bigdata_benchmark.py')
