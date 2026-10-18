/* Veracruz – named-attraction overlay, deliberately separate from municipal evidence.
   Uses the researched attraction GeoJSON and the existing MapLibre map instance.
   Source-referenced sites are NOT automatically confirmed visitor entrances. */
(() => {
  'use strict';
  const root = document.getElementById('veracruz-map-section');
  const map = window.__vx_attraction_map;
  const lib = window.maplibregl;
  if (!root || !map || !lib) {
    console.error('[Veracruz attractions] Existing map is unavailable. Check script load order.');
    return;
  }
  const search = root.querySelector('#vx-search');
  const side = root.querySelector('.vx-side');
  const status = root.querySelector('#vx-status');
  if (!search || !side || !status) {
    console.error('[Veracruz attractions] Explorer controls could not be found.');
    return;
  }
  const lang = () => (document.documentElement.lang || 'en').toLowerCase().slice(0, 2);
  const normalize = value => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
  const words = {
    en: {heading:'Mapped attractions',matches:'Attraction results',view:'Show all mapped attractions',close:'Hide attraction list',source:'View original geographic source',site:'Attraction or site',area:'Geographic area',note:'The marker identifies the mapped place, not a verified visitor entrance or road stop.',restricted:'Location reference only. Public access has not been confirmed.',empty:'No attraction matches your search.'},
    es: {heading:'Atractivos ubicados',matches:'Resultados de atractivos',view:'Ver todos los atractivos ubicados',close:'Ocultar lista de atractivos',source:'Consultar fuente geográfica',site:'Atractivo o sitio',area:'Área geográfica',note:'El marcador ubica el lugar, no una entrada de visitantes ni un punto de llegada verificado.',restricted:'Referencia geográfica. No se ha confirmado acceso público.',empty:'No hay atractivos que coincidan con la búsqueda.'},
    ja: {heading:'所在地が確認された観光地',matches:'観光地の検索結果',view:'所在地一覧を表示',close:'一覧を閉じる',source:'出典を開く',site:'観光スポット',area:'広域の位置',note:'地図上の地点は入口や車での到着地点を保証するものではありません。',restricted:'所在地のみ。一般公開は未確認です。',empty:'該当する観光地はありません。'}
  };
  const text = () => words[lang()] || words.en;
  const attractionType = props => {
    const t = props.mapped_feature_type || '';
    if (/archaeological|site_reference/.test(t)) return {symbol:'🏛',color:'#8060b4',name:{en:'Archaeological site',es:'Zona arqueológica',ja:'遺跡'}};
    if (/waterfall/.test(t)) return {symbol:'💧',color:'#168cad',name:{en:'Waterfall',es:'Cascada',ja:'滝'}};
    if (/fort/.test(t)) return {symbol:'🏰',color:'#8060b4',name:{en:'Historic fort',es:'Fortaleza',ja:'要塞'}};
    if (/building|museum/.test(t)) return {symbol:'🏛',color:'#8060b4',name:{en:'Heritage site',es:'Patrimonio',ja:'文化遺産'}};
    if (/beach|island|waterbody/.test(t)) return {symbol:'🌊',color:'#168cad',name:{en:'Coast or water',es:'Agua y costa',ja:'海・水辺'}};
    return {symbol:'🌿',color:'#27856d',name:{en:'Nature or landscape',es:'Naturaleza y paisaje',ja:'自然'}};
  };
  const panel = document.createElement('section');
  panel.className = 'vxa-panel';
  panel.setAttribute('aria-label', 'Mapped attractions');
  panel.hidden = true;
  status.insertAdjacentElement('afterend', panel);
  const toggle = document.createElement('button');
  toggle.type = 'button';
  toggle.className = 'vxa-toggle';
  status.insertAdjacentElement('afterend', toggle);
  let attractions = [];
  let markers = [];
  let expanded = false;
  let popup = null;
  let activeId = null;
  function renderPanel() {
    panel.replaceChildren();
    const q = normalize(search.value);
    const found = attractions.filter(f => normalize(f.properties.attraction_name_original).includes(q));
    const showPanel = Boolean(q) || expanded;
    panel.hidden = !showPanel;
    toggle.textContent = `${text().heading} · ${attractions.length}  ${expanded ? '▴' : '▾'}`;
    toggle.setAttribute('aria-expanded',String(expanded));
    if (!showPanel) return;
    const title = document.createElement('h4');
    title.textContent = q ? `${text().matches} · ${found.length}` : `${text().heading} · ${found.length}`;
    panel.append(title);
    if (!found.length) {
      const empty = document.createElement('p'); empty.className = 'vxa-empty'; empty.textContent=text().empty;panel.append(empty);return;
    }
    for (const f of found) {
      const p=f.properties,t=attractionType(p),b=document.createElement('button');
      b.type='button'; b.className='vxa-item';
      const symbol=document.createElement('span');symbol.className='vxa-type';symbol.textContent=t.symbol;
      const label=document.createElement('span');
      label.textContent=p.attraction_name_original;
      const meta=document.createElement('small');
      meta.textContent=t.name[lang()]||t.name.en;
      label.append(document.createElement('br'),meta);b.append(symbol,label);
      b.addEventListener('click',()=>focus(f));panel.append(b);
    }
  }
  function makeCard(f) {
    const p=f.properties,t=attractionType(p),card=document.createElement('div');
    card.className='vxa-card';
    const heading=document.createElement('h3'); heading.textContent=`${t.symbol} ${p.attraction_name_original}`;
    const type=document.createElement('p');type.className='vxa-card-type';type.textContent=t.name[lang()]||t.name.en;
    const note=document.createElement('p');
    note.textContent=p.mapping_status==='mapped_general_area_NOT_routing_stop'?text().restricted:text().note;
    card.append(heading,type,note);
    if (/^https:\/\//.test(p.source_url || '')) {
      const link=document.createElement('a');link.href=p.source_url;link.target='_blank';link.rel='noopener noreferrer';link.textContent=text().source+' ↗';card.append(link);
    }
    return card;
  }
  function focus(f) {
    const id=String(f.properties.place_id);
    activeId=id;
    const coords=f.geometry.coordinates;
    map.flyTo({center:coords,zoom:Math.max(map.getZoom(),10.2),essential:true});
    if (popup) popup.remove();
    popup=new lib.Popup({offset:22,maxWidth:'320px',closeButton:true,closeOnClick:false})
      .setLngLat(coords).setDOMContent(makeCard(f)).addTo(map);
    markers.forEach(entry=>{
      entry.el.classList.toggle('vxa-selected',entry.id===id);
      entry.label.classList.toggle('vxa-label-selected',entry.id===id);
    });
    popup.on('close',()=>{
      if(activeId===id){activeId=null;markers.forEach(entry=>{entry.el.classList.remove('vxa-selected');entry.label.classList.remove('vxa-label-selected');});}
    });
    // Clear the municipality-only search filter after opening the attraction.
    // The popup remains visible and the municipality directory becomes available again.
    if (search.value) {search.value='';search.dispatchEvent(new Event('input',{bubbles:true}));}
    expanded=false;renderPanel();
  }
  function marker(f) {
    const props=f.properties,t=attractionType(props);
    const el=document.createElement('div');el.className='vxa-marker';
    el.setAttribute('role','button');el.setAttribute('tabindex','0');
    el.setAttribute('aria-label',props.attraction_name_original);
    el.title=props.attraction_name_original;
    // Absolute positioning is MapLibre's responsibility; never apply CSS transforms
    // to the actual Marker root (MapLibre uses its transform for geo projection).
    const circle=document.createElement('span');circle.className='vxa-marker-circle';circle.textContent=t.symbol;
    circle.style.background=t.color;
    const label=document.createElement('span');label.className='vxa-marker-label';label.textContent=props.attraction_name_original;
    el.append(circle,label);
    el.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();focus(f);});
    el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();focus(f);}});
    new lib.Marker({element:el,anchor:'center',subpixelPositioning:true}).setLngLat(f.geometry.coordinates).addTo(map);
    markers.push({id:String(props.place_id),el,label});
  }
  function updateLabels() {
    const z=map.getZoom();
    markers.forEach(m=>m.el.classList.toggle('vxa-labels-on',z>=8.3||activeId===m.id));
  }
  search.addEventListener('input',renderPanel);
  search.addEventListener('keydown',e=>{
    if(e.key!=='Enter')return;
    const q=normalize(search.value);
    const found=q?attractions.find(f=>normalize(f.properties.attraction_name_original).includes(q)):null;
    if(found){e.preventDefault();focus(found);}
  });
  toggle.addEventListener('click',()=>{expanded=!expanded;renderPanel();});
  map.on('zoom',updateLabels);
  document.addEventListener('change',e=>{
    if(e.target!==search)renderPanel();
  });
  fetch('data/attractions_batch1.geojson',{cache:'no-store'})
    .then(r=>{if(!r.ok)throw new Error(`HTTP ${r.status}`);return r.json();})
    .then(fc=>{
      if(fc.type!=='FeatureCollection'||!Array.isArray(fc.features))throw new Error('Expected GeoJSON FeatureCollection');
      attractions=fc.features.filter(f=>f.geometry?.type==='Point'&&f.geometry.coordinates.length===2&&f.geometry.coordinates.every(Number.isFinite));
      attractions.forEach(marker);
      updateLabels();renderPanel();
      console.info(`[Veracruz attractions] ${attractions.length} attraction markers loaded`);
    })
    .catch(err=>{
      console.error('[Veracruz attractions] Failed to load attraction layer:',err);
      toggle.textContent='Attractions unavailable: '+err.message;
    });
})();
