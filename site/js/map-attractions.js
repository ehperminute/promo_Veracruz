/* Veracruz attraction explorer v2.
 * Source of truth: site/data/attractions.csv -> build_attractions.py -> attractions.geojson
 * This overlay only reads data. It never overwrites the municipality map or research database.
 */
(() => {
 'use strict';
 const root=document.getElementById('veracruz-map-section');
 const map=window.__vx_attraction_map,lib=window.maplibregl;
 if(!root||!map||!lib){console.warn('[Attractions] Map not ready; check base script order.');return;}
 const search=root.querySelector('#vx-search'),side=root.querySelector('.vx-side'),status=root.querySelector('#vx-status');
 if(!search||!side||!status){console.warn('[Attractions] Missing explorer controls.');return;}
 const mainDetail=root.querySelector('#vx-detail'),mainList=root.querySelector('#vx-list');
 const lang=()=>['en','es','ja'].includes(document.documentElement.lang?.slice(0,2))?document.documentElement.lang.slice(0,2):'en';
 const tr={
 en:{attractions:'Attractions',results:'Matching attractions',none:'No named attractions match this search.',guide:'Destination guide',back:'Back to places',map:'Map point',source:'Geographic source',noVisit:'This is a mapped geographic point, not a verified visitor entrance.',area:'This marker represents an area, not a specific visitor entrance.',photos:'Photography',details:'Discover',practical:'Planning your visit',unknown:'Visitor access and opening information have not been confirmed.',see:'Read full guide',empty:'More details are being researched.'},
 es:{attractions:'Atractivos',results:'Atractivos encontrados',none:'No hay atractivos con ese nombre.',guide:'Guía del lugar',back:'Volver a los lugares',map:'Ubicación en el mapa',source:'Fuente geográfica',noVisit:'Se trata de una ubicación geográfica, no de una entrada verificada.',area:'Este marcador representa un área, no una entrada concreta.',photos:'Fotografía',details:'Descubre',practical:'Antes de visitar',unknown:'Todavía no se ha confirmado el acceso ni los horarios.',see:'Ver la guía',empty:'Seguimos investigando información de este lugar.'},
 ja:{attractions:'観光スポット',results:'検索結果',none:'該当する観光地はありません。',guide:'観光ガイド',back:'一覧に戻る',map:'地図上の位置',source:'位置情報の出典',noVisit:'この地点は入場口として確認されていません。',area:'この地点は広い地域を示しており、入場口ではありません。',photos:'写真',details:'見どころ',practical:'訪問のヒント',unknown:'入場条件と営業時間は未確認です。',see:'ガイドを見る',empty:'詳細は調査中です。'}
 };
 const t=()=>tr[lang()];
 const norm=x=>String(x||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
 const div=(cls,tag='div')=>{const x=document.createElement(tag);x.className=cls;return x;};
 const label=(tag,cls,value)=>{const x=div(cls,tag);x.textContent=value;return x;};
 const safeLink=(url,text)=>{const a=document.createElement('a');a.textContent=text;a.href=url;a.target='_blank';a.rel='noopener noreferrer';return a;};
 const panel=div('vxa-panel','section');panel.hidden=true;panel.setAttribute('aria-label','Attractions');
 const toggle=div('vxa-toggle','button');toggle.type='button';
 status.insertAdjacentElement('afterend',toggle);toggle.insertAdjacentElement('afterend',panel);
 const guide=div('vxa-guide','section');guide.hidden=true;guide.setAttribute('aria-label','Attraction guide');panel.insertAdjacentElement('afterend',guide);
 let features=[],markers=[],expanded=false,active=null,popup=null;
 const nameOf=p=>p.name||p.attraction_name_original||'Attraction';
 const textOf=(p,k)=>p[k+'_'+lang()] || p[k+'_en'] || p[k+'_es'] || '';
 const iconOf=p=>p.icon||'📍';
 function clearSelection(){
  active=null;guide.hidden=true; if(mainDetail)mainDetail.style.removeProperty('display');if(mainList)mainList.style.removeProperty('display');
  if(popup){popup.remove();popup=null;}
  for(const m of markers)m.el.classList.remove('vxa-selected');
  renderList();
 }
 function guideRender(f){
  const p=f.properties;
  guide.replaceChildren();
  const back=label('button','vxa-back','← '+t().back);back.type='button';back.addEventListener('click',clearSelection);guide.append(back);
  if(p.photo_url){
   const fig=div('vxa-photo','figure'),img=document.createElement('img');img.loading='lazy';img.src=p.photo_url;img.alt=nameOf(p);img.referrerPolicy='no-referrer';
   img.addEventListener('error',()=>{fig.remove();});fig.append(img);
   const cap=div('','figcaption');cap.append(safeLink(p.photo_source_url,p.photo_credit||t().photos));fig.append(cap);guide.append(fig);
  }
  guide.append(label('h3','vxa-name',iconOf(p)+' '+nameOf(p)));
  if(p.municipality)guide.append(label('p','vxa-municipality',p.municipality+' · '+p.type));
  const intro=textOf(p,'description');if(intro)guide.append(label('p','vxa-intro',intro));
  const detail=textOf(p,'details');if(detail){guide.append(label('h4','vxa-subhead',t().details));guide.append(label('p','vxa-bodytext',detail));}
  const visit=textOf(p,'visit_note');if(visit){guide.append(label('h4','vxa-subhead',t().practical));guide.append(label('p','vxa-bodytext',visit));}
  if(p.status!=='entrance_verified'){
   const disclosure=div('vxa-disclosure','details');disclosure.append(label('summary','',t().map));disclosure.append(label('p','',p.status==='mapped_area'?t().area:t().noVisit));
   guide.append(disclosure);
  }
  const links=div('vxa-links');
  if(p.source_url)links.append(safeLink(p.source_url,t().source+' ↗'));
  if(p.photo_source_url)links.append(safeLink(p.photo_source_url,t().photos+' ↗'));
  guide.append(links);
  guide.hidden=false;
  if(mainDetail)mainDetail.style.display='none';if(mainList)mainList.style.display='none';
  side.scrollTo({top:0,behavior:'smooth'});
 }
 function minimalPopup(f){
  const p=f.properties,holder=div('vxa-popup');
  holder.append(label('strong','',iconOf(p)+' '+nameOf(p)));
  holder.append(label('p','',p.municipality||p.type||''));
  const b=label('button','vxa-open',t().see+' →');b.type='button';b.addEventListener('click',()=>guideRender(f));holder.append(b);
  return holder;
 }
 function focus(f){
  active=String(f.properties.id||f.id);const coords=f.geometry.coordinates;
  map.flyTo({center:coords,zoom:Math.max(map.getZoom(),10),essential:true});
  for(const m of markers)m.el.classList.toggle('vxa-selected',m.id===active);
  // Clear municipality-only search before showing guide; its input listener hides guides.
  if(search.value){search.value='';search.dispatchEvent(new Event('input',{bubbles:true}));}
  if(popup)popup.remove();
  popup=new lib.Popup({offset:20,maxWidth:'250px',closeButton:true}).setLngLat(coords).setDOMContent(minimalPopup(f)).addTo(map);
  guideRender(f);renderList();
 }
 function marker(f){
  const p=f.properties,el=div('vxa-marker');el.tabIndex=0;el.setAttribute('role','button');el.setAttribute('aria-label',nameOf(p));el.title=nameOf(p);
  const core=div('vxa-marker-icon');core.textContent=iconOf(p);el.append(core);
  const n=label('span','vxa-marker-label',nameOf(p));el.append(n);
  el.addEventListener('click',e=>{e.stopPropagation();focus(f)});
  el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();focus(f);}});
  new lib.Marker({element:el,anchor:'center',subpixelPositioning:true}).setLngLat(f.geometry.coordinates).addTo(map);
  markers.push({el,id:String(p.id||f.id)});
 }
 function renderList(){
  const q=norm(search.value),matches=features.filter(f=>norm(nameOf(f.properties)+' '+(f.properties.municipality||'')+' '+(f.properties.type||'')).includes(q));
  const isOpen=Boolean(q)||expanded;
  panel.hidden=!isOpen || !guide.hidden;
  toggle.textContent=`${t().attractions} · ${features.length}  ${expanded?'▴':'▾'}`;
  toggle.setAttribute('aria-expanded',String(expanded));
  if(!isOpen || !guide.hidden) return;
  panel.replaceChildren();panel.append(label('h4','',q?`${t().results} · ${matches.length}`:t().attractions));
  if(!matches.length){panel.append(label('p','vxa-empty',t().none));return;}
  for(const f of matches){
   const p=f.properties,b=div('vxa-item','button');b.type='button';
   b.append(label('span','vxa-item-icon',iconOf(p)));
   const s=div('vxa-item-name');s.append(label('strong','',nameOf(p)),label('small','',p.municipality||p.type||''));b.append(s);
   b.addEventListener('click',()=>focus(f));panel.append(b);
  }
 }
 function zoomLabels(){
  const z=map.getZoom();
  for(const m of markers)m.el.classList.toggle('vxa-labels-on',z>=9.2 || m.id===active);
 }
 toggle.addEventListener('click',()=>{expanded=!expanded;clearSelection();renderList();});
 search.addEventListener('input',()=>{if(!guide.hidden){guide.hidden=true;if(mainDetail)mainDetail.style.removeProperty('display');if(mainList)mainList.style.removeProperty('display');}renderList();});
 search.addEventListener('keydown',e=>{if(e.key!=='Enter')return;const q=norm(search.value);const f=features.find(f=>q && norm(nameOf(f.properties)).includes(q));if(f){e.preventDefault();focus(f);}});
 map.on('zoom',zoomLabels);
 fetch('data/attractions.geojson',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('HTTP '+r.status);return r.json();}).then(fc=>{
  if(fc.type!=='FeatureCollection'||!Array.isArray(fc.features))throw Error('Invalid GeoJSON');
  features=fc.features.filter(f=>f.geometry?.type==='Point'&&f.geometry.coordinates?.length===2&&f.geometry.coordinates.every(Number.isFinite));
  features.forEach(marker);zoomLabels();renderList();
  console.info('[Veracruz attractions] Loaded',features.length,'source-linked attraction points');
 }).catch(e=>{console.error('[Veracruz attractions]',e);toggle.textContent='Attractions: '+e.message;});
})();
