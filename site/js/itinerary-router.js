/* Veracruz itinerary planner v3: searchable places, map clicks and ordered road stops.
   On-demand routing from an OSRM-compatible service; external Google Maps directions
   are always available. No routes or prices are invented on failed API calls. */
(() => {
  'use strict';
  const root = document.querySelector('#veracruz-map-section');
  const sidebar = root?.querySelector('.vx-side');
  const map = window.__vx_attraction_map;
  if (!root || !sidebar || document.querySelector('#vxw-itinerary')) return;

  const I18N = {
    en: {title:'Plan your road trip',note:'Search for an attraction or choose points on the map. Add as many stops as you need (up to 12), then reorder them.',search:'Find a municipality or attraction…',pick:'Add points on map',picking:'Stop choosing points',add:'Add',from:'Start',to:'Finish',via:'Stop',remove:'Remove',up:'Move earlier',down:'Move later',route:'Calculate road route',clear:'Clear trip',external:'Open road directions',segment:'Directions part',ready:'Add a starting point and a destination.',need:'Add at least two different stops.',max:'Maximum 12 points per itinerary.',same:'That place is already on your itinerary.',running:'Requesting road directions…',success:'Road route',failed:'The road-routing service did not return a usable route. Open external driving directions instead.',timeout:'Routing service timed out. Open external directions instead.',notFound:'No matching municipalities or attractions.',map:'Click an attraction marker OR any map location to add the next stop.',cancel:'Map selection off.',approx:'Map coordinates may not be an actual vehicle entrance. Check access and opening hours.',snapped:'Some points were snapped far from a road; check access before traveling.',travel:'approx. without traffic',service:'Live map routing uses a public demo server; it may be unavailable. External directions remain available.',set:'Ready to calculate.',changed:'Stops changed; calculate again.',routeOpen:'Show planner',municipalityKind:'Municipality · approximate reference',attractionKind:'Attraction',hint:'Stops are visited in the order shown.',segmentNote:'Multiple links preserve all stops on mobile.'},
    es: {title:'Planear un recorrido vial',note:'Busca atractivos o elige puntos en el mapa. Agrega hasta 12 lugares y cambia su orden.',search:'Buscar municipio o atractivo…',pick:'Agregar puntos en el mapa',picking:'Dejar de elegir puntos',add:'Agregar',from:'Salida',to:'Llegada',via:'Parada',remove:'Quitar',up:'Mover antes',down:'Mover después',route:'Calcular ruta vial',clear:'Vaciar recorrido',external:'Abrir indicaciones viales',segment:'Indicaciones tramo',ready:'Agrega una salida y un destino.',need:'Agrega por lo menos dos puntos diferentes.',max:'Máximo 12 puntos por recorrido.',same:'Ese lugar ya está en el recorrido.',running:'Consultando la ruta vial…',success:'Ruta por carretera',failed:'El servicio de rutas no devolvió una ruta válida. Abre las indicaciones externas.',timeout:'Se agotó el tiempo de espera. Abre las indicaciones externas.',notFound:'No hay coincidencias con la búsqueda. Comprueba el nombre del municipio o atractivo.',map:'Toca un marcador O cualquier punto del mapa para añadir la siguiente parada.',cancel:'Selección en mapa desactivada.',approx:'La coordenada podría no ser la entrada para vehículos. Verifica accesos y horarios.',snapped:'Hay puntos alejados de las carreteras; revisa los accesos.',travel:'aprox. sin tráfico',service:'La ruta interna depende de un servicio público de pruebas y puede fallar. Las indicaciones externas siguen disponibles.',set:'Ya puedes calcular la ruta.',changed:'Cambiaste las paradas; calcula otra vez.',routeOpen:'Abrir planificador',municipalityKind:'Municipio · ubicación aproximada',attractionKind:'Atractivo',hint:'Se recorrerán los puntos en el orden mostrado.',segmentNote:'Se divide en varios enlaces para conservar todas las paradas en móviles.'},
    ja: {title:'車での旅行ルート',note:'観光地を検索するか地図上で選択。最大12地点まで追加・並べ替えができます。',search:'市町村・観光地を検索…',pick:'地図上で地点を追加',picking:'地点選択を終了',add:'追加',from:'出発地',to:'到着地',via:'経由地',remove:'削除',up:'前へ',down:'後へ',route:'道路ルートを計算',clear:'全て削除',external:'外部の道路案内',segment:'経路パート',ready:'出発地と到着地を追加してください。',need:'異なる地点を2つ以上追加してください。',max:'最大12地点です。',same:'すでに追加された地点です。',running:'道路ルートを確認中…',success:'道路ルート',failed:'道路ルートサービスを利用できません。外部の地図で確認してください。',timeout:'応答がありません。外部の地図を利用してください。',notFound:'該当する市町村・観光地がありません。',map:'観光地のマーカー、または地図上の地点をクリックしてください。',cancel:'地図選択を終了しました。',approx:'観光地の座標は車の入口と異なる場合があります。',snapped:'道路から遠い地点があります。実際のアクセスを確認してください。',travel:'渋滞なしの概算',service:'公開デモサーバーのため利用できない場合があります。外部案内をご利用ください。',set:'ルートを計算できます。',changed:'地点を変更しました。再計算してください。',routeOpen:'プランナーを開く',municipalityKind:'市町村 · 概略位置',attractionKind:'観光地',hint:'表示順に訪問します。',segmentNote:'全地点を含めるため案内リンクを分割しています。'}
  };
  const lang = () => {const x = document.querySelector('#language-select')?.value || document.documentElement.lang || 'en'; return I18N[String(x).slice(0,2)] ? String(x).slice(0,2) : 'en';};
  const tx = () => I18N[lang()];
  const make = (tag, className, label) => {const e = document.createElement(tag); if(className)e.className=className;if(label!==undefined)e.textContent=label;return e;};
  const norm = s => String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
  const isGeo = p => Array.isArray(p) && p.length===2 && p.every(Number.isFinite) && p[0]>-101 && p[0]<-92 && p[1]>16 && p[1]<24;
  const placeKey = p => p.id;
  const MAX = 12;

  const panel=make('section','vxw-panel');panel.id='vxw-itinerary';
  const title=make('h3','vxw-title',tx().title),note=make('p','vxw-lead',tx().note);
  const head=make('div','vxw-head');head.append(title,note);panel.append(head);
  /* PP6-SEARCH-STATE-V4: report catalog status and refresh pending searches. */
  const searchWrap=make('div','vxw-search-wrap');
  const search=make('input','vxw-search');search.type='search';search.placeholder=tx().search;search.autocomplete='off';search.setAttribute('aria-label',tx().search);search.setAttribute('aria-expanded','false');
  const suggestionBox=make('div','vxw-results');suggestionBox.hidden=true;searchWrap.append(search,suggestionBox);panel.append(searchWrap);
  const catalogState=make('p','vxw-catalog-state','Loading municipalities and attractions…');
  panel.append(catalogState);
  const pick=make('button','vxw-pick',tx().pick);pick.type='button';pick.setAttribute('aria-pressed','false');panel.append(pick);
  const how=make('p','vxw-hint',tx().hint);panel.append(how);
  const stopsList=make('ol','vxw-stops');panel.append(stopsList);
  const toolbar=make('div','vxw-buttons');
  const calc=make('button','vxw-main',tx().route),clear=make('button','vxw-subtle',tx().clear);calc.type=clear.type='button';
  toolbar.append(calc,clear);panel.append(toolbar);
  const status=make('p','vxw-status',tx().ready);status.setAttribute('role','status');status.setAttribute('aria-live','polite');panel.append(status);
  const summary=make('p','vxw-summary');summary.hidden=true;panel.append(summary);
  const directions=make('div','vxw-directions');panel.append(directions);
  const caveat=make('p','vxw-caveat',tx().approx+' '+tx().service);panel.append(caveat);
  const before=sidebar.querySelector('#vx-list');if(before)sidebar.insertBefore(panel,before);else sidebar.append(panel);
  const floating=root.querySelector('#vx-map')?make('button','vxw-map-open',tx().routeOpen):null;
  if(floating){floating.type='button';root.querySelector('#vx-map').append(floating);floating.addEventListener('click',()=>{panel.scrollIntoView({behavior:'smooth',block:'start'});search.focus({preventScroll:true});});}

  let places=[],selected=[],picking=false,busy=false,serial=0,currentRoute=null,aborter=null,routeSeq=0;
  const SOURCE='vxw-road-source', LAYER='vxw-road-line';
  const setStatus=(s,error=false)=>{status.textContent=s;status.classList.toggle('vxw-error',error);};
  function clearLine(){currentRoute=null;if(map?.getLayer?.(LAYER))map.removeLayer(LAYER);if(map?.getSource?.(SOURCE))map.removeSource(SOURCE);summary.hidden=true;summary.textContent='';document.dispatchEvent(new CustomEvent('vxw:route-cleared'));}
  function changed(){routeSeq++;if(aborter)aborter.abort();busy=false;aborter=null;clearLine();setStatus(selected.length>=2?tx().changed:tx().ready);renderStops();renderDirections();document.dispatchEvent(new CustomEvent('vxw:stops-changed'));}
  function add(place){if(selected.length>=MAX){setStatus(tx().max,true);return false;}if(selected.some(p=>placeKey(p)===placeKey(place))){setStatus(tx().same,true);return false;}selected.push(place);changed();return true;}
  function renderStops(){stopsList.replaceChildren();selected.forEach((p,i)=>{
    const li=make('li','vxw-stop');
    const label=make('div','vxw-stop-name');label.append(make('small','vxw-stop-role',i===0?tx().from:i===selected.length-1?tx().to:tx().via),make('strong','',p.name));
    label.append(make('small','vxw-municipality',p.kind==='municipality'?tx().municipalityKind:(p.municipality||tx().attractionKind)));
    const actions=make('div','vxw-stop-actions');
    const up=make('button','vxw-icon','↑'),down=make('button','vxw-icon','↓'),remove=make('button','vxw-icon vxw-remove','×');
    [up,down,remove].forEach(b=>b.type='button');up.title=up.ariaLabel=tx().up;down.title=down.ariaLabel=tx().down;remove.title=remove.ariaLabel=tx().remove;
    up.disabled=i===0;down.disabled=i===selected.length-1;
    up.addEventListener('click',()=>{[selected[i-1],selected[i]]=[selected[i],selected[i-1]];changed();});
    down.addEventListener('click',()=>{[selected[i],selected[i+1]]=[selected[i+1],selected[i]];changed();});
    remove.addEventListener('click',()=>{selected.splice(i,1);changed();});
    actions.append(up,down,remove);li.append(label,actions);stopsList.append(li);
  });calc.disabled=selected.length<2 || busy;clear.disabled=selected.length===0;
  }
  function linkFor(segment){const value=p=>`${p.coords[1].toFixed(6)},${p.coords[0].toFixed(6)}`;
    const u=new URL('https://www.google.com/maps/dir/');u.searchParams.set('api','1');u.searchParams.set('travelmode','driving');u.searchParams.set('origin',value(segment[0]));u.searchParams.set('destination',value(segment[segment.length-1]));
    if(segment.length>2)u.searchParams.set('waypoints',segment.slice(1,-1).map(value).join('|'));return u.toString();}
  function renderDirections(){directions.replaceChildren();if(selected.length<2)return;
    // Google Maps URLs allow only three via points in mobile browsers. Overlap endpoints.
    let segments=[];for(let i=0;i<selected.length-1;i+=4){segments.push(selected.slice(i,Math.min(i+5,selected.length)));}
    if(segments.length>1)directions.append(make('small','vxw-directions-note',tx().segmentNote));
    segments.forEach((segment,i)=>{const a=make('a','vxw-external',segments.length===1?tx().external:`${tx().segment} ${i+1}/${segments.length} ↗`);a.href=linkFor(segment);a.target='_blank';a.rel='noopener noreferrer';directions.append(a);});
  }
  function closeResults(){suggestionBox.hidden=true;search.setAttribute('aria-expanded','false');}
  function showSearch(){const q=norm(search.value);suggestionBox.replaceChildren();if(!q){closeResults();return;}
    const found=places.filter(p=>norm(p.name+' '+p.municipality).includes(q)&&!selected.some(x=>x.id===p.id)).sort((a,b)=>{const rank=p=>norm(p.name)===q?0:norm(p.name).startsWith(q)?1:2;return rank(a)-rank(b)||(a.kind==='municipality'?-1:1)-(b.kind==='municipality'?-1:1)||a.name.localeCompare(b.name);}).slice(0,9);
    if(!found.length)suggestionBox.append(make('p','vxw-no-matches',places.length?tx().notFound:'Cargando municipios y atractivos…'));
    for(const p of found){const button=make('button','vxw-suggestion');button.type='button';button.append(make('strong','',p.name));button.append(make('small','',p.kind==='municipality'?tx().municipalityKind:(p.municipality||tx().attractionKind)));button.addEventListener('click',()=>{add(p);search.value='';closeResults();search.focus();});suggestionBox.append(button);}
    suggestionBox.hidden=false;search.setAttribute('aria-expanded','true');
  }
  search.addEventListener('input',showSearch);search.addEventListener('keydown',e=>{if(e.key==='Escape')closeResults();if(e.key==='Enter'&&!suggestionBox.hidden){const b=suggestionBox.querySelector('button');if(b){e.preventDefault();b.click();}}});
  document.addEventListener('click',e=>{if(!searchWrap.contains(e.target))closeResults();});
  function pickMode(value){picking=value;pick.textContent=picking?tx().picking:tx().pick;pick.classList.toggle('vxw-active',picking);pick.setAttribute('aria-pressed',String(picking));root.classList.toggle('vxw-picking',picking);if(map?.getCanvas)map.getCanvas().style.cursor=picking?'crosshair':'';setStatus(picking?tx().map:tx().cancel);}
  pick.addEventListener('click',()=>pickMode(!picking));
  // Captures actual MapLibre attraction marker clicks while the user chooses stops.
  root.addEventListener('click',event=>{
    if(!picking)return;
    const marker=event.target.closest?.('.vxa-marker,.vx-geo-marker');if(!marker)return;
    const mid=marker.dataset.vxMunicipalityId;
    const id=mid?'municipality:'+mid:marker.dataset.vxPlaceId;
    const name=marker.getAttribute('aria-label')||marker.title;
    const p=places.find(x=>x.id===id)||(places.find(x=>norm(x.name)===norm(name)&&x.kind===(mid?'municipality':'attraction')));
    event.preventDefault();event.stopPropagation();event.stopImmediatePropagation();
    if(p)add(p);else setStatus(tx().notFound,true);
  },true);
  if(map?.on){map.on('click',e=>{if(!picking||!e?.lngLat)return;
    const coords=[Number(e.lngLat.lng),Number(e.lngLat.lat)];if(!isGeo(coords))return;
    serial++;const p={id:'point:'+serial,name:`${coords[1].toFixed(5)}, ${coords[0].toFixed(5)}`,municipality:'',coords};add(p);
  });map.on('style.load',()=>{if(currentRoute)drawRoute();});}
  function drawRoute(){if(!currentRoute || !map?.addSource || !map?.isStyleLoaded?.())return;
    const geo={type:'Feature',properties:{},geometry:currentRoute};
    if(map.getSource(SOURCE))map.getSource(SOURCE).setData(geo);else map.addSource(SOURCE,{type:'geojson',data:geo});
    if(!map.getLayer(LAYER))map.addLayer({id:LAYER,type:'line',source:SOURCE,paint:{'line-color':'#6c30c7','line-width':6,'line-opacity':0.94}});
    const coords=currentRoute.coordinates;let west=180,south=90,east=-180,north=-90;
    for(const [x,y] of coords){if(!Number.isFinite(x)||!Number.isFinite(y))continue;west=Math.min(west,x);east=Math.max(east,x);south=Math.min(south,y);north=Math.max(north,y);}
    if(west<=east && map.fitBounds)map.fitBounds([[west,south],[east,north]],{padding:45,maxZoom:13,duration:350});
  }
  calc.addEventListener('click',async()=>{
    if(busy || selected.length<2){setStatus(tx().need,true);return;}
    const requestId=++routeSeq;const points=selected.map(p=>({coords:p.coords,id:p.id}));
    busy=true;calc.disabled=true;clearLine();setStatus(tx().running);
    const coords=points.map(p=>p.coords.map(n=>n.toFixed(6)).join(',')).join(';');
    // Permits a configured, properly authorized OSRM-compatible service.
    // By default try two public OSRM demonstration endpoints, manually and at most
    // once per Calculate click. These are NOT production SLAs. A configured
    // VX_ROUTING_BASE_URL replaces both and must be an authorized HTTPS endpoint.
    const services=window.VX_ROUTING_BASE_URL
      ? [String(window.VX_ROUTING_BASE_URL)]
      : ['https://routing.openstreetmap.de/routed-car','https://router.project-osrm.org'];
    let lastFailure=null;
    try{
      for(let i=0;i<services.length;i++){
        if(requestId!==routeSeq)return;
        if(i>0)await new Promise(resolve=>setTimeout(resolve,1100));
        if(requestId!==routeSeq)return;
        let base;
        try{base=new URL(services[i]);if(base.protocol!=='https:')throw Error('HTTPS required');}
        catch(e){lastFailure=e;break;}
        const url=base.href.replace(/\/$/,'')+'/route/v1/driving/'+coords+'?overview=full&geometries=geojson&steps=false';
        aborter=new AbortController();const timer=setTimeout(()=>aborter?.abort(),8500);
        try{
          const r=await fetch(url,{signal:aborter.signal});
          if(requestId!==routeSeq)return;
          if(!r.ok)throw Error('HTTP '+r.status);
          const body=await r.json(),route=body?.routes?.[0],geom=route?.geometry;
          if(body?.code!=='Ok')throw Error(body?.code||'Unknown response');
          if(geom?.type!=='LineString'||!Array.isArray(geom.coordinates)||geom.coordinates.length<2||!Number.isFinite(route?.distance))throw Error('Invalid route geometry');
          currentRoute=geom;drawRoute();document.dispatchEvent(new CustomEvent('vxw:route-calculated',{detail:{distanceMeters:route.distance,durationSeconds:route.duration}}));
          const distance=(route.distance/1000).toFixed(1),duration=Number.isFinite(route.duration)?(route.duration/3600).toFixed(1):null;
          summary.hidden=false;summary.textContent=`${tx().success}: ${distance} km`+(duration?` · ${duration} h (${tx().travel})`:'');
          const far=body.waypoints?.some(w=>Number.isFinite(w.distance)&&w.distance>1500);
          setStatus(far?tx().snapped:tx().set,!!far);
          return;
        }catch(e){lastFailure=e;console.warn('[Veracruz route service]',base.hostname,e);}
        finally{clearTimeout(timer);aborter=null;}
      }
      if(requestId===routeSeq)setStatus(`${tx().failed} (${lastFailure?.message||lastFailure?.name||'service error'})`,true);
    }finally{if(requestId===routeSeq){busy=false;aborter=null;renderStops();}}
  });
  clear.addEventListener('click',()=>{selected=[];pickMode(false);changed();});
  const currentLanguage=()=>{title.textContent=tx().title;note.textContent=tx().note;search.placeholder=tx().search;pick.textContent=picking?tx().picking:tx().pick;calc.textContent=tx().route;clear.textContent=tx().clear;how.textContent=tx().hint;caveat.textContent=tx().approx+' '+tx().service;if(floating)floating.textContent=tx().routeOpen;renderStops();renderDirections();};
  document.querySelector('#language-select')?.addEventListener('change',currentLanguage);
  const load=async()=>{try{const responses=await Promise.all([fetch('data/attractions.geojson',{cache:'no-store'}),fetch('data/map_points.geojson',{cache:'no-store'})]);
      for(const r of responses)if(!r.ok)throw Error('HTTP '+r.status);
      const [attractions,municipalities]=await Promise.all(responses.map(r=>r.json()));
      const mapped=(attractions.features||[]).filter(f=>f.geometry?.type==='Point'&&isGeo(f.geometry.coordinates)&&f.properties?.name&&(f.properties?.id||f.id)).map(f=>({id:String(f.properties.id||f.id),name:String(f.properties.name),municipality:String(f.properties.municipality||''),kind:'attraction',coords:f.geometry.coordinates}));
      const towns=(municipalities.features||[]).filter(f=>f.geometry?.type==='Point'&&isGeo(f.geometry.coordinates)&&f.properties?.name&&f.properties?.municipality_id).map(f=>({id:'municipality:'+String(f.properties.municipality_id),name:String(f.properties.name),municipality:String(f.properties.name),kind:'municipality',approx:true,coords:f.geometry.coordinates}));
      places=[...towns,...mapped];
      catalogState.textContent=`${towns.length} municipalities / municipios · ${mapped.length} attractions / atractivos`;
      // A user can search before the asynchronous files finish loading.
      if(search.value.trim())showSearch();
      if(mapped.length<2||towns.length<2)throw Error('Missing map references');
      const url=new URL(location.href),saved=url.searchParams.get('vxroute');if(saved){for(const id of saved.split(',').slice(0,MAX)){const p=places.find(x=>x.id===id);if(p&&!selected.some(x=>x.id===p.id))selected.push(p);}}
      renderStops();renderDirections();document.dispatchEvent(new CustomEvent('vxw:stops-changed'));setStatus(tx().ready);
    }catch(e){catalogState.textContent=`Catalog failed to load: ${e.message}`;setStatus(`Could not load mapped attractions: ${e.message}`,true);console.error('[Veracruz itinerary]',e);}};
  renderStops();load();
  window.VeracruzItineraryV2={getStops:()=>selected.map(p=>({...p})),addStopById:id=>{const p=places.find(p=>p.id===id);return p?add(p):false;},clear:()=>{selected=[];changed();},getProviderURL:()=>String(window.VX_ROUTING_BASE_URL||'https://router.project-osrm.org')};
})();
