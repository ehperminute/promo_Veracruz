/* Veracruz route planner: regional static road graph, browser Dijkstra, no routing API. */
(() => {
 'use strict';
 const ROOT=document.getElementById('veracruz-map-section');
 if(!ROOT)return;
 const TXT={
  en:{title:'Plan a route',region:'Xalapa · Coatepec · Xico',from:'Start at',to:'Finish at',stops:'Stops (optional)',add:'Add stop',remove:'Remove',run:'Find shortest road route',ready:'Choose two attractions and calculate a route.',loading:'Loading regional road network…',wait:'Preparing regional routing data. The map explorer still works.',error:'Routing data could not be loaded.',same:'Choose different starting and ending attractions.',none:'No drivable path between these points in the current road graph.',result:'Shortest road distance',distance:'km',snap:'Site access is not verified. Snapping to roads may add walking/driving distance.',limited:'Currently available in the Xalapa–Coatepec–Xico region; more areas will follow.',compare:'Approximate road distance, not travel time or driving instructions.',processing:'Calculating route…',available:'attractions available',near:'Nearby optional stops (straight-line proximity only)',plus:'Add',noNear:'No other mapped attractions nearby.',clear:'Clear route'},
  es:{title:'Planear ruta',region:'Xalapa · Coatepec · Xico',from:'Salida',to:'Llegada',stops:'Paradas (opcionales)',add:'Agregar parada',remove:'Quitar',run:'Calcular ruta más corta',ready:'Elige dos atractivos para calcular la ruta.',loading:'Cargando la red vial regional…',wait:'Preparando los datos de rutas. El explorador sigue disponible.',error:'No se pudieron cargar los datos de rutas.',same:'Elige atractivos distintos para salir y llegar.',none:'No se encontró ruta transitable entre estos puntos en la red disponible.',result:'Distancia vial más corta',distance:'km',snap:'Los accesos a los atractivos no están verificados. Puede haber distancia adicional hasta la entrada.',limited:'Disponible por ahora para Xalapa–Coatepec–Xico; después se ampliará.',compare:'Distancia vial aproximada, no tiempo de viaje ni indicaciones de manejo.',processing:'Calculando ruta…',available:'atractivos disponibles',near:'Paradas opcionales cercanas (proximidad en línea recta)',plus:'Agregar',noNear:'No hay otros atractivos cartografiados cerca.',clear:'Limpiar ruta'},
  ja:{title:'ルートを計画',region:'ハラパ・コアテペック・ヒコ',from:'出発地',to:'目的地',stops:'立ち寄り先（任意）',add:'経由地を追加',remove:'削除',run:'最短道路経路を検索',ready:'出発地と目的地を選んでください。',loading:'地域の道路網を読み込み中…',wait:'ルート情報を準備しています。地図は利用できます。',error:'道路データを読み込めませんでした。',same:'異なる出発地と目的地を選んでください。',none:'利用可能な道路データでは経路が見つかりません。',result:'最短道路距離',distance:'km',snap:'観光地の車両入口は未確認です。道路から追加の移動が必要な場合があります。',limited:'現在はハラパ・コアテペック・ヒコ地域で利用可能です。',compare:'概算の道路距離です。所要時間や運転案内ではありません。',processing:'経路を計算中…',available:'件の観光地',near:'近くの候補地（直線距離の目安）',plus:'追加',noNear:'近くに他の場所がありません。',clear:'ルートを消去'}
 };
 const currentLang=()=>{let x=(document.documentElement.lang||'en').slice(0,2);return TXT[x]?x:'en'};
 const text=()=>TXT[currentLang()];
 const make=(tag,cls,txt)=>{let e=document.createElement(tag);if(cls)e.className=cls;if(txt!==undefined)e.textContent=txt;return e};
 const panel=make('section','vxr-panel');panel.id='vx-route-planner';
 const head=make('div','vxr-heading'),heading=make('h3','',text().title),tag=make('small','',text().region);
 head.append(heading,tag);panel.append(head);
 const message=make('p','vxr-message',text().loading);panel.append(message);
 const fields=make('div','vxr-fields'),fromLabel=make('label','',text().from),toLabel=make('label','',text().to);
 const startSelect=make('select','vxr-select'),finishSelect=make('select','vxr-select');startSelect.setAttribute('aria-label',text().from);finishSelect.setAttribute('aria-label',text().to);
 fromLabel.append(startSelect);toLabel.append(finishSelect);fields.append(fromLabel,toLabel);panel.append(fields);
 const stopsHeader=make('p','vxr-subheading',text().stops),stopsList=make('div','vxr-stops'),stopChooser=make('select','vxr-select'),addButton=make('button','vxr-secondary',text().add);
 addButton.type='button';const addRow=make('div','vxr-add');addRow.append(stopChooser,addButton);
 panel.append(stopsHeader,stopsList,addRow);
 const actions=make('div','vxr-actions'),runButton=make('button','vxr-primary',text().run),clearButton=make('button','vxr-secondary',text().clear);
 runButton.type='button';clearButton.type='button';actions.append(runButton,clearButton);panel.append(actions);
 const results=make('section','vxr-results');results.setAttribute('aria-live','polite');panel.append(results);
 const nearby=make('section','vxr-nearby');panel.append(nearby);
 const note=make('p','vxr-note',text().limited+' '+text().compare);panel.append(note);
 const side=ROOT.querySelector('.vx-side');if(!side)return;
 const anchor=ROOT.querySelector('#vx-status');if(anchor)anchor.insertAdjacentElement('afterend',panel);else side.prepend(panel);
 let graph=null,stops=[],layer=null,activeRoute=null;
 fields.hidden=true;stopsHeader.hidden=true;stopsList.hidden=true;addRow.hidden=true;actions.hidden=true;
 function setStatus(s,bad=false){message.textContent=s;message.classList.toggle('vxr-error',bad)}
 function eligibleSites(){return graph?.sites||[]}
 function optionList(sel,exclude=[]){sel.replaceChildren();eligibleSites().forEach(s=>{const o=make('option','',s.icon+' '+s.name);o.value=s.id;o.disabled=exclude.includes(s.id);sel.append(o)})}
 function renderStops(){stopsList.replaceChildren();for(let i=0;i<stops.length;i++){
   const s=eligibleSites().find(x=>x.id===stops[i]);if(!s)continue;
   const row=make('div','vxr-stop'),name=make('span','',(i+1)+'. '+s.name),remove=make('button','vxr-mini',text().remove);remove.type='button';remove.addEventListener('click',()=>{stops.splice(i,1);renderStops();});row.append(name,remove);stopsList.append(row);
  }
  optionList(stopChooser,[startSelect.value,finishSelect.value,...stops]);
  const first=[...stopChooser.options].find(o=>!o.disabled);if(first)stopChooser.value=first.value;
  addButton.disabled=!first;}
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
 function renderOverlay(){const map=window.__vx_attraction_map;if(!map||!activeRoute)return;
   try{
    const id='vx-browser-route';const data={type:'FeatureCollection',features:[{type:'Feature',properties:{kind:'route'},geometry:{type:'LineString',coordinates:activeRoute.coordinates}},...activeRoute.sites.map((s,i)=>({type:'Feature',properties:{kind:'stop',index:String(i+1)},geometry:{type:'Point',coordinates:s.at}}))]};
    if(map.getSource(id)){map.getSource(id).setData(data);return;}
    map.addSource(id,{type:'geojson',data});
    map.addLayer({id:id+'-line',type:'line',source:id,filter:['==',['get','kind'],'route'],paint:{'line-color':'#2563a6','line-width':5,'line-opacity':0.92}});
    map.addLayer({id:id+'-points',type:'circle',source:id,filter:['==',['get','kind'],'stop'],paint:{'circle-color':'#e38a2c','circle-radius':10,'circle-stroke-color':'#fff','circle-stroke-width':3}});
    map.addLayer({id:id+'-labels',type:'symbol',source:id,filter:['==',['get','kind'],'stop'],layout:{'text-field':['get','index'],'text-size':12,'text-allow-overlap':true},paint:{'text-color':'#12293a'}});
   }catch(err){console.warn('[Veracruz route overlay]',err);setStatus('Route computed, but map drawing failed: '+err.message,true)}
 }
 function wipe(){activeRoute=null;results.replaceChildren();nearby.replaceChildren();try{const m=window.__vx_attraction_map;if(m?.getSource('vx-browser-route'))m.getSource('vx-browser-route').setData({type:'FeatureCollection',features:[]})}catch(_e){}setStatus(text().ready);}
 function renderSuggestions(routeSites,points){nearby.replaceChildren();let chosen=new Set(routeSites.map(s=>s.id)),mid=points.filter((_,i)=>i%Math.max(1,Math.floor(points.length/300))===0);
   const candidates=eligibleSites().filter(s=>!chosen.has(s.id)).map(s=>({s,d:Math.min(...mid.map(p=>distApprox(s.at,p)))})).filter(x=>x.d<=6).sort((a,b)=>a.d-b.d).slice(0,6);
   if(!candidates.length)return;
   nearby.append(make('h4','',text().near));
   candidates.forEach(({s,d})=>{const line=make('div','vxr-near-row');line.append(make('span','',s.name+' · '+d.toFixed(1)+' km'));const btn=make('button','vxr-mini',text().plus);btn.type='button';btn.addEventListener('click',()=>{stops.push(s.id);renderStops();wipe();});line.append(btn);nearby.append(line);});
 }
 function calculate(){if(!graph)return;const ids=[startSelect.value,...stops,finishSelect.value];if(new Set(ids).size!==ids.length){setStatus(text().same,true);return;}
   const sites=ids.map(id=>eligibleSites().find(s=>s.id===id));if(sites.some(s=>!s)){setStatus(text().same,true);return;}
   setStatus(text().processing);try{let sum=0,explored=0,path=[];
    for(let i=0;i<sites.length-1;i++){let r=dijkstra(sites[i].node,sites[i+1].node);sum+=r.km;explored+=r.explored;path.push(...(i?r.path.slice(1):r.path));}
    const coordinates=path.map(idx=>graph.positions[idx]);activeRoute={coordinates,sites};renderOverlay();
    const map=window.__vx_attraction_map;if(map){let west=Infinity,east=-Infinity,south=Infinity,north=-Infinity;for(const [lon,lat] of coordinates){west=Math.min(west,lon);east=Math.max(east,lon);south=Math.min(south,lat);north=Math.max(north,lat);}if(Number.isFinite(west)){map.fitBounds([[west,south],[east,north]],{padding:70,maxZoom:13,duration:500});}}
    results.replaceChildren();const strong=make('strong','',text().result+': '+sum.toFixed(2)+' '+text().distance);results.append(strong,make('p','vxr-note',text().snap));setStatus(text().ready);renderSuggestions(sites,coordinates);
   }catch(err){console.error('[Veracruz Dijkstra]',err);setStatus(err.message,true);}
 }
 addButton.addEventListener('click',()=>{if(stopChooser.value&&!stops.includes(stopChooser.value)&&!([startSelect.value,finishSelect.value].includes(stopChooser.value))){stops.push(stopChooser.value);renderStops();wipe();}});
 clearButton.addEventListener('click',()=>{stops=[];renderStops();wipe();});runButton.addEventListener('click',calculate);
 startSelect.addEventListener('change',()=>{renderStops();wipe()});finishSelect.addEventListener('change',()=>{renderStops();wipe()});
 async function initialize(){
   try{
    const resp=await fetch('data/routes/xalapa_network.json',{cache:'no-store'});if(!resp.ok)throw Error('HTTP '+resp.status);
    const data=await resp.json();if(data.version!==1||!Array.isArray(data.positions)||!Array.isArray(data.edges)||data.positions.length!==data.edges.length||!Array.isArray(data.sites)||data.sites.length<2)throw Error('Invalid regional road graph');
    graph=data;optionList(startSelect);optionList(finishSelect);if(graph.sites.length>1)finishSelect.value=graph.sites[1].id;renderStops();
    fields.hidden=false;stopsHeader.hidden=false;stopsList.hidden=false;addRow.hidden=false;actions.hidden=false;
    setStatus(text().ready);note.textContent=text().limited+' · '+graph.sites.length+' '+text().available+'. '+text().compare;
    const map=window.__vx_attraction_map;if(map){map.on('style.load',renderOverlay)}
   }catch(err){console.warn('[Veracruz route graph]',err);setStatus(text().wait+' '+text().error,true);}
 }
 initialize();
})();
