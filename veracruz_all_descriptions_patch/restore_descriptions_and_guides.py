#!/usr/bin/env python3
"""Recover all 295 official product descriptions, then enrich the existing map guides.

Never edits the source-first master. Missing original source = hard stop: no site files changed.
The exported website holds short previews, attribution, and links (not duplicated full articles).
The complete source text is retained in a separate local SQLite and CSV for research.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys

BASE=Path(__file__).resolve().parent
PRODUCTS_URL='https://veracruz.mx/productos.php'


def trimmed(text, maxchars=330):
    text=re.sub(r'\s+',' ',str(text or '')).strip()
    if len(text) <= maxchars: return text
    cut=text[:maxchars].rsplit(' ',1)[0]
    return (cut if cut else text[:maxchars])+'…'


def build_guides(conn, features, present):
    out={}
    claim_products={}
    for cid,pid in conn.execute('select claim_id,product_id from official_product_claim_links'):
        claim_products.setdefault(cid,set()).add(pid)
    original={}
    for row in conn.execute('''SELECT r.product_id,p.title_as_published,r.description_text_original,
         r.municipality_heading_original,r.status,e.source_url
         FROM original_product_description_recovery r
         JOIN catalog_product_cards p USING(product_id)
         JOIN official_product_evidence e USING(product_id)'''):
        original[row[0]]={'title':row[1],'description':row[2], 'municipalities':row[3],
                          'status':row[4],'source_url':row[5]}
    for f in features:
        p=f['properties']; mid=str(p['municipality_id'])
        for a in p.get('activities',[]):
            activity=str(a['id']);key=mid+'::'+activity
            entry=dict(present.get(key,{"article":{},"source_phrases":[],"source_urls":a.get('source_urls',[])}))
            ids=sorted({product_id for claim in a.get('claim_ids',[]) for product_id in claim_products.get(claim,[])})
            product_list=[]
            for pid in ids:
                row=original[pid]
                if row['status']!='original_restored' or not row['description']:raise RuntimeError('Unrestored product '+pid)
                product_list.append({
                    'product_id':pid,
                    'title':row['title'],
                    'original_preview_es':trimmed(row['description']),
                    'source_url':row['source_url'],
                    'source_scope':'Official tourism-product description; may cover more than this municipality'
                })
            entry['official_products']=product_list[:5]
            entry['original_source_coverage']='linked_original_web_description' if product_list else (
                 'catalog_excerpt' if entry.get('has_original') else 'other_source_evidence')
            entry['original_full_text_archived_locally']=bool(product_list)
            out[key]=entry
    return out


def with_addon(html_text):
    """Include a separate guide module; never patch or replace map-explorer.js."""
    if 'veracruz-guide-originals-addon.js' in html_text:
        return html_text, False
    tag = ('\n<link rel="stylesheet" href="css/veracruz-guide-originals.css">\n'
           '<script defer src="js/veracruz-guide-originals-addon.js"></script>\n')
    matches = list(re.finditer(r'</body\s*>', html_text, re.IGNORECASE))
    if not matches:
        raise RuntimeError('site/index.html has no closing body tag; site untouched')
    loc = matches[-1].start()
    return html_text[:loc] + tag + html_text[loc:], True


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('repo',nargs='?',default='.',help='promo_Veracruz repository root')
    ap.add_argument('--html',help='Optional exact October 6 HTML snapshot (preferred)')
    args=ap.parse_args();repo=Path(args.repo).resolve()
    site=repo/'site';geo=site/'data/map_points.geojson';notes_path=site/'data/map_guide_notes.json';js=site/'js/map-explorer.js';index=site/'index.html'
    if not geo.is_file() or not js.is_file() or not index.is_file():
        sys.exit('Error: site/index.html, site/data/map_points.geojson and site/js/map-explorer.js are required.')
    features=json.loads(geo.read_text(encoding='utf-8'))['features']
    n_pairs=sum(len(x['properties'].get('activities',[])) for x in features)
    if n_pairs!=216:sys.exit(f'Unexpected geographic data: expected 216 activity entries, found {n_pairs}; site not changed.')
    # Only add external script and CSS to homepage; never inspect or change map-explorer.js.
    original_html=index.read_text(encoding='utf-8');patched_html,needed=with_addon(original_html)
    present=json.loads(notes_path.read_text(encoding='utf-8')) if notes_path.is_file() else json.loads((BASE/'assets/map_guide_notes_latest.json').read_text(encoding='utf-8'))
    restored_dir=repo/'data/recovered_source_descriptions';restored_dir.mkdir(parents=True,exist_ok=True)
    db=restored_dir/'veracruz_pp3_master_with_originals.sqlite'
    source=BASE/'assets/veracruz_pp3_master_source_first.sqlite'
    if not source.is_file():sys.exit('Missing bundled source-first database')
    def complete_restoration(path):
        if not path.is_file():return False
        try:
            with sqlite3.connect(path) as check:
                return check.execute("select count(*) from original_product_description_recovery where status='original_restored'").fetchone()[0]==295
        except sqlite3.DatabaseError:
            return False
    if not complete_restoration(db):
        shutil.copy2(source,db)
        cmd=[sys.executable,str(BASE/'tools/restore_all_original_products.py'),'--db',str(db),'--out',str(restored_dir/'restoration_audit')]
        if args.html:cmd+=['--html',str(Path(args.html).resolve())]
        print('Recovering original descriptions; all 295 must match before website changes...',flush=True)
        subprocess.run(cmd,check=True)
    else:
        print('Reusing previously verified 295-product restoration; no network fetch needed.',flush=True)
    conn=sqlite3.connect(db)
    try:
        n=conn.execute("select count(*) from original_product_description_recovery where status='original_restored'").fetchone()[0]
        if n!=295: raise RuntimeError(f'Only {n} of 295 originals restored; website files untouched')
        new_notes=build_guides(conn,features,present)
        if len(new_notes)!=216:raise RuntimeError('guide list incomplete')
    finally:conn.close()
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    # Write to temporary files before swapping; existing files always backed up.
    for path in [notes_path,index, site/'js/veracruz-guide-originals-addon.js',site/'css/veracruz-guide-originals.css']:
        if path.exists():shutil.copy2(path,path.with_name(path.name+'.before-source-restore-'+stamp))
    notes_path.write_text(json.dumps(new_notes,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    shutil.copy2(BASE/'assets/veracruz-guide-originals-addon.js',site/'js/veracruz-guide-originals-addon.js')
    shutil.copy2(BASE/'assets/veracruz-guide-originals.css',site/'css/veracruz-guide-originals.css')
    if needed:index.write_text(patched_html,encoding='utf-8')
    report={'all_original_product_descriptions':295,'published_map_guides':len(new_notes),
            'guides_with_direct_official_product_text':sum(bool(n['official_products']) for n in new_notes.values()),
            'guides_using_other_evidence':sum(not n['official_products'] for n in new_notes.values()),
            'full_original_text_database':str(db),'static_site_guide_data':str(notes_path),
            'homepage_script_tag_added':needed,'map_explorer_js_untouched':True,'generated_at_utc':stamp,
            'important':'Original source text is Spanish; the existing short English guides remain editorial summaries. Multi-municipality packages may reference other towns.'}
    (restored_dir/'MAP_GUIDE_RESTORATION_REPORT.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print('\nSUCCESS\n'+json.dumps(report,indent=2,ensure_ascii=False))

if __name__=='__main__':
    try:main()
    except Exception as e:sys.exit('RESTORATION FAILED — site files unchanged until final installation phase: '+str(e))
