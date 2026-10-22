"""Export current specific tourism evidence for the static UI, without revising source claims."""
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'data/recovered_source_descriptions/veracruz_pp3_master_with_originals.sqlite'
DEST = ROOT / 'site/data/interest_evidence.json'

# Labels are *display translations*, not source quotations or a new taxonomy.
LABELS_ES = {
  'hiking':'Senderismo','kayaking':'Kayak','boat_excursion':'Paseo en lancha',
  'museum_visit':'Visita a museos','archaeological_visit':'Visita arqueológica',
  'rappelling':'Rápel','birdwatching':'Observación de aves','snorkeling':'Esnórquel',
  'guided_heritage_walk':'Paseo patrimonial guiado','temazcal':'Temazcal',
  'ziplining':'Tirolesa','canyoning':'Barranquismo','coffee_cupping':'Catación de café',
  'coffee_tasting':'Degustación de café','guided_city_tour':'Recorrido urbano guiado',
  'coffee_farm_visit':'Visita a finca cafetalera','natural_pool_jumping':'Salto a pozas',
  'river_boat_navigation':'Navegación fluvial','traditional_cooking_workshop':'Taller de cocina tradicional',
  'camping':'Campismo','coffee_roasting':'Tostado de café','cycling':'Ciclismo',
  'horseback_riding':'Cabalgata','rafting':'Rafting','scuba_diving':'Buceo',
  'coffee_harvesting':'Cosecha de café','coffee_planting':'Siembra de café'
}

def execute():
    db=sqlite3.connect(f'file:{SOURCE}?mode=ro',uri=True)
    db.row_factory=sqlite3.Row
    result=[]
    q='''SELECT p.municipality_id,m.name_official,p.feature_id,p.family,p.original_text_support_count,
        p.claim_ids,p.source_ids,p.source_urls,g.latitude,g.longitude,
        a.name_en
       FROM s4_statewide_evidence_pairs_v1 p
       JOIN municipalities m ON m.municipality_id=p.municipality_id
       JOIN municipality_georeferences g ON g.municipality_id=p.municipality_id
       LEFT JOIN activities a ON a.activity_id=p.feature_id
       ORDER BY m.name_official,p.feature_id'''
    for r in db.execute(q):
        code=str(r['feature_id'])
        en = r['name_en'] if r['name_en'] and str(r['name_en']).strip() and ' ' in str(r['name_en']).strip() else code.replace('_',' ').title()
        # A handful of source-derived activity 'name_es' values are sentence fragments. Never reuse blindly.
        es=LABELS_ES.get(code,code.replace('_',' ').capitalize())
        urls=[s for s in (r['source_urls'] or '').split('|') if s.startswith('https://')]
        result.append({'municipality_id':str(r['municipality_id']),'municipality':r['name_official'],
                       'feature_id':code,'label_es':es,'label_en':en,'family':r['family'],
                       'original_text_support':int(r['original_text_support_count'])>0,
                       'source_urls':sorted(set(urls))[:3],
                       'claim_ids':(r['claim_ids'] or '').split('|'),
                       'coordinates':[r['longitude'],r['latitude']]})
    n=db.execute('select count(*) from s4_statewide_evidence_pairs_v1').fetchone()[0]
    assert len(result)==n==216, f'Unexpected source counts {len(result)} / {n}'
    assert len({r['municipality_id'] for r in result})==61
    assert len({r['feature_id'] for r in result})==78
    data={'schema':'veracruz-activity-interest-v1','source_file':SOURCE.relative_to(ROOT).as_posix(),
          'evidence_status':'accepted_specific_activity_relationships (not booking availability)',
          'coordinate_status':'approximate municipality reference, NOT a road entrance',
          'price_status':'No observed provider prices; budget calculations are user-entered assumptions.',
          'total_links':len(result),'municipalities':61,'features':78,'records':result}
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    print('Exported',len(result),'relationships across',61,'municipalities and',78,'specific activities')
    db.close()
    return data
if __name__=='__main__':execute()
