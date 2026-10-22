/* Source-backed activity explorer. 78 individual activity types, not legacy clusters. */
(() => {
  'use strict';
  const host = document.getElementById('vx-activities');
  if (!host || host.dataset.ready) return;
  host.dataset.ready = '1';
  const L = {
    es: {tag:'EXPERIENCIAS DOCUMENTADAS',title:'Elige qué te gustaría descubrir',intro:'Actividades concretas, lugares documentados y enlaces a las fuentes. Busca una experiencia y después agrégala a tu ruta.',search:'Buscar actividades o municipios…',filter:'Todas',all:'Todas',show:'Mostrar más actividades',less:'Mostrar menos',locations:'Municipios documentados',more:'Ver lugares y fuentes',map:'Ver en el mapa',add:'Añadir a ruta',added:'Añadido a la ruta: ',exists:'Ya está en tu ruta o el planificador sigue cargando. Intenta otra vez.',source:'Consultar fuente',photo:'Fotografía documental:',illustration:'Ilustración editorial, no fotografía del lugar',none:'No se encontraron actividades.',count:'tipos de experiencia',links:'vínculos documentados',covered:'municipio(s) documentado(s)',warning:'Documentado no significa abierto ni reservable: comprueba fechas, acceso, precios y operadores antes de viajar.',wait:'El mapa sigue cargando; vuelve a intentar en un momento.',learn:'Explora el mapa para ver la ubicación municipal aproximada.'},
    en: {tag:'DOCUMENTED EXPERIENCES',title:'Discover activities, not just destinations',intro:'Specific activities, documented municipalities and source links. Explore an experience, then add places to your itinerary.',search:'Search activities or municipalities…',filter:'All',all:'All',show:'Show more activities',less:'Show fewer',locations:'Documented municipalities',more:'Places and sources',map:'See on map',add:'Add to route',added:'Added to itinerary: ',exists:'Already in your itinerary or the planner is still loading. Try again.',source:'Source',photo:'Documentary photograph:',illustration:'Editorial illustration, not a destination photograph',none:'No matching activities.',count:'specific activity types',links:'documented links',covered:'documented municipality/municipalities',warning:'Documented does not mean currently open or bookable. Verify dates, access, prices and providers before visiting.',wait:'The map is still loading. Try again in a moment.',learn:'Map points refer to approximate municipality locations.'},
    ja: {tag:'資料に基づく体験',title:'アクティビティから旅先を探す',intro:'具体的な体験、資料で確認された市町村、出典へのリンクから旅を考えましょう。',search:'体験・市町村を検索…',filter:'すべて',all:'すべて',show:'もっと見る',less:'少なく表示',locations:'資料で確認された市町村',more:'場所・出典',map:'地図で見る',add:'ルートに追加',added:'ルートに追加しました: ',exists:'すでに追加済みか、読み込み中です。もう一度お試しください。',source:'出典',photo:'資料写真:',illustration:'イラスト（現地写真ではありません）',none:'該当する体験はありません。',count:'種類',links:'資料に基づく記録',covered:'資料がある市町村',warning:'資料への掲載は現在の営業・予約を保証しません。訪問前にご確認ください。',wait:'地図の読み込み中です。',learn:'地図の市町村位置は概略です。'}
  };
  const lang = () => {const v=document.querySelector('#language-select')?.value || 'es';return L[v] ? v:'en';};
  const norm = s => String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase().trim();
  const el = (tag,cls,text) => {const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
  const safeURL = s => {try{const u=new URL(String(s));return u.protocol==='https:'?u.href:null;}catch{return null;}};
  let data,filter='',query='',shown=12;
  const intro=el('div','vxa-intro');
  const heading=el('div','vxa-heading');
  const tag=el('span','vxa-kicker'),title=el('h2'),subtitle=el('p');
  heading.append(tag,title,subtitle);intro.append(heading);
  const controls=el('div','vxa-controls');
  const search=el('input','vxa-search');search.type='search';search.autocomplete='off';
  search.setAttribute('aria-label','Search activities or towns');
  const familyBar=el('div','vxa-families');familyBar.setAttribute('role','group');familyBar.setAttribute('aria-label','Activity categories');
  controls.append(search,familyBar);intro.append(controls);
  const counter=el('p','vxa-count');
  const grid=el('div','vxa-grid');grid.id='vxa-grid';
  const more=el('button','vxa-more');more.type='button';
  const caveat=el('p','vxa-caveat');
  const live=el('p','vxa-live');live.setAttribute('role','status');live.setAttribute('aria-live','polite');
  host.append(intro,counter,grid,more,caveat,live);

  const name = a => lang()==='es'?a.label_es:(a.label_en||a.label_es);
  const description = a => lang()==='es'?a.description_es:(a.description_en||a.description_es);
  const tr = () => L[lang()];

  function selectOnMap(feature){
    const select=document.getElementById('vx-activity');
    if(select && [...select.options].some(o=>o.value===feature)){
      select.value=feature;select.dispatchEvent(new Event('change',{bubbles:true}));
      document.getElementById('veracruz-map-section')?.scrollIntoView({block:'start',behavior:'smooth'});
      return true;
    }
    live.textContent=tr().wait;return false;
  }

  function municipalityButton(m){
    const b=el('button','vxa-municipality');b.type='button';
    const text=el('span','',m.name),addLabel=el('span','vxa-plus','+');
    b.append(text,addLabel);b.title=tr().add+': '+m.name;
    b.addEventListener('click',()=>{
      const router=window.VeracruzItineraryV2;
      const ok=router?.addStopById?.('municipality:'+m.municipality_id);
      if(ok){live.textContent=tr().added+m.name;document.getElementById('vxw-itinerary')?.scrollIntoView({block:'start',behavior:'smooth'});}
      else{live.textContent=tr().exists;}
    });return b;
  }

  function buildCard(a){
    const card=el('article','vxa-card');card.dataset.feature=a.feature_id;
    const imgWrap=el('div','vxa-photo');
    const img=el('img');img.loading='lazy';img.decoding='async';
    img.src=a.media_url;img.alt=tr().illustration;
    imgWrap.append(img);
    if(a.photo){
      const u=safeURL(a.photo.url);
      if(u){img.src=u;img.alt=a.photo.alt;img.addEventListener('error',()=>{img.src=a.media_url;img.alt=tr().illustration;figlabel.textContent=tr().illustration;const attribution=imgWrap.querySelector('.vxa-photo-source');if(attribution)attribution.hidden=true;});}
    }
    const figlabel=el('small','vxa-image-credit',a.photo ? tr().photo+' '+a.photo.caption : tr().illustration);
    imgWrap.append(figlabel);
    if(a.photo?.source){const source=safeURL(a.photo.source);if(source){const link=el('a','vxa-photo-source','© ↗');link.href=source;link.target='_blank';link.rel='noopener noreferrer';link.title=a.photo.caption;imgWrap.append(link);}}
    card.append(imgWrap);
    const body=el('div','vxa-card-body');
    const small=el('p','vxa-meta',(data.families[a.family]?.[lang()==='es'?0:lang()==='ja'?2:1]||a.family)+' · '+a.municipality_count+' '+tr().covered);
    const h=el('h3','',name(a));
    const text=el('p','vxa-description',description(a));
    body.append(small,h,text);
    const actions=el('div','vxa-actions');
    const mapButton=el('button','vxa-map',tr().map);mapButton.type='button';mapButton.addEventListener('click',()=>selectOnMap(a.feature_id));
    actions.append(mapButton);body.append(actions);
    const details=el('details','vxa-details');
    const summary=el('summary','',tr().more);details.append(summary);
    const list=el('div','vxa-place-list');
    for(const municipality of a.municipalities){
      const item=el('div','vxa-place');item.append(municipalityButton(municipality));
      const links=[...new Set(municipality.source_urls)].map(safeURL).filter(Boolean);
      if(links.length){const link=el('a','vxa-source',tr().source+' ↗');link.href=links[0];link.target='_blank';link.rel='noopener noreferrer';item.append(link);}
      list.append(item);
    }
    details.append(list);body.append(details);card.append(body);
    return card;
  }

  function matches(a){if(filter && a.family!==filter)return false;
    if(!query)return true;
    return norm([a.label_es,a.label_en,a.family,...a.municipalities.map(x=>x.name)].join(' ')).includes(query);
  }
  function render(){if(!data)return;
    const t=tr();tag.textContent=t.tag;title.textContent=t.title;subtitle.textContent=t.intro;
    search.placeholder=t.search;caveat.textContent=t.warning;const nav=document.getElementById('nav-activities');if(nav)nav.textContent=lang()==='es'?'Actividades':lang()==='ja'?'体験':'Activities';
    familyBar.replaceChildren();
    const families=[['',t.all],...Object.entries(data.families).map(([k,n])=>[k,n[lang()==='es'?0:lang()==='ja'?2:1]])];
    for(const [key,label] of families){const b=el('button','vxa-chip'+(filter===key?' is-active':''),label);b.type='button';b.setAttribute('aria-pressed',String(filter===key));b.addEventListener('click',()=>{filter=key;shown=12;render();});familyBar.append(b);}
    const all=data.cards.filter(matches);
    counter.textContent=`${all.length} ${t.count} · ${data.counts.links} ${t.links}`;
    grid.replaceChildren();
    for(const card of all.slice(0,shown))grid.append(buildCard(card));
    if(!all.length)grid.append(el('p','vxa-empty',t.none));
    more.hidden=all.length<=12;more.textContent=shown>=all.length?t.less:t.show;
    more.onclick=()=>{shown=shown>=all.length?12:Math.min(shown+12,all.length);render();};
  }
  search.addEventListener('input',()=>{query=norm(search.value);shown=12;render();});
  document.querySelector('#language-select')?.addEventListener('change',render);
  fetch('data/activity_cards.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json();}).then(d=>{
    if(d.kind!=='documented_activity_types_not_clusters'||d.cards?.length!==78||d.counts?.links!==216)throw Error('Current evidence catalog mismatch');
    data=d;render();
  }).catch(e=>{grid.replaceChildren(el('p','vxa-error','Activity catalog unavailable: '+e.message));console.error('[Veracruz activity cards]',e);});
})();
