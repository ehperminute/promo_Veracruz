/* Pricing UI: verified ledger provenance, conditional quotes, user-entered trip assumptions.
   No transactions, availability checks or fabricated routing distances. */
(() => {
'use strict';
const C=window.VeracruzPricingCore,router=window.VeracruzItineraryV2,panel=document.getElementById('vxw-itinerary');
if(!C||!router||!panel||document.getElementById('vxp-prices'))return;
const dictionary={
 en:{title:'Estimate trip costs · compare local providers',intro:'Choose offers for your itinerary. Published prices are not live quotes. Expenses without a price stay visible as unknown.',people:'Travelers',days:'Days',nights:'Nights',rooms:'Rooms',budget:'Your budget (MXN, optional)',heading:'Providers and admission fees near your stops',empty:'Add municipalities or attractions to see prices at your stops.',no:'No local prices in our checked ledger for',unverified:'Provider–activity match and current availability are NOT verified; check before reserving.',regional:'More published regional tours (reference only; not matched to stops)',regionalHelp:'These regional listings do not have a confirmed pickup or destination match; they cannot enter the subtotal.',source:'Source',published:'Selected advertised offers',assumptions:'User-entered estimates',subtotal:'Indicative subtotal · NOT a complete trip quote',missing:'Not yet priced',warning:'Conditions to check',km:'Road distance (km)',kmManual:'Manual road distance (km), if routing fails',consumption:'Fuel economy (km/L)',fuel:'Fuel price (MXN/L)',tolls:'Tolls for the itinerary (MXN)',food:'Meals/person/day (MXN)',lodging:'Room/night (MXN) if no published room rate chosen',other:'Other known expenses (MXN)',travel:'Transport and other costs',auto:'from calculated road route',manual:'you supplied',absent:'unknown · calculate a route or enter road kilometres',totalWarn:'A subtotal below your budget does not mean the trip fits it. Unpriced costs may remain.',over:'Selected and entered costs already exceed your budget.',recorded:'Published',estimated:'Estimated',from:'from',pending:'Reference price · unit unconfirmed',checked:'Price checked',copy:'Copy itemized estimate',copied:'Estimate copied',noOffers:'No selected services; activity costs are still unknown.',rates:'Source-linked offers found for',regionalTag:'Regional / package reference',raw:'Base quoted amount',tax:'Conditions',coverage:'Covered stops',notCovered:'Stops without local price listings',loading:'Loading published prices…',loadError:'Prices could not be loaded.',missingRoom:'No accommodation price selected',hint:'Do not add a package and its included components twice; confirm group minimums and tax.',money:'MXN'},
 es:{title:'Estimar costos · comparar prestadores locales',intro:'Elige servicios para tu recorrido. Los precios publicados no son cotizaciones en tiempo real. Los gastos sin precio siguen como pendientes.',people:'Personas',days:'Días',nights:'Noches',rooms:'Habitaciones',budget:'Tu presupuesto (MXN, opcional)',heading:'Prestadores y entradas para tus paradas',empty:'Agrega municipios o atractivos para consultar precios por parada.',no:'Sin tarifas locales en nuestra lista para',unverified:'La relación prestador–actividad y la disponibilidad actual NO están verificadas; confirma antes de reservar.',regional:'Más recorridos regionales publicados (solo referencia)',regionalHelp:'No se ha verificado su punto de salida ni correspondencia con esta ruta; no se suman.',source:'Fuente',published:'Ofertas publicadas seleccionadas',assumptions:'Gastos estimados por ti',subtotal:'Subtotal orientativo · NO es cotización completa',missing:'Costos pendientes',warning:'Condiciones a confirmar',km:'Distancia vial (km)',kmManual:'Distancia vial manual (km) si falla el servicio',consumption:'Rendimiento (km/L)',fuel:'Precio gasolina (MXN/L)',tolls:'Casetas del recorrido (MXN)',food:'Comidas/persona/día (MXN)',lodging:'Habitación/noche (MXN) si no elegiste hotel publicado',other:'Otros gastos (MXN)',travel:'Transporte y otros gastos',auto:'de ruta vial calculada',manual:'dato ingresado por ti',absent:'desconocido · calcula la ruta o ingresa kilómetros viales',totalWarn:'Estar debajo del presupuesto NO garantiza que alcance: podrían faltar gastos.',over:'Los costos seleccionados ya rebasan tu presupuesto.',recorded:'Publicado',estimated:'Estimado',from:'desde',pending:'Referencia · unidad sin confirmar',checked:'Precio consultado',copy:'Copiar presupuesto desglosado',copied:'Presupuesto copiado',noOffers:'Sin servicios elegidos; aún se desconocen costos de actividades.',rates:'Ofertas con fuente para',regionalTag:'Recorrido regional / paquete',raw:'Tarifa anunciada',tax:'Condiciones',coverage:'Paradas con tarifas',notCovered:'Paradas sin tarifas locales',loading:'Cargando precios publicados…',loadError:'No se pudieron cargar los precios.',missingRoom:'Sin tarifa de hospedaje elegida',hint:'No sumes un paquete y sus servicios incluidos dos veces; confirma mínimos y impuestos.',money:'MXN'},
 ja:{title:'旅行費用の概算 · 事業者の料金',intro:'各地点の掲載料金を選択できます。空き状況・最終価格は未確認です。料金不明の項目を表示します。',people:'人数',days:'日数',nights:'宿泊数',rooms:'部屋数',budget:'予算 (MXN・任意)',heading:'立寄り先の事業者・入場料',empty:'目的地を追加すると料金候補が表示されます。',no:'現時点で掲載料金なし：',unverified:'事業者との対応・営業・空き状況は未確認です。予約前に確認してください。',regional:'地域ツアー（参考のみ）',regionalHelp:'出発地が未確認なので合計には含めません。',source:'情報源',published:'選択した掲載料金',assumptions:'入力した概算',subtotal:'参考小計 · 最終旅行料金ではありません',missing:'未算出の費用',warning:'確認が必要な条件',km:'走行距離 (km)',kmManual:'手入力の走行距離 (km)',consumption:'燃費 (km/L)',fuel:'燃料価格 (MXN/L)',tolls:'有料道路 (MXN)',food:'食事/人/日 (MXN)',lodging:'掲載宿泊料金がない場合の部屋/泊 (MXN)',other:'その他 (MXN)',travel:'交通費など',auto:'道路ルートから',manual:'手入力',absent:'未確認 · 道路ルートの算出か手入力が必要',totalWarn:'小計が予算内でも未算出費用があります。',over:'入力済み費用が予算を超えました。',recorded:'掲載料金',estimated:'概算',from:'最低',pending:'参考料金（単位未確認）',checked:'確認日',copy:'内訳をコピー',copied:'コピー済み',noOffers:'体験料金は未選択です。',rates:'掲載された料金',regionalTag:'地域ツアー／パッケージ',raw:'表示料金',tax:'条件',coverage:'料金掲載のある場所',notCovered:'料金のない場所',loading:'料金を読み込み中…',loadError:'読み込みに失敗しました。',missingRoom:'宿泊料金は未選択です',hint:'パッケージに含まれるサービスを二重計上しないでください。',money:'MXN'}
};
const lang=()=>{const v=String(document.getElementById('language-select')?.value||document.documentElement.lang||'en').slice(0,2);return dictionary[v]?v:'en';};
const t=()=>dictionary[lang()];
const mk=(tag,cls,txt)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(txt!==undefined)e.textContent=txt;return e;};
const mx=n=>new Intl.NumberFormat(lang()==='en'?'en-US':lang()==='ja'?'ja-JP':'es-MX',{style:'currency',currency:'MXN',maximumFractionDigits:2}).format(n);
const section=mk('details','vxp');section.id='vxp-prices';const trigger=mk('summary','vxp-trigger');section.append(trigger);
const intro=mk('p','vxp-intro');section.append(intro);
const fields=mk('div','vxp-fields');section.append(fields);
function field(key,value,min,max,step='1'){const label=mk('label','vxp-field');const title=mk('span');const input=mk('input');input.type='number';input.min=String(min);input.max=String(max);input.step=step;input.value=value===null?'':String(value);input.dataset.priceInput=key;label.append(title,input);fields.append(label);input.addEventListener('input',refresh);return {title,input};}
const inputs={people:field('people',2,1,100),days:field('days',2,1,100),nights:field('nights',1,0,60),rooms:field('rooms',1,1,50),budget:field('budget',null,0,1000000,'50'),manualKm:field('kmManual',null,0,100000,'1'),efficiency:field('consumption',null,1,100,'.1'),fuelPrice:field('fuel',null,0,1000,'.01'),tolls:field('tolls',null,0,1000000,'1'),mealsPerPersonDay:field('food',null,0,100000,'1'),manualLodgingRoomNight:field('lodging',null,0,100000,'1'),additional:field('other',null,0,100000,'1')};
const distanceLine=mk('p','vxp-distance');section.insertBefore(distanceLine,fields);
const h=mk('h4','vxp-h'),offersBox=mk('div','vxp-offers'),regional=mk('details','vxp-regional'),regTitle=mk('summary'),regList=mk('div','vxp-regional-list');regional.append(regTitle,regList);section.append(h,offersBox,regional);
const tip=mk('p','vxp-tip');section.append(tip);
const tally=mk('div','vxp-tally');tally.setAttribute('role','status');tally.setAttribute('aria-live','polite');section.append(tally);
const copyBtn=mk('button','vxp-copy');copyBtn.type='button';section.append(copyBtn);
// Place the itemized estimate after routing/directions in the single journey flow.
panel.append(section);
let rows=[],chosen=new Set(),roadKm=null,roadTime=null,loading=true,lastResult=null;
const get=n=>inputs[n].input.value;
const config=()=>({offers:rows.filter((x,i)=>chosen.has(i)),party:get('people'),days:get('days'),nights:get('nights'),rooms:get('rooms'),roadKm,manualKm:get('manualKm'),efficiency:get('efficiency'),fuelPrice:get('fuelPrice'),tolls:get('tolls'),mealsPerPersonDay:get('mealsPerPersonDay'),manualLodgingRoomNight:get('manualLodgingRoomNight'),additional:get('additional')});
const selectedStops=()=>router.getStops?.()||[];
function currentCityNames(){const result=[];for(const p of selectedStops()){const city=p.kind==='municipality'?p.name:p.municipality;if(city&&!result.some(x=>C.norm(x)===C.norm(city)))result.push(city);}return result;}
function changeOffer(index,checked){if(checked)chosen.add(index);else chosen.delete(index);refresh();}
function renderOffers(){offersBox.replaceChildren();const stops=selectedStops();
 if(!stops.length){offersBox.append(mk('p','vxp-muted',t().empty));return;}
 const towns=currentCityNames();if(!towns.length)offersBox.append(mk('p','vxp-muted',t().empty));
 for(const city of towns){const cityRows=rows.map((r,i)=>({...r,_index:i})).filter(r=>!C.isRegional(r)&&C.norm(r.municipality_or_area)===C.norm(city));
   const cityBlock=mk('div','vxp-city');const heading=mk('h5','',city);cityBlock.append(heading);
   if(!cityRows.length){cityBlock.append(mk('p','vxp-muted',t().no+' '+city));offersBox.append(cityBlock);continue;}
   for(const r of cityRows){const line=mk('div','vxp-offer');const eligible=C.quote(r,Number(get('people'))||1,Number(get('days'))||1,Number(get('nights'))||0,Number(get('rooms'))||1).usable;
     const main=mk('label','vxp-choice');const checkbox=mk('input');checkbox.type='checkbox';checkbox.dataset.offer=String(r._index);checkbox.checked=chosen.has(r._index);checkbox.disabled=!eligible;
     checkbox.addEventListener('change',()=>changeOffer(r._index,checkbox.checked));const text=mk('span');text.append(mk('strong','',r.offering),mk('small','',r.provider+' · '+r.unit));
     main.append(checkbox,text);line.append(main);
     const value=mk('div','vxp-offer-price',mx(Number(r.price_mxn))+(r.price_basis?.includes('FROM')?' +':'') );line.append(value);
     if(!eligible)line.append(mk('p','vxp-muted',t().pending));
     const terms=mk('p','vxp-terms',r.terms_and_exclusions||'');if(terms.textContent)line.append(terms);
     const footer=mk('div','vxp-offer-meta');footer.append(mk('span','',t().checked+': '+r.checked_at));
     if(/^https?:\/\//.test(r.source_url||'')){const a=mk('a','',t().source+' ↗');a.href=r.source_url;a.target='_blank';a.rel='noopener noreferrer';footer.append(a);}line.append(footer);cityBlock.append(line);
   }
   offersBox.append(cityBlock);
 }
}
function renderRegional(){regList.replaceChildren();for(const r of rows.filter(C.isRegional)){
 const line=mk('p','vxp-regional-item');line.append(mk('strong','',r.offering+' — '+mx(Number(r.price_mxn))));line.append(mk('span','', ' · '+r.provider+' · '+r.unit));
 if(/^https?:\/\//.test(r.source_url||'')){const a=mk('a','',t().source+' ↗');a.href=r.source_url;a.rel='noopener noreferrer';a.target='_blank';line.append(a);}regList.append(line);
 }}
function refresh(){const validStops=new Set(C.matching(selectedStops(),rows).map(r=>rows.indexOf(r)));for(const id of [...chosen])if(!validStops.has(id))chosen.delete(id);
 // Prevent selected disabled or invalid units from disappearing silently on party changes.
 lastResult=C.estimate(config());renderSummary();}
function renderSummary(){const r=lastResult||C.estimate(config());tally.replaceChildren();
 const h=mk('p','vxp-tally-title',t().subtotal);tally.append(h);
 tally.append(mk('p','vxp-number',mx(r.subtotal)));
 tally.append(mk('p','vxp-total-part',t().published+': '+mx(r.published)+' · '+t().assumptions+': '+mx(r.assumptions)));
 if(r.items.length){const lines=mk('ul','vxp-breakdown');for(const item of r.items){lines.append(mk('li','',item.name+' · '+mx(item.amount)+' ('+(item.category==='published'?t().recorded:t().estimated)+')'));}tally.append(lines);}
 const budget=C.bounded(get('budget'),0,1e6);if(budget!==null)tally.append(mk('p','vxp-budget-msg',r.subtotal>budget?t().over:t().totalWarn));
 const remaining=currentCityNames().filter(city=>!rows.some(x=>!C.isRegional(x)&&C.norm(x.municipality_or_area)===C.norm(city)));
 if(remaining.length)tally.append(mk('p','vxp-caution',t().notCovered+': '+remaining.join(', ')));
 const missing=[...r.missing];if(currentCityNames().length>0&&!config().offers.length&&!missing.includes('Activity and entrance fees'))missing.push('Activity and entrance fees');
 if(missing.length){tally.append(mk('h5','',t().missing));const list=mk('ul','vxp-unknown');for(const m of missing)list.append(mk('li','',m));tally.append(list);}
 if(r.warnings.length){tally.append(mk('h5','',t().warning));const list=mk('ul','vxp-unknown');for(const m of r.warnings)list.append(mk('li','',m));tally.append(list);}
 tally.append(mk('p','vxp-tally-foot',t().unverified));
}
function translate(){const tt=t();trigger.textContent=tt.title;intro.textContent=tt.intro;h.textContent=tt.heading;regTitle.textContent=tt.regional;
 for(const [k,v] of Object.entries(inputs)){const prop=k==='manualKm'?'kmManual':k==='efficiency'?'consumption':k==='fuelPrice'?'fuel':k==='mealsPerPersonDay'?'food':k==='manualLodgingRoomNight'?'lodging':k==='additional'?'other':k;v.title.textContent=tt[prop];}
 const ref=roadKm===null?tt.absent:`${roadKm.toFixed(1)} km (${tt.auto})`;
 distanceLine.textContent=tt.km+': '+ref;
 tip.textContent=tt.hint;copyBtn.textContent=tt.copy;
 renderOffers();renderRegional();refresh();}
function onStopsChange(){roadKm=null;roadTime=null;translate();}
// The route engine clears the previous route on every stop change or re-calculation.
document.addEventListener('vxw:stops-changed',onStopsChange);
document.addEventListener('vxw:route-cleared',()=>{roadKm=null;translate();});
document.addEventListener('vxw:route-calculated',e=>{const meters=Number(e.detail?.distanceMeters);if(Number.isFinite(meters)&&meters>=0){roadKm=meters/1000;translate();}});
document.getElementById('language-select')?.addEventListener('change',translate);
copyBtn.addEventListener('click',async()=>{const r=lastResult||C.estimate(config());const out=[t().title,selectedStops().map((p,i)=>(i+1)+'. '+p.name).join(' → '),t().subtotal+': '+mx(r.subtotal),t().published+': '+mx(r.published),t().assumptions+': '+mx(r.assumptions),...r.items.map(x=>x.name+': '+mx(x.amount)),t().missing+': '+r.missing.join('; '),t().unverified];
 try{await navigator.clipboard.writeText(out.join('\n'));copyBtn.textContent=t().copied;}catch(e){copyBtn.textContent=t().copy+' (browser clipboard unavailable)';}});
translate();
fetch('data/provider_prices.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json();}).then(data=>{
 if(!Array.isArray(data.entries)||data.entries.length<1)throw Error('Missing published ledger');rows=data.entries;loading=false;translate();
}).catch(e=>{loading=false;offersBox.replaceChildren(mk('p','vxp-caution',t().loadError+' '+e.message));console.error('[Veracruz prices]',e);});
window.VeracruzTripPricing={getEstimate:()=>C.estimate(config()),getOffers:()=>rows.slice(),isLoaded:()=>!loading};
})();
