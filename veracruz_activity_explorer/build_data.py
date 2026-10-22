#!/usr/bin/env python3
"""Build source-backed public activity cards from the *current* strict evidence export.

Never derive the catalog from legacy S4 cluster files. The photographs currently
available are editorially curated, not inferred from loose image-name matches.
"""
import collections
import hashlib
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent

FEATURED = [
    'paper_balloon_workshop','backstrap_loom_weaving','leather_shoemaking_demonstration',
    'vanilla_extract_workshop','coffee_farm_visit','birdwatching','rafting',
    'kayaking','hiking','archaeological_visit','waterfall_visit','coffee_tasting',
    'mangrove_excursion','sandboarding','traditional_cooking_workshop','snorkeling',
]

DESCRIPTIONS = {
    'paper_balloon_workshop': ('Conoce la elaboración artesanal de globos de papel y verifica los horarios de los talleres.', 'Explore the craft of paper balloons; check workshop access and dates.'),
    'backstrap_loom_weaving': ('Acércate al trabajo artesanal con telar de cintura. Consulta si se reciben visitantes.', 'Learn about backstrap-loom weaving; confirm whether visitors are welcomed.'),
    'leather_shoemaking_demonstration': ('Descubre la elaboración artesanal de calzado; disponibilidad sujeta a cada taller.', 'Explore artisan shoemaking; workshop access depends on the provider.'),
    'vanilla_extract_workshop': ('Conoce actividades relacionadas con la vainilla y su transformación local.', 'Explore vanilla-related workshops and local processing traditions.'),
    'coffee_farm_visit': ('Visitas vinculadas con el cultivo del café; confirma qué fincas reciben visitantes.', 'Explore coffee-growing experiences; check which farms accept visits.'),
    'birdwatching': ('Busca lugares con observación de aves documentada; lleva equipo adecuado y respeta el entorno.', 'Find documented birdwatching experiences; travel responsibly.'),
    'rafting': ('Experiencias de descenso de río documentadas; confirma guía, nivel y condiciones del agua.', 'Explore documented river-rafting activities; verify guides and river conditions.'),
    'kayaking': ('Opciones documentadas para remar en kayak; comprueba acceso, equipo y condiciones.', 'Find documented kayaking experiences; verify access, equipment and conditions.'),
    'hiking': ('Explora experiencias de senderismo documentadas y confirma accesos y dificultad.', 'Explore documented hiking experiences; check trail access and difficulty.'),
    'archaeological_visit': ('Patrimonio arqueológico documentado; verifica horarios de cada sitio.', 'Discover documented archaeological heritage; verify opening hours.'),
    'waterfall_visit': ('Explora cascadas documentadas; revisa accesos, seguridad y temporada.', 'Find documented waterfall visits; verify access, safety and seasonality.'),
    'coffee_tasting': ('Degustaciones de café documentadas; las reservas y precios dependen del operador.', 'Discover documented coffee tastings; availability and prices depend on providers.'),
    'mangrove_excursion': ('Recorridos vinculados con ecosistemas de manglar; privilegia operadores responsables.', 'Explore documented mangrove excursions; choose responsible operators.'),
    'sandboarding': ('Experiencias documentadas de deslizamiento en dunas; confirma equipo y acceso.', 'Find documented sandboarding activities; verify equipment and access.'),
    'traditional_cooking_workshop': ('Talleres de cocina tradicional documentados; consulta fechas y participación.', 'Explore documented traditional cooking workshops; confirm dates and participation.'),
    'snorkeling': ('Experiencias de esnórquel documentadas; confirma temporada, seguridad y equipo.', 'Discover documented snorkeling; check conditions and equipment.'),
}

FAMILY_NAMES = {
    'food_agriculture': ['Gastronomía y campo','Food & agriculture','食・農業'],
    'history_culture': ['Historia y cultura','History & culture','歴史・文化'],
    'land_adventure': ['Aventura terrestre','Land adventure','陸上アクティビティ'],
    'nature_observation': ['Naturaleza','Nature','自然'],
    'other_specific_unclassified': ['Experiencias singulares','Distinctive experiences','特別な体験'],
    'scenic_transport': ['Paseos y recorridos','Scenic journeys','周遊・乗り物'],
    'traditional_crafts': ['Artesanías','Traditional crafts','工芸'],
    'water_adventure': ['Agua y ríos','Water & rivers','水辺・川'],
    'wellness_spiritual': ['Bienestar y tradiciones','Wellness & traditions','ウェルネス・伝統'],
}

def create_art(feature_id, family):
    import colorsys
    from html import escape
    digest=hashlib.sha256(feature_id.encode()).digest()
    hue=(int.from_bytes(digest[:2],'big')/65535)
    r1,g1,b1=colorsys.hls_to_rgb(hue,.31,.47)
    r2,g2,b2=colorsys.hls_to_rgb((hue+.11)%1,.55,.40)
    def rgb(r,g,b): return f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
    bg1=rgb(r1,g1,b1); bg2=rgb(r2,g2,b2)
    family_icon = {
      'water_adventure':'M 150 230 Q 220 175 290 230 T 430 230 T 570 230 M 130 300 Q 210 250 290 300 T 450 300 T 590 300',
      'land_adventure':'M 145 330 L 260 160 L 350 270 L 435 135 L 580 330 Z',
      'nature_observation':'M 350 330 V 115 M 350 155 C 190 100 185 270 350 260 M 350 175 C 515 85 555 265 350 285',
      'traditional_crafts':'M 200 165 H 505 V 335 H 200 Z M 260 160 V 340 M 325 160 V 340 M 395 160 V 340 M 465 160 V 340 M 200 210 H 505 M 200 265 H 505',
      'food_agriculture':'M 280 205 C 230 145 360 120 325 68 M 375 205 C 330 130 460 120 410 68 M 175 220 H 500 L 460 330 H 220 Z',
      'history_culture':'M 165 180 L 350 105 L 535 180 M 200 190 V 325 M 280 190 V 325 M 420 190 V 325 M 500 190 V 325 M 170 330 H 530',
      'scenic_transport':'M 165 260 C 240 175 395 345 560 160 M 180 310 H 520 M 220 290 L 260 330 M 450 290 L 490 330',
      'wellness_spiritual':'M 350 315 C 270 240 270 190 350 140 C 430 190 430 240 350 315 M 350 300 Q 230 185 195 215 M 350 300 Q 470 185 505 215',
      'other_specific_unclassified':'M 350 115 L 390 215 L 495 235 L 410 300 L 435 380 L 350 335 L 265 380 L 290 300 L 205 235 L 310 215 Z',
    }.get(family,'M 160 325 H 540')
    art=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 420" role="img" aria-label="Ilustración conceptual, no fotografía">
    <defs><linearGradient id="grad" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{bg1}"/><stop offset="1" stop-color="{bg2}"/></linearGradient></defs>
    <rect width="700" height="420" fill="url(#grad)"/>
    <circle cx="618" cy="75" r="135" fill="#ffffff" opacity="0.12"/>
    <circle cx="80" cy="375" r="130" fill="#ffffff" opacity="0.10"/>
    <path d="{escape(family_icon)}" fill="none" stroke="#ffffff" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" opacity="0.92"/>
    <path d="M 85 365 H 615" stroke="#ffffff" stroke-width="3" opacity="0.4"/>
    </svg>'''
    return art


def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument('--site',required=True)
    args=ap.parse_args()
    site=Path(args.site)
    source=json.loads((site/'data/interest_evidence.json').read_text(encoding='utf-8'))
    if source.get('total_links')!=216 or len(source.get('records',[]))!=216:
        raise SystemExit('Unexpected strict evidence version; refusing to use legacy or partial catalog')
    mapjs=(site/'js/map-explorer.js').read_text(encoding='utf-8')
    tr=re.search(r'const activityEs = \{(.*?)\};',mapjs,re.S)
    if not tr: raise SystemExit('Missing translations in map-explorer.js')
    trans=dict(re.findall(r"'([^']+)':'([^']*)'",tr.group(1)))
    grouped=collections.defaultdict(list)
    for row in source['records']:
        grouped[row['feature_id']].append(row)
    photos = json.loads((site/'data/attractions.geojson').read_text(encoding='utf-8'))['features']
    selected_photo_by_feature = {
        'archaeological_visit': 'El Tajín',
        'waterfall_visit': 'Cascada de Texolo',
        'fortress_visit': 'San Juan de Ulúa',
    }
    selected_photos = {}
    for feature in photos:
        prop = feature.get('properties', {})
        for feature_id, place_name in selected_photo_by_feature.items():
            if prop.get('name') == place_name and prop.get('photo_url') and prop.get('photo_source_url'):
                selected_photos[feature_id] = {
                  'url':prop['photo_url'], 'source':prop['photo_source_url'],
                  'caption':f"{place_name} ({prop.get('municipality', 'Veracruz')}) · {prop.get('photo_credit', 'Wikimedia Commons')}",
                  'alt':f"Fotografía de {place_name}, {prop.get('municipality','Veracruz')}",
                }
    all_cards=[]
    artdir=BASE/'site/assets/activity-illustrations'
    artdir.mkdir(parents=True,exist_ok=True)
    for feature_id,records in grouped.items():
        if feature_id not in trans: raise SystemExit(f'Activity label translation missing: {feature_id}')
        region=records[0]['family']; label_es=trans[feature_id]
        short_es,short_en=DESCRIPTIONS.get(feature_id,(
            f'Experiencia documentada en la fuente turística. Consulta los municipios y las condiciones de acceso.',
            f'Documented experience in the tourism evidence. Check municipalities and access conditions.',
        ))
        places=[]
        for r in records:
            places.append({'municipality_id':r['municipality_id'], 'name':r['municipality'],
                           'original_text_support':bool(r['original_text_support']),
                           'source_urls':r['source_urls'][:3]})
        places.sort(key=lambda p:(not p['original_text_support'],p['name'].casefold()))
        artname=f'{feature_id}.svg'
        (artdir/artname).write_text(create_art(feature_id,region),encoding='utf-8')
        all_cards.append({
           'feature_id':feature_id, 'label_es':label_es,'label_en':records[0]['label_en'],
           'family':region,'description_es':short_es,'description_en':short_en,
           'media_url':f'assets/activity-illustrations/{artname}',
           'media_kind':'illustration', 'photo':selected_photos.get(feature_id), 'municipality_count':len({r['municipality_id'] for r in records}),
           'source_support_count':sum(bool(r['original_text_support']) for r in records),
           'municipalities':places,
        })
    all_cards.sort(key=lambda c: (c['feature_id'] not in FEATURED, FEATURED.index(c['feature_id']) if c['feature_id'] in FEATURED else 999, c['label_es'].casefold()))
    payload={'schema':'veracruz_activity_cards_v1','source':'site/data/interest_evidence.json',
             'kind':'documented_activity_types_not_clusters', 'counts':{'activities':len(all_cards),'links':len(source['records']), 'municipalities':len({r['municipality_id'] for r in source['records']})},
             'families':FAMILY_NAMES,'cards':all_cards,
             'caveat':'Documentary evidence only: no assurance of access, present availability, booking, price or popularity.'}
    out=BASE/'site/data/activity_cards.json'
    out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Built {len(all_cards)} cards, {len(source["records"])} evidence links, {len(list(artdir.glob("*.svg")))} illustrations')

if __name__=='__main__':main()
