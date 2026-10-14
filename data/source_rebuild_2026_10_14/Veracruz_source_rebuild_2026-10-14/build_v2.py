#!/usr/bin/env python3
"""Reassemble Veracruz tourism raw evidence; preserves evidence granularity and uncertainty.
Works offline against included frozen inputs. No model training or invented activity claims.
"""
from pathlib import Path
from collections import defaultdict,Counter
import csv,re,hashlib,json,unicodedata

ROOT=Path(__file__).resolve().parent
BASE=ROOT/'base'/'output'
CAT=ROOT/'catalog_extraction'
OUT=ROOT/'deliverables'
OUT.mkdir(exist_ok=True)

def rd(p):
    with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def wr(p,rows,fields=None):
    rows=list(rows); fields=fields or (list(rows[0]) if rows else [])
    with open(OUT/p,'w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
def stable_id(*part):return hashlib.sha256('|'.join(map(str,part)).encode()).hexdigest()[:20]
def nor(s):
    s=unicodedata.normalize('NFKD',str(s)).casefold()
    s=''.join(c for c in s if not unicodedata.combining(c))
    return ' '.join(re.findall(r'[a-z0-9]+',s))
def clean(s):return re.sub(r'\s+',' ',s or '').strip()

def locate(raw,term):
    """Find term ignoring accents and whitespace, return original unicode excerpt."""
    data=[]; indices=[]
    for i,ch in enumerate(raw):
        for c in unicodedata.normalize('NFKD',ch.casefold()):
            if unicodedata.combining(c):continue
            data.append(c if c.isalnum() else ' ');indices.append(i)
    s=''.join(data); target=' '.join(re.findall('[a-z0-9]+',nor(term)))
    if not target:return None
    query=r'\s+'.join(map(re.escape,target.split()))
    m=re.search(r'(?<![a-z0-9])'+query+r'(?![a-z0-9])',s)
    if not m:return None
    ix=indices[m.start()];end=indices[m.end()-1]+1
    return (clean(raw[max(0,ix-150):min(len(raw),end+200)]),clean(raw[ix:end]),ix)

geo=rd(BASE/'municipalities_212.csv')
muni={x['municipality_id']:x for x in geo}; geo_name={nor(x['municipality']):x['municipality_id'] for x in geo}
can=rd(BASE/'destination_candidates.csv');candids=set(x['municipality_id'] for x in can)
assert len(geo)==212 and len(muni)==212
products=rd(BASE/'tourism_products_295.csv')
prod_links=rd(BASE/'tourism_product_municipality_links.csv')
catrows=rd(BASE/'official_catalog_municipality_sections.csv')
claims=rd(BASE/'destination_activity_and_heritage_evidence.csv')
places=rd(BASE/'named_places_events_and_attraction_leads.csv')
activity_links=rd(BASE/'municipality_observed_activity_links.csv')
source_pages=rd(CAT/'catalog_full_text_pages.csv')
source_blocks=rd(CAT/'catalog_all_text_blocks.csv')
source_sections=rd(CAT/'catalog_sections.csv')
providers=rd(BASE/'catalog_provider_directory_blocks.csv')
context=rd(BASE/'additional_official_source_leads.csv')
taxonomy=rd(BASE/'activity_taxonomy.csv')

for dest,src in [('municipalities_212.csv',geo),('official_tourism_products_295.csv',products),
                 ('tourism_card_municipality_mentions.csv',prod_links),
                 ('catalog_municipality_experience_associations.csv',catrows),
                 ('original_activity_cultural_and_heritage_claims.csv',claims),
                 ('named_place_event_heritage_leads.csv',places),
                 ('catalog_provider_blocks.csv',providers),('activity_taxonomy_raw_mappings.csv',taxonomy),
                 ('catalog_full_text_pages_66.csv',source_pages),
                 ('catalog_source_text_blocks_1175.csv',source_blocks),
                 ('catalog_sections_32.csv',source_sections),
                 ('prior_official_source_leads.csv',context),
                 ('evidence_based_municipality_activity_pairs.csv',activity_links),
                 ('destination_candidates_98.csv',can)]:wr(dest,src)

# Explicit named-place strings (not automatically deemed attractions or geolocated).
# The catalog narratives contain these. Keep only names found verbatim in source text.
NAMED_SEEDS=[
 'San Miguel Aguasuelos','Chichicaxtle','Sistema Arrecifal Veracruzano','Villa Rica','Playa Muñecos',
 'Dunas de Chachalacas','Cerro de las Antenas','Barranca de San Miguel','Sierra de Zongolica',
 'Finca Santa Martha','Playa Mata de Uva','Malecón de Veracruz','Laguna de Tamiahua',
 'Playa Atexakatl','El Tajín','Cempoala','Quiahuiztlán','Tres Zapotes',
 'San Lorenzo Tenochtitlán','Casa de Cortés','Puente Colgante','Museo del Café',
 'Museo de la Orquídea','Jardín Botánico Francisco Javier Clavijero',
 'Cascada de Texolo','Cascada Texolo','Río Filobobos','Cofre de Perote','Pico de Orizaba',
 'Cascada de Atlahuitzia','Cascada Atlahuitzia','Roca Partida','Salto de Eyipantla',
 'Selva del Marinero','Reserva de la Biosfera de Los Tuxtlas','Playa Chachalacas',
 'Cerro de los Metates','Cerro de Los Metates','Cerro del Borrego','Jardín Botánico Clavijero',
 'Cascada de Xico','Ruta de la Orquídea','Parque Nacional Cofre de Perote',
 'Cascada de la Monja','Laguna de Catemaco','Arrecife de Enmedio',
 'Laguna de Sontecomapan','Museo del Danzante','Río de los Pescados',
]

# Record original named place leads where their *exact name* also occurs in the 2025 PDF.
# Short, generic, or multi-place leads excluded to avoid false positive matching.
for x in places:
   s=clean(x['raw_place_or_feature'])
   if len(s)>9 and len(s)<65 and not any(y in s for y in ('|',' / ',';','(',')')):
       if s not in NAMED_SEEDS and nor(s) not in geo_name and len(s.split())>1:NAMED_SEEDS.append(s)

page_by_number={int(x['pdf_page']):x for x in source_pages}
page_named=[]
seen=set()
for p in source_pages:
    n=int(p['pdf_page']);
    # Only check pages that contain prose / actual attraction descriptions; tables can also have named captions.
    for name in NAMED_SEEDS:
        m=locate(p['text'],name)
        if m:
            snippet, exact, offset=m
            key=(n,nor(name))
            if key in seen:continue
            seen.add(key)
            page_named.append(dict(mention_id=stable_id('CAT-NAME',n,nor(name)),
               name_found=exact,canonical_search_name=name,section=p['section'],
               source_pdf_file=p['source_file'],pdf_file_page=p['source_page'],
               catalog_global_spread_page=n,printed_page_spread=p['printed_spread'],
               catalog_original_context=snippet,
               municipality_id='',place_municipality='NOT_ASSIGNED_FROM_PHRASE_ALONE',
               evidence_kind='literal_named_place_or_subject_mention',
               visitor_access='not_checked',
               validation_note='Presence in source text verified; activity provider, physical location and open status must not be inferred'))
wr('catalog_named_places_verbatim_matches.csv',page_named,
   ['mention_id','name_found','canonical_search_name','section','source_pdf_file','pdf_file_page',
    'catalog_global_spread_page','printed_page_spread','catalog_original_context','municipality_id',
    'place_municipality','evidence_kind','visitor_access','validation_note'])

# Catalog prose preserved separately from tables and provider directory pages,
# so downstream text mining does not unintentionally read contact blocks as offers.
section_narratives=[]
for p in source_pages:
  pg=int(p['pdf_page']); text=p['text']
  if pg<4:continue
  markers=['DÓNDE LO ENCUENTRAS','DIRECTORIO DE PRESTADORES','MUNICIPIO  CONECTIVIDAD','PRESTADORES DE SERVICIOS']
  prose_class='narrative_or_experience_description' if pg%2==0 else 'directory_or_photo_caption_or_continuation'
  # Some narrative headings occur on odd pages or PDF pages shifted: classification is heuristic and is *not* used to discard content.
  if any(m in text.upper() for m in markers): prose_class='mixed_table_directory_caption'
  section_narratives.append(dict(global_spread_page=pg,source_pdf_file=p['source_file'],
     pdf_file_page=p['source_page'],section=p['section'],printed_page_spread=p['printed_spread'],
     text_classification=prose_class,raw_text=text))
wr('catalog_all_section_text_classified.csv',section_narratives)

# One destination summary across all source types. Missing evidence remains explicitly UNKNOWN.
links_per=defaultdict(list)
for a in activity_links:links_per[a['municipality_id']].append(a)
cat_per=defaultdict(list)
for a in catrows:cat_per[a['municipality_id']].append(a)
prod_per=defaultdict(list)
for a in prod_links:prod_per[a['municipality_id']].append(a)
places_per=defaultdict(list)
for a in places:places_per[a['municipality_id']].append(a)
context_per=defaultdict(list)
for a in context:context_per[a['municipality_id']].append(a)
claims_per=defaultdict(list)
for a in claims:claims_per[a['municipality_id']].append(a)
by_can={x['municipality_id']:x for x in can}
profiles=[]
for x in geo:
    mid=x['municipality_id']; cat=cat_per[mid]; act=links_per[mid]; pc=prod_per[mid];pl=places_per[mid];cx=context_per[mid]
    claim=claims_per[mid]
    visible=['activity_tag' for _ in act]
    typecounts=Counter(y['source_kind'] for y in pl)
    statuses=Counter(y['record_type'] for y in claim)
    profiles.append(dict(municipality_id=mid,municipality=x['municipality'],
      initial_55='yes' if mid in by_can and by_can[mid]['initial_55']=='1' else 'no',
      research_candidate_98='yes' if mid in candids else 'no',
      research_evidence_tier=by_can.get(mid,{}).get('tourism_evidence_tier','not_screened_as_candidate'),
      official_catalog_chapter_count=len(cat),
      catalog_chapters=' | '.join(sorted({y['official_section'] for y in cat})),
      observed_specific_activity_count=len(act),
      observed_specific_activity_codes=' | '.join(sorted(y['canonical_activity_tag'] for y in act)),
      source_claims_count=len(claim),
      cultural_leads_count=statuses['cultural_lead'],
      named_place_event_or_heritage_leads_count=len(pl),
      named_features=' | '.join(sorted(set(y['raw_place_or_feature'] for y in pl))),
      original_official_product_mentions=len(pc),
      new_government_source_leads_count=len(cx),
      evidence_status='some_specific_activity_evidence' if act else 'NO_ACCEPTED_SPECIFIC_ACTIVITY_EVIDENCE_YET',
      no_activity_detected_does_not_mean='no_activity_exists' if not act else '',
      live_offer_checked='no',visitor_capacity_measured='no'))
wr('ALL_212_municipality_evidence_profiles.csv',profiles)
wr('CANDIDATES_98_activity_attraction_profiles.csv',[p for p in profiles if p['research_candidate_98']=='yes'])

# Unified evidence ledger: one record per originally supported assertion, with explicit type.
# The catalog chapter record is already represented among the 396 typed claims;
# product mentions, named places and supplementary official leads are different types.
product_by_id={x['product_id']:x for x in products}
ledger=[]
for x in claims:
    ledger.append(dict(evidence_id=x['claim_id'],municipality_id=x['municipality_id'],municipality=x['municipality'],
       evidence_family=x['record_type'],source_type=x['source_type'],source_record_id=x['source_record_id'],
       original_claim_text=x['activity_or_feature_original'],original_activity_tag=x['source_activity_tag'],
       canonical_activity_tag=x['canonical_activity_tag'],geography_role=x['geographic_scope'],
       evidence_status=x['evidence_status'],source_document_or_url=x['source_url_or_file'],
       source_page=x['source_page'],date_or_year=x['published_or_review_date'],
       caveat=x['limitations']))
for x in prod_links:
    prod=product_by_id[x['product_id']]
    ledger.append(dict(evidence_id=x['link_id'],municipality_id=x['municipality_id'],municipality=x['municipality'],
       evidence_family='MARKETED_PRODUCT_CARD_MUNICIPALITY_MENTION',source_type='official_product_cards',
       source_record_id=x['product_id'],original_claim_text=prod['product_title_as_published'],
       original_activity_tag='',canonical_activity_tag='',geography_role=x['geography_role'],
       evidence_status='published_product_title_without_activity_confirmation',source_document_or_url=x['source_snapshot'],
       source_page='',date_or_year='snapshot_2026-10-06',
       caveat='Product card may mention multiple municipalities; not a location-specific activity listing'))
for x in places:
    ledger.append(dict(evidence_id=x['mention_id'],municipality_id=x['municipality_id'],municipality=x['municipality'],
       evidence_family='NAMED_PLACE_EVENT_OR_TRADITION_LEAD',source_type=x['source_kind'],
       source_record_id=x['source_record_id'],original_claim_text=x['raw_place_or_feature'],
       original_activity_tag=x['linked_activity_or_tradition_as_published'],canonical_activity_tag='',
       geography_role=x['physical_location_verified'],evidence_status='place_or_event_mentioned_current_access_unverified',
       source_document_or_url=x['source_url'],source_page='',date_or_year='',caveat=x['caution']))
for x in context:
    # Specific official activity leads may already be included in the 396 typed claims,
    # so this register is contextual-only: do not duplicate activity descriptions.
    if x['record_type']=='activity':continue
    ledger.append(dict(evidence_id=x['context_id'],municipality_id=x['municipality_id'],municipality=x['municipality'],
       evidence_family='ADDITIONAL_OFFICIAL_SOURCE_LEAD',source_type=x['record_type'],
       source_record_id=x['context_id'],original_claim_text=x['summary_from_prior_research'],
       original_activity_tag='',canonical_activity_tag='',geography_role='municipality_contextual',
       evidence_status='previously_reviewed_lead_not_reopened',source_document_or_url=x['source_url_or_urls'],
       source_page='',date_or_year='',caveat=x['note']))
assert len({x['evidence_id'] for x in ledger})==len(ledger)
wr('UNIFIED_SOURCE_EVIDENCE_LEDGER.csv',ledger)

# Add human-readable record-level type index, not an invented "one row per activity" table.
manifest=[]
for name,record_kind,nrows in [
 ('municipalities_212.csv','administrative_reference',len(geo)),
 ('official_tourism_products_295.csv','official_marketing_cards',len(products)),
 ('tourism_card_municipality_mentions.csv','product_card_place_mentions',len(prod_links)),
 ('catalog_municipality_experience_associations.csv','official_2025_chapter_municipality_mentions',len(catrows)),
 ('original_activity_cultural_and_heritage_claims.csv','typed_source_evidence',len(claims)),
 ('evidence_based_municipality_activity_pairs.csv','derived_unique_tag_pairs',len(activity_links)),
 ('named_place_event_heritage_leads.csv','original_named_place_leads',len(places)),
 ('UNIFIED_SOURCE_EVIDENCE_LEDGER.csv','all_evidence_types_in_one_typed_long_table',len(ledger)),
 ('catalog_named_places_verbatim_matches.csv','additional_pdf_named_place_mentions',len(page_named)),
 ('catalog_full_text_pages_66.csv','full_extracted_pdf_text',len(source_pages)),
 ('catalog_source_text_blocks_1175.csv','original_pdf_text_and_layout_blocks',len(source_blocks)),
 ('catalog_provider_blocks.csv','unmatched_published_provider_blocks',len(providers)),
 ('ALL_212_municipality_evidence_profiles.csv','derived_coverage_index',len(profiles)),
 ('CANDIDATES_98_activity_attraction_profiles.csv','historical_screening_candidate_index',len(candids))]:
    manifest.append(dict(table=name,record_type=record_kind,rows=nrows,sha256=hashlib.sha256((OUT/name).read_bytes()).hexdigest(),note='All links/claims retain limitations; no booking availability certified'))
wr('TABLE_MANIFEST.csv',manifest)

# Specific reproducible validation, not a generic "PASS" claim.
problems=[]
assert len(source_pages)==66 and len(source_blocks)==1175
assert len(products)==295 and len(catrows)==187 and len(claims)==396
assert len(profiles)==212 and len(candids)==98
assert len({p['pdf_page'] for p in source_pages})==66
assert len({e['claim_id'] for e in claims})==len(claims)
assert len({(x['municipality_id'],x['canonical_activity_tag']) for x in activity_links})==len(activity_links)
assert all(x['municipality_id'] in muni for x in catrows+claims+prod_links if x['municipality_id'])
assert len({(x['municipality_id'],x['official_section']) for x in catrows})==len(catrows), 'Duplicate chapter-municipality edges'
for row in catrows:
    p=page_by_number.get(int(row['pdf_page']))
    if not p or p['source_file']!=row['pdf_filename'] or p['section']!=row['official_section']:
       problems.append({'issue':'PDF page / chapter mismatch','record':row['catalog_record_id'],'source':row['pdf_filename'],'detail':row['official_section']})
    # A municipality may have shortened alias in the original PDF; flag rather than silently claim checked.
    if p and not locate(p['text'],row['raw_municipality']):
       problems.append({'issue':'Municipality string not directly matched in extracted page text',
                        'record':row['catalog_record_id'],'source':p['source_file'],
                        'detail':f"page {p['source_page']} {row['raw_municipality']}"})
wr('SOURCE_MAPPING_EXCEPTIONS.csv',problems,['issue','record','source','detail'])
stats={
 'municipalities':len(geo),'historical_candidates':len(candids),'catalog_pages':len(source_pages),
 'catalog_original_text_blocks':len(source_blocks),'catalog_sections':len(source_sections),
 'catalog_municipality_chapter_links':len(catrows),'pdf_verbatim_named_place_mentions':len(page_named),
 'pdf_verbatim_distinct_names':len(set(nor(r['canonical_search_name']) for r in page_named)),
 'original_product_cards':len(products),'product_municipality_mentions':len(prod_links),
 'typed_evidence_claims':len(claims),'distinct_municipality_activity_pairs':len(activity_links),
 'original_named_place_event_leads':len(places),'unified_typed_ledger_rows':len(ledger),
 'candidates_with_specific_tag':sum(bool(links_per[k]) for k in candids),
 'candidates_without_specific_tag':sum(not bool(links_per[k]) for k in candids),
 'source_mapping_warnings':len(problems),
 'validated': len(problems)==0
}
(OUT/'VALIDATION.json').write_text(json.dumps(stats,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(stats,indent=2,ensure_ascii=False))
