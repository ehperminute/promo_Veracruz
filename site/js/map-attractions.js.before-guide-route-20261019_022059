/* Veracruz consolidated explorer: 31 mapped attractions + complete recovered evidence catalog.
 * All geographic features come from attractions.geojson.  The catalog DOES NOT invent pins.
 * Existing municipality markers/filters and description sources remain untouched.
 */
(() => {
'use strict';
const root=document.getElementById('veracruz-map-section'),map=window.__vx_attraction_map,lib=window.maplibregl;
if(!root||!map||!lib){console.warn('[Veracruz catalog] Base map unavailable');return;}
const search=root.querySelector('#vx-search'),side=root.querySelector('.vx-side'),status=root.querySelector('#vx-status');
if(!search||!side||!status){console.warn('[Veracruz catalog] Sidebar controls missing');return;}
const mainDetail=root.querySelector('#vx-detail'),mainList=root.querySelector('#vx-list');
const L={en:{map:'Mapped attractions',catalog:'Complete research catalog',all:'All records',place:'Named places',lead:'Locations, traditions & events',product:'Tourism products',matches:'Search results',nothing:'No records match your search.',back:'Back to results',location:'Location',area:'Municipality reference only — not the attraction entrance.',unknown:'Exact coordinates have not been verified. No pin was placed.',route:'This is a tour or multi-stop experience, not one geographic point.',original:'Original evidence / activity',source:'Original source',photo:'Photo source',info:'About this place',note:'Visiting information',more:'Show more',details:'Open guide',results:'results',explore:'Explore the original source',nearby:'Associated municipality',summary:'Published title / source text',notEntrance:'Map point is not a verified visitor entrance.'},es:{map:'Atractivos en el mapa',catalog:'Catálogo completo de investigación',all:'Todos',place:'Lugares identificados',lead:'Lugares, tradiciones y eventos',product:'Productos turísticos',matches:'Resultados de búsqueda',nothing:'No hay resultados.',back:'Volver a resultados',location:'Ubicación',area:'Referencia municipal aproximada: NO es la entrada del atractivo.',unknown:'No se han verificado coordenadas exactas; no se inventó ningún marcador.',route:'Es un recorrido o producto que puede abarcar varios sitios, no un único punto.',original:'Actividad o testimonio de origen',source:'Fuente original',photo:'Fuente de la foto',info:'Conoce este lugar',note:'Para tu visita',more:'Ver más',details:'Abrir guía',results:'resultados',explore:'Consultar la fuente original',nearby:'Municipio relacionado',summary:'Nombre publicado / evidencia original',notEntrance:'El punto del mapa no es una entrada de visitantes verificada.'},ja:{map:'地図上の観光名所',catalog:'資料全体を探す',all:'すべて',place:'名称のある場所',lead:'場所・行事・伝統',product:'観光商品',matches:'検索結果',nothing:'見つかりませんでした',back:'結果へ戻る',location:'位置',area:'市町村の参考地点です。観光スポットの入口ではありません。',unknown:'正確な位置は未確認のため地図ピンは表示しません。',route:'複数の場所にわたるツアーや観光商品です。',original:'出典の記載',source:'情報源',photo:'写真提供元',info:'この場所について',note:'訪問情報',more:'もっと見る',details:'ガイドを開く',results:'検索結果',explore:'元の資料を見る',nearby:'関連自治体',summary:'元の名称・資料',notEntrance:'訪問者用の入口は未確認です。'}};
const lang=()=>['en','es','ja'].includes(document.documentElement.lang?.slice(0,2))?document.documentElement.lang.slice(0,2):'en', t=()=>L[lang()];
const normal=s=>String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
const el=(tag,cls,content)=>{const e=document.createElement(tag); if(cls)e.className=cls;if(content!==undefined)e.textContent=content;return e;};
const validURL=s=>{try{const u=new URL(s);return ['https:','http:'].includes(u.protocol);}catch{return false;}};
const link=(url,title)=>{const e=el('a','',title);if(validURL(url)){e.href=url;e.target='_blank';e.rel='noopener noreferrer';}return e;};
const strip=s=>String(s||'').trim();
const txt=(p,field)=>strip(p[field+'_'+lang()]||p[field+'_en']||p[field+'_es']||'');
const cats=[['all','all'],['mapped','map'],['named_place','place'],['place_event_lead','lead'],['tourism_product','product']];
const controls=el('div','vxc-controls');const toggle=el('button','vxc-toggle');toggle.type='button';toggle.textContent=t().catalog;
const select=el('select','vxc-select');cats.forEach(([v,k])=>{const o=el('option','',t()[k]);o.value=v;select.append(o);});select.setAttribute('aria-label',t().catalog);controls.append(toggle,select);
status.insertAdjacentElement('afterend',controls);
const panel=el('section','vxc-panel');panel.hidden=true;controls.insertAdjacentElement('afterend',panel);
const guide=el('article','vxc-guide');guide.hidden=true;panel.insertAdjacentElement('afterend',guide);
let mapped=[],catalog=[],markers=[],expanded=false,active=null,paging=65;
const selectedKind=()=>select.value;
const asEntry=f=>({id:'MAP-'+(f.properties.id||f.id),name:f.properties.name,kind:'mapped',municipality:f.properties.municipality||'',source_url:f.properties.source_url||'',source_text_es:'',activity:f.properties.type||'',feature:f,lat:f.geometry.coordinates[1],lon:f.geometry.coordinates[0],geographic_precision:f.properties.status||'mapped_feature'});
const entries=()=>[...mapped.map(asEntry),...catalog];
function clearGuide(){active=null;guide.hidden=true;if(mainList)mainList.style.removeProperty('display');if(mainDetail)mainDetail.style.removeProperty('display');markers.forEach(m=>m.el.classList.remove('vxc-selected'));render();}
function isMatch(e,q){return !q||normal([e.name,e.municipality,e.activity,e.source_text_es].join(' ')).includes(q);}
function filtered(){const q=normal(search.value),kind=selectedKind();return entries().filter(x=>(kind==='all'||(kind==='mapped'?x.kind==='mapped':x.kind===kind))&&isMatch(x,q));}
function sidebarHide(yes){root.classList.toggle('vxc-active',yes);if(mainList)mainList.style.display=yes?'none':'';if(mainDetail)mainDetail.style.display=yes?'none':'';}
function guideFor(e){
 active=e.id;sidebarHide(true);guide.hidden=false;panel.hidden=true;guide.replaceChildren();
 const b=el('button','vxc-back','← '+t().back);b.type='button';b.addEventListener('click',clearGuide);guide.append(b);
 let p=e.feature?.properties || e;
 if(p.photo_url && validURL(p.photo_url)){
  const fig=el('figure','vxc-figure'),img=el('img');img.src=p.photo_url;img.alt=e.name;img.loading='lazy';img.addEventListener('error',()=>fig.remove());fig.append(img);
  if(p.photo_source_url && validURL(p.photo_source_url))fig.append(link(p.photo_source_url,p.photo_credit||t().photo));guide.append(fig);
 }
 guide.append(el('h3','vxc-title',(p.icon ? p.icon+' ':'')+e.name));
 const sub=el('p','vxc-sub',e.municipality || e.activity || (e.kind==='tourism_product'?t().product:t().place));guide.append(sub);
 if(e.kind==='mapped'){
  const intro=txt(p,'description'),detail=txt(p,'details'),visit=txt(p,'visit_note');
  if(intro)guide.append(el('p','vxc-intro',intro));
  if(detail){guide.append(el('h4','',t().info));guide.append(el('p','vxc-body',detail));}
  if(visit){guide.append(el('h4','',t().note));guide.append(el('p','vxc-body',visit));}
  if(p.status!=='entrance_verified')guide.append(el('p','vxc-disclaimer',t().notEntrance));
 }else{
  if(e.activity)guide.append(el('p','vxc-intro',e.activity));
  if(e.source_text_es){guide.append(el('h4','',t().summary));guide.append(el('p','vxc-body',e.source_text_es));}
  const msg=e.kind==='tourism_product'?t().route:e.geographic_precision==='municipality_reference'?t().area:t().unknown;
  guide.append(el('p','vxc-disclaimer',msg));
  if(e.municipality)guide.append(el('p','vxc-sub',t().nearby+': '+e.municipality));
 }
 if(validURL(e.source_url))guide.append(link(e.source_url,t().source+' ↗'));
 const matched=markers.find(m=>m.id===e.id);if(matched)matched.el.classList.add('vxc-selected');
 if(e.feature)map.flyTo({center:e.feature.geometry.coordinates,zoom:Math.max(10,map.getZoom()),essential:true});
 else if(e.geographic_precision==='municipality_reference'&&e.lon&&e.lat)map.flyTo({center:[Number(e.lon),Number(e.lat)],zoom:Math.max(8,map.getZoom()),essential:true});
 side.scrollTo({top:0,behavior:'smooth'});
}
function render(){
 const q=normal(search.value),open=expanded || q.length>0;
 toggle.textContent=(expanded?'▴ ':'▾ ')+t().catalog+' · '+catalog.length+' + '+mapped.length+' '+t().map.toLowerCase();
 panel.hidden=!open || !guide.hidden;select.hidden=!open;
 sidebarHide(open || !guide.hidden);
 if(!open || !guide.hidden)return;
 const matches=filtered();panel.replaceChildren();panel.append(el('h4','vxc-results',q?t().matches+' · '+matches.length:matches.length+' '+t().results));
 if(!matches.length){panel.append(el('p','vxc-empty',t().nothing));return;}
 for(const item of matches.slice(0,paging)){
  const row=el('button','vxc-record');row.type='button';
  const symbol=el('span','vxc-icon',item.kind==='mapped'?(item.feature.properties.icon||'📍'):item.kind==='named_place'?'◌':item.kind==='place_event_lead'?'◈':'◇');
  const inner=el('span','vxc-record-main');inner.append(el('strong','',item.name));
  inner.append(el('small','',[(item.kind==='mapped'?t().map:item.kind==='named_place'?t().place:item.kind==='place_event_lead'?t().lead:t().product),item.municipality].filter(Boolean).join(' · ')));
  row.append(symbol,inner);row.addEventListener('click',()=>guideFor(item));panel.append(row);
 }
 if(matches.length>paging){const more=el('button','vxc-more',t().more+' ('+(matches.length-paging)+')');more.addEventListener('click',()=>{paging+=65;render();});panel.append(more);}
}
function marker(f){const p=f.properties,e=el('div','vxa-marker');e.tabIndex=0;e.setAttribute('role','button');e.setAttribute('aria-label',p.name);e.title=p.name;
 // MapLibre needs absolute positioned marker elements. Do not override its transform.
 e.style.position='absolute';const core=el('span','vxa-marker-icon',p.icon||'📍');e.append(core,el('span','vxa-marker-label',p.name));
 const entry=asEntry(f);
 e.addEventListener('click',ev=>{ev.stopPropagation();guideFor(entry)});
 e.addEventListener('keydown',ev=>{if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();guideFor(entry);}});
 new lib.Marker({element:e,anchor:'center',subpixelPositioning:true}).setLngLat(f.geometry.coordinates).addTo(map);
 markers.push({el:e,id:entry.id,osm:entry.id.startsWith('MAP-OSM-'),name:normal(p.name)});
}
const zoomLabels=()=>{const z=map.getZoom(),q=normal(search.value);markers.forEach(m=>{
 m.el.classList.toggle('vxa-labels-on',z>=9.2||m.id===active||(q&&m.name.includes(q)));
 if(m.osm)m.el.style.display=(z>=9.0||m.id===active||(q&&m.name.includes(q)))?'':'none';
});};
toggle.addEventListener('click',()=>{expanded=!expanded; paging=65;guide.hidden=true;render();});
select.addEventListener('change',()=>{paging=65;guide.hidden=true;render();});
search.addEventListener('input',()=>{paging=65;guide.hidden=true;render();zoomLabels();});
search.addEventListener('keydown',e=>{if(e.key!=='Enter'||!search.value.trim())return;const match=filtered()[0];if(match){e.preventDefault();guideFor(match);}});
map.on('zoom',zoomLabels);
Promise.all([fetch('data/attractions.geojson',{cache:'no-store'}).then(r=>r.ok?r.json():Promise.reject(Error('Attractions HTTP '+r.status))),fetch('data/tourism_catalog.json',{cache:'no-store'}).then(r=>r.ok?r.json():Promise.reject(Error('Catalog HTTP '+r.status)))]).then(([f,c])=>{
 if(f.type!=='FeatureCollection'||!Array.isArray(f.features)||!Array.isArray(c.records))throw Error('Bad map/catalog data');
 mapped=f.features.filter(v=>v.geometry?.type==='Point'&&v.geometry.coordinates?.length===2&&v.geometry.coordinates.every(Number.isFinite));
 catalog=c.records; mapped.forEach(marker);zoomLabels();render();
 console.info('[Veracruz] '+mapped.length+' mapped attractions; '+catalog.length+' recovered catalog records searchable.');
}).catch(e=>{console.error('[Veracruz catalog]',e);toggle.textContent='Catalog error: '+e.message;});
})();
