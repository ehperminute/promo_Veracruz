#!/usr/bin/env python3
"""Targeted, repeatable patch for Veracruz's live static site. No original file deletion."""
import argparse
import re
from pathlib import Path

REPLACE_TAIL='''  start();
  // VX-TRIP-HASH-NAV-FIX-V2: same-page gallery links must update the journal.
  function openFromHash() {
    start();
    const anchor = $('tj-title-heading');
    if (anchor) requestAnimationFrame(() => anchor.scrollIntoView({behavior:'smooth',block:'start'}));
  }
  window.VXTripJournalOpenHash = openFromHash;
  window.addEventListener('hashchange', openFromHash);
})();'''

LANG_CSS='''/* Unified language selector across homepage, journal, story and provider forms. */
:where(.language-control,.vp-lang-control,.vx-common-language) { display:inline-flex; align-items:center; gap:.6rem; font-weight:650; font-size:.92rem; }
:where(.language-control,.vp-lang-control,.vx-common-language) label, :where(.language-control,.vp-lang-control,.vx-common-language) span { color:inherit; }
:where(.language-control,.vp-lang-control,.vx-common-language) select,
.tj-bar select.vx-language-select { width:auto; min-width:125px; min-height:40px; padding:7px 30px 7px 12px; border:1px solid #91b4bd; border-radius:9px; background:#fff; color:#163a46; font:600 14px/1.3 system-ui,sans-serif; }
.vx-common-language select:focus-visible, .language-control select:focus-visible, .vp-lang-control select:focus-visible { outline:3px solid #efba55; outline-offset:2px; }
.tj-bar .vx-common-language { margin-left:auto; }
.vp-form-page header { background:#10364b; }
@media(max-width:600px) {.vx-common-language { flex-wrap:wrap; } }
'''

LANG_JS='''// Keeps the visual selector and language preference consistent without replacing
// the page-specific dictionaries/translations. V1, additive and idempotent.
(()=>{'use strict';
  const names={es:'Idioma',en:'Language',ja:'言語'};
  const ids=['language-select','tj-lang','vx-lang','vp-language','lang'];
  const sel=ids.map(x=>document.getElementById(x)).find(Boolean);
  if(!sel)return;
  const current=sel.value;
  ['es','en','ja'].forEach(v=>{const opt=[...sel.options].find(x=>x.value===v);if(opt)sel.append(opt)});
  sel.value=current;
  sel.classList.add('vx-language-select');
  sel.setAttribute('aria-label','Idioma / Language / 言語');
  const old=sel.closest('label, .language-control, .vp-lang-control');
  if(old)old.classList.add('vx-common-language');
  function updateLabel(){
    let l=sel.value;
    if(!names[l]){try{l=localStorage.getItem('veracruz_language')}catch(e){}};
    if(!names[l])l='es';
    const container=sel.closest('.vx-common-language');
    if(!container)return;
    const label=container.querySelector('label[for],span[data-vpi18n],span:not([class]),#tj-lang-label,#vx-lang-label');
    if(label&&label!==sel)label.textContent=names[l];
  }
  sel.addEventListener('change',()=>{try{localStorage.setItem('veracruz_language',sel.value)}catch(e){}updateLabel()});
  updateLabel();
  setTimeout(updateLabel,120);
})();
'''

def ensure_link(html, insert, tag):
    if tag in html: return html
    if '</head>' not in html: raise ValueError('Missing </head>')
    return html.replace('</head>',insert+'\n</head>',1)

def install(root):
    site=root/'site'
    js=site/'js'/'trip-journal.js'
    gallery=site/'js'/'trip-gallery.js'
    if not js.exists() or not gallery.exists():
        raise SystemExit('This expects the Travel Journal and Trip Stories already installed; no changes made.')
    raw=js.read_text(encoding='utf-8')
    if 'VX-TRIP-HASH-NAV-FIX-V2' not in raw:
        at=raw.rfind('  start();')
        if at<0: raise SystemExit('Unexpected journal script shape; cannot patch safely.')
        # Replace only startup tail, including any V1 listener.
        before=raw[:at]
        raw=before+REPLACE_TAIL+'\n'
        js.write_text(raw,encoding='utf-8')
    gs=gallery.read_text(encoding='utf-8')
    marker='VX-TRIP-GALLERY-SAME-HASH-FIX-V1'
    if marker not in gs:
        needle='actions.append(v);'
        if needle not in gs:raise SystemExit('Unexpected gallery script shape; no gallery patch applied.')
        gs=gs.replace(needle,'''// VX-TRIP-GALLERY-SAME-HASH-FIX-V1: refresh when same example is clicked twice.
    v.addEventListener('click',ev=>{
      if(location.hash===new URL(v.href,location.href).hash && window.VXTripJournalOpenHash){ev.preventDefault();window.VXTripJournalOpenHash();}
    });
    actions.append(v);''',1)
        gallery.write_text(gs,encoding='utf-8')
    (site/'css'/'vx-language-unified.css').write_text(LANG_CSS,encoding='utf-8')
    (site/'js'/'vx-language-unified.js').write_text(LANG_JS,encoding='utf-8')
    for name in ['index.html','viajes.html','enviar-viaje.html','proveedores.html','planner.html']:
        path=site/name
        if not path.exists():continue
        page=path.read_text(encoding='utf-8')
        if name=='viajes.html' and 'class="vx-common-language"' not in page:
            page=page.replace('<label for="tj-lang" id="tj-lang-label">Idioma / Language</label><select id="tj-lang">','<span class="vx-common-language"><label for="tj-lang" id="tj-lang-label">Idioma / Language</label><select id="tj-lang">',1)
            page=page.replace('</select></header>','</select></span></header>',1)
        if name=='enviar-viaje.html' and 'class="vx-common-language"' not in page:
            page=page.replace('<label for="vx-lang" id="vx-lang-label">Idioma</label><select id="vx-lang">','<span class="vx-common-language"><label for="vx-lang" id="vx-lang-label">Idioma</label><select id="vx-lang">',1)
            page=page.replace('</select></header>','</select></span></header>',1)
        if name=='viajes.html':
            page=re.sub(r'js/trip-journal\.js(?:\?v=[^"\']+)?','js/trip-journal.js?v=20261025hash2',page)
            page=re.sub(r'js/trip-gallery\.js(?:\?v=[^"\']+)?','js/trip-gallery.js?v=20261025hash2',page)
        page=ensure_link(page,'<link rel="stylesheet" href="css/vx-language-unified.css?v=1">','css/vx-language-unified.css')
        if 'js/vx-language-unified.js' not in page:
            page=page.replace('</body>','<script defer src="js/vx-language-unified.js?v=1"></script>\n</body>',1)
        # Replace only language option ordering for the homepage; existing preference unaffected.
        path.write_text(page,encoding='utf-8')
    print('PASS: journal hash navigation, gallery link, and unified language controls installed.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('repo',nargs='?',default='.')
    root=Path(p.parse_args().repo).resolve()
    install(root)
