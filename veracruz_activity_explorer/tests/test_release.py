#!/usr/bin/env python3
import json
import sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
record=json.loads((R/'site/data/activity_cards.json').read_text())
assert record['counts']=={'activities':78,'links':216,'municipalities':61},record['counts']
assert len(record['cards'])==78
assert len({x['feature_id'] for x in record['cards']})==78
assert sum(x['municipality_count'] for x in record['cards'])==216
assert all(x['media_kind']=='illustration' for x in record['cards'])
assert len(list((R/'site/assets/activity-illustrations').glob('*.svg')))==78
assert all(x['municipalities'] for x in record['cards'])
assert all(any(m['source_urls'] for m in x['municipalities']) for x in record['cards'])
for c in record['cards']:
    assert c['media_url'].startswith('assets/activity-illustrations/')
    if c['photo']:
        assert c['photo']['url'].startswith('https://')
        assert c['photo']['source'].startswith('https://commons.wikimedia.org/')
print('PASS: 78 specific activities; 216 supported links; 61 municipalities; media and source references.')
