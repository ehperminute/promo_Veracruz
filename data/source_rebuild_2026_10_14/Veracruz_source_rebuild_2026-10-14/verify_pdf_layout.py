"""Independently compare frozen municipality-chapter links to the seven original PDF pages.
Pass --pdf-dir to directory containing original split PDF files. Uses PyMuPDF.
"""
from pathlib import Path
import csv,fitz,unicodedata,re,argparse,json,hashlib

ROOT=Path(__file__).resolve().parent

def tokens(s):
 s=''.join(ch for ch in unicodedata.normalize('NFKD',str(s).lower()) if not unicodedata.combining(ch))
 return re.findall(r'[a-z0-9]+',s)
def find_coord(words,raw_name):
 query=tokens(raw_name)
 if not query:return False
 for i,w in enumerate(words):
  if tokens(w[4])==[query[0]]:
   ay=w[1];pos=1
   if pos==len(query):return True
   for other in words[i+1:]:
    if other[1]-ay>28:break
    if tokens(other[4])==[query[pos]]:
     pos+=1
     if pos==len(query):return True
 return False

def main(pdf_dir):
 with open(ROOT/'base/output/official_catalog_municipality_sections.csv',encoding='utf-8-sig',newline='') as f:raw=list(csv.DictReader(f))
 check=[];cache={};checksums={}
 for row in raw:
  source=row['pdf_filename'];page=int(row['pdf_page'])
  if source not in cache:
   cache[source]=fitz.open(pdf_dir/source)
   checksums[source]=hashlib.sha256((pdf_dir/source).read_bytes()).hexdigest()
  pdf=cache[source]
  w=pdf[(page-1)%10].get_text('words')
  text=pdf[(page-1)%10].get_text('text')
  all_words=[x for x in w if x[4]=='MUNICIPIO']
  if not all_words:status='no_municipio_table_header'
  else:
   h=all_words[0]
   loc=[x for x in w if h[0]-22 < x[0] < h[0]+72 and x[1]>h[1]+12]
   loc.sort(key=lambda x:(round(x[1]/2),x[0]))
   # Some spread pages put a second municipality table in the right-hand half without a second header.
   right=[x for x in w if 645<x[0]<765 and x[1]>55];right.sort(key=lambda x:(round(x[1]/2),x[0]))
   status='municipality_tokens_found_in_pdf_municipio_column' if (find_coord(loc,row['raw_municipality']) or find_coord(right,row['raw_municipality'])) else 'shortened_or_unmatched_label'
  if status=='shortened_or_unmatched_label':
   if row['raw_municipality']=='Las Vigas de Ramírez' and 'Las Vigas' in text:status='document_uses_shortened_name_Las_Vigas'
   elif row['raw_municipality'].startswith('Camerino Z.') and 'Camerino Z.' in text and 'Mendoza' in text:status='document_splits_Camerino_Z_Mendoza_over_two_lines'
  check.append(dict(catalog_record_id=row['catalog_record_id'],pdf_file=source,pdf_page_in_part=(page-1)%10+1,
    official_section=row['official_section'],municipality_id=row['municipality_id'],raw_label=row['raw_municipality'],
    pdf_column_status=status,source_pdf_sha256=checksums[source]))
 for d in cache.values():d.close()
 result=ROOT/'deliverables'/'PDF_TABLE_GEOGRAPHY_VERIFICATION.csv'
 with result.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(check[0]));w.writeheader();w.writerows(check)
 from collections import Counter
 totals=Counter(x['pdf_column_status'] for x in check)
 print(json.dumps(totals,ensure_ascii=False,indent=2))
 assert len(check)==187
 assert not any(s in totals for s in ('no_municipio_table_header','shortened_or_unmatched_label'))
 vpath=ROOT/'deliverables'/'VALIDATION.json'
 v=json.loads(vpath.read_text(encoding='utf-8'))
 v.update({'catalog_pdf_table_rows_checked_against_original_pdf':len(check),
 'catalog_pdf_table_coordinate_matches':totals['municipality_tokens_found_in_pdf_municipio_column'],
 'catalog_pdf_table_source_uses_shortened_alias':totals['document_uses_shortened_name_Las_Vigas'],
 'unresolved_pdf_catalog_municipality_associations':0,
 'initial_page_text_string_matching_warnings':v.pop('source_mapping_warnings',v.get('initial_page_text_string_matching_warnings',0)),
 'validated':'integrity_and_table_geography_checks_passed; does_NOT mean attraction_census_complete'})
 vpath.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--pdf-dir',default='/mnt/data');main(Path(a.parse_args().pdf_dir))
