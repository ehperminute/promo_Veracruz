"""S8 prototype: evidence-grounded activity matching, not preference prediction.

Run: python scripts/marketing/build_s8_activity_matches.py
Expects latest S7 calendar at outputs/or/s7_calendar_budget_100000.csv.
No external network access, no live campaign or invented conversions.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CULTURE = ROOT / 'data/reference/S8_cultural_activity_catalog_v2.csv'
AUDIT = ROOT / 'data/reference/S8_destination_activity_audit.csv'
CALENDAR = ROOT / 'outputs/or/s7_calendar_budget_100000.csv'
OUT = ROOT / 'outputs/marketing/s8_activity_audience_matches_100k.csv'

AUDIENCE = {
 'archaeological_site': 'archaeology_and_pre_hispanic_history',
 'museum': 'museum_and_heritage_visitors',
 'museum_or_cultural_center': 'museum_and_heritage_visitors',
 'historic_architecture_or_monument': 'historic_architecture_visitors',
 'festival_or_living_tradition': 'festival_and_living_heritage_interest',
 'crafts': 'traditional_crafts_interest',
 'historic_urban_landscape': 'historic_architecture_visitors',
}


def main():
    for f in (CULTURE, AUDIT, CALENDAR):
        if not f.exists():
            raise SystemExit(f'Missing required input: {f} — do not fabricate missing data')
    culture = pd.read_csv(CULTURE).fillna('')
    audit = pd.read_csv(AUDIT).fillna('')
    s7 = pd.read_csv(CALENDAR)
    if s7['destination'].duplicated().any():
        raise ValueError('Unexpected duplicate selected destinations in S7 calendar')
    merged = s7.merge(culture, on='destination', how='left', validate='one_to_one').merge(
        audit[['destination','documented_adventure_activities','adventure_source_urls']],
        on='destination', how='left', validate='one_to_one')
    if merged['cultural_feature'].isna().any():
        raise ValueError('Cultural evidence missing for selected destination')
    rows = []
    for _, r in merged.iterrows():
        common = {'destination':r['destination'], 'season_s7':r['period'],
                  'region':r['region'], 's7_assumed_cost_mxn':int(r['assumed_cost_mxn'])}
        level = str(r['evidence_level'])
        for kind in str(r['activity_type']).split(';'):
            kind = kind.strip()
            if kind and kind in AUDIENCE and level.startswith('PRIMARY_SOURCE'):
                rows.append({**common, 'interest_segment_hypothesis':AUDIENCE[kind],
                    'activity':str(r['cultural_feature']), 'evidence_kind':'primary_heritage_source',
                    'source_urls':str(r['source_urls']), 'promotion_status':'heritage_description_only_check_hours_and_permissions',
                    'caveat':'Segment is a hypothesis; no evidence of response or demand in Veracruz'})
        adventures = str(r['documented_adventure_activities'])
        if adventures and adventures.lower() != 'nan':
            for item in adventures.split(' | '):
                if item.strip():
                    rows.append({**common,'interest_segment_hypothesis':'outdoor_and_adventure_interest',
                        'activity':item.strip(), 'evidence_kind':'documented_activity_record',
                        'source_urls':str(r['adventure_source_urls']),
                        'promotion_status':'verify_current_provider_access_safety_and_season',
                        'caveat':'Activity documented, but bookability and seasonal operation not verified'})
        if not any(z['destination']==r['destination'] for z in rows):
            rows.append({**common,'interest_segment_hypothesis':'not_yet_evidence_matched',
                 'activity':'', 'evidence_kind':'insufficient_specific_current_evidence',
                 'source_urls':'','promotion_status':'research_required_before_activity_advertising',
                 'caveat':'Do not substitute broad S4 flags for activity-level evidence'})
    out = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    out.to_csv(OUT,index=False,encoding='utf-8-sig')
    print(f'Wrote {len(out)} activity-interest records for {s7.destination.nunique()} S7 destinations: {OUT}')
    print(out.promotion_status.value_counts().to_string())

if __name__ == '__main__':
    main()
