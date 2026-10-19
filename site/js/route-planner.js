/* Veracruz route planner: regional static road graph, browser Dijkstra, no routing API. */
(() => {
 'use strict';
 const ROOT=document.getElementById('veracruz-map-section');
 if(!ROOT)return;
 const TXT={
  en:{title:'Plan a route',region:'Xalapa · Coatepec · Xico',from:'Start at',to:'Finish at',stops:'Stops (optional)',add:'Add stop',remove:'Remove',run:'Find shortest road route',ready:'Choose two attractions and calculate a route.',loading:'Loading regional road network…',wait:'Preparing regional routing data. The map explorer still works.',error:'Routing data could not be loaded.',same:'Choose different starting and ending attractions.',none:'No drivable path between these points in the current road graph.',result:'Shortest road distance',distance:'km',snap:'Site access is not verified. Snapping to roads may add walking/driving distance.',limited:'Currently available in the Xalapa–Coatepec–Xico region; more areas will follow.',compare:'Approximate road distance, not travel time or driving instructions.',processing:'Calculating route…',available:'attractions available',near:'Nearby optional stops (straight-line proximity only)',plus:'Add',noNear:'No other mapped attractions nearby.',clear:'Clear route', choose:'Tap “Choose start on map” and then two attraction markers, or search below.', chooseStart:'Choose start on map', chooseEnd:'Choose destination on map', chooseStop:'Choose stop on map', pickStart:'Start selected. Now tap a destination.', pickEnd:'Destination selected. Calculate the route or tap another destination.', pickStop:'Stop added to itinerary.', outside:'This attraction is outside the available Xalapa road network.', search:'Search regional attractions…', noMatches:'No attractions found in this region', noChoice:'Choose a starting attraction and a destination.', rough:'Illustrative driving time at 30–50 km/h average', notETA:'Not a real ETA: road speeds, access, traffic and stops are unverified.', swap:'Swap start / finish', hint:'You can change both places at any time.'},
  es:{title:'Planear ruta',region:'Xalapa · Coatepec · Xico',from:'Salida',to:'Llegada',stops:'Paradas (opcionales)',add:'Agregar parada',remove:'Quitar',run:'Calcular ruta más corta',ready:'Elige dos atractivos para calcular la ruta.',loading:'Cargando la red vial regional…',wait:'Preparando los datos de rutas. El explorador sigue disponible.',error:'No se pudieron cargar los datos de rutas.',same:'Elige atractivos distintos para salir y llegar.',none:'No se encontró ruta transitable entre estos puntos en la red disponible.',result:'Distancia vial más corta',distance:'km',snap:'Los accesos a los atractivos no están verificados. Puede haber distancia adicional hasta la entrada.',limited:'Disponible por ahora para Xalapa–Coatepec–Xico; después se ampliará.',compare:'Distancia vial aproximada, no tiempo de viaje ni indicaciones de manejo.',processing:'Calculando ruta…',available:'atractivos disponibles',near:'Paradas opcionales cercanas (proximidad en línea recta)',plus:'Agregar',noNear:'No hay otros atractivos cartografiados cerca.',clear:'Limpiar ruta', choose:'Pulsa “Elegir salida en el mapa” y después dos marcadores, o busca abajo.', chooseStart:'Elegir salida en el mapa', chooseEnd:'Elegir llegada en el mapa', chooseStop:'Elegir parada en el mapa', pickStart:'Salida elegida. Ahora toca un destino.', pickEnd:'Llegada elegida. Calcula la ruta o toca otro destino.', pickStop:'Parada agregada.', outside:'Este atractivo queda fuera de la red vial disponible de Xalapa.', search:'Buscar atractivos de la región…', noMatches:'No hay atractivos de esta región', noChoice:'Elige un punto de salida y otro de llegada.', rough:'Tiempo ilustrativo a una media de 30–50 km/h', notETA:'No es un tiempo real: velocidad, accesos, tránsito y paradas sin verificar.', swap:'Intercambiar salida / llegada', hint:'Puedes cambiar ambos puntos en cualquier momento.'},
  ja:{title:'ルートを計画',region:'ハラパ・コアテペック・ヒコ',from:'出発地',to:'目的地',stops:'立ち寄り先（任意）',add:'経由地を追加',remove:'削除',run:'最短道路経路を検索',ready:'出発地と目的地を選んでください。',loading:'地域の道路網を読み込み中…',wait:'ルート情報を準備しています。地図は利用できます。',error:'道路データを読み込めませんでした。',same:'異なる出発地と目的地を選んでください。',none:'利用可能な道路データでは経路が見つかりません。',result:'最短道路距離',distance:'km',snap:'観光地の車両入口は未確認です。道路から追加の移動が必要な場合があります。',limited:'現在はハラパ・コアテペック・ヒコ地域で利用可能です。',compare:'概算の道路距離です。所要時間や運転案内ではありません。',processing:'経路を計算中…',available:'件の観光地',near:'近くの候補地（直線距離の目安）',plus:'追加',noNear:'近くに他の場所がありません。',clear:'ルートを消去', choose:'地図上で出発地、次に目的地を選ぶか、下から検索してください。', chooseStart:'地図で出発地', chooseEnd:'地図で目的地', chooseStop:'地図で経由地', pickStart:'出発地を選択しました。次に目的地をタップ。', pickEnd:'目的地を選びました。経路を計算できます。', pickStop:'経由地を追加しました。', outside:'この場所は現在のハラパ道路網の対象外です。', search:'この地域の名所を検索…', noMatches:'該当する場所はありません', noChoice:'出発地と目的地を選んでください。', rough:'平均時速30〜50 kmと仮定した参考時間', notETA:'実際の到着時間ではありません。速度、アクセス、交通状況は未確認です。', swap:'出発地と目的地を入れ替える', hint:'出発地と目的地はいつでも変更できます。'}
 };
 const currentLang=()=>{let x=(document.documentElement.lang||'en').slice(0,2);return TXT[x]?x:'en'};
 const text=()=>TXT[currentLang()];
 const make=(tag,cls,txt)=>{let e=document.createElement(tag);if(cls)e.className=cls;if(txt!==undefined)e.textContent=txt;return e};
 const panel=make('section','vxr-panel');panel.id='vx-route-planner';
 const head=make('div','vxr-heading'),heading=make('h3','',text().title),tag=make('small','',text().region);
 head.append(heading,tag);panel.append(head);
 const message=make('p','vxr-message',text().loading);panel.append(message);
 const how=make('p','vxr-hint',currentLang()==='es'?'Elige salida y llegada en el mapa o escribiendo el nombre. Solo funciona en Xalapa–Coatepec–Xico.':currentLang()==='ja'?'地図か検索欄で出発地と目的地を選びます。現在はハラパ周辺のみ。':'Choose start and destination on the map or by name. Routing is currently limited to Xalapa–Coatepec–Xico.');panel.append(how);
 const pickButtons=make('div','vxr-pick-buttons');
 const selectOnMap=make('button','vxr-pick',currentLang()==='es'?'Seleccionar puntos en el mapa':currentLang()==='ja'?'地図から場所を選択':'Select places on map');
 selectOnMap.type='button';selectOnMap.setAttribute('aria-pressed','false');
 pickButtons.append(selectOnMap);panel.append(pickButtons);
 const mapHelp=make('p','vxr-map-help');pickButtons.insertAdjacentElement('afterend',mapHelp);
 const fields=make('div','vxr-fields');
 const startSelect=make('select','vxr-hidden-select'),finishSelect=make('select','vxr-hidden-select'),stopChooser=make('select','vxr-hidden-select');
 [startSelect,finishSelect,stopChooser].forEach(x=>{x.hidden=true;x.tabIndex=-1});
 const makeSearch=(caption)=>{const label=make('label','vxr-search-label',caption),holder=make('div','vxr-combo'),input=make('input','vxr-query');input.type='search';input.placeholder=text().search;input.autocomplete='off';input.setAttribute('role','combobox');input.setAttribute('aria-autocomplete','list');input.setAttribute('aria-expanded','false');const menu=make('div','vxr-suggestions');menu.hidden=true;holder.append(input,menu);label.append(holder);return {label,input,menu}};
 const fromBox=makeSearch(text().from),toBox=makeSearch(text().to),stopBox=makeSearch(currentLang()==='es'?'Buscar una parada opcional':currentLang()==='ja'?'経由地を検索':'Find an optional stop');
 fields.append(fromBox.label,toBox.label);panel.append(fields);panel.append(startSelect,finishSelect,stopChooser);
 const swapBtn=make('button','vxr-secondary vxr-swap',text().swap);swapBtn.type='button';panel.append(swapBtn);
 const stopsHeader=make('p','vxr-subheading',text().stops),stopsList=make('div','vxr-stops'),addButton=make('button','vxr-secondary',text().add);
 addButton.type='button';const addRow=make('div','vxr-add');addRow.append(stopBox.label,addButton);
 panel.append(stopsHeader,stopsList,addRow);
 const actions=make('div','vxr-actions'),runButton=make('button','vxr-primary',text().run),clearButton=make('button','vxr-secondary',text().clear);
 runButton.type='button';clearButton.type='button';actions.append(runButton,clearButton);panel.append(actions);
 const results=make('section','vxr-results');results.setAttribute('aria-live','polite');panel.append(results);
 const nearby=make('section','vxr-nearby');panel.append(nearby);
 const note=make('p','vxr-note',text().limited+' '+text().compare);panel.append(note);
 const side=ROOT.querySelector('.vx-side');if(!side)return;
 const anchor=ROOT.querySelector('#vx-status');if(anchor)anchor.insertAdjacentElement('afterend',panel);else side.prepend(panel);
 let graph=null,stops=[],activeRoute=null,routeSvg=null,routeNeedsFrame=false,routeEventsAdded=false,picking=null,summaryBadge=null,selectablePins=[];
 fields.hidden=true;stopsHeader.hidden=true;stopsList.hidden=true;addRow.hidden=true;actions.hidden=true;pickButtons.hidden=true;swapBtn.hidden=true;
 function setStatus(s,bad=false){message.textContent=s;message.classList.toggle('vxr-error',bad)}
 function eligibleSites(){return graph?.sites||[]}
 const fold=(s)=>String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
 const getSite=(id)=>eligibleSites().find(s=>s.id===id);
 function optionList(sel,exclude=[]){const current=sel.value;sel.replaceChildren();const blank=make('option','','');blank.value='';sel.append(blank);eligibleSites().forEach(s=>{const o=make('option','',s.name);o.value=s.id;o.disabled=exclude.includes(s.id);sel.append(o)});sel.value=eligibleSites().some(s=>s.id===current&&!exclude.includes(s.id))?current:''}
 function phaseHint(kind){
   const es=currentLang()==='es',ja=currentLang()==='ja';
   if(kind==='start')return es?'1/2: toca un marcador dorado para elegir la salida.':ja?'1/2: 金色のマーカーで出発地を選んでください。':'1/2: tap a gold marker to choose the start.';
   if(kind==='end')return es?'2/2: ahora toca otro marcador dorado para elegir la llegada.':ja?'2/2: 別の金色のマーカーで目的地を選んでください。':'2/2: now tap another gold marker to choose the destination.';
   if(kind==='stop')return es?'Toca marcadores dorados para añadir paradas opcionales.':ja?'金色のマーカーで立ち寄り先を追加できます。':'Tap gold markers to add optional stops.';
   return es?'Los marcadores dorados indican los atractivos conectados a la red vial regional.':ja?'金色のマーカーだけが現在の地域道路網で利用できます。':'Gold markers indicate attractions connected to this regional road network.';
 }
 function dropSelectablePins(){for(const marker of selectablePins)marker.remove();selectablePins=[];}
 function refreshSelectablePins(){
   dropSelectablePins();
   if(!picking||!graph)return;
   const map=window.__vx_attraction_map,lib=window.maplibregl;
   if(!map||!lib?.Marker){setStatus('The map is not ready for marker selection; use the search boxes instead.',true);return;}
   const es=currentLang()==='es';
   for(const site of eligibleSites()){
     const pin=make('button','vxr-route-site-pin');pin.type='button';pin.title=site.name;pin.setAttribute('aria-label',site.name);
     pin.style.position='absolute';pin.style.top='0';pin.style.left='0';
     const icon=make('span','vxr-route-site-icon',site.icon||'📍');
     const name=make('span','vxr-route-site-name',site.name);
     pin.append(icon,name);
     const id=site.id;
     if(id===startSelect.value||id===finishSelect.value||stops.includes(id))pin.classList.add('chosen');
     pin.addEventListener('click',event=>{event.preventDefault();event.stopPropagation();event.stopImmediatePropagation();
        if(picking)changeSite(picking,getSite(id));
     });
     const marker=new lib.Marker({element:pin,anchor:'center'}).setLngLat(site.at).addTo(map);
     selectablePins.push(marker);
   }
 }
 function setPicking(kind){
   picking=kind;
   selectOnMap.classList.toggle('active',Boolean(kind));
   selectOnMap.setAttribute('aria-pressed',String(Boolean(kind)));
   selectOnMap.textContent=kind?(currentLang()==='es'?'Terminar selección':currentLang()==='ja'?'選択を終了':'Done selecting'):(currentLang()==='es'?'Seleccionar puntos en el mapa':currentLang()==='ja'?'地図から場所を選択':'Select places on map');
   mapHelp.textContent=phaseHint(kind);
   refreshSelectablePins();
 }
 selectOnMap.addEventListener('click',()=>setPicking(picking?null:!startSelect.value?'start':!finishSelect.value?'end':'stop'));
 function changeSite(kind,site){
   if(!site)return;
   if(kind==='stop'){
     if(!stops.includes(site.id)&&site.id!==startSelect.value&&site.id!==finishSelect.value){stops.push(site.id);renderStops();wipe();setPicking(null);setStatus(text().pickStop)}
     return;
   }
   const select=kind==='start'?startSelect:finishSelect;
   const control=kind==='start'?fromBox:toBox;
   select.value=site.id;control.input.value=site.name;control.menu.hidden=true;control.input.setAttribute('aria-expanded','false');
   // The same destination cannot simultaneously be an intermediate stop.
   stops=stops.filter(id=>id!==site.id);renderStops();wipe();
   if(kind==='start'){setPicking('end');setStatus(phaseHint('end'))} else {setPicking(null);setStatus(text().pickEnd)}
 }
 function updateMenu(box,selector,mode){
   const query=fold(box.input.value),matches=eligibleSites().filter(s=>!query||fold(s.name).includes(query)).slice(0,7);
   box.menu.replaceChildren();
   if(!matches.length)box.menu.append(make('p','vxr-no-match',text().noMatches));
   matches.forEach(s=>{const b=make('button','vxr-suggestion',(s.icon||'📍')+' '+s.name+' · '+text().region);b.type='button';b.setAttribute('role','option');b.addEventListener('pointerdown',e=>e.preventDefault());b.addEventListener('click',()=>{if(mode==='stop'){stopChooser.value=s.id;box.input.value=s.name;box.menu.hidden=true;addButton.disabled=false}else changeSite(mode,s)});box.menu.append(b)});
   box.menu.hidden=false;box.input.setAttribute('aria-expanded','true');
 }
 function closeMenu(box){box.menu.hidden=true;box.input.setAttribute('aria-expanded','false')}
 function attachSearch(box,select,mode){
   box.input.addEventListener('focus',()=>updateMenu(box,select,mode));
   box.input.addEventListener('input',()=>{if(mode==='start'||mode==='end'){select.value='';wipe()}else stopChooser.value='';updateMenu(box,select,mode)});
   box.input.addEventListener('keydown',ev=>{
     if(ev.key==='Escape'){closeMenu(box);return}
     if(ev.key==='Enter'){
       const first=box.menu.querySelector('button');if(first){ev.preventDefault();first.click();box.input.blur();closeMenu(box)}
     }
   });
   box.input.addEventListener('blur',()=>setTimeout(()=>closeMenu(box),120));
 }
 attachSearch(fromBox,startSelect,'start');attachSearch(toBox,finishSelect,'end');attachSearch(stopBox,stopChooser,'stop');
 swapBtn.addEventListener('click',()=>{const a=getSite(startSelect.value),b=getSite(finishSelect.value);startSelect.value=b?.id||'';finishSelect.value=a?.id||'';fromBox.input.value=b?.name||'';toBox.input.value=a?.name||'';renderStops();wipe()});
 // Capture clicks before destination-guide handlers consume them.
 ROOT.addEventListener('click',event=>{
   if(!graph||!picking)return;
   const marker=event.target.closest?.('.vxa-marker');if(!marker)return;
   const name=marker.getAttribute('aria-label')||marker.title||marker.querySelector('.vxa-marker-label')?.textContent||'';
   const matching=eligibleSites().filter(s=>fold(s.name)===fold(name));
   event.preventDefault();event.stopImmediatePropagation();
   if(!matching.length){setStatus(text().outside,true);return;}
   changeSite(picking,matching[0]);
 },true);
 function renderStops(){stopsList.replaceChildren();for(let i=0;i<stops.length;i++){
   const s=getSite(stops[i]);if(!s)continue;
   const row=make('div','vxr-stop'),name=make('span','',(i+1)+'. '+s.name),controls=make('span','vxr-stop-actions');
   const up=make('button','vxr-mini','↑'),down=make('button','vxr-mini','↓'),remove=make('button','vxr-mini',text().remove);
   up.type=down.type=remove.type='button';up.disabled=i===0;down.disabled=i===stops.length-1;
   up.addEventListener('click',()=>{[stops[i-1],stops[i]]=[stops[i],stops[i-1]];renderStops();wipe()});
   down.addEventListener('click',()=>{[stops[i+1],stops[i]]=[stops[i],stops[i+1]];renderStops();wipe()});
   remove.addEventListener('click',()=>{stops.splice(i,1);renderStops();wipe()});controls.append(up,down,remove);row.append(name,controls);stopsList.append(row);
  }
  const previous=stopChooser.value;optionList(stopChooser,[startSelect.value,finishSelect.value,...stops]);if(getSite(previous))stopChooser.value=previous;
  addButton.disabled=!stopChooser.value || !getSite(stopChooser.value);
 }
 function heapPush(heap,item){heap.push(item);let i=heap.length-1;while(i>0){let p=(i-1)>>1;if(heap[p][0]<=item[0])break;heap[i]=heap[p];i=p;}heap[i]=item;}
 function heapPop(heap){let first=heap[0],last=heap.pop();if(heap.length){let i=0;while(true){let a=i*2+1;if(a>=heap.length)break;let b=a+1,c=b<heap.length&&heap[b][0]<heap[a][0]?b:a;if(heap[c][0]>=last[0])break;heap[i]=heap[c];i=c;}heap[i]=last;}return first;}
 function dijkstra(begin,end){
   const edges=graph.edges,n=edges.length,dist=new Float64Array(n),prev=new Int32Array(n);dist.fill(Infinity);prev.fill(-1);dist[begin]=0;
   const heap=[];heapPush(heap,[0,begin]);let explored=0;
   while(heap.length){const [d,u]=heapPop(heap);if(d>dist[u]+1e-9)continue;explored++;if(u===end){let path=[];for(let k=end;k!==-1;k=prev[k]){path.push(k);if(k===begin)break;}path.reverse();return {km:d,path,explored};}
    for(const [v,w] of edges[u]){let alt=d+w;if(alt<dist[v]-1e-9){dist[v]=alt;prev[v]=u;heapPush(heap,[alt,v]);}}
   }
   throw new Error(text().none);
 }
 function distApprox(a,b){const lat1=a[1]*Math.PI/180,lat2=b[1]*Math.PI/180,dlat=lat2-lat1,dlon=(b[0]-a[0])*Math.PI/180,h=Math.sin(dlat/2)**2+Math.cos(lat1)*Math.cos(lat2)*Math.sin(dlon/2)**2;return 12742.0176*Math.asin(Math.min(1,Math.sqrt(h)));}
 // Draw geographic polylines in a transparent SVG inside the MapLibre container.
 // This does not depend on the basemap style-loading lifecycle or layer IDs.
 const NS='http://www.w3.org/2000/svg';
 function svgEl(tag){return document.createElementNS(NS,tag);}
 function clearOverlay(){if(routeSvg){routeSvg.remove();routeSvg=null;}routeNeedsFrame=false;}
 function clearSummary(){if(summaryBadge){summaryBadge.remove();summaryBadge=null;}}

 function refreshOverlay(){
   if(!activeRoute||!routeSvg)return;
   const map=window.__vx_attraction_map,container=map?.getContainer?.();
   if(!map||!container||!map.project)throw Error('Map projection is unavailable');
   const w=container.clientWidth,h=container.clientHeight;
   if(!w||!h)return;
   routeSvg.setAttribute('viewBox',`0 0 ${w} ${h}`);
   const projected=activeRoute.coordinates.map(p=>map.project(p));
   if(projected.some(p=>!Number.isFinite(p.x)||!Number.isFinite(p.y)))throw Error('Invalid projected road coordinates');
   const line=projected.map((p,i)=>`${i?'L':'M'}${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ');
   routeSvg.querySelector('.vxr-route-halo').setAttribute('d',line);
   routeSvg.querySelector('.vxr-route-line').setAttribute('d',line);
   const markers=routeSvg.querySelector('.vxr-route-stops');markers.replaceChildren();
   activeRoute.sites.forEach((site,i)=>{
     const p=map.project(site.at);
     const halo=svgEl('circle');halo.setAttribute('cx',p.x);halo.setAttribute('cy',p.y);halo.setAttribute('r','13');halo.setAttribute('fill','#fff');markers.append(halo);
     const c=svgEl('circle');c.setAttribute('cx',p.x);c.setAttribute('cy',p.y);c.setAttribute('r','10');c.setAttribute('fill','#da7a20');markers.append(c);
     const label=svgEl('text');label.setAttribute('x',p.x);label.setAttribute('y',p.y+4);label.setAttribute('fill','#fff');label.setAttribute('font-size','12');label.setAttribute('font-family','sans-serif');label.setAttribute('font-weight','bold');label.setAttribute('text-anchor','middle');label.textContent=String(i+1);markers.append(label);
   });
 }
 function scheduleRefresh(){
   if(routeNeedsFrame||!routeSvg)return;
   routeNeedsFrame=true;
   requestAnimationFrame(()=>{routeNeedsFrame=false;if(!routeSvg)return;try{refreshOverlay()}catch(err){setStatus('Route display error: '+err.message,true);console.error('[Veracruz routing SVG]',err)}});
 }
 function renderOverlay(){
   const map=window.__vx_attraction_map,container=map?.getContainer?.();
   if(!map||!container||!map.project)throw Error('Cannot draw a route: MapLibre map projection is unavailable.');
   if(!activeRoute||activeRoute.coordinates.length<2)throw Error('Not enough road points to draw a route.');
   clearOverlay();
   const svg=svgEl('svg');svg.setAttribute('aria-hidden','true');svg.setAttribute('class','vxr-geographic-overlay');
   Object.assign(svg.style,{position:'absolute',inset:'0',width:'100%',height:'100%',pointerEvents:'none',overflow:'hidden',zIndex:'12'});
   const halo=svgEl('path');halo.setAttribute('class','vxr-route-halo');halo.setAttribute('fill','none');halo.setAttribute('stroke','#ffffff');halo.setAttribute('stroke-width','9');halo.setAttribute('stroke-linecap','round');halo.setAttribute('stroke-linejoin','round');
   const line=svgEl('path');line.setAttribute('class','vxr-route-line');line.setAttribute('fill','none');line.setAttribute('stroke','#1757d2');line.setAttribute('stroke-width','5');line.setAttribute('stroke-linecap','round');line.setAttribute('stroke-linejoin','round');
   const markers=svgEl('g');markers.setAttribute('class','vxr-route-stops');svg.append(halo,line,markers);container.append(svg);routeSvg=svg;
   if(!routeEventsAdded){
     for(const event of ['move','zoom','resize','rotate','pitch'])map.on(event,scheduleRefresh);
     routeEventsAdded=true;
   }
   refreshOverlay();
 }
 function wipe(){activeRoute=null;clearOverlay();clearSummary();results.replaceChildren();nearby.replaceChildren();setStatus(text().ready);}
 function renderSuggestions(routeSites,points){nearby.replaceChildren();let chosen=new Set(routeSites.map(s=>s.id)),mid=points.filter((_,i)=>i%Math.max(1,Math.floor(points.length/300))===0);
   const candidates=eligibleSites().filter(s=>!chosen.has(s.id)).map(s=>({s,d:Math.min(...mid.map(p=>distApprox(s.at,p)))})).filter(x=>x.d<=6).sort((a,b)=>a.d-b.d).slice(0,6);
   if(!candidates.length)return;
   nearby.append(make('h4','',text().near));
   candidates.forEach(({s,d})=>{const line=make('div','vxr-near-row');line.append(make('span','',s.name+' · '+d.toFixed(1)+' km'));const btn=make('button','vxr-mini',text().plus);btn.type='button';btn.addEventListener('click',()=>{stops.push(s.id);renderStops();wipe();});line.append(btn);nearby.append(line);});
 }
 function calculate(){if(!graph)return;if(!startSelect.value||!finishSelect.value){setStatus(text().noChoice,true);return;}const ids=[startSelect.value,...stops,finishSelect.value];if(new Set(ids).size!==ids.length){setStatus(text().same,true);return;}
   const sites=ids.map(id=>eligibleSites().find(s=>s.id===id));if(sites.some(s=>!s)){setStatus(text().same,true);return;}
   setStatus(text().processing);try{let sum=0,explored=0,path=[];
    for(let i=0;i<sites.length-1;i++){let r=dijkstra(sites[i].node,sites[i+1].node);sum+=r.km;explored+=r.explored;path.push(...(i?r.path.slice(1):r.path));}
    const coordinates=path.map(idx=>graph.positions[idx]);
    if(coordinates.length<2||new Set(coordinates.map(p=>p.join(","))).size<2)throw Error("These attractions connect to the same road node; select a different pair.");
    activeRoute={coordinates,sites};renderOverlay();
    const map=window.__vx_attraction_map;if(map){let west=Infinity,east=-Infinity,south=Infinity,north=-Infinity;for(const [lon,lat] of coordinates){west=Math.min(west,lon);east=Math.max(east,lon);south=Math.min(south,lat);north=Math.max(north,lat);}if(Number.isFinite(west)){map.fitBounds([[west,south],[east,north]],{padding:70,maxZoom:13,duration:500});}}
    results.replaceChildren();const strong=make('strong','vxr-distance',text().result+': '+sum.toFixed(2)+' '+text().distance);
    results.append(strong,make('p','vxr-note',text().compare+' '+text().snap));
    setStatus(text().result+': '+sum.toFixed(2)+' '+text().distance);
    clearSummary();const target=ROOT.querySelector('#vx-map');if(target){summaryBadge=make('div','vxr-map-summary');summaryBadge.append(make('strong','',sum.toFixed(2)+' km'),make('small','',currentLang()==='es'?'Solo distancia · sin estimación de tiempo':currentLang()==='ja'?'距離のみ・所要時間未計算':'Distance only · no travel-time estimate'));target.append(summaryBadge)}
    results.scrollIntoView?.({block:'nearest',behavior:'smooth'});renderSuggestions(sites,coordinates);
   }catch(err){console.error('[Veracruz Dijkstra]',err);activeRoute=null;clearOverlay();clearSummary();setStatus(err.message,true);}
 }
 addButton.addEventListener('click',()=>{if(stopChooser.value&&!stops.includes(stopChooser.value)&&!([startSelect.value,finishSelect.value].includes(stopChooser.value))){stops.push(stopChooser.value);stopChooser.value='';stopBox.input.value='';renderStops();wipe();}});
 clearButton.addEventListener('click',()=>{stops=[];startSelect.value='';finishSelect.value='';fromBox.input.value='';toBox.input.value='';stopChooser.value='';stopBox.input.value='';renderStops();wipe();setPicking(null);});runButton.addEventListener('click',calculate);
 
 async function initialize(){
   try{
    const resp=await fetch('data/routes/xalapa_network.json',{cache:'no-store'});if(!resp.ok)throw Error('HTTP '+resp.status);
    const data=await resp.json();if(data.version!==1||!Array.isArray(data.positions)||!Array.isArray(data.edges)||data.positions.length!==data.edges.length||!Array.isArray(data.sites)||data.sites.length<2)throw Error('Invalid regional road graph');
    graph=data;optionList(startSelect);optionList(finishSelect);renderStops();setPicking(null);
    fields.hidden=false;stopsHeader.hidden=false;stopsList.hidden=false;addRow.hidden=false;actions.hidden=false;pickButtons.hidden=false;swapBtn.hidden=false;
    setStatus(text().ready);note.textContent=text().limited+' · '+graph.sites.length+' '+text().available+'. '+text().compare;
    mapHelp.textContent=phaseHint(null);
    // Route overlay is independent of MapLibre's style.load lifecycle.
   }catch(err){console.warn('[Veracruz route graph]',err);setStatus(text().wait+' '+text().error,true);}
 }
 initialize();
})();
