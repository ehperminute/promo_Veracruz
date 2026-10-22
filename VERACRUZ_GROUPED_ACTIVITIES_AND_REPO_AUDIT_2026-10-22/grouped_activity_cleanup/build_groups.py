#!/usr/bin/env python3
"""Reorganize the current 78 activity records into sections with >=2 items.
Does not change the activity table, evidence relationships, clusters, or canonical SQLite.
"""
import json
from pathlib import Path
from urllib.parse import quote

ROOT=Path(__file__).resolve().parent
SRC=ROOT/'site/data/activity_cards.json'
DST=ROOT/'site/data/activity_sections.json'

# Every image is a specific editorial documentary photograph, with its source and credit.
# The photograph represents ONE example of the section, not every record in it.
PHOTO_SPECS={
  'food_agriculture': ('Café la onza.jpg','https://commons.wikimedia.org/wiki/File:Caf%C3%A9_la_onza.jpg','Koffermejia','CC BY-SA 4.0','Café en Coatepec, Veracruz'),
  'history_culture': ('El Tajin.JPG','https://commons.wikimedia.org/wiki/File:El_Tajin.JPG','Ismamq','CC BY-SA 3.0','Zona arqueológica de El Tajín, Veracruz'),
  'land_adventure': ('Tirolesa en Veracruz Jalcomulco.jpg','https://commons.wikimedia.org/wiki/File:Tirolesa_en_Veracruz_Jalcomulco.jpg','Claudiafroilan','CC BY-SA 4.0','Tirolesa en Jalcomulco, Veracruz'),
  'nature_observation': ('Cascada_texolo.jpg','https://commons.wikimedia.org/wiki/File:Cascada_texolo.jpg','Jonathan UG','CC BY-SA 4.0','Cascada de Texolo, Xico'),
  'other_specific_unclassified': ('XIII Concurso de Globos de Papel de China (4072996750).jpg','https://commons.wikimedia.org/wiki/File:XIII_Concurso_de_Globos_de_Papel_de_China_%284072996750%29.jpg','Eneas De Troya','CC BY 2.0','Globo artesanal elaborado por un equipo de Zozocolco; foto tomada en Ohtenco, CDMX'),
  'traditional_crafts': ('SEMILLEROS CREATIVOS 18 - Muestra de Verano Ricardo Flores Magón Semillero Creativo Telar de Cintura y zapateado Oteapan Veracruz DSC08463.jpg','https://commons.wikimedia.org/wiki/File:SEMILLEROS_CREATIVOS_18_-_Muestra_de_Verano_Ricardo_Flores_Mag%C3%B3n_Semillero_Creativo_Telar_de_Cintura_y_zapateado_Oteapan_Veracruz_DSC08463.jpg','Complejo Cultural los Pinos','CC BY 2.0','Proyecto de telar de cintura en Oteapan, Veracruz'),
  'water_adventure': ('Rafting Rio Salvaje.JPG','https://commons.wikimedia.org/wiki/File:Rafting_Rio_Salvaje.JPG','Kiubu','Public domain','Rafting en Jalcomulco, Veracruz'),
  'wellness_spiritual': ('Nanciyaga27.JPG','https://commons.wikimedia.org/wiki/File:Nanciyaga27.JPG','AlejandroLinaresGarcia','CC BY-SA 3.0','Temazcal de la Reserva Ecológica Nanciyaga, Catemaco'),
}

MERGED={'scenic_transport':'land_adventure'}
NAMES={
'land_adventure':['Aventura terrestre y recorridos','Land adventures & excursions','陸の冒険・周遊'],
}

def main():
 data=json.loads(SRC.read_text(encoding='utf-8'))
 assert data['counts']['activities']==78 and data['counts']['links']==216
 grouped={}
 for activity in data['cards']:
  category=MERGED.get(activity['family'],activity['family'])
  grouped.setdefault(category,[]).append(activity)
 for cat in grouped:
  grouped[cat].sort(key=lambda a:(a['label_es'].casefold(),a['feature_id']))
 sections=[]
 for category, items in sorted(grouped.items()):
  assert len(items)>1, (category,len(items))
  name,source,author,license,caption=PHOTO_SPECS[category]
  sections.append({
    'id':category,
    'labels':NAMES.get(category,data['families'][category]),
    'photo':{
       'url':'https://commons.wikimedia.org/wiki/Special:FilePath/'+quote(name,safe='')+'?width=900',
       'source_url':source,'credit':author+' · '+license,'caption_es':caption,
       'caption_en':caption,
       'note':'Real documentary photograph illustrating one example of the theme, not every place/activity listed.',
    },
    'activities':items,
    'activity_count':len(items),
  })
 out={'schema':'veracruz_activity_sections_v1','based_on':data['source'],
      'research_scope':'216 accepted links, 78 specific activity types; grouping is navigation only, not clustering.',
      'photo_policy':'Commons source-linked representative photographs; some photographed events occurred outside Veracruz even when made by Veracruz artisans; check each caption.',
      'sections':sections,'counts':{'sections':len(sections),'activities':sum(len(x['activities']) for x in sections),'links':216}}
 assert out['counts']['sections']==8 and out['counts']['activities']==78
 DST.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print('Sections:',[(x['id'],x['activity_count']) for x in sections])
 print('Groups:',out['counts'])

if __name__=='__main__':main()
