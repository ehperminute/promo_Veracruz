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
   scrollZoom:false, // Scrolling the homepage should not change the map zoom.
   style:{version:8,sources:{osm:{type:'raster',tiles:['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],tileSize:256,
    attribution:'© OpenStreetMap contributors'}},layers:[{id:'osm-tiles',type:'raster',source:'osm'}]}
 });
if(mapObject)mapObject.addControl(new maplibregl.NavigationControl({showCompass:false}),'top-right');
const state={features:[],filter:'',query:'',all:false,selected:null,ready:false};
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
 detail.hidden=false;$('vx-side')?.scrollTo({top:0,behavior:'smooth'}); // Do not scroll the whole page unexpectedly.
 if(mapObject){mapObject.flyTo({center:feature.geometry.coordinates,zoom:Math.max(mapObject.getZoom(),8.7),essential:true});}
}
// Native MapLibre GeoJSON layers render with the basemap, unlike separately
// positioned DOM marker buttons. This removes CSS/page-scroll drift.
// The icons encode ALL available experience types as coloured segments.
function badgeName(types){
  const t=[...new Set(types||[])].filter(k=>Object.hasOwn(palette,k)).sort();
  return t.length?'vx-badge-'+t.join('-'):'vx-badge-empty';
}
function registerBadge(types){
  if(!mapObject)return;
  const id=badgeName(types);
  if(mapObject.hasImage(id))return;
  const keys=[...new Set(types||[])].filter(k=>Object.hasOwn(palette,k)).sort();
  const c=document.createElement('canvas'),size=88;
  c.width=c.height=size;
  const ctx=c.getContext('2d');
  if(!ctx)return;
  const center=size/2,ringRadius=31;
  ctx.lineWidth=12;
  if(keys.length){
    keys.forEach((k,i)=>{
      const full=2*Math.PI/keys.length;
      const begin=-Math.PI/2+i*full+(keys.length===1?0:0.055);
      const end=-Math.PI/2+(i+1)*full-(keys.length===1?0:0.055);
      ctx.beginPath();ctx.arc(center,center,ringRadius,begin,end);
      ctx.strokeStyle=palette[k];ctx.stroke();
    });
  }else{
    ctx.beginPath();ctx.arc(center,center,ringRadius,0,2*Math.PI);
    ctx.strokeStyle='#a4b1a8';ctx.stroke();
  }
  ctx.beginPath();ctx.arc(center,center,22,0,2*Math.PI);
  ctx.fillStyle='#285b48';ctx.fill();
  ctx.lineWidth=3;ctx.strokeStyle='#fff';ctx.stroke();
  ctx.beginPath();ctx.arc(center,center,4,0,2*Math.PI);
  ctx.fillStyle='#fff';ctx.fill();
  mapObject.addImage(id,ctx.getImageData(0,0,size,size),{pixelRatio:2});
}
function mapFeatures(){
  return {type:'FeatureCollection',features:visible().map(f=>({
    type:'Feature',geometry:f.geometry,
    properties:{key:String(f.id),badge:badgeName(f.properties.types)}
  }))};
}
function refreshMapSource(){
  if(!mapObject || !state.ready)return;
  state.features.forEach(f=>registerBadge(f.properties.types));
  const src=mapObject.getSource('vx-locations');
  if(src)src.setData(mapFeatures());
}
function prepareMapLayers(){
  if(state.ready)return;
  mapObject.addSource('vx-locations',{
    type:'geojson',data:{type:'FeatureCollection',features:[]},
    cluster:true,clusterRadius:52,clusterMaxZoom:10
  });
  mapObject.addLayer({id:'vx-clusters',type:'circle',source:'vx-locations',
    filter:['has','point_count'],paint:{
      'circle-color':'#286953','circle-radius':['step',['get','point_count'],19,10,23,30,27],
      'circle-stroke-color':'#eef6ef','circle-stroke-width':3
    }
  });
  mapObject.addLayer({id:'vx-cluster-count',type:'symbol',source:'vx-locations',
    filter:['has','point_count'],layout:{'text-field':['to-string',['get','point_count']],
      'text-size':13,'text-allow-overlap':true},paint:{'text-color':'#fff'}
  });
  mapObject.addLayer({id:'vx-places',type:'symbol',source:'vx-locations',
    filter:['!', ['has','point_count']],
    layout:{'icon-image':['get','badge'],'icon-allow-overlap':true,
      'icon-ignore-placement':true,'icon-size':1}
  });
  mapObject.on('click','vx-places',e=>{
    const key=e.features?.[0]?.properties?.key;
    const selected=state.features.find(f=>String(f.id)===String(key));
    if(selected)openDetail(selected);
  });
  mapObject.on('click','vx-clusters',async e=>{
    const cluster=e.features?.[0];if(!cluster)return;
    try{
      const zoom=await mapObject.getSource('vx-locations').getClusterExpansionZoom(cluster.properties.cluster_id);
      mapObject.easeTo({center:cluster.geometry.coordinates,zoom:zoom+0.1,duration:550});
    }catch(error){console.warn('Cluster expansion:',error);}
  });
  for(const id of ['vx-places','vx-clusters']){
    mapObject.on('mouseenter',id,()=>{mapObject.getCanvas().style.cursor='pointer';});
    mapObject.on('mouseleave',id,()=>{mapObject.getCanvas().style.cursor='';});
  }
  state.ready=true;
  refreshMapSource();
}
function render(){const t=copy();$('vx-title').textContent=t.title;$('vx-subtitle').textContent=t.subtitle;
 $('vx-search').placeholder=t.search;$('vx-toggle-label').textContent=state.all?t.all:t.documented;
 $('vx-caveat').textContent=`${t.approximate} ${t.counts}`;
 const select=$('vx-category'),saved=state.filter;select.replaceChildren(new Option(t.category,''));for(const k of orderedTypes){if(state.features.some(f=>f.properties.types.includes(k)))select.append(new Option(t.types[k],k));}select.value=saved;
 const shown=visible();$('vx-status').textContent=shown.length?t.visible(shown.length,state.features.length):t.noResults;$('vx-top-count').textContent=state.features.length?`${state.features.length} municipios · 216 actividades vinculadas`:'';
 const list=$('vx-list');list.replaceChildren();for(const f of shown){const p=f.properties;const button=element('button','vx-result');button.type='button';const top=element('div','vx-result-top');top.append(element('strong','',p.name));top.append(element('span','vx-result-count',String(p.activity_count)));button.append(top);if(p.types.length){const tags=element('div','vx-mini-dots');for(const type of p.types)tags.append(dot(type));button.append(tags);}else button.append(element('span','vx-no-data',t.absence));button.onclick=()=>openDetail(f);list.append(button);}
 const leg=$('vx-legend');leg.replaceChildren();for(const k of orderedTypes){if(!state.features.some(f=>f.properties.types.includes(k)))continue;const tag=element('span','vx-legend-item');tag.append(dot(k),document.createTextNode(t.types[k]));leg.append(tag);}
 if(state.selected){const f=state.features.find(f=>String(f.id)===String(state.selected));if(f)openDetailWithoutMove(f);}
 refreshMapSource();
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
if(mapObject){
 mapObject.on('load',prepareMapLayers);
 mapObject.on('error',e=>console.warn('MapLibre basemap:',e.error?.message));
 // CSS/layout changes to an embedded map do not always emit window.resize.
 if(typeof ResizeObserver!=='undefined')new ResizeObserver(()=>mapObject.resize()).observe($('vx-map'));
}
fetch('data/map_points.geojson',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error(`HTTP ${r.status}`);return r.json();}).then(fc=>{
 if(fc.type!=='FeatureCollection'||!Array.isArray(fc.features))throw Error('Invalid GeoJSON');
 state.features=fc.features.filter(f=>f.geometry?.type==='Point'&&f.geometry.coordinates.length===2&&
   f.geometry.coordinates.every(Number.isFinite)&&f.geometry.coordinates[0]>-100&&f.geometry.coordinates[0]<-93&&
   f.geometry.coordinates[1]>17&&f.geometry.coordinates[1]<23&&Array.isArray(f.properties?.activities)&&Array.isArray(f.properties?.types));
 render();if(mapObject&&state.features.length){const b=new maplibregl.LngLatBounds();state.features.forEach(f=>b.extend(f.geometry.coordinates));mapObject.fitBounds(b,{padding:42,maxZoom:6.6,duration:0});}
}).catch(error=>{$('vx-status').textContent='Map catalog could not be loaded. '+error.message;console.error('Veracruz map:',error);});
render();
})();
