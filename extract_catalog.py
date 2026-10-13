import fitz,glob,csv,re,json,collections,os
from pathlib import Path
BASE=Path(__file__).resolve().parent
files=sorted(glob.glob('/mnt/data/veracruz_catalogo_de_experiencias_web-*.pdf'))
sections={4:'Artesanía',6:'Aviturismo',8:'Buceo y snorkel',10:'Cabalgata',12:'Camping',14:'Cañonismo',16:'Bici tour',18:'City tour',20:'Cuatrimotos',22:'Ecoturismo',24:'Entorno acuático',26:'Excursiones',28:'Gastronomía',30:'Herpetología',31:'Descanso natural / hospedaje',33:'Kayak',35:'Liberación de tortugas',36:'Paraísos indígenas',38:'Parapente',40:'Pesca',42:'Pueblos mágicos',44:'Rafting, rápel y tirolesa',46:'Recorrido cultural',49:'Ruta del café',51:'Sanación ancestral',53:'Sandboarding',54:'Senderismo',56:'Senderismo de montaña',58:'Turismo de romance',60:'Turismo orquideófilo',62:'Turismo religioso',64:'Zonas arqueológicas'}
def current_section(page):
 n=max((n for n in sections if n<=page),default=0)
 return sections.get(n,'Portada/introducción')
def save(name,rows,fields):
 with open(BASE/name,'w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
blocks=[];pages=[]; municipalities=[]; operators=[]; needs=[]
for f in files:
 d=fitz.open(f)
 for idx,p in enumerate(d):
  page=sum(int(re.search(r'-(\d+)-(\d+)\.pdf',x).group(2))-int(re.search(r'-(\d+)-(\d+)\.pdf',x).group(1))+1 for x in files[:files.index(f)])+idx+1
  section=current_section(page);texts=p.get_text('text',sort=True)
  pages.append(dict(pdf_page=page,section=section,source_file=Path(f).name,source_page=idx+1,printed_spread=f'{2*page-2}-{2*page-1}',text=texts))
  bl=p.get_text('blocks')
  for k,b in enumerate(bl):
   if len(b)<5 or not b[4].strip():continue
   x0,y0,x1,y1=map(lambda v:round(float(v),1),b[:4]);s=b[4].strip()
   blocks.append(dict(pdf_page=page,section=section,block_idx=k,x0=x0,y0=y0,x1=x1,y1=y1,text=s))
  # Municipality rows are usually right-hand tabular columns; pick the beginning of each municipality cell based on first bullet and terrestrial connectivity language.
  for k,b in enumerate(bl):
   if len(b)<5:continue
   x0,y0,x1,y1=b[:4]; s=b[4].strip()
   if not (x0>=610 and y0<670 and y1<720):continue
   if 'CDMX' not in s and 'Aeropuerto' not in s and 'aeropuerto' not in s:continue
   if '•' not in s and '·' not in s:continue
   # first bullet separates municipality from connectivity; avoid air-only columns
   lead=re.split(r'[•·]',s,1)[0].strip().replace('\n',' ')
   if not lead or len(lead)>55 or any(v in lead.lower() for v in ['cdmx','aeropuerto','conectividad','veracruz “','heriberto','internacional']): continue
   # Only a municipality first cell generally starts left of 900; some layouts vary
   if x0>930:continue
   # Find nearby right-side blocks on same row (potential multi-line provider lists)
   ymid=(y0+y1)/2
   nearby=[bb[4].strip() for bb in bl if len(bb)>=5 and bb is not b and bb[0]>x0+145 and abs(bb[1]-y0)<18 and bb[1]<530 and 'DIRECTORIO' not in bb[4] and 'CONECTIVIDAD' not in bb[4]]
   municipalities.append(dict(pdf_page=page,printed_spread=f'{2*page-2}-{2*page-1}',section=section,municipality_raw=lead,access_text=s,adjacent_table_text=' | '.join(nearby),source_file=Path(f).name,confidence='extracted_review_needed'))
  # Provider contact blocks; need to keep phone and social handle, and exclude municipality rows
  for k,b in enumerate(bl):
   if len(b)<5:continue
   x0,y0,x1,y1=b[:4];s=b[4].strip()
   if not( y0>140 and ('FB:' in s or 'IG:' in s or 'Tel.' in s or 'Cel.' in s or '@' in s) and len(s)>18): continue
   if 'CDMX' in s or 'Aeropuerto' in s:continue
   lines=s.splitlines(); head=lines[0].strip()
   if head.lower().startswith(('fb:','ig:','tel.','cel.','www.','http','x:','tw:','@')):head='[continued block]'
   operators.append(dict(pdf_page=page,section=section,provider_name_raw=head,contact_block=s,source_file=Path(f).name,confidence='directory_block_review_needed'))
save('catalog_full_text_pages.csv',pages,['pdf_page','section','source_file','source_page','printed_spread','text'])
save('catalog_all_text_blocks.csv',blocks,['pdf_page','section','block_idx','x0','y0','x1','y1','text'])
save('catalog_municipality_rows.csv',municipalities,['pdf_page','printed_spread','section','municipality_raw','access_text','adjacent_table_text','source_file','confidence'])
save('catalog_provider_contacts.csv',operators,['pdf_page','section','provider_name_raw','contact_block','source_file','confidence'])
save('catalog_sections.csv',[dict(section=x,start_pdf_page=n,end_pdf_page=(list(sections.keys())[i+1]-1 if i+1<len(sections) else 66),printed_page_start=2*n-2) for i,(n,x) in enumerate(sections.items())],['section','start_pdf_page','end_pdf_page','printed_page_start'])
print('pages',len(pages),'blocks',len(blocks),'municipalities',len(municipalities),'providers',len(operators))
print('municipality samples',[(r['pdf_page'],r['municipality_raw']) for r in municipalities[:20]])
print('provider samples',[(r['pdf_page'],r['provider_name_raw']) for r in operators[:12]])
