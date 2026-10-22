#!/usr/bin/env python3
"""Portable install / data regression tests. No browser or live network needed."""
import json, shutil, tempfile
from pathlib import Path
from install import apply
here=Path(__file__).resolve().parent
j=json.loads((here/'site/data/activity_sections.json').read_text(encoding='utf8'))
assert j['counts']=={'sections':8,'activities':78,'links':216}
assert all(s['activity_count']>=2 for s in j['sections'])
assert sum(s['activity_count'] for s in j['sections'])==78
assert len(set(a['feature_id'] for s in j['sections'] for a in s['activities']))==78
with tempfile.TemporaryDirectory() as temp:
    root=Path(temp)
    (root/'site/data').mkdir(parents=True)
    (root/'site/index.html').write_text('<!doctype html><html><head></head><body><nav><a href="#veracruz-map-section">Map</a></nav><section id="veracruz-map-section"></section></body></html>',encoding='utf8')
    records=[]
    for s in j['sections']:
        for a in s['activities']:
            records.extend({'municipality_id':m['municipality_id'],'feature_id':a['feature_id']} for m in a['municipalities'])
    (root/'site/data/interest_evidence.json').write_text(json.dumps({'records':records,'total_links':len(records)}),encoding='utf8')
    apply(root)
    first=(root/'site/index.html').read_bytes()
    apply(root)
    second=(root/'site/index.html').read_bytes()
    assert first==second,'Installer modified HTML on reinstallation'
    assert first.count(b'js/activity-groups.js')==1
    assert b'vx-activities' in first
print('PASS: 8 groups (>1 each), 78 unique activities, 216 evidence links, installer idempotence.')
