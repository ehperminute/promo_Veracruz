#!/usr/bin/env python3
"""Idempotently add an editable planning range to the existing itinerary cost panel."""
from pathlib import Path
import sys

def install(root):
    root = Path(root).resolve()
    index = root / 'site' / 'index.html'
    if not index.exists():
        raise SystemExit(f'Expected existing site/index.html, not found at {root}')
    html = index.read_text(encoding='utf8')
    if 'itinerary-pricing.js' not in html:
        raise SystemExit('First install the unified Veracruz planner; itinerary-pricing.js is missing')
    src = Path(__file__).parent / 'assets'
    for filename in ['budget-range-core.js','budget-range.js','budget-range.css']:
        d = root / 'site' / ('css' if filename.endswith('.css') else 'js') / filename
        d.parent.mkdir(parents=True,exist_ok=True)
        d.write_bytes((src / filename).read_bytes())
    if 'css/budget-range.css' not in html:
        mark='</head>'
        if mark not in html:raise SystemExit('Head close tag missing')
        html=html.replace(mark,'<link rel="stylesheet" href="css/budget-range.css?v=1">\n'+mark,1)
    scripts='<script defer src="js/budget-range-core.js?v=1"></script>\n<script defer src="js/budget-range.js?v=1"></script>'
    if 'js/budget-range.js' not in html:
        # Insert after the existing pricing logic and preserve the website's load order.
        import re
        pat=r'(<script[^>]+src="js/itinerary-pricing\.js[^"\n]*"[^>]*></script>)'
        html,n=re.subn(pat,lambda m:m.group(1)+'\n'+scripts,html,count=1)
        if n!=1:raise SystemExit('Cannot locate the current pricing script in site/index.html')
    index.write_text(html,encoding='utf8')
    assert html.count('js/budget-range.js')==1 and html.count('css/budget-range.css')==1
    print('PASS: editable cost-range estimator installed; original offers and research data unchanged')
if __name__=='__main__':install(sys.argv[1] if len(sys.argv)>1 else '.')
