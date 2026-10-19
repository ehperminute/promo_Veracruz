#!/usr/bin/env python3
"""Non-destructive exact-version patch for map/guide/route integration.
Run from promo_Veracruz root as:
    python veracruz_guide_route_fix/install.py .
"""
from pathlib import Path
import shutil, sys, datetime
ROOT = Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
MAP = ROOT/'site/js/map-attractions.js'
ROUTE = ROOT/'site/js/route-planner.js'
HTML = ROOT/'site/index.html'
CSS = ROOT/'site/css/attraction-guide-route.css'
TAG = 'VX_GUIDE_ROUTE_20261018_V1'

def once(s,needle,replacement,which):
    n=s.count(needle)
    if n!=1: raise RuntimeError(f'{which}: expected one exact insertion point, found {n}; no files changed.')
    return s.replace(needle,replacement,1)

def main():
    for p in (MAP,ROUTE,HTML):
        if not p.exists(): raise FileNotFoundError(f'Missing {p}; no files changed')
    m=MAP.read_text(encoding='utf-8'); r=ROUTE.read_text(encoding='utf-8'); h=HTML.read_text(encoding='utf-8')
    if TAG in m and TAG in r and 'attraction-guide-route.css?v=20261018-v1' in h:
        print('Guide + route integration already installed. No changes.');return
    if TAG in m or TAG in r:
        raise RuntimeError('Partial installation or unexpected version; do not overwrite. Send the three current files.')
    # Introduce reliable route selection without relying on DOM selectors or old scripts.
    route_api="""
 // VX_GUIDE_ROUTE_20261018_V1: narrow public API for attraction guide route actions.
 function findRouteSite(item){
   if(!graph||!item)return null;
   const all=eligibleSites(),exact=all.find(s=>s.id===item.id);
   if(exact)return exact;
   const named=all.filter(s=>fold(s.name)===fold(item.name));
   if(!named.length)return null;
   if(named.length===1)return named[0];
   if(Array.isArray(item.coordinates))return named.sort((a,b)=>distApprox(a.at,item.coordinates)-distApprox(b.at,item.coordinates))[0];
   return null;
 }
 window.VeracruzRoutePlanner={
   find(item){const s=findRouteSite(item);return s?{id:s.id,name:s.name}:null;},
   choose(kind,item){
     if(!['start','end','stop'].includes(kind))return false;
     const s=findRouteSite(item);if(!s)return false;
     if(kind==='end'&&s.id===startSelect.value){setStatus(text().same,true);return false;}
     if(kind==='stop'&&(s.id===startSelect.value||s.id===finishSelect.value))return false;
     changeSite(kind,s);
     setPicking(null); // Route selection is optional; guide buttons never hijack map clicks.
     setStatus(kind==='start'?text().pickStart:kind==='end'?text().pickEnd:text().pickStop);
     panel.hidden=false;
     return true;
   },
   show(){panel.hidden=false;panel.scrollIntoView({block:'nearest',behavior:'smooth'});}
 };
"""
    r=once(r,' initialize();\n})();',route_api+'\n initialize();\n})();','route API footer')
    # Attraction guide is explicitly the top card, so the route planner can't bury it.
    m=once(m,"const guide=el('article','vxc-guide');guide.hidden=true;panel.insertAdjacentElement('afterend',guide);",
           "const guide=el('article','vxc-guide');guide.hidden=true;panel.insertAdjacentElement('afterend',guide);\n// VX_GUIDE_ROUTE_20261018_V1\nconst mapPreview=el('aside','vxc-mini-preview');mapPreview.hidden=true;const mapContainer=root.querySelector('#vx-map');if(mapContainer)mapContainer.append(mapPreview);",'guide declaration')
    m=once(m,"function clearGuide(){active=null;guide.hidden=true;", "function clearGuide(){mapPreview.hidden=true;mapPreview.replaceChildren();const rp=root.querySelector('#vx-route-planner');if(rp)rp.hidden=false;active=null;guide.hidden=true;",'guide close')
    m=once(m," active=e.id;sidebarHide(true);guide.hidden=false;panel.hidden=true;guide.replaceChildren();",
           " active=e.id;sidebarHide(true);guide.hidden=false;panel.hidden=true;guide.replaceChildren();\n const rp=root.querySelector('#vx-route-planner');if(rp)rp.hidden=true;\n side.prepend(guide); // Present guide first, rather than scrolling to the route form.\n mapPreview.hidden=true;mapPreview.replaceChildren();",'guide opening')
    # In existing guide, p is the actual GeoJSON property bag, which includes photos + coordinates.
    point="""
 // Guide-first route actions; only attractions connected to the current regional graph qualify.
 if(e.kind==='mapped'){
   const route=window.VeracruzRoutePlanner;
   const ref={id:p.id||e.feature?.id||e.id,name:e.name,coordinates:e.feature?.geometry?.coordinates};
   if(route?.find(ref)){
     const tr={en:['Start here','Finish here','Add stop'],es:['Salir de aquí','Llegar aquí','Agregar parada'],ja:['ここから出発','ここを目的地に','経由地に追加']}[lang()];
     const group=el('div','vxc-route-actions');
     ['start','end','stop'].forEach((kind,i)=>{
       const button=el('button','vxc-route-action',tr[i]);button.type='button';
       button.addEventListener('click',()=>{
         if(route.choose(kind,ref)){
           clearGuide();route.show();
         }
       });group.append(button);
     });
     guide.append(group);
   }
 }
 if(e.kind==='mapped'&&p.photo_url&&validURL(p.photo_url)&&mapContainer){
   const img=el('img');img.src=p.photo_url;img.alt='';img.loading='lazy';
   img.addEventListener('error',()=>{mapPreview.hidden=true;});
   const label=el('strong','',e.name),dismiss=el('button','vxc-mini-close','×');dismiss.type='button';dismiss.setAttribute('aria-label','Close preview');
   dismiss.addEventListener('click',()=>{mapPreview.hidden=true;});
   mapPreview.append(img,label,dismiss);mapPreview.hidden=false;
 }
"""
    m=once(m," if(validURL(e.source_url))guide.append(link(e.source_url,t().source+' ↗'));",point+" if(validURL(e.source_url))guide.append(link(e.source_url,t().source+' ↗'));",'guide actions')
    # Search / catalog toggles can dismiss the guide; restore route panel there too.
    m=once(m,"toggle.addEventListener('click',()=>{expanded=!expanded; paging=65;guide.hidden=true;render();});",
           "toggle.addEventListener('click',()=>{expanded=!expanded; paging=65;clearGuide();});",'catalog toggle')
    m=once(m,"select.addEventListener('change',()=>{paging=65;guide.hidden=true;render();});",
           "select.addEventListener('change',()=>{paging=65;clearGuide();});",'catalog filter')
    m=once(m,"search.addEventListener('input',()=>{paging=65;guide.hidden=true;render();zoomLabels();});",
           "search.addEventListener('input',()=>{paging=65;clearGuide();zoomLabels();});",'catalog search')
    # Add a versioned external stylesheet and refresh existing script cache keys.
    h=once(h,'<script defer src="js/route-planner.js?v=20261018-route-click-fix-1"></script>',
           '<script defer src="js/route-planner.js?v=20261018-guide-route-v1"></script>','route script link')
    h=once(h,'<script defer src="js/map-attractions.js?v=20261018-finalfreeze"></script>',
           '<script defer src="js/map-attractions.js?v=20261018-guide-route-v1"></script>','attraction script link')
    h=once(h,'<link rel="stylesheet" href="css/map-attractions.css?v=20261018-fullcatalog1">',
           '<link rel="stylesheet" href="css/map-attractions.css?v=20261018-fullcatalog1">\n<link rel="stylesheet" href="css/attraction-guide-route.css?v=20261018-v1">','new stylesheet link')
    # Write only after verifying all strings and destination paths; unique backups.
    ts=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    for p in (MAP,ROUTE,HTML):
        bak=p.with_name(p.name+f'.before-guide-route-{ts}')
        shutil.copy2(p,bak)
    css_source=Path(__file__).with_name('attraction-guide-route.css')
    if not css_source.exists():raise RuntimeError('Missing CSS (existing files only backed up).')
    MAP.write_text(m,encoding='utf-8')
    ROUTE.write_text(r,encoding='utf-8')
    HTML.write_text(h,encoding='utf-8')
    shutil.copy2(css_source,CSS)
    print('Installed: guide-first sidebar, in-guide route controls, optional small photo preview.')
    print('Backups are alongside the original HTML and JS files.')
    print('No tourism data, road graphs, or attraction coordinates changed.')

if __name__=='__main__':
    try:main()
    except Exception as exc:print('STOP — '+str(exc));sys.exit(1)
