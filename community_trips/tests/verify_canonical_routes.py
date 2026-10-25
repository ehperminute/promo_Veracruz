#!/usr/bin/env python3
"""Optional source-integrity check against the recovered canonical database."""
import json,sqlite3,sys
from pathlib import Path
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd()
db=root/'data/recovered_source_descriptions/veracruz_pp3_master_with_originals.sqlite'
if not db.exists():raise SystemExit(f'Canonical research DB not found: {db}')
examples=json.loads((root/'site/data/trip_examples.json').read_text())['trips']
con=sqlite3.connect(db)
for example in examples:
    for stop in example['trip']['stops']:
        mun=stop['id'].split(':')[-1]
        actual=con.execute('SELECT name_official FROM municipalities WHERE municipality_id=?',(mun,)).fetchone()
        if not actual or actual[0]!=stop['name']:
            raise SystemExit(f'Unknown or mismatched municipality: {stop}')
print(f'PASS: {len(examples)} editorial trip templates reference validated municipality IDs.')
for activity in ['coffee_tasting','rafting','archaeological_visit','vanilla_extract_workshop',
                 'boat_excursion','birdwatching','paper_balloon_workshop','leather_shoemaking_demonstration']:
    count=con.execute('SELECT COUNT(*) FROM s4_statewide_evidence_pairs_v1 WHERE feature_id=?',(activity,)).fetchone()[0]
    if count==0:raise SystemExit('Missing activity evidence '+activity)
print('PASS: all eight named activity themes exist in the recovered activity evidence.')
con.close()
