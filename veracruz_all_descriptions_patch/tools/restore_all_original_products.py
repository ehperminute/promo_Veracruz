#!/usr/bin/env python3
"""Restore ORIGINAL Veracruz tourism-product narratives to the existing master.

No synthesized/translated text is ever written to an original-source column.
Usage: python restore_all_original_products.py --db veracruz_pp3_master.sqlite
Prefers the historical repository snapshot, falls back to fetching the live page.
Requires requests and beautifulsoup4. Every one of the 295 card titles must align
before any restoration transaction is committed. The original HTML is archived.
"""
import argparse
import csv
import hashlib
import html
import json
import re
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

SITE = 'https://veracruz.mx/productos.php'
HISTORICAL_SHA256 = '0483a351060d107a027e9a075e1838db1852ca13af04b36f8190aa7408ade3bf'
SNAPSHOT_REL = Path('data/raw/veracruz_productos_2026-10-06.html')
PARSER_VERSION = 'recover_exact_source_text_dom_v1'
TITLE_TAGS = {'h1','h2','h3','h4','h5','h6'}
SKIP_PARENTS = {'script','style','noscript','nav','footer','button','svg'}


def norm(s):
    import unicodedata
    s = ''.join(c for c in unicodedata.normalize('NFD', html.unescape(str(s or '')))
                if unicodedata.category(c) != 'Mn').lower()
    return ' '.join(re.findall(r'[a-z0-9]+', s))


def clean(s):
    return re.sub(r'\s+', ' ', html.unescape(str(s or ''))).strip()


def heading_candidates(soup, titles):
    known = {norm(x) for x in titles}
    headings = [x for x in soup.find_all(re.compile('^h[1-6]$'))
                if norm(x.get_text(' ', strip=True)) in known]
    # Prefer the predominant title-heading level: municipality subheadings can
    # themselves equal a product name (e.g. three products named 'Orizaba').
    by_level={n:[h for h in headings if h.name==n] for n in TITLE_TAGS}
    primary=max(by_level.values(),key=len)
    if len(primary)>=int(len(titles)*0.92): return primary
    if len(headings) >= len(titles): return headings
    # Some templates use custom classes rather than semantic heading elements.
    seen = {id(x) for x in headings}
    for node in soup.find_all(['strong','b','div','span','a']):
        if id(node) in seen or node.find(['h1','h2','h3','h4','h5','h6','strong','b','div','span','a']):
            continue
        if norm(node.get_text(' ', strip=True)) in known:
            headings.append(node);seen.add(id(node))
    headings.sort(key=lambda x: x.sourceline or 0)
    return headings


def align_headings(soup, cards):
    candidates = heading_candidates(soup, [x['title_as_published'] for x in cards])
    # HTML order: use a forward-only exact title matcher. This handles recurring titles.
    matched=[]; i=0
    for card in cards:
        goal=norm(card['title_as_published']); found=None
        while i<len(candidates):
            node=candidates[i]; i+=1
            if norm(node.get_text(' ',strip=True))==goal:
                found=node;break
        if found is None:
            raise ValueError('Cannot identify all products in original HTML: missing or out-of-order card '
                             +card['product_id']+' '+repr(card['title_as_published'])+'. Found '+str(len(matched))+'/295.')
        matched.append(found)
    if len(matched)!=295: raise ValueError('Expected 295 headings; got '+str(len(matched)))
    return matched


def contains_ancestor(node, ancestor):
    return any(x is ancestor for x in node.parents)


def extract_between(first, next_heading):
    municipality_lines=[]; body_parts=[]
    for node in first.next_elements:
        if node is next_heading: break
        if not isinstance(node,NavigableString): continue
        if contains_ancestor(node,first): continue
        if any(getattr(p,'name',None) in SKIP_PARENTS for p in node.parents): continue
        val=clean(node)
        if not val: continue
        if any(getattr(p,'name',None) in {'h2','h3','h4','h5','h6'} for p in node.parents):
            municipality_lines.append(val)
        else:
            body_parts.append(val)
    return clean(' '.join(municipality_lines)), clean(' '.join(body_parts))


def parse_products(raw, cards):
    soup=BeautifulSoup(raw,'html.parser')
    headings=align_headings(soup,cards)
    rows=[]
    for i, (card,head) in enumerate(zip(cards,headings)):
        # For the last card stop at a footer/title boundary if present.
        end=headings[i+1] if i+1 < len(headings) else None
        loc,desc=extract_between(head,end)
        if i==len(cards)-1:
            # Unlike intermediate cards, this has no following product header.
            # The footer is excluded by SKIP_PARENTS above, but ensure no stray menus.
            desc=re.split(r'\b(?:Aviso de Privacidad|Todos los derechos reservados|Política de Privacidad)\b',desc,maxsplit=1,flags=re.I)[0].strip()
        if len(desc)<20:
            raise ValueError('Missing/too-short description for '+card['product_id']+' ('+card['title_as_published']+'): '+repr(desc))
        if len(desc)>16000:
            raise ValueError('Unusually long text for '+card['product_id']+' ('+card['title_as_published']+'); review markup.')
        rows.append(dict(product_id=card['product_id'], source_card_index=card['source_card_index'],
                         title_as_published=card['title_as_published'],
                         municipality_heading_original=loc, original_description_es=desc,
                         description_length=len(desc)))
    return rows


def find_snapshot(explicit, base):
    if explicit:
        path=Path(explicit)
        if not path.is_file():raise FileNotFoundError(path)
        return path
    parent=base.parent
    possibilities=[parent/SNAPSHOT_REL,Path.cwd()/SNAPSHOT_REL,
                   parent.parent/SNAPSHOT_REL,Path.home()/'promo_Veracruz'/SNAPSHOT_REL,
                   Path.home()/'promo_veracruz'/SNAPSHOT_REL,
                   Path.home()/'Documents'/'GitHub'/'promo_Veracruz'/SNAPSHOT_REL,
                   Path.home()/'Documents'/'promo_Veracruz'/SNAPSHOT_REL,
                   Path.home()/'Desktop'/'promo_Veracruz'/SNAPSHOT_REL,
                   Path.home()/'Downloads'/'promo_Veracruz'/SNAPSHOT_REL]
    for p in possibilities:
        if p.is_file():return p
    return None


def get_html(explicit,db, live_allowed):
    snapshot=find_snapshot(explicit,db)
    if snapshot:
        raw=snapshot.read_bytes()
        origin='verified_2026_10_06_snapshot' if hashlib.sha256(raw).hexdigest()==HISTORICAL_SHA256 else 'provided_html_unverified_version'
        return raw,str(snapshot),origin
    if not live_allowed:
        raise RuntimeError('The historical HTML snapshot is not available locally and live download disabled')
    response=requests.get(SITE,timeout=45,headers={'User-Agent':'Mozilla/5.0 (compatible; VeracruzResearchArchive/1.0)'})
    response.raise_for_status()
    if len(response.content)<50000: raise RuntimeError('Live page is suspiciously short: '+str(len(response.content)))
    return response.content, SITE,'live_page_not_identical_to_2026_10_06_snapshot'


def ensure_schema(conn):
    conn.executescript('''
      CREATE TABLE IF NOT EXISTS original_product_description_recovery (
        product_id TEXT PRIMARY KEY REFERENCES catalog_product_cards(product_id),
        source_id TEXT NOT NULL REFERENCES sources(source_id),
        description_text_original TEXT,
        municipality_heading_original TEXT,
        origin TEXT NOT NULL,
        source_snapshot_sha256 TEXT,
        status TEXT NOT NULL CHECK(status IN('original_restored','original_not_recovered')),
        extraction_method TEXT NOT NULL,
        extraction_date_utc TEXT,
        notes TEXT
      );
      CREATE TABLE IF NOT EXISTS original_source_snapshots (
        snapshot_sha256 TEXT PRIMARY KEY,
        source_id TEXT REFERENCES sources(source_id),
        url TEXT,
        source_origin TEXT NOT NULL,
        archived_file TEXT NOT NULL,
        original_size_bytes INTEGER NOT NULL,
        archived_utc TEXT NOT NULL
      );
      CREATE TABLE IF NOT EXISTS replaced_generated_passage_backups (
        passage_id TEXT PRIMARY KEY REFERENCES passages(passage_id),
        product_id TEXT NOT NULL REFERENCES catalog_product_cards(product_id),
        previous_text TEXT NOT NULL,
        previous_extraction_method TEXT NOT NULL,
        replaced_utc TEXT NOT NULL
      );
      CREATE TABLE IF NOT EXISTS original_product_restore_log (
        event_id TEXT PRIMARY KEY,
        snapshot_sha256 TEXT,
        restored_product_count INTEGER NOT NULL,
        replaced_generated_passages INTEGER NOT NULL,
        original_source_origin TEXT NOT NULL,
        notes TEXT
      );
    ''')
    conn.executemany('''INSERT OR IGNORE INTO original_product_description_recovery
       (product_id,source_id,origin,status,extraction_method,notes)
       SELECT product_id,source_id,'unavailable','original_not_recovered',?,
              'No original HTML bytes accessible. Summary-only text retained, never mistaken for original.'
       FROM official_product_evidence WHERE product_id=?''',
       [(PARSER_VERSION, pid) for (pid,) in conn.execute('SELECT product_id FROM official_product_evidence').fetchall()])
    # Fix the flag introduced by previous passes: "screened" is not "original ingested".
    conn.execute('''UPDATE catalog_product_cards SET description_ingested=0 WHERE product_id IN (
         SELECT product_id FROM official_product_evidence WHERE full_original_description_archived=0)''')


def rebuild_source_evidence_audit(conn,out):
    """Rebuild post-restoration evidence coverage; never use generated summaries as quotes."""
    out.mkdir(parents=True,exist_ok=True)
    products={x[0] for x in conn.execute("SELECT product_id FROM original_product_description_recovery WHERE status='original_restored'")}
    # Emit claim-level full original source text, with summaries excluded altogether.
    q='''SELECT a.claim_id,a.activity_id,a.municipality_id,a.original_phrase,p.passage_id,
             p.source_id,p.source_locator,p.extraction_method,p.original_text_es
         FROM activity_claims a JOIN passages p USING(passage_id) ORDER BY a.claim_id'''
    claim_rows=[]; claim_has_original={}
    for r in conn.execute(q):
        claim_id,act,mid,phrase,pid,sid,locator,method,body=r
        is_real = sid.startswith('PDF') and pid.startswith('CAT25-') or method.startswith('original_web_product_description_')
        claim_has_original[claim_id]=bool(is_real)
        claim_rows.append((claim_id,act,mid,phrase,pid,sid,locator,'original_retained' if is_real else 'original_missing',body if is_real else ''))
    with (out/'ALL_CLAIMS_REAL_ORIGINAL_QUOTATIONS_ONLY.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['claim_id','activity_id','municipality_id','claim_phrase','passage_id',
                                    'source_id','source_locator','original_text_status','source_original_text_es']);w.writerows(claim_rows)
    audits=[]
    for mid,feat,ids in conn.execute('SELECT municipality_id,feature_id,claim_ids FROM s4_statewide_evidence_pairs_v1'):
        refs=ids.split('|'); real=sum(claim_has_original.get(x,False) for x in refs)
        summary=len(refs)-real
        audits.append((mid,feat,ids,len(refs),real,summary))
        conn.execute('''UPDATE s4_statewide_evidence_pairs_v1 SET original_text_support_count=?,
                  summary_only_evidence_count=? WHERE municipality_id=? AND feature_id=?''',(real,summary,mid,feat))
    with (out/'S4_FEATURE_PAIRS_REEVALUATED_AFTER_SOURCE_RESTORE.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['municipality_id','feature_id','claim_ids','supporting_claims',
                                    'original_quote_count','summary_only_count']);w.writerows(audits)


def restore(conn,rows,raw,origin,out):
    sha=hashlib.sha256(raw).hexdigest()
    archived=out/'source_archive'/(origin+'_'+sha+'.html')
    archived.parent.mkdir(parents=True,exist_ok=True)
    archived.write_bytes(raw)
    retrieved=datetime.now(timezone.utc).isoformat()
    source_id=conn.execute('SELECT source_id FROM official_product_evidence LIMIT 1').fetchone()[0]
    replacements=0
    # Match previously unlinked source passages by exact product title and (where
    # titles recur) their explicitly assigned municipality, never by a guess.
    title_map={}
    for x in conn.execute('SELECT product_id,title_as_published,municipality_names_as_published FROM catalog_product_cards'):
        title_map.setdefault(norm(x[1]),[]).append((x[0],x[2] or ''))
    other_refs=conn.execute('''SELECT p.passage_id,p.source_locator,m.name_official
           FROM passages p JOIN activity_claims a ON a.passage_id=p.passage_id
           LEFT JOIN municipalities m ON m.municipality_id=a.municipality_id
           WHERE p.source_id='WEB4' AND p.extraction_method NOT LIKE 'original_web_product_description%'
           AND NOT EXISTS (SELECT 1 FROM official_product_claim_links l WHERE l.claim_id=a.claim_id)
           GROUP BY p.passage_id''').fetchall()
    extra={}
    for passage_id,locator,municipality in other_refs:
        candidates=title_map.get(norm(locator),[])
        if len(candidates)>1:
            candidates=[p for p in candidates if norm(municipality) in [norm(m) for m in p[1].split('|')]]
        if len(candidates)!=1:
            raise ValueError('Cannot unambiguously restore source passage '+passage_id+'; '+str(locator)+' / '+str(municipality))
        extra[passage_id]=candidates[0][0]
    extras_by_product={}
    for passage_id,product_id in extra.items(): extras_by_product.setdefault(product_id,[]).append(passage_id)
    # Single atomic transaction: either all 295 product records and ALL 472 WEB4 passages update or none do.
    with conn:
        conn.execute('''INSERT OR REPLACE INTO original_source_snapshots VALUES (?,?,?,?,?,?,?)''',
                     (sha,source_id,SITE,origin,str(archived.relative_to(out)),len(raw),retrieved))
        for x in rows:
            product=x['product_id']; desc=x['original_description_es']
            conn.execute('''UPDATE original_product_description_recovery SET
                    description_text_original=?, municipality_heading_original=?, origin=?,
                    source_snapshot_sha256=?,status='original_restored',extraction_method=?,
                    extraction_date_utc=?,notes=? WHERE product_id=?''',
                    (desc,x['municipality_heading_original'],origin,sha,PARSER_VERSION,retrieved,
                     'Source text, whitespace normalized; original HTML archived unchanged.',product))
            conn.execute('UPDATE catalog_product_cards SET description_ingested=1 WHERE product_id=?',(product,))
            conn.execute('''UPDATE official_product_evidence SET full_original_description_archived=1,
                    evidence_status='original_description_restored; prior summary remains separate'
                    WHERE product_id=?''',(product,))
            conn.execute('''UPDATE official_product_description_screening SET is_verbatim_archived=1,
                    methodology='ORIGINAL SOURCE TEXT RESTORED; previous paraphrase remains in summary_paraphrase'
                    WHERE product_id=?''',(product,))
            refs=conn.execute('''SELECT DISTINCT p.passage_id,p.original_text_es,p.extraction_method
                     FROM passages p JOIN activity_claims a ON a.passage_id=p.passage_id
                     JOIN official_product_claim_links l ON l.claim_id=a.claim_id
                     WHERE l.product_id=?''',(product,)).fetchall()
            if extras_by_product.get(product):
                refs+=conn.execute('SELECT passage_id,original_text_es,extraction_method FROM passages WHERE passage_id IN ('
                        +','.join('?'*len(extras_by_product[product]))+')',
                        extras_by_product[product]).fetchall()
            # The original generated passage is retained in the backup before being replaced.
            for passage_id,old_text,old_method in refs:
                conn.execute('''INSERT OR IGNORE INTO replaced_generated_passage_backups
                             VALUES(?,?,?,?,?)''', (passage_id,product,old_text,old_method,retrieved))
                conn.execute('''UPDATE passages SET original_text_es=?,
                    passage_type='product_description',extraction_method=?,source_locator=?
                    WHERE passage_id=?''',
                    (desc,'original_web_product_description_'+PARSER_VERSION,
                     'Product #'+str(x['source_card_index'])+' '+x['title_as_published']+'; raw HTML SHA256 '+sha,passage_id))
                replacements+=1
        conn.execute('''INSERT OR REPLACE INTO original_product_restore_log VALUES(?,?,?,?,?,?)''',
          (sha,sha,len(rows),replacements,origin,'Every one of 295 products verified against original text; raw source HTML retained.'))
    current_total=conn.execute("SELECT count(*) FROM passages WHERE source_id='WEB4' AND extraction_method LIKE 'original_web_product_description%'").fetchone()[0]
    if current_total!=472:
        raise RuntimeError('Expected all 472 web-source passages to be restored, got '+str(current_total))
    with conn:
        rebuild_source_evidence_audit(conn,out)
    return sha,replacements,archived


def write_status(conn,out,restored=False,reason=None,sha=None,origin=None):
    out.mkdir(parents=True,exist_ok=True)
    entries=conn.execute('''SELECT c.product_id,c.source_card_index,c.title_as_published,
                    r.status,length(r.description_text_original),r.origin,r.source_snapshot_sha256,
                    e.source_url
        FROM catalog_product_cards c JOIN original_product_description_recovery r USING (product_id)
        JOIN official_product_evidence e USING (product_id) ORDER BY c.source_card_index''').fetchall()
    with (out/'ALL_295_ORIGINAL_TEXT_RECOVERY_STATUS.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f);w.writerow(['product_id','source_card_index','title','status','original_text_length',
                                    'origin','source_sha256','source_url']);w.writerows(entries)
    recovered=sum(e[3]=='original_restored' for e in entries)
    raw_counts=conn.execute('SELECT count(*) FROM replaced_generated_passage_backups').fetchone()[0]
    summary=dict(total_product_cards=len(entries),restored_original_descriptions=recovered,
                 unarchived_original_descriptions=len(entries)-recovered,
                 regenerated_passages_replaced=raw_counts,run_succeeded=restored,
                 source_sha256=sha,source_origin=origin,error=reason,
                 historical_snapshot_sha256_expected=HISTORICAL_SHA256,
                 database_integrity=conn.execute('PRAGMA integrity_check').fetchone()[0],
                 foreign_key_errors=len(conn.execute('PRAGMA foreign_key_check').fetchall()))
    (out/'RESTORATION_AUDIT.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db',default='veracruz_pp3_master.sqlite')
    p.add_argument('--html',help='Historical raw HTML source file (preferred). Auto-detected if present.')
    p.add_argument('--offline',action='store_true',help='Do not fetch current live HTML if snapshot is missing.')
    p.add_argument('--out',default='restoration_results')
    args=p.parse_args()
    db=Path(args.db).resolve();out=Path(args.out).resolve()
    if not db.is_file():sys.exit('ERROR: DB missing '+str(db))
    conn=sqlite3.connect(db)
    conn.execute('PRAGMA foreign_keys=ON')
    cards=[dict(zip(['product_id','source_card_index','title_as_published'],r)) for r in
           conn.execute('SELECT product_id,source_card_index,title_as_published FROM catalog_product_cards ORDER BY source_card_index')]
    if len(cards)!=295: sys.exit('ERROR: expected exactly 295 product cards, got '+str(len(cards)))
    try:
        ensure_schema(conn);conn.commit()
        raw,where,origin=get_html(args.html,db,not args.offline)
        rows=parse_products(raw,cards)
        sha,replacements,archive=restore(conn,rows,raw,origin,out)
        with (out/'ALL_295_RESTORED_ORIGINAL_DESCRIPTIONS.csv').open('w',newline='',encoding='utf-8-sig') as f:
            w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
        status=write_status(conn,out,True,sha=sha,origin=origin)
        print(json.dumps(status,indent=2,ensure_ascii=False))
        print('Original bytes archived at:',archive)
    except Exception as exc:
        status=write_status(conn,out,False,reason=str(exc))
        print(json.dumps(status,indent=2,ensure_ascii=False),file=sys.stderr)
        sys.exit(2)
    finally:
        conn.close()
if __name__=='__main__':main()
