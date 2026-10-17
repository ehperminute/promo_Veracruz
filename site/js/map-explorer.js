/* Veracruz tourism explorer — static, read-only display of the latest curated SQLite export.
   The geometry is a municipality-scale APPROXIMATE reference point. Not a site of activity. */
(() => {
'use strict';
const root = document.getElementById('veracruz-map-section');
if (!root) return;
const palette = {
  adventure:'#dc7d3d',water:'#188ba8',nature:'#35856c',food:'#c55e62',
  culture:'#815caa',crafts:'#a77b3c',wellness:'#35a09a',scenic:'#5978bd',other:'#7e8587'
};
const translations = {
 es:{title:'Veracruz, por explorar',subtitle:'Descubre experiencias documentadas en todo el estado',search:'Buscar municipios, actividades o experiencias…',
   documented:'Con actividades documentadas',all:'Todos los municipios',category:'Todas las experiencias',visible:(v,t)=>`${v} de ${t} municipios`,
   approximate:'Los puntos representan ubicaciones municipales aproximadas, NO coordenadas de atracciones ni paradas utilizables para rutas.',
   absence:'Sin actividad documentada en este conjunto de evidencia. Esto NO significa que el municipio carezca de turismo.',
   activity:'Actividades documentadas',more:'Ver actividades y fuentes',sources:'Fuentes',noResults:'No hay resultados para estos filtros.',
   original:'Texto original conservado',summary:'Evidencia con resumen de fuente (descripción original pendiente)',back:'Volver a explorar',
   missingMap:'No se pudo cargar el mapa base. Los datos siguen disponibles en la lista.',
   counts:'La cobertura indica evidencia disponible, no popularidad, calidad ni demanda.',
   types:{adventure:'Aventura',water:'Agua',nature:'Naturaleza',food:'Gastronomía y campo',culture:'Cultura e historia',crafts:'Artesanías',wellness:'Bienestar',scenic:'Paseos panorámicos',other:'Otras'}},
 en:{title:'Veracruz, waiting to be explored',subtitle:'Discover documented experiences across the state',search:'Search municipalities, activities, or experiences…',
   documented:'Documented activities',all:'All municipalities',category:'All experiences',visible:(v,t)=>`${v} of ${t} municipalities`,
   approximate:'Markers are approximate municipality reference points, NOT attraction locations or routing stops.',
   absence:'No activity documented in this evidence set. This does NOT mean the municipality has no tourism.',
   activity:'Documented activities',more:'Activities and sources',sources:'Sources',noResults:'No matching municipalities.',
   original:'Original source passage retained',summary:'Source-summary evidence (original description pending)',back:'Back to explore',
   missingMap:'Map tiles could not be loaded. Location data is still available in the list.',
   counts:'Coverage reflects available evidence, not popularity, quality, or demand.',
   types:{adventure:'Adventure',water:'Water',nature:'Nature',food:'Food & agriculture',culture:'History & culture',crafts:'Crafts',wellness:'Wellness',scenic:'Scenic transport',other:'Other'}},
 ja:{title:'ベラクルスを探索',subtitle:'州内の資料に基づく体験を探す',search:'市町村名・アクティビティを検索…',
   documented:'資料で確認された体験',all:'全自治体',category:'すべての体験',visible:(v,t)=>`${v} / ${t} 自治体`,
   approximate:'地点は自治体の概略位置です。観光施設や移動経路の正確な位置ではありません。',
   absence:'この資料では確認できるアクティビティがありません。観光資源がないという意味ではありません。',
   activity:'資料に基づくアクティビティ',more:'アクティビティと出典',sources:'出典',noResults:'該当する場所はありません。',
   original:'原典テキストあり',summary:'出典要約のみ（原文未復元）',back:'一覧に戻る',
   missingMap:'地図タイルを読み込めませんでした。リストから情報を確認できます。',
   counts:'記録の有無は人気・品質・需要の評価ではありません。',
   types:{adventure:'冒険',water:'水辺',nature:'自然',food:'食と農業',culture:'歴史・文化',crafts:'工芸',wellness:'ウェルネス',scenic:'景観ルート',other:'その他'}}
};
const element=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=String(text);return n;};
function language(){const cand=[document.getElementById('language-select')?.value,document.querySelector('select[name="language"]')?.value,document.documentElement.lang];for(const c of cand){if(c && translations[String(c).toLowerCase().slice(0,2)])return String(c).toLowerCase().slice(0,2);}return 'es';}
function copy(){return translations[language()];}
function clean(s){return String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase().trim();}
root.innerHTML=`<div class="vx-top"><div><span class="vx-kicker">VERACRUZ · EXPLORER</span><h2 id="vx-title"></h2><p id="vx-subtitle"></p></div><div id="vx-top-count" class="vx-count-pill"></div></div>
 <div class="vx-explorer"><div class="vx-toolbar"><label class="vx-search-wrap"><svg viewBox="0 0 24 24" width="19" height="19" aria-hidden="true"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2"/><path d="m16.5 16.5 5 5" stroke="currentColor" stroke-width="2"/></svg><input id="vx-search" type="search" autocomplete="off" /></label>
 <select id="vx-category" aria-label="Experience category"></select><label class="vx-toggle"><input type="checkbox" id="vx-show-all"/><span id="vx-toggle-label"></span></label></div>
 <div class="vx-body"><div id="vx-map" aria-label="Interactive Veracruz municipality map"><div id="vx-map-fallback" hidden></div></div><aside class="vx-side"><div id="vx-status" class="vx-status" aria-live="polite"></div><div id="vx-detail" class="vx-detail" hidden></div><div id="vx-list" class="vx-list"></div></aside></div>
 <div class="vx-foot"><div id="vx-legend" class="vx-legend"></div><p id="vx-caveat"></p></div></div>`;
const $ = id=>root.querySelector('#'+id);
const mapObject=typeof maplibregl==='undefined'?null:new maplibregl.Map({
   container:'vx-map',center:[-96.4,19.5],zoom:6.05,minZoom:5,
   style:{version:8,sources:{osm:{type:'raster',tiles:['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],tileSize:256,
    attribution:'© OpenStreetMap contributors'}},layers:[{id:'osm-tiles',type:'raster',source:'osm'}]}
 });
if(mapObject)mapObject.addControl(new maplibregl.NavigationControl({showCompass:false}),'top-right');
const state={features:[],filter:'',query:'',all:false,markers:[],selected:null,ready:false};
const nameOf=a=>language()==='es'?a.name_es:(a.name_en||a.name_es);
const orderedTypes=Object.keys(palette);
function eligible(f){const p=f.properties;return (!state.filter||p.types.includes(state.filter)) && (state.all||p.activity_count>0) && (!state.query||clean([p.name,...p.activities.flatMap(a=>[a.name_es,a.name_en,a.id]),...p.types.map(k=>copy().types[k]||k)].join(' ')).includes(state.query));}
function visible(){return state.features.filter(eligible);}
function labelType(k){return copy().types[k]||k;}
function dot(t){const d=element('i','vx-dot');d.style.background=palette[t]||palette.other;return d;}
function badges(p,holder){if(!p.types.length){holder.append(element('span','vx-empty-chip','—'));return;}
  for(const t of p.types){const tag=element('span','vx-tag');tag.append(dot(t),document.createTextNode(labelType(t)));holder.append(tag);}}
function openDetail(feature){state.selected=feature.id;const p=feature.properties, t=copy(),detail=$('vx-detail');detail.replaceChildren();
 const top=element('div','vx-detail-top');top.append(element('h3','',p.name));const close=element('button','vx-close','×');close.type='button';close.setAttribute('aria-label',t.back);close.onclick=()=>{detail.hidden=true;state.selected=null;};top.append(close);detail.append(top);
 const chips=element('div','vx-tags');badges(p,chips);detail.append(chips);
 const note=element('p','vx-note',t.approximate);detail.append(note);
 if(p.activities.length){detail.append(element('h4','',`${t.activity} · ${p.activities.length}`));
   const list=element('ul','vx-activity-list');for(const a of p.activities){const li=element('li','vx-activity');const r=element('div','vx-activity-title');r.append(dot(a.type),document.createTextNode(nameOf(a)));li.append(r);
    const evidence=element('p','vx-proof',a.original_text_support_count>0?t.original:t.summary);li.append(evidence);
    if(a.source_urls.length){const links=element('div','vx-links');a.source_urls.slice(0,3).forEach((url,i)=>{try{if(new URL(url).protocol!=='https:')return;}catch{return;}
      const link=element('a','',`${t.sources} ${i+1} ↗`);link.href=url;link.target='_blank';link.rel='noopener noreferrer';links.append(link);});li.append(links);}list.append(li);}detail.append(list);
 }else{detail.append(element('p','vx-note',t.absence));}
 detail.hidden=false;$('vx-side')?.scrollTo({top:0,behavior:'smooth'});detail.scrollIntoView?.({block:'nearest',behavior:'smooth'});
 if(mapObject){mapObject.flyTo({center:feature.geometry.coordinates,zoom:Math.max(mapObject.getZoom(),8.7),essential:true});}
}
function makePin(feature){const p=feature.properties;const b=element('button','vx-pin');b.type='button';b.title=p.name;b.setAttribute('aria-label',p.name);b.append(element('span','vx-pin-center',p.activity_count?'•':'·'));const colors=element('span','vx-pin-colors');for(const t of p.types.slice(0,4)) colors.append(dot(t));if(p.types.length>4)colors.append(element('small','',`+${p.types.length-4}`));b.append(colors);b.onclick=()=>openDetail(feature);return b;}
function makeCluster(group){const b=element('button','vx-cluster',String(group.length));b.type='button';b.title=`${group.length} municipios`;b.onclick=()=>{if(!mapObject)return;const bb=new maplibregl.LngLatBounds();group.forEach(f=>bb.extend(f.geometry.coordinates));mapObject.fitBounds(bb,{padding:90,maxZoom:12,duration:500});};return b;}
function clearMarkers(){state.markers.forEach(m=>m.remove());state.markers=[];}
function drawMarkers(){if(!mapObject || !state.ready)return;clearMarkers();const candidates=visible();if(!candidates.length)return;
 // Screen-space clustering only at statewide and regional zooms (no category is lost).
 const groups=[];const zoom=mapObject.getZoom();const clusterThreshold=zoom<8.5?46:0;
 for(const f of candidates){const coordinate=f.geometry.coordinates;if(!clusterThreshold){groups.push([f]);continue;}
   const xy=mapObject.project(coordinate);let found=null;for(const g of groups){const avg=g._xy;if(Math.hypot(avg.x-xy.x,avg.y-xy.y)<clusterThreshold){found=g;break;}}
   if(found){found.push(f);const n=found.length;found._xy={x:found._xy.x+(xy.x-found._xy.x)/n,y:found._xy.y+(xy.y-found._xy.y)/n};}
   else {const g=[f];g._xy={x:xy.x,y:xy.y};groups.push(g);}
 }
 for(const group of groups){const coord=group.length===1?group[0].geometry.coordinates:mapObject.unproject(group._xy).toArray();
   const e=group.length===1?makePin(group[0]):makeCluster(group);
   state.markers.push(new maplibregl.Marker({element:e,anchor:'center'}).setLngLat(coord).addTo(mapObject));
 }
}
function render(){const t=copy();$('vx-title').textContent=t.title;$('vx-subtitle').textContent=t.subtitle;
 $('vx-search').placeholder=t.search;$('vx-toggle-label').textContent=state.all?t.all:t.documented;
 $('vx-caveat').textContent=`${t.approximate} ${t.counts}`;
 const select=$('vx-category'),saved=state.filter;select.replaceChildren(new Option(t.category,''));for(const k of orderedTypes){if(state.features.some(f=>f.properties.types.includes(k)))select.append(new Option(t.types[k],k));}select.value=saved;
 const shown=visible();$('vx-status').textContent=shown.length?t.visible(shown.length,state.features.length):t.noResults;$('vx-top-count').textContent=state.features.length?`${state.features.length} municipios · 216 actividades vinculadas`:'';
 const list=$('vx-list');list.replaceChildren();for(const f of shown){const p=f.properties;const button=element('button','vx-result');button.type='button';const top=element('div','vx-result-top');top.append(element('strong','',p.name));top.append(element('span','vx-result-count',String(p.activity_count)));button.append(top);if(p.types.length){const tags=element('div','vx-mini-dots');for(const type of p.types)tags.append(dot(type));button.append(tags);}else button.append(element('span','vx-no-data',t.absence));button.onclick=()=>openDetail(f);list.append(button);}
 const leg=$('vx-legend');leg.replaceChildren();for(const k of orderedTypes){if(!state.features.some(f=>f.properties.types.includes(k)))continue;const tag=element('span','vx-legend-item');tag.append(dot(k),document.createTextNode(t.types[k]));leg.append(tag);}
 if(state.selected){const f=state.features.find(f=>String(f.id)===String(state.selected));if(f)openDetailWithoutMove(f);}
 drawMarkers();
}
function openDetailWithoutMove(feature){ // Update language in an already open detail without triggering map movement.
 const m=mapObject;
 // Keep state selected and render the detail in its current coordinates without re-flying.
 // Instead of reusing openDetail's flyTo, only call on explicit clicks; language-change simply closes it.
 $('vx-detail').hidden=true;state.selected=null;
}
$('vx-search').addEventListener('input',e=>{state.query=clean(e.target.value);render();});
$('vx-category').addEventListener('change',e=>{state.filter=e.target.value;render();});
$('vx-show-all').addEventListener('change',e=>{state.all=e.target.checked;render();});
// Site translation may change through its own custom code; listen at document level.
document.addEventListener('change',e=>{if(e.target!==$('vx-category')&&e.target!==$('vx-show-all')&&e.target!==$('vx-search'))render();});
new MutationObserver(()=>render()).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
if(mapObject){mapObject.on('moveend',drawMarkers);mapObject.on('load',()=>{state.ready=true;drawMarkers();});mapObject.on('error',e=>console.warn('MapLibre basemap:',e.error?.message));}
fetch('data/map_points.geojson',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error(`HTTP ${r.status}`);return r.json();}).then(fc=>{
 if(fc.type!=='FeatureCollection'||!Array.isArray(fc.features))throw Error('Invalid GeoJSON');
 state.features=fc.features.filter(f=>f.geometry?.type==='Point'&&f.geometry.coordinates.length===2&&
   f.geometry.coordinates.every(Number.isFinite)&&f.geometry.coordinates[0]>-100&&f.geometry.coordinates[0]<-93&&
   f.geometry.coordinates[1]>17&&f.geometry.coordinates[1]<23&&Array.isArray(f.properties?.activities)&&Array.isArray(f.properties?.types));
 render();if(mapObject&&state.features.length){const b=new maplibregl.LngLatBounds();state.features.forEach(f=>b.extend(f.geometry.coordinates));mapObject.fitBounds(b,{padding:42,maxZoom:6.6,duration:0});}
}).catch(error=>{$('vx-status').textContent='Map catalog could not be loaded. '+error.message;console.error('Veracruz map:',error);});
render();
})();
