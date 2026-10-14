#!/usr/bin/env python3
"""Rebuild the Veracruz municipal + experience evidence layer from frozen inputs.
Only Python standard library. Does NOT model tourism demand, classify unsourced absences,
or claim that a source's municipality entry identifies an attraction's physical location.
"""
from __future__ import annotations
import csv, hashlib, io, json, re, shutil, unicodedata
from pathlib import Path
from collections import Counter,defaultdict

BASE=Path(__file__).resolve().parent
IN=BASE/'inputs'; OUT=BASE/'output'; OUT.mkdir(exist_ok=True)

def read(name):
    with (IN/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(name, records, cols=None):
    records=list(records)
    if cols is None:cols=list(records[0]) if records else []
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');w.writeheader();w.writerows(records)
    return len(records)
def norm(s):
    s=''.join(c for c in unicodedata.normalize('NFKD',str(s)) if not unicodedata.combining(c)).casefold()
    return re.sub(r'[^a-z0-9]+',' ',s).strip()
def jid(*terms):return hashlib.sha256('||'.join(str(x) for x in terms).encode('utf8')).hexdigest()[:18]
def truth(s):return str(s).strip().lower() in ('true','1','yes')
def listpipe(s):return [x.strip() for x in str(s).split('|') if x.strip()]
def safety(x):return str(x or '').strip()

# Source 1: official administrative frame (no tourism inference)
geo=[r for r in read('inegi_ageeml_utf8.csv') if r['CVE_ENT']=='30']
assert len(geo)==212 and len({r['CVEGEO'] for r in geo})==212
keyname={r['CVEGEO']:r['NOM_MUN'] for r in geo}; names={norm(r['NOM_MUN']):r['CVEGEO'] for r in geo}
alias={
 'alto lucero':'Alto Lucero de Gutiérrez Barrios',
 'las vigas':'Las Vigas de Ramírez',
 'poza rica':'Poza Rica de Hidalgo',
 'zozocolco':'Zozocolco de Hidalgo',
 'ursulo galvan':'Úrsulo Galván',
 'san andres':'San Andrés Tuxtla',
 'alamo':'Álamo Temapache',
 'fortin de las flores':'Fortín',
 'fortin de las flores veracruz':'Fortín',
 'camerino z mendoza':'Camerino Z. Mendoza',
 'cosautlan':'Cosautlán de Carvajal',
 'papantla de olarte':'Papantla',
 'las choapas veracruz':'Las Choapas',
}
issues=[]
def geo_id(name, origin, sourceid):
    n=norm(name);mapped=alias.get(n)
    if mapped:n=norm(mapped)
    code=names.get(n)
    if not code:
        issues.append(dict(issue_type='geography_unmatched',source=origin,source_record=sourceid,raw_value=name,impact='record retained in unresolved_geographies.csv',action='Review municipality/location spelling; do not guess'))
    return code or ''

scope={str(r['clave_municipio']).zfill(5):r for r in read('scope_212_prior.csv')}
assert set(scope)==set(keyname), ('scope mismatch',set(scope)^set(keyname))
infra={str(r['clave_municipio']).zfill(5):r for r in read('infra_212.csv')}
assert set(infra)==set(keyname)

# Explicitly distinguish source-derived tier from selected scope. Original 55 is historical.
municipalities=[]
for g in sorted(geo,key=lambda r:r['CVEGEO']):
 k=g['CVEGEO'];s=scope[k];m=infra[k]
 a=s['source_support_tier']; level='direct' if a.startswith('A -') else 'contextual' if a.startswith('B -') else 'not_established'
 include=truth(s['original_55']) or truth(s['newly_identified'])
 municipalities.append(dict(municipality_id=k,municipality=g['NOM_MUN'],state_code='30',municipality_code=g['CVE_MUN'],municipal_seat=g['NOM_CAB'],
 population_reference=g['POB_TOTAL'],inhabited_housing_units_reference=g['TOTAL DE VIVIENDAS HABITADAS'],
 population_reference_vintage='not_specified_in_uploaded_file',
 initial_55=1 if truth(s['original_55']) else 0,additional_2026_candidate=1 if truth(s['newly_identified']) else 0,
 candidate_for_research=1 if include else 0,tourism_evidence_tier=level,
 region_names_as_published=s['official_regions'],official_tourism_product_card_count=s['product_cards_n'],
 official_catalog_sections_count=s['catalog_2025_sections_n'],inah_site_count_in_prior_screening=s['inah_open_sites_n'],
 registered_accommodation_businesses_proxy=m['alojamiento_n'],food_and_drink_businesses_proxy=m['alimentos_bebidas_n'],
 hotel_occupancy='unknown_unless_datatur_center_data_linked',
 evidence_note='Tier is evidence-screening priority, not measured tourism demand or a verified bookable service.',
 inegi_source='catun_municipio.zip/AGEEML_20268211656753_utf8.csv',
 infrastructure_source='project digest/data/interim/mart_infraestructura_municipio_veracruz.csv'))
write('municipalities_212.csv',municipalities)
write('destination_candidates.csv',[m for m in municipalities if m['candidate_for_research']])

# Source 2: complete 295-card index; a product can mention multiple municipalities.
products=read('tourism_cards_295.csv')
assert len(products)==295 and len({int(r['source_card_index']) for r in products})==295
cards=[]; product_links=[]
for r in products:
 idx=r['source_card_index']; cid=f'VCARD-{int(idx):03}'
 cards.append(dict(product_id=cid,source_card_index=idx,product_title_as_published=r['producto'],municipality_names_as_published=r['municipios'],
 source_snapshot=r['source_snapshot'],record_type='marketed_product_card',activity_inferred='NO',current_availability='not_checked'))
 for m in listpipe(r['municipios']):
  k=geo_id(m,'veracruz_products',cid)
  product_links.append(dict(link_id=jid(cid,m),product_id=cid,municipality_id=k,municipality=keyname.get(k,''),raw_municipality=m,
    geography_role='mentioned_in_marketed_itinerary_not_verified_site_location',activity_inferred='NO',source_snapshot=r['source_snapshot']))
write('tourism_products_295.csv',cards);write('tourism_product_municipality_links.csv',product_links)

# Source 3: official experience catalog, lossless row recovery. Many umbrella topics ARE NOT individual tours.
catstd=read('catalog_standard_rows_128.csv');catrec=read('catalog_recovered_rows_58.csv');catmanual=read('catalog_manually_verified_rows.csv');taxrows=read('catalog_taxonomy_32.csv')
tax={norm(r['source_section']):r for r in taxrows}
assert len(catstd)==128 and len(catrec)==58 and len(taxrows)==32
catrow=[]; seen=set()
for typ,records in [('standard_table',catstd),('nonstandard_table_recovered',catrec),('manually_verified_pdf_table',catmanual)]:
 for r in records:
  mun=r.get('municipality_raw',r.get('municipality',''))
  sect=r['section']; page=r['pdf_page']; f=r.get('source_file',r.get('source_filename',''))
  k=geo_id(mun,'tourism_catalog',f+':'+page)
  taxon=tax.get(norm(sect))
  if taxon is None:
   issues.append(dict(issue_type='taxonomy_unmapped',source='tourism_catalog',source_record=str(page),raw_value=sect,impact='tag blank',action='Review official section heading'))
  dedup=(k or norm(mun),norm(sect),page)
  if dedup in seen:
   issues.append(dict(issue_type='catalog_duplicate_row',source='tourism_catalog',source_record=f+':'+page,raw_value=mun+' / '+sect,impact='duplicate not counted as new municipality-activity link',action='Source row retained once'))
   continue
  seen.add(dedup)
  catrow.append(dict(catalog_record_id=jid('CAT',f,page,sect,mun),municipality_id=k,municipality=keyname.get(k,''),
       raw_municipality=mun,official_section=sect,raw_activity_tag=taxon['activity_tag'] if taxon else '',
       broad_family=taxon['broad_family'] if taxon else '',tag_specificity=taxon['tag_specificity'] if taxon else '',
       section_can_support_activity_tag=taxon['used_as_experience_feature'] if taxon else '',
       pdf_page=page,printed_pages=r.get('printed_spread',''),pdf_filename=f,
       extraction_type=typ,location_role='municipality_listed_in_section_not_verified_activity_site',
       provider_association='NOT_ESTABLISHED_FROM_DIRECTORY',publication_year='2025',
       current_availability='not_verified'))
write('official_catalog_municipality_sections.csv',catrow)

# Normalization is derived; never rewrite original text and never promote umbrella claims.
TAG_ALIAS={
 'mountain_hiking':('hiking','Mountain/high-altitude subtype; retain source wording, no parent-double-count'),
 'diving_or_snorkeling':('diving_or_snorkeling_undifferentiated','Publication says either/both; do not infer specific dive or snorkel'),
 'scuba_snorkeling':('diving_or_snorkeling_undifferentiated','Compound previous label cannot support separate subactivities'),
 'cultural_tours':('cultural_tour','Plural variation'),
 'craft_workshops':('artisan_workshop','Same activity class as artisan_workshop'),
 'archaeological_visits':('archaeological_visit','Plural variation'),
 'sea_turtle_conservation':('turtle_conservation_visit','Same source activity class'),
 'traditional_wellness':('traditional_wellness','Preserve traditional context'),
 'kayaking':('kayaking','Same activity'),
 'hiking':('hiking','Same activity'),
 'food_tasting_or_tour':('food_tasting_or_tour','Compound publication group, not atomically separated'),
 'nature_lodging':('','Accommodation attribute not a visitor activity'),
 'pueblo_magico':('','Administrative designation not visitor activity'),
 'ecotourism':('','Umbrella category not a specific activity'),
 'aquatic_experience':('','Umbrella category not a specific activity'),
 'multi_adventure_offer':('','Composite umbrella: does not prove three distinct services at each listed municipality'),
 'romance_tourism':('','Event/travel sector umbrella not specific activity'),
 'guided_excursion':('','Umbrella without a named activity'),
 'water_sports_unspecified':('','Activity type unspecified; cannot assign precise tag'),
 'nearby_access_only':('','Nearby access is not an activity at this municipality'),
}
# Specific past tags from prior structured research are kept as source identifiers.
prior=read('prior_55_evidence_879.csv')
assert len(prior)==879
known_tags={r['activity_tag'] for r in prior if r['activity_tag']}
alltags=sorted(known_tags|{r['activity_tag'] for r in taxrows if r['activity_tag']})
taxonomy=[]
section_tax={r['activity_tag']:r for r in taxrows}
for tag in alltags:
 p=section_tax.get(tag,{})
 canonical,why=TAG_ALIAS.get(tag,(tag,'Original specific tag retained; no inferred splitting'))
 if p.get('tag_specificity') in ('attribute','umbrella'):canonical=''
 # Prior broad cultural leads are not proof of an available tour.
 if tag.endswith('_lead') or tag in {'historic_landmark_lead','festival_or_living_tradition'}:
  # festivals are an experience type but status is LEAD, not current bookability
  if tag.endswith('_lead'):canonical=''
 taxonomy.append(dict(raw_activity_tag=tag,canonical_activity_tag=canonical,
     broad_family=p.get('broad_family','source-specific; see claim'),
     catalog_section=p.get('source_section',''),source_tag_specificity=p.get('tag_specificity','prior_source'),
     mapping_rule=why if tag in TAG_ALIAS else 'Retain literal evidence-tag; flag overlapping/ambiguous types for model-specific handling',
     is_direct_model_feature='1' if canonical else '0'))
write('activity_taxonomy.csv',taxonomy)
tagcanon={r['raw_activity_tag']:r['canonical_activity_tag'] for r in taxonomy}

# Source 4: typed, source-linked evidence. Do not inject marketed product titles as activities.
evidence=[]
def claim(*,source_type,source_id,municipality_id,raw_municipality,raw_activity,raw_tag,source_ref,source_page='',evidence_status='',geo_scope='',qualifier='',provider='',record_type='activity_or_experience',publication=''):
 tag=tagcanon.get(raw_tag,raw_tag)
 if record_type!='activity_or_experience':tag=''
 evidence.append(dict(claim_id=jid(source_type,source_id,raw_municipality,raw_activity,raw_tag),
 municipality_id=municipality_id,municipality=keyname.get(municipality_id,''),raw_municipality=raw_municipality,
 record_type=record_type,activity_or_feature_original=raw_activity,source_activity_tag=raw_tag,canonical_activity_tag=tag,
 evidence_status=evidence_status,geographic_scope=geo_scope,source_type=source_type,source_record_id=source_id,
 source_url_or_file=source_ref,source_page=source_page,published_or_review_date=publication,
 provider_name_as_published=provider,limitations=qualifier,
 current_availability='not_verified',evidence_of_absence='NO'))

for c in catrow:
 typ=c['tag_specificity']
 kind='activity_or_experience' if typ in ('specific','section_combined') and truth(c['section_can_support_activity_tag']) else 'catalog_category_or_attribute'
 claim(source_type='official_experience_catalog_2025',source_id=c['catalog_record_id'],municipality_id=c['municipality_id'],raw_municipality=c['raw_municipality'],
 raw_activity=c['official_section'],raw_tag=c['raw_activity_tag'],source_ref=c['pdf_filename'],source_page=c['printed_pages'],
 evidence_status='published_municipality_section',geo_scope=c['location_role'],publication='2025',record_type=kind,
 qualifier='Section-level municipality association; activity and provider may not be one-to-one; 2026 operation unverified.')

for p in prior:
 kind=p['record_kind']
 if kind in ('catalog_experience','catalog_attribute','tourism_product'):continue
 raw=p['destination']; k=geo_id(raw,'previous_s4_s8_evidence',p['evidence_id'])
 # A historical activity remains a historical LEAD in the data even if detailed.
 rectype='activity_or_experience'
 if kind=='prior_cultural_lead':rectype='cultural_lead'
 if kind=='prior_heritage_primary':rectype='heritage_site_lead'
 claim(source_type=kind,source_id=p['evidence_id'],municipality_id=k,raw_municipality=raw,
 raw_activity=p['activity_or_feature'],raw_tag=p['activity_tag'],source_ref=p['source_ref'],source_page=p['source_page'],
 evidence_status=p['evidence_status'],geo_scope=p['location_scope'],qualifier=p['description_or_limitation'],
 provider=p['provider_as_published'],record_type=rectype)

# Source 5: focused official URLs from the previous 212-municipality screen. Retain exact summary wording and status.
context=[]
for k,s in scope.items():
 examples=listpipe(s['official_new_evidence']);urls=listpipe(s['official_new_urls'])
 for idx,example in enumerate(examples):
  typ=example.split(':',1)[0].strip() if ':' in example else 'context'
  link=urls[0] if len(urls)==1 else '|'.join(urls)
  context.append(dict(context_id=jid(k,example),municipality_id=k,municipality=keyname[k],
       record_type=typ,summary_from_prior_research=example,source_url_or_urls=link,
       current_availability='not_verified',note='Previously researched official-page lead; not independently re-checked in this build'))
  if typ=='activity':
   claim(source_type='government_targeted_research_lead',source_id=jid(k,example),municipality_id=k,raw_municipality=keyname[k],
      raw_activity=example,raw_tag='',source_ref=link,
      evidence_status='official_activity_description_from_prior_screen_not_rechecked',
      geo_scope='municipality_narrative_not_individual_product_location',record_type='named_activity_lead',
      qualifier='Source summary may contain multiple activities. No atomic activity tags inferred without record-by-record verification.')
write('additional_official_source_leads.csv',context)
write('destination_activity_and_heritage_evidence.csv',evidence)

# Source 6: INAH physical site listing, not identical to tours advertised in the catalog.
inah_inventory={norm(r['nombre']):r for r in read('inah_original_inventory.csv') if 'veracruz' in norm(r['estado'])}
inah_map=[]
for k,s in scope.items():
 for site in listpipe(s['inah_sites']):
  entry=inah_inventory.get(norm(site))
  if not entry:
   issues.append(dict(issue_type='inah_site_not_found_in_original',source='INAH',source_record=k,raw_value=site,
                      impact='source site URL missing',action='Inspect original INAH inventory name before linking'))
  inah_map.append(dict(site_id=jid('INAH',k,site),municipality_id=k,municipality=keyname[k],
    site_name=site,record_type='archaeological_site',geography_role='physical_municipality_as_screened_from_INAH',
    inah_condition_as_published=entry['condicion'] if entry else '',
    inah_url=entry['url'] if entry else '',
    inah_physical_address_as_published=entry['ubicacion_fisica'] if entry else '',
    source='INAH_zonas_arqueologicas.csv (project digest); municipality audit',
    current_operating_status='not_reverified_in_this_build'))
write('inah_physical_site_register.csv',inah_map)

# Preserve named cultural features and prior adventure site/location strings unchanged,
# without automatically splitting narrative phrases into independent tourism locations.
place_mentions=[]
for r in read('s4_adventure_original_67.csv'):
    name=r['destino'];k=geo_id(name,'prior_adventure_place',r['id'])
    if not r['lugar_asociado'].strip():continue
    place_mentions.append(dict(mention_id=jid('AV',r['id']),municipality_id=k,municipality=keyname.get(k,''),
        source_kind='adventure_location_association',raw_place_or_feature=r['lugar_asociado'],
        linked_activity_or_tradition_as_published=r['actividad_concreta'],source_url=r['url_fuente'],
        source_record_id=r['id'],physical_location_verified='NOT_IN_THIS_BUILD',
        caution=r['nota_restriccion']))
for r in read('s8_cultural_catalog_55.csv'):
    name=r['destination'];k=geo_id(name,'prior_cultural_feature',name)
    if not r['cultural_feature'].strip():continue
    place_mentions.append(dict(mention_id=jid('CULT',name,r['cultural_feature']),municipality_id=k,municipality=keyname.get(k,''),
        source_kind='cultural_place_event_or_tradition_lead',raw_place_or_feature=r['cultural_feature'],
        linked_activity_or_tradition_as_published=r['activity_type'],source_url=r['source_urls'],
        source_record_id=name,physical_location_verified='NOT_IN_THIS_BUILD',caution=r['qualification']))
for r in inah_map:
    place_mentions.append(dict(mention_id=r['site_id'],municipality_id=r['municipality_id'],municipality=r['municipality'],
        source_kind='INAH_archaeological_site',raw_place_or_feature=r['site_name'],
        linked_activity_or_tradition_as_published='archaeological site',source_url='INAH project source inventory',
        source_record_id=r['site_id'],physical_location_verified='SOURCE_INAH_AS_PREVIOUSLY_SCREENED',
        caution='Physical municipality identified separately from catalog tour sales municipality'))
write('named_places_events_and_attraction_leads.csv',place_mentions)


# Source 7: source-level provider directory. No inferred provider / location / activity join.
provider=read('catalog_provider_blocks_275.csv')
assert len(provider)==275
providers=[]
for r in provider:
 providers.append(dict(provider_block_id=jid(r['source_file'],r['pdf_page'],r['provider_name_raw'],r['contact_block']),
   provider_name_as_published=r['provider_name_raw'],source_section=r['section'],source_pdf=r['source_file'],
   pdf_page=r['pdf_page'],contact_block_as_published=r['contact_block'],
   provider_activity_join='unknown',provider_municipality_join='unknown',
   provider_current_operation='not_verified',raw_extraction_confidence=r['confidence']))
write('catalog_provider_directory_blocks.csv',providers)

# Coverage and normalized observed-activity links: group claims, not evidence that non-observed tags are absent.
valid=[]
for e in evidence:
 if e['municipality_id'] and e['canonical_activity_tag'] and e['record_type']=='activity_or_experience':valid.append(e)
by=defaultdict(list)
for e in valid:by[(e['municipality_id'],e['canonical_activity_tag'])].append(e)
links=[]
for (k,t),ee in sorted(by.items()):
 links.append(dict(municipality_id=k,municipality=keyname[k],canonical_activity_tag=t,
   supporting_assertions=len(ee),source_types=' | '.join(sorted(set(v['source_type'] for v in ee))),
   original_activity_labels=' | '.join(sorted(set(v['activity_or_feature_original'] for v in ee))),
   evidence_claim_ids='|'.join(v['claim_id'] for v in ee),
   historical_or_tentative_assertions=sum(any(x in v['evidence_status'].casefold() for x in ('histor','competencia','potencial','en_estudio','plan_municipal','diagnostico')) for v in ee),
   published_2025_catalog_assertions=sum(v['source_type']=='official_experience_catalog_2025' for v in ee),
   strongest_supported_status='published_experience_section' if any(v['source_type']=='official_experience_catalog_2025' for v in ee) else 'older_or_qualified_documentary_activity',
   absence_of_other_activities='NOT_ASSESSED'))
write('municipality_observed_activity_links.csv',links)
act_by_m=defaultdict(set)
for l in links:act_by_m[l['municipality_id']].add(l['canonical_activity_tag'])
prod_by_m=Counter(v['municipality_id'] for v in product_links if v['municipality_id'])
cat_by_m=Counter(v['municipality_id'] for v in catrow if v['municipality_id'])
lead_by_m=Counter(v['municipality_id'] for v in evidence if v['record_type'] in ('cultural_lead','heritage_site_lead','named_activity_lead') and v['municipality_id'])
coverage=[]
for m in municipalities:
 k=m['municipality_id'];tags=sorted(act_by_m[k]); c=cat_by_m[k]
 coverage.append(dict(municipality_id=k,municipality=m['municipality'],candidate_for_research=m['candidate_for_research'],
 tourism_evidence_tier=m['tourism_evidence_tier'],observed_activity_tags_count=len(tags),
 observed_activity_tags=' | '.join(tags),official_catalog_municipality_rows=c,official_product_mentions=prod_by_m[k],
 separate_cultural_heritage_or_new_official_leads=lead_by_m[k],
 no_observed_activity_tags_means='UNKNOWN_NOT_NO_TOURISM' if not tags else '',
 current_availability='not_verified'))
write('destination_activity_coverage_212.csv',coverage)
write('candidate_experience_profiles.csv',[c for c in coverage if c['candidate_for_research']])

# Record unmatched rows in a separate ledger and prove referential integrity.
unresolved=[]
for c in catrow:
 if not c['municipality_id']:unresolved.append(dict(source='catalog',raw_municipality=c['raw_municipality'],source_id=c['catalog_record_id'],raw_value=c['official_section']))
for v in product_links:
 if not v['municipality_id']:unresolved.append(dict(source='product_card',raw_municipality=v['raw_municipality'],source_id=v['product_id'],raw_value=''))
for e in evidence:
 if not e['municipality_id']:unresolved.append(dict(source=e['source_type'],raw_municipality=e['raw_municipality'],source_id=e['source_record_id'],raw_value=e['activity_or_feature_original']))
write('unresolved_geographies.csv',unresolved,cols=['source','raw_municipality','source_id','raw_value'])
write('quality_exceptions.csv',issues,cols=['issue_type','source','source_record','raw_value','impact','action'])

# One compact manifest of source snapshots and transformations.
sources=[
 ('INEGI AGEEML municipality reference','inegi_ageeml_utf8.csv','Administrative ID/name/population; not tourism supply'),
 ('Project 212 municipality source screening','scope_212_prior.csv','Previously researched direct/contextual tourism evidence tiers; not a census of attractions'),
 ('Project DENUE municipal infrastructure mart','infra_212.csv','Business counts, not capacity or vacancy'),
 ('SECTUR Veracruz tourism product extract','tourism_cards_295.csv','295 marketed card titles with municipality mentions, not necessarily tour availability'),
 ('SECTUR 2025 experiences tables','catalog_standard_rows_128.csv','128 source table municipality rows'),
 ('SECTUR 2025 recovered tables','catalog_recovered_rows_58.csv','58 special-layout municipality rows'),
 ('SECTUR 2025 directly verified missing table','catalog_manually_verified_rows.csv','Los Reyes herpetology row on PDF spread 60–61'),
 ('SECTUR section taxonomy','catalog_taxonomy_32.csv','32 catalog section names and classifications'),
 ('Prior S4/S8 evidence with provenance','prior_55_evidence_879.csv','879 source assertions, filtered into distinct record types'),
 ('SECTUR published operator directory','catalog_provider_blocks_275.csv','275 contact blocks, not verified unique providers'),
 ('Original 55 destination reference','destination_reference_55.csv','Historical curated set, not a statistically optimal universe'),
 ('Prior catalog page text','catalog_page_text_66.csv','66 PDF page text extractions; source page numbers'),
]
manifest=[]
for label,f,purpose in sources:
 b=(IN/f).read_bytes(); manifest.append(dict(source_name=label,input_file='inputs/'+f,sha256=hashlib.sha256(b).hexdigest(),size_bytes=len(b),role=purpose))
write('source_manifest.csv',manifest)

stats={
 'official_veracruz_municipalities':len(municipalities),
 'working_research_candidates':sum(c['candidate_for_research'] for c in municipalities),
 'original_curated_municipalities':sum(c['initial_55'] for c in municipalities),
 'direct_evidence_municipalities':sum(c['tourism_evidence_tier']=='direct' for c in municipalities),
 'context_evidence_municipalities':sum(c['tourism_evidence_tier']=='contextual' for c in municipalities),
 'other_municipalities_without_screened_evidence':sum(c['tourism_evidence_tier']=='not_established' for c in municipalities),
 'original_tourism_product_cards':len(cards),
 'product_municipality_mentions':len(product_links),
 'official_catalog_table_rows_deduplicated':len(catrow),
 'catalog_rows_with_valid_municipal_id':sum(bool(r['municipality_id']) for r in catrow),
 'provider_contact_blocks_not_verified_unique':len(providers),
 'inah_sites_with_original_source_urls':sum(bool(x['inah_url']) for x in inah_map),
 'named_place_event_or_tradition_leads':len(place_mentions),
 'new_unified_typed_evidence_assertions':len(evidence),
 'documented_as_published_distinct_municipality_activity_links':len(links),
 'municipalities_with_one_or_more_observed_specific_activity_tags':sum(bool(t) for t in act_by_m.values()),
 'original_55_with_activity_tags':sum(bool(act_by_m[c['municipality_id']]) for c in municipalities if c['initial_55']),
 'working_candidates_with_activity_tags':sum(bool(act_by_m[c['municipality_id']]) for c in municipalities if c['candidate_for_research']),
 'geographically_unresolved_claims':len(unresolved),
 'qa_issue_count':len(issues),
 'full_tourist_activity_census':False,
 'current_bookability_checked':False,
}
assert len(municipalities)==212 and len(cards)==295 and len(providers)==275
assert len(coverage)==212
assert set(l['municipality_id'] for l in links)<=set(keyname)
assert {r['municipality_id'] for r in municipalities}==set(keyname)
assert sum(c['initial_55'] for c in municipalities)==55
(OUT/'validation_summary.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(stats,ensure_ascii=False,indent=2))
