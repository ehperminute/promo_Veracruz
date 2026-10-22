/* Preference-led evidence explorer. No model estimates tourist tastes or prices.
   Optimization: bounded enumeration of municipality combinations with explicit
   constraints (selected interests, stop cap, assumed spending allowance, radius).
   Candidate pruning means this is a bounded optimizer, not a statewide exact MILP. */
(() => {
 'use strict';
 const novelty=window.VXDiscoveryScore;
 if(!novelty){console.error('[Veracruz discovery] novelty scoring missing');return;}
 const panel=document.getElementById('vxw-itinerary');
 if(!panel || document.getElementById('vxi-panel')) return;
 const tr={
 en:{title:'Find a trip that fits your interests',note:'Suggestions use documented municipality–activity links, not predicted personal tastes or verified bookings.',choices:'Interests',amount:'Planning budget (MXN)',allowance:'Assumed activity allowance per stop (MXN)',travel:'Assumed transport allowance (MXN)',radius:'Approx. search radius (km)',stops:'Suggested destinations',suggest:'Suggest stops',surprise:'Surprise me · distinctive places',why:'Why this?',rare:'Documented in {n} municipalities of our activity catalog',rareOne:'Documented in one municipality of our activity catalog',novelty:'Source-backed, less-obvious experiences—not verified low visitor numbers.',estimate:'Next: check published prices and unknown expenses below. This allowance is only a screening assumption.',use:'Use these stops in my route',no:'No documented matches under these constraints. Increase the radius or budget, or try another interest.',loading:'Loading documented activities…',ready:'Available: 216 activity links in 61 municipalities (78 specific activity types).',error:'Could not load verified research data.',budget:'Illustrative planning assumptions only. NOT a trip price: hotels, meals, entry fees, guide prices, road fuel costs and availability are unverified.',score:'Evidence-supported interests',all:'Any activity',clear:'Clear interests',sources:'Source',matched:'Documented here',origin:'Origin',originHint:'Uses your route’s first stop, otherwise Xalapa (approximate municipality reference).',apply:'Stops added. Calculate the road route separately.',cap:'No suggestion fits the assumed spending envelope.',unknown:'Recorded experience ≠ current availability.'},
 es:{title:'Descubre destinos según tus intereses',note:'Sugerencias basadas en vínculos documentados entre municipios y actividades; no son predicciones de gustos ni reservas confirmadas.',choices:'Intereses',amount:'Presupuesto de planeación (MXN)',allowance:'Gasto supuesto en actividades por destino (MXN)',travel:'Monto supuesto para transporte (MXN)',radius:'Radio aprox. de búsqueda (km)',stops:'Destinos sugeridos',suggest:'Sugerir destinos',surprise:'Sorpréndeme · experiencias singulares',why:'¿Por qué este lugar?',rare:'Documentada en {n} municipios de nuestro catálogo de actividades',rareOne:'Documentada en un municipio de nuestro catálogo de actividades',novelty:'Experiencias singulares con fuentes; no significa que reciban pocos visitantes.',estimate:'Después, revisa tarifas publicadas y costos pendientes. Este presupuesto es solo un supuesto para filtrar.',use:'Usar destinos en mi ruta',no:'Sin coincidencias documentadas con estos límites. Amplía el radio o presupuesto o cambia de interés.',loading:'Cargando actividades documentadas…',ready:'Disponibles: 216 vínculos de actividad en 61 municipios (78 actividades específicas).',error:'No se pudieron cargar los datos de investigación.',budget:'Supuestos ilustrativos del usuario. NO es precio de viaje: hospedaje, alimentos, accesos, guías, gasolina real y disponibilidad no están verificados.',score:'Intereses respaldados',all:'Cualquier actividad',clear:'Borrar intereses',sources:'Fuente',matched:'Documentado aquí',origin:'Origen',originHint:'Toma la primera parada de tu ruta; de lo contrario, Xalapa (referencia municipal aproximada).',apply:'Paradas agregadas. Calcula la ruta vial por separado.',cap:'No hay opciones para los gastos supuestos.',unknown:'Actividad documentada ≠ disponibilidad actual.'},
 ja:{title:'興味に合う行き先を探す',note:'資料に記録された体験に基づく候補です。好みの予測や予約可否ではありません。',choices:'興味',amount:'計画予算（MXN）',allowance:'一地点あたりの仮の体験予算（MXN）',travel:'仮の交通費（MXN）',radius:'検索半径の目安（km）',stops:'候補地',suggest:'候補を探す',surprise:'おまかせ・特色ある場所',why:'おすすめの理由',rare:'当カタログ内の{n}自治体で記録',rareOne:'当カタログ内の1自治体で記録',novelty:'資料上の特色ある体験。実際の訪問者数を示すものではありません。',estimate:'次に掲載料金と未確定費用をご確認ください。ここでの予算は仮定です。',use:'ルートに追加',no:'条件に合う記録がありません。半径・予算を変更してください。',loading:'資料を読み込み中…',ready:'61自治体・78種類の活動に216件の記録があります。',error:'資料を読み込めませんでした。',budget:'すべて仮定に基づく計画額です。宿泊・食事・入場料・実際の交通費・予約状況は含みません。',score:'関連する活動',all:'すべて',clear:'興味を消去',sources:'出典',matched:'関連活動',origin:'出発地',originHint:'既存の最初の地点、それ以外はハラパ市を使用します（概略位置）。',apply:'ルートに追加しました。道路ルートは別途計算してください。',cap:'想定予算では候補がありません。',unknown:'資料上の活動は現在の営業を保証しません。'}};
 const families={en:{land_adventure:'Hiking & land adventure',water_adventure:'Water sports',nature_observation:'Wildlife & nature',history_culture:'History & culture',food_agriculture:'Coffee & food',wellness_spiritual:'Wellness',traditional_crafts:'Crafts',scenic_transport:'Scenic transport',other_specific_unclassified:'Other specific activities'},es:{land_adventure:'Aventura terrestre',water_adventure:'Actividades acuáticas',nature_observation:'Naturaleza y fauna',history_culture:'Historia y cultura',food_agriculture:'Café y gastronomía',wellness_spiritual:'Bienestar',traditional_crafts:'Artesanías',scenic_transport:'Recorridos panorámicos',other_specific_unclassified:'Otras actividades específicas'},ja:{land_adventure:'陸上アドベンチャー',water_adventure:'水上体験',nature_observation:'自然観察',history_culture:'歴史と文化',food_agriculture:'コーヒーと食',wellness_spiritual:'ウェルネス',traditional_crafts:'伝統工芸',scenic_transport:'景観交通',other_specific_unclassified:'その他の体験'}};
 const lang=()=>document.getElementById('language-select')?.value||'en';
 const tt=()=>tr[lang()]||tr.en;
 const el=(tag,cls,content)=>{const x=document.createElement(tag);if(cls)x.className=cls;if(content!==undefined)x.textContent=content;return x;};
 const root=el('details','vxi');root.id='vxi-panel';
 const trigger=el('summary','vxi-trigger','Find destinations by interests · Surprise me / Por intereses');root.append(trigger);
 const title=el('h4'),lead=el('p','vxi-note');root.append(title,lead);const flow=el('p','vxi-flow');root.append(flow);
 const familyLabel=el('p','vxi-note');root.append(familyLabel);
 const familyBar=el('div','vxi-families');root.append(familyBar);
 const detailSearch=el('input');detailSearch.type='search';detailSearch.placeholder='Activity / actividad';detailSearch.setAttribute('aria-label','Search a specific activity / Buscar actividad concreta');
 const detailField=el('label','vxi-field');detailField.append(detailSearch);root.append(detailField);
 const detailList=el('div','vxi-families');root.append(detailList);
 const cost=el('div','vxi-budget-row');root.append(cost);
 function numberField(defaultValue,min,max){const label=el('label','vxi-field');const span=el('span');const input=el('input');input.type='number';input.min=String(min);input.max=String(max);input.step='50';input.value=String(defaultValue);label.append(span,input);cost.append(label);return {span,input};}
 const budget=numberField(3000,100,100000),perStop=numberField(500,0,20000),transport=numberField(650,0,20000);
 const radius=numberField(250,30,1500);const count=numberField(3,1,3);
 const actions=el('div','vxi-buttons'),suggest=el('button','vxi-run'),surprise=el('button','vxi-surprise');suggest.type=surprise.type='button';actions.append(suggest,surprise);root.append(actions);
 const state=el('p','vxi-status');state.setAttribute('role','status');state.textContent=tt().loading;root.append(state);
 const explain=el('p','vxi-note');root.append(explain);
 const results=el('div','vxi-results');root.append(results);
 const apply=el('button','vxi-apply');apply.type='button';apply.disabled=true;root.append(apply);
 panel.insertBefore(root,panel.querySelector('.vxw-search-wrap'));
 let records=[],groups=[],selectedFamilies=new Set(),selectedFeatures=new Set(),last=[],markers=[],ready=false,lastWasSurprise=false;
 const norm=s=>String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
 const label=(record)=>lang()==='es'?record.label_es:(record.label_en||record.label_es);
 const km=(a,b)=>{const lat1=a[1]*Math.PI/180,lat2=b[1]*Math.PI/180,dy=lat2-lat1,dx=(b[0]-a[0])*Math.PI/180;
   const z=Math.sin(dy/2)**2+Math.cos(lat1)*Math.cos(lat2)*Math.sin(dx/2)**2;return 12742*Math.asin(Math.min(1,Math.sqrt(z)));};
 const cleanNumber=(node,min,max)=>Math.max(min,Math.min(max,Number(node.value)||0));
 const btn=(text,active,onClick)=>{const b=el('button','vxi-chip',text);b.type='button';b.setAttribute('aria-pressed',String(active));b.addEventListener('click',onClick);return b;};
 function displayChoices(){familyBar.replaceChildren();for(const f of [...new Set(records.map(x=>x.family))].sort())familyBar.append(btn(families[lang()]?.[f]||f,selectedFamilies.has(f),()=>{selectedFamilies.has(f)?selectedFamilies.delete(f):selectedFamilies.add(f);displayChoices();}));
   detailList.replaceChildren();const query=norm(detailSearch.value).trim();if(query){const features=Array.from(new Map(records.map(r=>[r.feature_id,r])).values()).filter(r=>norm(r.label_es+' '+r.label_en+' '+r.feature_id).includes(query)).slice(0,8);
   for(const r of features)detailList.append(btn(label(r),selectedFeatures.has(r.feature_id),()=>{selectedFeatures.has(r.feature_id)?selectedFeatures.delete(r.feature_id):selectedFeatures.add(r.feature_id);displayChoices();}));}
   for(const id of selectedFeatures){const r=records.find(r=>r.feature_id===id);if(r&&!detailList.querySelector(`[data-feature="${id}"]`)){const b=btn('✓ '+label(r),true,()=>{selectedFeatures.delete(id);displayChoices();});b.dataset.feature=id;detailList.append(b);}}
 }
 function translate(){const t=tt();title.textContent=t.title;lead.textContent=t.note;familyLabel.textContent=t.choices;
   [[budget,t.amount],[perStop,t.allowance],[transport,t.travel],[radius,t.radius],[count,t.stops]].forEach(([f,v])=>f.span.textContent=v);
   suggest.textContent=t.suggest;surprise.textContent=t.surprise;apply.textContent=t.use;flow.textContent=t.estimate;explain.textContent=t.budget+' '+t.unknown+' '+t.novelty;displayChoices();if(last.length)renderResults(last);}
 function start(){const first=window.VeracruzItineraryV2?.getStops?.()?.[0];return first&&Array.isArray(first.coords)?first:{id:'municipality:30087',name:'Xalapa',coords:[-96.9215,19.5438]};}
 function candidates(){const by=new Map();for(const r of records){let c=by.get(r.municipality_id);if(!c){c={id:r.municipality_id,name:r.municipality,coords:r.coordinates,rows:[]};by.set(r.municipality_id,c);}c.rows.push(r);}return [...by.values()];}
 function scoreRow(r){return (selectedFeatures.has(r.feature_id)?10:0)+(selectedFamilies.has(r.family)?3:0);}
 function optimize(random=false){
   const o=start(),limRadius=cleanNumber(radius.input,30,1500),limit=cleanNumber(budget.input,100,100000),allowance=cleanNumber(perStop.input,0,20000),travelMoney=cleanNumber(transport.input,0,20000),maxStops=cleanNumber(count.input,1,3);
   const filtered=candidates().filter(c=>c.id!==o.id.replace('municipality:','')).map(c=>({...c,distance:km(o.coords,c.coords)})).filter(c=>c.distance<=limRadius);
   const wish=random?0:selectedFamilies.size+selectedFeatures.size;
   const frequency=novelty.frequency(records);
   let pool=filtered.filter(c=>random ? novelty.candidate(c,frequency)>-Infinity : (!wish||c.rows.some(r=>scoreRow(r)>0)));
   // Exploratory discovery searches *all* municipalities in the strict evidence matrix.
   // It rewards uncommon supported experiences, not missing data or claimed low crowds.
   if(random){pool.sort((a,b)=>(novelty.candidate(b,frequency)-novelty.candidate(a,frequency)) || a.distance-b.distance);
     // Broader shortlist than the old top-activity-count ranking; vary candidates without hiding the catalog.
     const take=pool.slice(0,Math.min(38,pool.length));for(let i=take.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[take[i],take[j]]=[take[j],take[i]];}pool=take.slice(0,24);
   }else{
     pool.sort((a,b)=>{const importance=c=>c.rows.reduce((v,r)=>v+scoreRow(r)+(r.original_text_support?0.4:0),0);
       return importance(b)-importance(a)||a.distance-b.distance||a.name.localeCompare(b.name);});pool=pool.slice(0,19);
   }
   if(!pool.length){last=[];state.textContent=tt().no;renderResults([]);return;}
   let best=null,bestScore=-Infinity;
   // Enumerate every unordered combination of 1..3 from the bounded candidate pool.
   function assess(chosen){const assumedCost=travelMoney+chosen.length*allowance;if(assumedCost>limit)return;
     const features=new Set(),familiesSeen=new Set(),matching=[];let textSupported=0;
     for(const c of chosen)for(const r of c.rows){features.add(r.feature_id);familiesSeen.add(r.family);if(scoreRow(r)>0)matching.push(r);if(r.original_text_support)textSupported++;}
     const relevant=new Set(matching.map(r=>r.feature_id)).size;
     const familyRelevant=new Set(matching.map(r=>r.family)).size;
     // Penalize geographic spread as *proximity*, never interpreted as driven kilometres.
     let spread=0,prev=o.coords;const ordered=[...chosen].sort((a,b)=>a.distance-b.distance);
     for(const c of ordered){spread+=km(prev,c.coords);prev=c.coords;}
     const total=wish?(relevant*15+familyRelevant*5):(features.size*3+familiesSeen.size*5);
     const s=random ? novelty.portfolio(ordered,frequency,spread) : total+Math.min(10,textSupported)*0.25-spread*0.006;
     if(s>bestScore){bestScore=s;best={chosen:ordered,matching:matching,assumedCost,approxSeparation:spread,origin:o,score:s};}
   }
   for(let i=0;i<pool.length;i++){
     assess([pool[i]]);
     if(maxStops>=2)for(let j=i+1;j<pool.length;j++){
       assess([pool[i],pool[j]]);
       if(maxStops>=3)for(let k=j+1;k<pool.length;k++)assess([pool[i],pool[j],pool[k]]);
     }
   }
   lastWasSurprise=random;
   last=best?[{...best,frequency}]:[];
   state.textContent=best?(random?tt().novelty:(wish?tt().score+': '+new Set(best.matching.map(x=>x.feature_id)).size:tt().matched+': '+new Set(best.chosen.flatMap(x=>x.rows.map(r=>r.feature_id))).size)):tt().cap;
   renderResults(last);
 }
 function renderResults(rs){results.replaceChildren();apply.disabled=!rs.length;for(const result of rs){
     const picked=result.chosen;
     const header=el('p','vxi-note',tt().origin+': '+result.origin.name+' · '+tt().budget.split('.')[0]+' — '+result.assumedCost.toLocaleString()+' MXN');results.append(header);
     for(const c of picked){const item=el('div','vxi-result');item.append(el('strong','',c.name));
       const hit=c.rows.filter(r=>selectedFeatures.size+selectedFamilies.size===0||scoreRow(r)>0);
       item.append(el('span','',tt().matched+': '+hit.map(label).slice(0,6).join(', ')));
       item.append(el('small','',`${c.distance.toFixed(0)} km straight-line from origin (not road distance)`));
       if(lastWasSurprise){const reasons=novelty.reasons(c,result.frequency);
         const evidence=el('div','vxi-reasons');evidence.append(el('strong','',tt().why));
         for(const r of reasons){const name=lang()==='es'?r.label_es:(r.label_en||r.label_es);
           evidence.append(el('span','',name+' — '+(r.municipalities===1?tt().rareOne:tt().rare.replace('{n}',String(r.municipalities)))));}
         item.append(evidence);
       }
       const source=hit.find(r=>r.source_urls.length);if(source){const a=el('a','',tt().sources+' ↗');a.href=source.source_urls[0];a.target='_blank';a.rel='noopener noreferrer';item.append(a);}results.append(item);
     }
   }}
 function updateMarkers(){const map=window.__vx_attraction_map;if(!map||!window.maplibregl)return;
   for(const m of markers)m.remove();markers=[];
   for(const [i,p] of (window.VeracruzItineraryV2?.getStops?.()||[]).entries()){
      if(!Array.isArray(p.coords)||p.coords.length!==2)continue;
      const node=el('div','vxi-map-pin',String(i+1));node.title=String(i+1)+'. '+p.name;
      node.style.cssText='background:#fcad39;color:#163329;border:2px solid #fff;box-shadow:0 0 0 2px #295842;border-radius:50%;width:26px;height:26px;display:grid;place-items:center;font-weight:800;font-size:12px;pointer-events:none;';
      try{const marker=new maplibregl.Marker({element:node,anchor:'bottom'}).setLngLat(p.coords).addTo(map);node.style.pointerEvents='none';markers.push(marker);}catch(e){console.warn('[Veracruz stop pin]',e);}
   }
 }
 apply.addEventListener('click',()=>{if(!last.length)return;const router=window.VeracruzItineraryV2;if(!router)return;
   router.clear();router.addStopById(last[0].origin.id);
   for(const c of last[0].chosen)router.addStopById('municipality:'+c.id);
   state.textContent=tt().apply;updateMarkers();root.open=false;panel.querySelector('.vxw-stops')?.scrollIntoView?.({block:'nearest',behavior:'smooth'});
 });
 suggest.addEventListener('click',()=>optimize(false));surprise.addEventListener('click',()=>{selectedFamilies.clear();selectedFeatures.clear();displayChoices();optimize(true);});
 detailSearch.addEventListener('input',displayChoices);
 document.getElementById('language-select')?.addEventListener('change',translate);
 document.addEventListener('vxw:stops-changed',updateMarkers);
 translate();
 fetch('data/interest_evidence.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json();}).then(data=>{
   if(data.total_links!==216||data.records.length!==216)throw Error('Unexpected research data version');records=data.records;ready=true;state.textContent=tt().ready;displayChoices();updateMarkers();
 }).catch(e=>{state.textContent=tt().error+' '+e.message;console.error('[interest evidence]',e);});
})();
