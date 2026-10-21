/* Veracruz statewide routing preview. Click-triggered OSRM demo; no page-load API requests. */
(() => {
  'use strict';
  const root = document.querySelector('#veracruz-map-section');
  const aside = root?.querySelector('.vx-side');
  if (!root || !aside || document.querySelector('#vx-statewide-route')) return;
  const copy = {
    es: {title:'Rutas viales en Veracruz — prueba', note:'Utiliza carreteras reales de OpenStreetMap mediante un servicio público de demostración. No garantiza acceso a las entradas, tráfico ni disponibilidad. No es navegación.', from:'Origen',to:'Destino',stops:'Paradas opcionales',none:'Sin parada',go:'Dibujar ruta vial',open:'Abrir indicaciones',clear:'Quitar línea',wait:'Cargando atractivos…',ready:'Selecciona origen y destino.',loading:'Consultando la red vial…',done:'Ruta aproximada',error:'No se pudo calcular la ruta aquí. Puedes abrir las indicaciones externas.',same:'Elige dos lugares diferentes.',bad:'Selecciona dos lugares.',points:'Lugares con coordenadas aproximadas. Comprueba el acceso real.',note2:'Servicio de demostración, no disponible garantizada. Solo se consulta al pulsar el botón.',dist:'km',time:'h (estimación sin tráfico)'},
    en: {title:'Road routes across Veracruz — preview',note:'Uses real OpenStreetMap roads through a public demonstration service. Does not guarantee venue entrances, traffic conditions or availability. Not turn-by-turn navigation.',from:'Start',to:'Finish',stops:'Optional stops',none:'No stop',go:'Draw road route',open:'Open driving directions',clear:'Clear road line',wait:'Loading attractions…',ready:'Select start and finish.',loading:'Querying the road network…',done:'Approximate road route',error:'Could not calculate the route here. External directions remain available.',same:'Choose two different locations.',bad:'Select two locations.',points:'Locations are approximate; verify their actual entrances.',note2:'Demonstration service, not guaranteed. Only queried when you click.',dist:'km',time:'h (estimate, no traffic)'},
    ja: {title:'ベラクルス州の道路ルート（試用）',note:'OpenStreetMap の道路と公開デモサーバーを使用。実際の入口・交通情報・営業状況は未確認。ナビゲーションではありません。',from:'出発地',to:'目的地',stops:'経由地（任意）',none:'経由地なし',go:'道路ルートを表示',open:'運転経路を開く',clear:'ルート線を消去',wait:'観光地を読み込み中…',ready:'出発地と目的地を選択してください。',loading:'道路ルートを検索中…',done:'概算の道路経路',error:'道路経路を表示できません。外部マップをご利用ください。',same:'異なる場所を選んでください。',bad:'出発地と目的地を選んでください。',points:'地点は概算です。実際の入口を確認してください。',note2:'公開デモは動作保証がありません。ボタンを押した時だけ検索します。',dist:'km',time:'時間（渋滞なしの目安）'}
  };
  const lang=()=>{const v=(document.documentElement.lang||'es').slice(0,2);return copy[v] ? v : 'es';};
  const t=()=>copy[lang()];
  const el=(tag,cls,label)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(label!==undefined)e.textContent=label;return e;};
  const panel=el('details','vxs-panel');panel.id='vx-statewide-route';
  const heading=el('summary','vxs-heading',t().title),description=el('p','vxs-note',t().note);
  panel.append(heading,description);
  const control=el('div','vxs-controls');
  const fields=['from','via1','via2','to'];
  const boxes={};
  for (const field of fields){
    const row=el('label','vxs-field'),span=el('span','',field==='from'?t().from:field==='to'?t().to:t().stops);
    const select=el('select','vxs-select');select.id='vxs-'+field;
    select.setAttribute('aria-label',span.textContent);
    row.append(span,select);control.append(row);boxes[field]=select;
  }
  panel.append(control);
  const btns=el('div','vxs-actions');const go=el('button','vxs-primary',t().go),clear=el('button','vxs-secondary',t().clear);
  go.type=clear.type='button';btns.append(go,clear);panel.append(btns);
  const status=el('p','vxs-message',t().wait);status.setAttribute('aria-live','polite');panel.append(status);
  const external=el('a','vxs-directions',t().open);external.target='_blank';external.rel='noopener noreferrer';external.hidden=true;panel.append(external);
  panel.append(el('p','vxs-note',t().points+' '+t().note2));
  const regional=document.querySelector('#vx-route-planner');
  if(regional)regional.insertAdjacentElement('afterend',panel);else aside.insertBefore(panel,aside.querySelector('#vx-list'));
  let features=[],result=null,busy=false,last=0;
  const LINE='vxs-statewide-route',SOURCE='vxs-statewide-source';
  const coord=f=>f.geometry.coordinates;
  const selected=()=>[boxes.from.value,boxes.via1.value,boxes.via2.value,boxes.to.value].filter(Boolean).map(id=>features.find(f=>String(f.properties.id||f.id)===id)).filter(Boolean);
  function fill(){
    const collator=new Intl.Collator(lang());
    const rows=[...features].sort((a,b)=>collator.compare(a.properties.name,b.properties.name));
    for(const key of fields){
      const sel=boxes[key],original=sel.value;sel.replaceChildren();
      const blank=el('option','',key==='via1'||key==='via2'?t().none:'—');blank.value='';sel.append(blank);
      for(const f of rows){const option=el('option','',`${f.properties.name} · ${f.properties.municipality||'Veracruz'}`);option.value=String(f.properties.id||f.id);sel.append(option)}
      if(original)sel.value=original;
    }
  }
  function directionsUrl(points){
    if(points.length<2)return '';
    const fmt=p=>`${coord(p)[1].toFixed(6)},${coord(p)[0].toFixed(6)}`;
    const url=new URL('https://www.google.com/maps/dir/');
    url.searchParams.set('api','1');url.searchParams.set('travelmode','driving');
    url.searchParams.set('origin',fmt(points[0]));url.searchParams.set('destination',fmt(points.at(-1)));
    if(points.length>2)url.searchParams.set('waypoints',points.slice(1,-1).map(fmt).join('|'));
    return url.toString();
  }
  function updateExternal(){const points=selected(),url=directionsUrl(points);external.hidden=!url;if(url)external.href=url;else external.removeAttribute('href');}
  function removeLine(){
    result=null;
    const m=window.__vx_attraction_map;
    if(m?.getLayer?.(LINE))m.removeLayer(LINE);
    if(m?.getSource?.(SOURCE))m.removeSource(SOURCE);
  }
  function showLine(){
    const m=window.__vx_attraction_map;
    if(!result||!m?.isStyleLoaded?.()||!m.addLayer)return;
    if(!m.getSource(SOURCE))m.addSource(SOURCE,{type:'geojson',data:result});
    else m.getSource(SOURCE).setData(result);
    if(!m.getLayer(LINE))m.addLayer({id:LINE,type:'line',source:SOURCE,paint:{'line-color':'#7b26cf','line-width':5,'line-opacity':0.9}});
    const coords=result.geometry.coordinates;
    if(coords.length){let w=Infinity,e=-Infinity,s=Infinity,n=-Infinity;for(const [lng,lat] of coords){w=Math.min(w,lng);e=Math.max(e,lng);s=Math.min(s,lat);n=Math.max(n,lat)}m.fitBounds([[w,s],[e,n]],{padding:55,maxZoom:13,duration:350});}
  }
  function fail(msg){status.textContent=msg;status.classList.add('vxs-error');}
  function message(msg){status.textContent=msg;status.classList.remove('vxs-error');}
  for(const key of fields)boxes[key].addEventListener('change',()=>{updateExternal();removeLine();message(t().ready)});
  clear.addEventListener('click',()=>{removeLine();message(t().ready)});
  go.addEventListener('click',async()=>{
    const points=selected();updateExternal();
    if(points.length<2){fail(t().bad);return;}
    if(new Set(points.map(p=>String(p.id||p.properties.id))).size!==points.length){fail(t().same);return;}
    if(busy)return;
    // No automatic polling or bulk scraping: only one request per real button click.
    if(Date.now()-last<1600){return;}
    busy=true;last=Date.now();go.disabled=true;removeLine();message(t().loading);
    try{
      // The public OSRM server is for limited, noncommercial prototype use only.
      // For deployment at scale replace window.VX_STATEWIDE_ROUTING_BASE with a permitted provider.
      const base=String(window.VX_STATEWIDE_ROUTING_BASE||'https://router.project-osrm.org').replace(/\/$/,'');
      const pairs=points.map(p=>coord(p).map(v=>Number(v).toFixed(6)).join(',')).join(';');
      const url=`${base}/route/v1/driving/${pairs}?overview=full&geometries=geojson&steps=false`;
      const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),16000);
      let reply;try{reply=await fetch(url,{signal:controller.signal});}finally{clearTimeout(timer);}
      if(!reply.ok)throw new Error('HTTP '+reply.status);
      const data=await reply.json(),r=data?.routes?.[0];
      if(data.code!=='Ok'||r?.geometry?.type!=='LineString'||!Array.isArray(r.geometry.coordinates)||r.geometry.coordinates.length<2||!Number.isFinite(r.distance))throw new Error(data.code||'Unexpected routing response');
      result=r.geometry;showLine();
      message(`${t().done}: ${(r.distance/1000).toFixed(1)} ${t().dist}${Number.isFinite(r.duration)?' · '+(r.duration/3600).toFixed(1)+' '+t().time:''}.`);
    }catch(e){console.warn('[Statewide routing preview]',e);fail(t().error);}finally{busy=false;go.disabled=false;}
  });
  (async()=>{
    try{
      const r=await fetch('data/attractions.geojson');if(!r.ok)throw new Error('Attractions HTTP '+r.status);
      const data=await r.json();if(data.type!=='FeatureCollection'||!Array.isArray(data.features))throw new Error('Invalid attractions format');
      features=data.features.filter(f=>f.geometry?.type==='Point'&&Array.isArray(f.geometry.coordinates)&&f.geometry.coordinates.length===2&&f.geometry.coordinates.every(Number.isFinite)&&f.properties?.name&&(f.properties.id||f.id));
      if(features.length<2)throw new Error('No mapped attraction endpoints');
      fill();message(`${t().ready} (${features.length})`);
      const map=window.__vx_attraction_map;
      map?.on?.('style.load',()=>{if(result)showLine()});
    }catch(e){console.error('[Statewide routing]',e);fail(t().error+' '+e.message);}
  })();
  document.addEventListener('change',e=>{
    if(e.target?.id==='language-select'||e.target?.name==='language'){
      heading.textContent=t().title;description.textContent=t().note;go.textContent=t().go;clear.textContent=t().clear;external.textContent=t().open;
    }
  });
  window.VeracruzStatewideRoutePreview={directionsUrl};
})();
