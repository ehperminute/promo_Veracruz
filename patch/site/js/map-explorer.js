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
   documented:'Con actividades documentadas',all:'Todos los municipios',category:'Todas las experiencias',specific:'Cualquier actividad',focus:'Ver coincidencias en el mapa',matching:(m,v)=>`${m} coincidencias de ${v} visibles`,gesture:'Usa dos dedos para mover o acercar el mapa',visible:(v,t)=>`${v} de ${t} municipios`,
   approximate:'Los puntos ubican municipios de forma aproximada; no señalan entradas a atractivos.',
   absence:'Sin actividad documentada en este conjunto de evidencia. Esto NO significa que el municipio carezca de turismo.',
   activity:'Actividades documentadas',more:'Ver actividades y fuentes',sources:'Fuentes',noResults:'No hay resultados para estos filtros.',
   original:'Texto original conservado',summary:'Evidencia con resumen de fuente (descripción original pendiente)',back:'Volver a explorar',
   missingMap:'No se pudo cargar el mapa base. Los datos siguen disponibles en la lista.',
   counts:'La cobertura indica evidencia disponible, no popularidad, calidad ni demanda.',
   types:{adventure:'Aventura',water:'Agua',nature:'Naturaleza',food:'Gastronomía y campo',culture:'Cultura e historia',crafts:'Artesanías',wellness:'Bienestar',scenic:'Paseos panorámicos',other:'Otras'}},
 en:{title:'Veracruz, waiting to be explored',subtitle:'Discover documented experiences across the state',search:'Search municipalities, activities, or experiences…',
   documented:'Documented activities',all:'All municipalities',category:'All experiences',specific:'Any activity',focus:'Zoom to matches',matching:(m,v)=>`${m} matches among ${v} shown`,gesture:'Use two fingers to move or zoom the map',visible:(v,t)=>`${v} of ${t} municipalities`,
   approximate:'Markers show approximate municipal locations, not precise attraction entrances.',
   absence:'No activity documented in this evidence set. This does NOT mean the municipality has no tourism.',
   activity:'Documented activities',more:'Activities and sources',sources:'Sources',noResults:'No matching municipalities.',
   original:'Original source passage retained',summary:'Source-summary evidence (original description pending)',back:'Back to explore',
   missingMap:'Map tiles could not be loaded. Location data is still available in the list.',
   counts:'Coverage reflects available evidence, not popularity, quality, or demand.',
   types:{adventure:'Adventure',water:'Water',nature:'Nature',food:'Food & agriculture',culture:'History & culture',crafts:'Crafts',wellness:'Wellness',scenic:'Scenic transport',other:'Other'}},
 ja:{title:'ベラクルスを探索',subtitle:'州内の資料に基づく体験を探す',search:'市町村名・アクティビティを検索…',
   documented:'資料で確認された体験',all:'全自治体',category:'すべての体験',specific:'すべてのアクティビティ',focus:'一致する地点を表示',matching:(m,v)=>`${v} 件中 ${m} 件が一致`,gesture:'地図の操作・ズームには2本指を使用',visible:(v,t)=>`${v} / ${t} 自治体`,
   approximate:'地点は自治体の概略位置です。観光施設や移動経路の正確な位置ではありません。',
   absence:'この資料では確認できるアクティビティがありません。観光資源がないという意味ではありません。',
   activity:'資料に基づくアクティビティ',more:'アクティビティと出典',sources:'出典',noResults:'該当する場所はありません。',
   original:'原典テキストあり',summary:'出典要約のみ（原文未復元）',back:'一覧に戻る',
   missingMap:'地図タイルを読み込めませんでした。リストから情報を確認できます。',
   counts:'記録の有無は人気・品質・需要の評価ではありません。',
   types:{adventure:'冒険',water:'水辺',nature:'自然',food:'食と農業',culture:'歴史・文化',crafts:'工芸',wellness:'ウェルネス',scenic:'景観ルート',other:'その他'}}
};
const activityEs = {
 '4x4_mountain_transfer':'Traslado de montaña en 4×4','aguamiel_extraction':'Extracción de aguamiel','aguamiel_tasting':'Degustación de aguamiel','ancestral_ritual_participation':'Participación en rituales ancestrales',
 'archaeological_visit':'Visita a zonas arqueológicas','aromatherapy':'Aromaterapia','artisan_workshop':'Taller de artesanía','atv':'Recorrido en cuatrimoto','backstrap_loom_weaving':'Tejido en telar de cintura',
 'birdwatching':'Observación de aves','boat_excursion':'Paseo en lancha','botanical_garden_visit':'Visita a jardín botánico','cable_car_ride':'Paseo en teleférico','camping':'Campismo','canyoning':'Barranquismo',
 'ceremony_honoring_mother_earth':'Ceremonia de homenaje a la Madre Tierra','clay_modelling_workshop':'Taller de modelado en barro','coffee_cupping':'Catación de café','coffee_depulping':'Despulpado de café',
 'coffee_farm_visit':'Visita a finca cafetalera','coffee_grinding':'Molienda de café','coffee_harvesting':'Cosecha de café','coffee_planting':'Siembra de café','coffee_roasting':'Tostado de café','coffee_tasting':'Degustación de café',
 'colonial_heritage_church_house_visit':'Visita a patrimonio colonial','colonial_house_visit':'Visita a casas coloniales','community_museum_visit':'Visita a museo comunitario','community_plant_nursery_visit':'Visita a vivero comunitario',
 'cycling':'Ciclismo','diving':'Buceo','ethnobotanical_learning':'Aprendizaje etnobotánico','fishing':'Pesca','fortress_visit':'Visita a fortaleza','gastronomy_tasting_tour':'Ruta de degustación gastronómica',
 'guided_city_tour':'Recorrido guiado por la ciudad','guided_heritage_walk':'Paseo guiado de patrimonio','herpetology_observation':'Observación de reptiles y anfibios','hiking':'Senderismo','hookah_diving':'Buceo con suministro desde superficie',
 'horseback_riding':'Paseo a caballo','hydrotherapy':'Hidroterapia','kayaking':'Kayak','leather_shoemaking_demonstration':'Demostración de zapatería artesanal','mangrove_excursion':'Recorrido por manglares',
 'marine_cave_exploration':'Exploración de cuevas marinas','massage':'Masaje','medicinal_plant_walk':'Paseo sobre plantas medicinales','mineral_clay_treatment':'Tratamiento con arcilla mineral',
 'mountain_biking':'Ciclismo de montaña','museum_visit':'Visita a museos','natural_dye_production':'Elaboración de tintes naturales','natural_pool_jumping':'Saltos a pozas naturales',
 'orchid_museum_visit':'Visita a museo de orquídeas','paper_balloon_workshop':'Taller de globos de papel','paragliding':'Parapente','pottery_making_workshop':'Taller de alfarería',
 'rafting':'Descenso de ríos (rafting)','rappelling':'Rápel','river_boat_navigation':'Navegación fluvial','sandboarding':'Deslizamiento en dunas','scuba_diving':'Buceo con equipo autónomo','snorkeling':'Esnórquel',
 'son_jarocho_festival_attendance':'Asistencia a festival de son jarocho','spiritual_cleansing_ritual':'Ritual de limpia espiritual','sport_fishing':'Pesca deportiva','swimming':'Natación','temazcal':'Temazcal',
 'traditional_cooking_workshop':'Taller de cocina tradicional','traditional_medicine_experience':'Experiencia de medicina tradicional','turtle_hatchling_release':'Liberación de crías de tortuga',
 'vanilla_extract_workshop':'Taller de extracto de vainilla','vanilla_planting':'Cultivo de vainilla','waterfall_visit':'Visita a cascada','wildlife_field_research_expedition':'Expedición de investigación de fauna',
 'wildlife_observation':'Observación de fauna','xantolo_festival_attendance':'Asistencia al Xantolo','ziplining':'Tirolesa'
};
const activityEnOverrides = {'4x4_mountain_transfer':'4×4 mountain transfer','atv':'ATV riding','hookah_diving':'Surface-supplied diving','scuba_diving':'Scuba diving','archaeological_visit':'Archaeological sites','boat_excursion':'Boat excursion','coffee_cupping':'Coffee cupping','son_jarocho_festival_attendance':'Son Jarocho festival','xantolo_festival_attendance':'Xantolo festival'};
function humanActivity(a){
 const k=a.id||'';
 if(language()==='es')return activityEs[k]||k.replace(/_/g,' ').replace(/\b\p{L}/gu,c=>c.toUpperCase());
 return activityEnOverrides[k]||k.replaceAll('_',' ').replace(/\b[a-z]/g,c=>c.toUpperCase());
}
const extras={
 es:{home:'Veracruz',region:'Región turística',allRegions:'Todas las regiones',backNav:'Atrás',forwardNav:'Adelante',guide:'Guía de experiencia',viewGuide:'Leer guía',area:'Municipio',sourcePassage:'Fragmento original de fuente (español)',sourceLinks:'Consulta las fuentes',photoPending:'Fotografía verificada pendiente',photoCredit:'Fotografía',tips:'Antes de ir',travelTip:'Confirma el punto de encuentro, los horarios, el acceso y las condiciones con el prestador antes de viajar.',dataWarning:'Punto municipal de referencia. Las actividades pueden encontrarse en otra localidad dentro del municipio.',emptyStory:'La fuente confirma la actividad, pero todavía no tenemos una descripción original recuperada para esta ficha.',broader:'Explora otras actividades en el municipio',about:'Ficha basada en registros documentados; no se han verificado tarifas ni horarios.',regionSource:'Fuente de regiones turísticas',allPlaces:'Explorar municipios'},
 en:{home:'Veracruz',region:'Tourism region',allRegions:'All regions',backNav:'Back',forwardNav:'Forward',guide:'Experience guide',viewGuide:'Read guide',area:'Municipality',sourcePassage:'Original source wording (Spanish)',sourceLinks:'Check the original sources',photoPending:'Verified photograph pending',photoCredit:'Photo',tips:'Before you go',travelTip:'Confirm the meeting point, opening hours, access and conditions with the provider before visiting.',dataWarning:'Municipality reference marker. Attractions may be located elsewhere within the municipality.',emptyStory:'The activity is documented, but the original description has not yet been recovered for this entry.',broader:'Explore other activities in this municipality',about:'Based on documented records; pricing and opening hours have not been verified.',regionSource:'Tourism-region source',allPlaces:'Explore municipalities'},
 ja:{home:'ベラクルス',region:'観光地域',allRegions:'すべての地域',backNav:'戻る',forwardNav:'進む',guide:'体験ガイド',viewGuide:'ガイドを読む',area:'自治体',sourcePassage:'原典の文言（スペイン語）',sourceLinks:'情報源を確認',photoPending:'確認済み写真は準備中',photoCredit:'写真',tips:'訪問前に',travelTip:'集合場所、営業時間、アクセス条件を事業者に確認してください。',dataWarning:'自治体の代表点です。観光施設の正確な位置とは限りません。',emptyStory:'活動の資料はありますが、原文説明はまだ確認できていません。',broader:'この自治体の他の体験を見る',about:'資料に基づく紹介です。料金・営業時間は未確認です。',regionSource:'観光地域の資料',allPlaces:'自治体を探索'}
};
function ex(){return extras[language()];}
function regionName(id){return state.regions?.names?.[id]?.[language()]||id||ex().allRegions;}
function snapshot(){return {filter:state.filter,region:state.region,activity:state.activity,selected:state.selected,guide:state.guide};}
function historyUpdate(){
 if(!$('vx-prev'))return;
 $('vx-prev').disabled=state.navIndex<=0;
 $('vx-next').disabled=state.navIndex>=state.navHistory.length-1;
 $('vx-prev').title=ex().backNav;$('vx-next').title=ex().forwardNav;
}
function navigate(changes){
 Object.assign(state,changes);
 state.navHistory=state.navHistory.slice(0,state.navIndex+1);
 state.navHistory.push(snapshot());state.navIndex=state.navHistory.length-1;
 render();
}
function restoreHistory(delta){
 const idx=state.navIndex+delta;
 if(idx<0||idx>=state.navHistory.length)return;
 state.navIndex=idx;Object.assign(state,state.navHistory[idx]);
 render();
}
function renderBreadcrumbs(){
 const c=$('vx-breadcrumbs');if(!c)return;c.replaceChildren();
 const crumb=(label,onClick,current=false)=>{const btn=element('button','vx-crumb'+(current?' vx-crumb-current':''),label);btn.type='button';btn.onclick=onClick;c.append(btn);};
 crumb(ex().home,()=>navigate({filter:'',region:'',activity:'',selected:null,guide:''}),!state.filter&&!state.region&&!state.selected);
 if(state.filter)crumb(copy().types[state.filter],()=>navigate({region:'',activity:'',selected:null,guide:''}),!state.region&&!state.selected);
 if(state.region)crumb(regionName(state.region),()=>navigate({selected:null,guide:''}),!state.selected&&!state.activity);
 if(state.activity&&!state.selected){const a=state.features.flatMap(f=>f.properties.activities).find(a=>a.id===state.activity);if(a)crumb(humanActivity(a),()=>navigate({activity:'',selected:null,guide:''}),true);}
 if(state.selected){const f=state.features.find(x=>String(x.id)===String(state.selected));if(f){crumb(f.properties.name,()=>navigate({guide:''}),!state.guide);if(state.guide){const a=f.properties.activities.find(x=>x.id===state.guide);if(a)crumb(humanActivity(a),()=>{},true);}}}
 historyUpdate();
}
const element=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=String(text);return n;};
function language(){const cand=[document.getElementById('language-select')?.value,document.querySelector('select[name="language"]')?.value,document.documentElement.lang];for(const c of cand){if(c && translations[String(c).toLowerCase().slice(0,2)])return String(c).toLowerCase().slice(0,2);}return 'es';}
function copy(){return translations[language()];}
function clean(s){return String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase().trim();}
root.innerHTML=`<div class="vx-top"><div><span class="vx-kicker">VERACRUZ · EXPLORER</span><h2 id="vx-title"></h2><p id="vx-subtitle"></p></div><div id="vx-top-count" class="vx-count-pill"></div></div>
 <div class="vx-explorer"><div class="vx-toolbar"><label class="vx-search-wrap"><svg viewBox="0 0 24 24" width="19" height="19" aria-hidden="true"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2"/><path d="m16.5 16.5 5 5" stroke="currentColor" stroke-width="2"/></svg><input id="vx-search" type="search" autocomplete="off" /></label>
 <select id="vx-category" aria-label="Experience theme"></select><select id="vx-region" aria-label="Tourism region"></select><select id="vx-activity" aria-label="Specific activity"></select><button id="vx-focus" type="button" class="vx-focus" hidden></button><label class="vx-toggle"><input type="checkbox" id="vx-show-all"/><span id="vx-toggle-label"></span></label></div>
 <div class="vx-body"><div id="vx-map" aria-label="Interactive Veracruz municipality map"><div id="vx-map-fallback" hidden></div><span id="vx-gesture" class="vx-gesture"></span></div><aside class="vx-side"><nav class="vx-nav" aria-label="Explorer navigation"><button id="vx-prev" class="vx-nav-arrow" type="button" disabled aria-label="Back">‹</button><button id="vx-next" class="vx-nav-arrow" type="button" disabled aria-label="Forward">›</button><div id="vx-breadcrumbs" class="vx-breadcrumbs"></div></nav><div id="vx-status" class="vx-status" aria-live="polite"></div><div id="vx-detail" class="vx-detail" hidden></div><div id="vx-list" class="vx-list"></div></aside></div>
 <div class="vx-foot"><div id="vx-legend" class="vx-legend"></div><p id="vx-caveat"></p></div></div>`;
const $ = id=>root.querySelector('#'+id);
const mapObject=typeof maplibregl==='undefined'?null:new maplibregl.Map({
   container:'vx-map',center:[-96.4,19.5],zoom:6.05,minZoom:5,
   cooperativeGestures:true, // Mobile: two fingers; desktop: Ctrl+wheel or touchpad pinch.
   scrollZoom:true,
   touchZoomRotate:true,
   touchPitch:false,
   style:'https://tiles.openfreemap.org/styles/positron'
 });
if(mapObject){
  mapObject.addControl(new maplibregl.NavigationControl({showCompass:false}),'top-right');
  // Two-finger pinch remains available, but accidental map rotation is disabled.
  mapObject.touchZoomRotate.enable();
  mapObject.touchZoomRotate.disableRotation();
}
const state={features:[],filter:'',activity:'',query:'',all:false,selected:null,guide:'',region:'',regions:null,guideNotes:{},photos:{},navHistory:[],navIndex:-1,ready:false};
const nameOf=a=>language()==='es'?a.name_es:(a.name_en||a.name_es);
const orderedTypes=Object.keys(palette);
function eligible(f){const p=f.properties;return (state.all||p.activity_count>0) && (!state.region||state.regions?.membership?.[p.municipality_id]===state.region) && (!state.query||clean([p.name,...p.activities.flatMap(a=>[a.name_es,a.name_en,a.id]),...p.types.map(k=>copy().types[k]||k)].join(' ')).includes(state.query));}
function visible(){return state.features.filter(eligible);}
function highlighting(){return !!(state.filter||state.activity);}
function matches(f){const p=f.properties;return (!state.filter||p.types.includes(state.filter)) && (!state.activity||p.activities.some(a=>a.id===state.activity));}
function matchingFeatures(){return visible().filter(matches);}
function activityLabel(a){return humanActivity(a);}
function labelType(k){return copy().types[k]||k;}
function dot(t){const d=element('i','vx-dot');d.style.background=palette[t]||palette.other;return d;}
function badges(p,holder){if(!p.types.length){holder.append(element('span','vx-empty-chip','—'));return;}
  for(const t of p.types){const tag=element('span','vx-tag');tag.append(dot(t),document.createTextNode(labelType(t)));holder.append(tag);}}
function validUrl(u){try{return new URL(u).protocol==='https:';}catch{return false;}}
function sourceLinks(urls,holder){for(const [i,url] of [...new Set(urls||[])].filter(validUrl).slice(0,4).entries()){
 const a=element('a','vx-source-link',`${copy().sources} ${i+1} ↗`);a.href=url;a.target='_blank';a.rel='noopener noreferrer';holder.append(a);
}}
function openDetail(feature){
 navigate({selected:String(feature.id),guide:''});
 if(mapObject)mapObject.flyTo({center:feature.geometry.coordinates,zoom:Math.max(mapObject.getZoom(),8.7),essential:true});
 $('vx-side')?.scrollTo({top:0,behavior:'smooth'});
}
function renderDetail(){
 const box=$('vx-detail');box.replaceChildren();
 const f=state.features.find(x=>String(x.id)===String(state.selected));
 if(!f){box.hidden=true;return;} box.hidden=false;
 const p=f.properties,t=copy(),e=ex();
 const top=element('div','vx-detail-top');top.append(element('h3','',p.name));
 const close=element('button','vx-close','×');close.type='button';close.setAttribute('aria-label',t.back);
 close.onclick=()=>navigate({selected:null,guide:''});top.append(close);box.append(top);
 const region=state.regions?.membership?.[p.municipality_id];if(region){const b=element('button','vx-region-link',regionName(region)+' ↗');b.type='button';b.onclick=()=>navigate({region,selected:null,guide:''});box.append(b);}
 const chips=element('div','vx-tags');badges(p,chips);box.append(chips);
 const note=element('p','vx-note',e.dataWarning);box.append(note);
 if(state.guide){
   const a=p.activities.find(x=>x.id===state.guide);
   if(a){
     const entry=state.guideNotes?.[p.municipality_id+'::'+a.id]||{};
     const header=element('div','vx-guide-title');header.append(dot(a.type),element('h4','',humanActivity(a)));box.append(header);
     const hero=state.photos?.[p.municipality_id+'::'+a.id];
     if(hero?.src&&/^https:\/\//.test(hero.src)&&hero?.credit&&hero?.source){
       const fig=element('figure','vx-figure'),img=element('img','');img.src=hero.src;img.alt=hero.alt||humanActivity(a);
       img.loading='lazy';img.referrerPolicy='no-referrer';fig.append(img);const cap=element('figcaption','');const link=element('a','',hero.credit);link.href=hero.source;link.rel='noopener noreferrer';link.target='_blank';cap.append(link);fig.append(cap);box.append(fig);
     }
     const intro=element('p','vx-guide-intro',language()==='es'?`En ${p.name}, las fuentes consultadas registran ${humanActivity(a).toLocaleLowerCase('es')}. Consulta los detalles documentados y confirma el lugar exacto antes de organizar tu visita.`:
       language()==='ja'?`${p.name}で${humanActivity(a)}が資料に記録されています。訪問前に詳細な場所を確認してください。`:
       `${humanActivity(a)} is documented in ${p.name}. Check the evidence below and confirm the exact location before planning your visit.`);
     box.append(intro);
     if(entry.source_phrases?.length){box.append(element('h4','',e.sourcePassage));
       for(const phrase of entry.source_phrases)box.append(element('blockquote','vx-source-excerpt',phrase.es));
     }else box.append(element('p','vx-note',e.emptyStory));
     box.append(element('h4','',e.tips),element('p','vx-guide-intro',e.travelTip));
     const links=element('div','vx-links');sourceLinks(a.source_urls,links);box.append(element('h4','',e.sourceLinks),links);
     box.append(element('p','vx-note',e.about));
     const back=element('button','vx-secondary',e.broader);back.type='button';back.onclick=()=>navigate({guide:''});box.append(back);
   }
   return;
 }
 if(p.activities.length){
  box.append(element('h4','',`${t.activity} · ${p.activities.length}`));
  const list=element('ul','vx-activity-list');
  for(const a of p.activities){
   const li=element('li','vx-activity');const b=element('button','vx-activity-open');b.type='button';
   b.append(dot(a.type),document.createTextNode(humanActivity(a)),element('span','vx-more-arrow','›'));
   b.onclick=()=>navigate({selected:String(f.id),guide:a.id});li.append(b);
   const entry=state.guideNotes?.[p.municipality_id+'::'+a.id];
   li.append(element('p','vx-proof',(entry?.source_phrases?.length||a.original_text_support_count>0)?t.original:t.summary));
   const links=element('div','vx-links');sourceLinks(a.source_urls,links);li.append(links);list.append(li);
  }box.append(list);
 }else box.append(element('p','vx-note',t.absence));
}
// Stable, geographic MapLibre markers. These are anchored by MapLibre itself,
// not projected/positioned by our page and do not require style.load, sprites,
// addSource, or the remote basemap glyph pipeline.
// This replaces the failing native style-layer path with a verifiable baseline.
const markerCache=new Map();
function buildMarker(f){
  const p=f.properties;
  // A DIV avoids generic button styles from the host website.  Essential
  // appearance is inline because the last site mixed cached JS and CSS.
  const pin=element('div','vx-geo-marker');
  pin.setAttribute('role','button');
  pin.tabIndex=0;
  pin.setAttribute('aria-label',p.name);
  pin.title=p.name;
  Object.assign(pin.style,{
    width:'25px',height:'25px',display:'flex',alignItems:'center',
    justifyContent:'center',border:'0',padding:'0',borderRadius:'50%',
    background:'transparent',cursor:'pointer',overflow:'visible',
    boxSizing:'border-box'
  });
  const ring=element('span','vx-geo-ring');
  const keys=[...new Set(p.types||[])].filter(k=>Object.hasOwn(palette,k));
  const colors=keys.map(k=>palette[k]);
  if(colors.length){
    const step=360/colors.length;
    ring.style.background='conic-gradient('+colors.map((color,i)=>
      color+' '+(i*step)+'deg '+((i+1)*step)+'deg').join(', ')+')';
  }else ring.style.background='#9ba6a4';
  Object.assign(ring.style,{
    display:'flex',width:'100%',height:'100%',borderRadius:'50%',
    padding:'3px',alignItems:'center',justifyContent:'center',
    border:'2px solid #fff',boxShadow:'0 2px 7px #09261c88',
    boxSizing:'border-box'
  });
  const core=element('span','vx-geo-core');
  Object.assign(core.style,{
    display:'block',width:'100%',height:'100%',borderRadius:'50%',
    background:'#244b42',border:'1px solid #fff',boxSizing:'border-box'
  });
  ring.append(core);pin.append(ring);
  function selectPin(e){e.preventDefault();e.stopPropagation();openDetail(f);}
  pin.addEventListener('click',selectPin);
  pin.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){selectPin(e);}});
  const marker=new maplibregl.Marker({element:pin,anchor:'center',subpixelPositioning:true})
    .setLngLat(f.geometry.coordinates).addTo(mapObject);
  markerCache.set(String(f.id),{marker,button:pin,ring});
}
function refreshMapSource(){
  if(!mapObject || !state.features.length)return;
  try{
    // 212 locality reference markers at most, 61 shown initially. Reuse existing
    // MapLibre objects across filters; do not recalculate screen coordinates.
    for(const f of state.features){
      if(!markerCache.has(String(f.id)))buildMarker(f);
      const entry=markerCache.get(String(f.id));
      const show=eligible(f);
      entry.button.style.display=show?'':'none';
      entry.button.classList.toggle('vx-geo-marker--muted',show&&highlighting()&&!matches(f));
      entry.button.classList.toggle('vx-geo-marker--match',show&&highlighting()&&matches(f));
      entry.button.classList.toggle('vx-geo-marker--selected',String(state.selected)===String(f.id));
      entry.button.style.opacity=show&&highlighting()&&!matches(f)?'.22':'1';
      entry.ring.style.boxShadow=String(state.selected)===String(f.id)?'0 0 0 4px #ffc24b,0 2px 7px #09261c88':
         show&&highlighting()&&matches(f)?'0 0 0 3px #f4b84d,0 2px 7px #09261c88':'0 2px 7px #09261c88';
    }
    updateMarkerZoom();
  }catch(error){
    console.error('[Veracruz map] Marker creation failed:',error);
    const status=document.getElementById('vx-status');
    if(status)status.textContent='Marker error: '+error.message;
  }
}
function updateMarkerZoom(){
  if(!mapObject)return;
  const big=mapObject.getZoom()>=8.1;
  for(const entry of markerCache.values()){
    entry.button.classList.toggle('vx-geo-marker--close',big);
    entry.button.style.width=big?'31px':'25px';
    entry.button.style.height=big?'31px':'25px';
  }
}
if(mapObject){mapObject.on('zoom',updateMarkerZoom);mapObject.on('moveend',()=>{if(state.features.length)renderResults();});}
// Sidebar follows the geographic viewport instead of showing an unexplained
// alphabetical table for the entire state. Nothing is removed from the data.
let showOutsidePlaces=false;
const panelWords={
 en:{near:'In the current map view',away:'Elsewhere in Veracruz',activities:'documented activities',oneActivity:'documented activity',show:'Show other places',hide:'Hide other places',none:'No documented places in this view. Pan or zoom out.',select:'Select to view activities and sources'},
 es:{near:'En el mapa actual',away:'En otras zonas de Veracruz',activities:'actividades documentadas',oneActivity:'actividad documentada',show:'Ver otros lugares',hide:'Ocultar otros lugares',none:'No hay lugares documentados en esta vista. Mueve o aleja el mapa.',select:'Selecciona para ver actividades y fuentes'},
 ja:{near:'現在の地図内',away:'ベラクルス州のその他の地域',activities:'資料にある体験',oneActivity:'資料にある体験',show:'ほかの場所を表示',hide:'ほかの場所を閉じる',none:'この範囲には対象地点がありません。地図を動かすか縮小してください。',select:'選択して体験と出典を見る'}
};
function renderResults(){
 const list=$('vx-list');if(!list)return;
 list.replaceChildren();
 // Details replace the list, rather than piling a destination article on top
 // of sixty unexplained rows.
 list.hidden=!!state.selected;
 if(state.selected)return;
 const tr=panelWords[language()]||panelWords.en;
 const shown=visible();
 const ordered=highlighting()?[...shown.filter(matches),...shown.filter(f=>!matches(f))]:shown;
 const bounds=mapObject?.getBounds?.();
 const inMap=f=>!bounds||bounds.contains(f.geometry.coordinates);
 const near=ordered.filter(inMap),outside=ordered.filter(f=>!inMap(f));
 const center=mapObject?.getCenter?.();
 const distance=f=>center?Math.hypot(f.geometry.coordinates[0]-center.lng,f.geometry.coordinates[1]-center.lat):0;
 near.sort((a,b)=>(highlighting()?Number(matches(b))-Number(matches(a)):0)||distance(a)-distance(b));
 outside.sort((a,b)=>(highlighting()?Number(matches(b))-Number(matches(a)):0)||distance(a)-distance(b));
 function row(f){
  const p=f.properties;const hit=matches(f);
  const btn=element('button','vx-result'+(highlighting()?(hit?' vx-is-match':' vx-is-muted'):''));
  btn.type='button';btn.title=tr.select;
  const top=element('div','vx-result-top');top.append(element('strong','',p.name));
  const badge=element('span','vx-result-count',p.activity_count+' '+(p.activity_count===1?tr.oneActivity:tr.activities));
  top.append(badge);btn.append(top);
  if(p.types.length){
   const typeLine=element('div','vx-map-type-line');
   for(const type of p.types){const group=element('span','vx-type-word');group.append(dot(type),document.createTextNode(labelType(type)));typeLine.append(group);}
   btn.append(typeLine);
  }
  if(p.activities.length){
   const desc=element('div','vx-map-preview',p.activities.slice(0,3).map(activityLabel).join(' · ')+(p.activities.length>3?' · …':''));
   btn.append(desc);
  }else btn.append(element('div','vx-map-preview',copy().absence));
  btn.onclick=()=>openDetail(f);list.append(btn);
 }
 function heading(title,n){const h=element('div','vx-map-list-heading',title+' · '+n);list.append(h);}
 heading(tr.near,near.length);
 if(!near.length)list.append(element('p','vx-map-list-empty',tr.none));
 near.slice(0,60).forEach(row);
 if(outside.length){
  const toggle=element('button','vx-map-outside-toggle',(showOutsidePlaces?tr.hide:tr.show)+' ('+outside.length+')');
  toggle.type='button';toggle.onclick=()=>{showOutsidePlaces=!showOutsidePlaces;renderResults();};
  list.append(toggle);
  if(showOutsidePlaces){heading(tr.away,outside.length);outside.forEach(row);}
 }
}
function render(){
 const t=copy();$('vx-title').textContent=t.title;$('vx-subtitle').textContent=t.subtitle;
 $('vx-search').placeholder=t.search;$('vx-toggle-label').textContent=state.all?t.all:t.documented;
 $('vx-gesture').textContent=t.gesture;
 $('vx-caveat').textContent=`${t.approximate} ${t.counts} · ${ex().regionSource}: veracruz.mx`;
 const select=$('vx-category'),saved=state.filter;
 select.replaceChildren(new Option(t.category,''));
 for(const k of orderedTypes)if(state.features.some(f=>f.properties.types.includes(k)))select.append(new Option(t.types[k],k));
 select.value=saved;
 const regionSelect=$('vx-region');regionSelect.replaceChildren(new Option(ex().allRegions,''));
 for(const id of Object.keys(state.regions?.names||{}))regionSelect.append(new Option(regionName(id),id));
 regionSelect.value=state.region;
 const activitySelect=$('vx-activity'),savedActivity=state.activity;
 activitySelect.replaceChildren(new Option(t.specific,''));
 const seen=new Map();
 for(const f of state.features)for(const a of f.properties.activities)if(!seen.has(a.id))seen.set(a.id,a);
 const options=[...seen.values()].sort((a,b)=>activityLabel(a).localeCompare(activityLabel(b),language()));
 for(const a of options)activitySelect.append(new Option(activityLabel(a),a.id));
 activitySelect.value=savedActivity;
 const shown=visible(),match=matchingFeatures();
 $('vx-status').textContent=highlighting()?t.matching(match.length,shown.length):(shown.length?t.visible(shown.length,state.features.length):t.noResults);
 $('vx-top-count').textContent=state.features.length?`${state.features.length} municipios · ${state.features.reduce((n,f)=>n+f.properties.activity_count,0)} actividades vinculadas`:'';
 $('vx-focus').hidden=!highlighting()||match.length===0;
 $('vx-focus').textContent=t.focus;
 renderResults();
 const leg=$('vx-legend');leg.replaceChildren();
 for(const k of orderedTypes){if(!state.features.some(f=>f.properties.types.includes(k)))continue;
  const tag=element('button','vx-legend-item'+(state.filter===k?' vx-legend-active':''));
  tag.type='button';tag.setAttribute('aria-pressed',String(state.filter===k));tag.append(dot(k),document.createTextNode(t.types[k]));
  tag.onclick=()=>{navigate({filter:state.filter===k?'':k,selected:null,guide:''});};leg.append(tag);
 }
 renderBreadcrumbs();renderDetail();
 refreshMapSource();
}
$('vx-search').addEventListener('input',e=>{state.query=clean(e.target.value);render();});
$('vx-category').addEventListener('change',e=>{navigate({filter:e.target.value,selected:null,guide:''});});
$('vx-activity').addEventListener('change',e=>{navigate({activity:e.target.value,selected:null,guide:''});});
$('vx-focus').addEventListener('click',()=>{
 if(!mapObject)return;const found=matchingFeatures();if(!found.length)return;
 if(found.length===1){mapObject.flyTo({center:found[0].geometry.coordinates,zoom:9.4,essential:true});return;}
 const bounds=new maplibregl.LngLatBounds();for(const f of found)bounds.extend(f.geometry.coordinates);
 mapObject.fitBounds(bounds,{padding:55,maxZoom:9.4,duration:650});
});
$('vx-region').addEventListener('change',e=>{
 navigate({region:e.target.value,selected:null,guide:''});
 if(mapObject&&e.target.value){
  const pts=state.features.filter(f=>state.regions?.membership?.[f.properties.municipality_id]===e.target.value);
  if(pts.length){const b=new maplibregl.LngLatBounds();pts.forEach(f=>b.extend(f.geometry.coordinates));
   mapObject.fitBounds(b,{padding:60,maxZoom:8.5,duration:600});}
 }
});
$('vx-prev').addEventListener('click',()=>restoreHistory(-1));
$('vx-next').addEventListener('click',()=>restoreHistory(1));
$('vx-show-all').addEventListener('change',e=>{state.all=e.target.checked;render();});
// Site translation may change through its own custom code; listen at document level.
document.addEventListener('change',e=>{if(e.target!==$('vx-category')&&e.target!==$('vx-region')&&e.target!==$('vx-activity')&&e.target!==$('vx-show-all')&&e.target!==$('vx-search'))render();});
new MutationObserver(()=>render()).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
if(mapObject){
 // Markers now attach directly to map projection, regardless of style-load timing.
 mapObject.on('error',e=>console.warn('MapLibre basemap:',e.error?.message));
 if(typeof ResizeObserver!=='undefined')new ResizeObserver(()=>mapObject.resize()).observe($('vx-map'));
}
Promise.all([
 fetch('data/map_points.geojson',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error(`GeoJSON HTTP ${r.status}`);return r.json();}),
 fetch('data/map_regions.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error(`Regions HTTP ${r.status}`);return r.json();}),
 fetch('data/map_guide_notes.json',{cache:'no-store'}).then(r=>r.ok?r.json():{}).catch(()=>({})),
 fetch('data/map_photos.json',{cache:'no-store'}).then(r=>r.ok?r.json():{}).catch(()=>({}))
]).then(([fc,regions,notes,photos])=>{
 if(fc.type!=='FeatureCollection'||!Array.isArray(fc.features))throw Error('Invalid GeoJSON');
 state.features=fc.features.filter(f=>f.geometry?.type==='Point'&&f.geometry.coordinates.length===2&&
   f.geometry.coordinates.every(Number.isFinite)&&f.geometry.coordinates[0]>-100&&f.geometry.coordinates[0]<-93&&
   f.geometry.coordinates[1]>17&&f.geometry.coordinates[1]<23&&Array.isArray(f.properties?.activities)&&Array.isArray(f.properties?.types));
 state.regions=regions;state.guideNotes=notes;state.photos=photos;
 state.navHistory=[snapshot()];state.navIndex=0;
 render();if(mapObject&&state.features.length){const b=new maplibregl.LngLatBounds();state.features.forEach(f=>b.extend(f.geometry.coordinates));mapObject.fitBounds(b,{padding:42,maxZoom:6.6,duration:0});}
}).catch(error=>{$('vx-status').textContent='Map catalog could not be loaded. '+error.message;console.error('Veracruz map:',error);});
render();
})();
