#!/usr/bin/env python3
"""Simple deployment smoke test: standard library only."""
import argparse
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('repo',nargs='?',default='.');r=Path(p.parse_args().repo).resolve()
s=r/'site'
assert (s/'js'/'trip-journal.js').exists(), 'Journal missing'
assert (s/'js'/'trip-gallery.js').exists(), 'Gallery missing'
j=(s/'js'/'trip-journal.js').read_text()
g=(s/'js'/'trip-gallery.js').read_text()
h=(s/'viajes.html').read_text()
assert 'VX-TRIP-HASH-NAV-FIX-V2' in j, 'Same-page hash handling not installed'
assert "window.addEventListener('hashchange', openFromHash)" in j
assert 'VX-TRIP-GALLERY-SAME-HASH-FIX-V1' in g
assert 'trip-journal.js?v=20261025hash2' in h, 'Cache bust absent'
for html in ['index.html','viajes.html','enviar-viaje.html','proveedores.html']:
    content=(s/html).read_text()
    assert 'vx-language-unified.css' in content, html
    assert 'vx-language-unified.js' in content, html
print('PASS: hash navigation, cache-bust and unified language assets on 4 pages.')
