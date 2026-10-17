#!/usr/bin/env python3
"""Read only the CURRENT PP3 SQLite database; export a static, conservative map layer.

Uses approximate municipality reference points, NEVER venue/attraction coordinates.
Uses only already accepted S4 statewide positive feature pairs. No edits to SQLite.
"""
from __future__ import annotations
import argparse, hashlib, json, sqlite3
from pathlib import Path
from collections import Counter

TYPES = {
    'land_adventure': 'adventure',
    'water_adventure': 'water',
    'nature_observation': 'nature',
    'food_agriculture': 'food',
    'history_culture': 'culture',
    'traditional_crafts': 'crafts',
    'wellness_spiritual': 'wellness',
    'scenic_transport': 'scenic',
    'other_specific_unclassified': 'other',
}
# Explicit names for taxonomy IDs with no corresponding activity row.
NAMES = {
    'coffee_farm_visit': ('Visita a finca cafetalera', 'Coffee farm visit'),
    'massage': ('Masaje', 'Massage'),
    'mineral_clay_treatment': ('Tratamiento con arcilla mineral', 'Mineral clay treatment'),
}

def export(database: Path, target: Path) -> dict:
    if not database.is_file(): raise FileNotFoundError(database)
    con = sqlite3.connect(f'file:{database.resolve()}?mode=ro', uri=True)
    con.row_factory = sqlite3.Row
    if con.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
        raise ValueError('Database integrity check failed')
    municipalities = con.execute('''
      SELECT m.municipality_id, m.name_official, m.tourism_region,
             g.latitude, g.longitude, g.coordinate_kind, g.verification_status,
             g.source_id AS geo_source_id
      FROM municipalities m
      JOIN municipality_georeferences g USING (municipality_id)
      ORDER BY m.name_official COLLATE NOCASE
    ''').fetchall()
    if len(municipalities) != 212:
        raise ValueError(f'Expected 212 municipality references, got {len(municipalities)}')
    activities_by = {}
    pairs = con.execute('''
      SELECT p.*, a.name_es, a.name_en
      FROM s4_statewide_evidence_pairs_v1 p
      LEFT JOIN activities a ON p.feature_id = a.activity_id
      ORDER BY p.municipality_id, p.family, p.feature_id
    ''').fetchall()
    if len(pairs) != 216:
        raise ValueError(f'Expected 216 strict municipality/activity pairs, got {len(pairs)}')
    for p in pairs:
        municipality_id = p['municipality_id']
        family = p['family']
        if family not in TYPES:
            raise ValueError('Unrecognized evidence family: '+str(family))
        es, en = (p['name_es'],p['name_en']) if p['name_es'] and p['name_en'] else NAMES.get(p['feature_id'], (None,None))
        if not (es and en): raise ValueError(f'Missing bilingual label for {p["feature_id"]}')
        urls = sorted(set(u.strip() for u in (p['source_urls'] or '').split('|') if u.strip().startswith('https://')))
        record = {
          'id':p['feature_id'], 'name_es':es,'name_en':en,
          'family':family, 'type': TYPES[family],
          'claim_count':p['claim_count'],
          'original_text_support_count':p['original_text_support_count'],
          'summary_only_evidence_count':p['summary_only_evidence_count'],
          'claim_ids':p['claim_ids'].split('|') if p['claim_ids'] else [],
          'source_urls':urls,
        }
        activities_by.setdefault(municipality_id,[]).append(record)
    features=[]
    for m in municipalities:
        acts = activities_by.get(m['municipality_id'], [])
        types=sorted({a['type'] for a in acts})
        properties={
          'municipality_id':m['municipality_id'],
          'name':m['name_official'],
          'municipality_region_preliminary':m['tourism_region'],
          'location_kind':'approximate_municipality_reference',
          'coordinate_verification':m['verification_status'],
          'geographic_source_id':m['geo_source_id'],
          'activity_evidence':'documented_specific_activity' if acts else 'insufficient_documented_activity_not_absence',
          'types':types,
          'activity_count':len(acts),
          'activities':acts,
        }
        features.append({'type':'Feature','id':m['municipality_id'],
          'geometry':{'type':'Point','coordinates':[m['longitude'],m['latitude']]},
          'properties':properties})
    result={
      'type':'FeatureCollection',
      'metadata':{
        'generated_from':'veracruz_pp3_master.sqlite',
        'database_sha256':hashlib.sha256(database.read_bytes()).hexdigest(),
        'coordinates_note':'Approximate municipality reference coordinates, not attraction coordinates, venue location, or road routing endpoints.',
        'evidence_note':'Only documented positive municipality/activity evidence pairs; missing documentation is NOT absence of tourism.',
        'web_descriptions_note':'295 webpage product descriptions remain unrecovered in this source version; NO generated paraphrases exported as original descriptions.',
        'data_version':'source_first_evidence_repair_2026-10-17',
        'municipalities':len(features),
        'municipalities_with_documented_activities':len(activities_by),
        'accepted_municipality_activity_pairs':len(pairs),
        'pairs_with_retained_original_passage':sum(p['original_text_support_count']>0 for p in pairs),
      },
      'features':features,
    }
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    con.close()
    return result['metadata']

if __name__ == '__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('sqlite',type=Path)
    ap.add_argument('--output',type=Path,default=Path('site/data/map_points.geojson'))
    args=ap.parse_args()
    print(json.dumps(export(args.sqlite,args.output),ensure_ascii=False,indent=2))
