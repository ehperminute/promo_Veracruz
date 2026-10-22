/* Editable planning envelope for unpriced itinerary stops. Separate from published supplier quotes. */
(() => {
'use strict';
const panel=document.getElementById('vxp-prices');
const core=window.VeracruzBudgetRangeCore;
if(!panel||!core||document.getElementById('vxr-budget'))return;
const i18n={
 es:{title:'Presupuesto orientativo (aunque falten precios)',explain:'Rango para PLANEAR, no tarifa local ni cotización. Ajusta los supuestos: no son precios observados en cada municipio.',mode:'Nivel de gasto supuesto',light:'Económico',balanced:'Intermedio',flexible:'Amplio',activities:'Actividades pagadas previstas (total)',more:'Editar supuestos (MXN)',room:'Habitación/noche',food:'Comida/persona/día',activity:'Actividades/persona',low:'Mín.',high:'Máx.',show:'Presupuesto de referencia',hint:'Incluye tarifas publicadas seleccionadas, si las hay. Los demás importes son supuestos de planeación; no incluyen costos que no se conocen.',roads:'Sin kilometraje vial: gasolina pendiente.',fuel:'Combustible calculado',tolls:'Casetas aún no cotizadas',missing:'No incluye: posibles casetas, regreso no trazado, traslados sin precio, disponibilidad y otros cargos desconocidos.',none:'Añade al menos un destino a la ruta.',invalid:'Revisa que cada mínimo sea menor o igual al máximo.',assumptions:'Alojamiento, alimentación y actividades presupuestadas',quotes:'Tarifas publicadas elegidas',note:'No sumes otra vez paquetes con hospedaje o alimentos incluidos. Este rango no garantiza el precio del viaje.',fuelparams:'Si no introduces rendimiento y precio de gasolina arriba, se usa un ejemplo editable de 12 km/L y MXN $23.68/L.',fuelDefault:'Rendimiento ilustrativo 12 km/L; gasolina de referencia MXN 23.68/L (Profeco, ago. 2026).',stops:'Municipios en la ruta'},
 en:{title:'Planning budget (even when prices are missing)',explain:'A PLANNING range, not a local price or supplier quote. Adjust the assumptions: they are not observed prices for each town.',mode:'Assumed spending style',light:'Low-cost',balanced:'Mid-range',flexible:'Flexible',activities:'Planned paid activities (total)',more:'Edit assumptions (MXN)',room:'Room/night',food:'Food/person/day',activity:'Activities/person',low:'Low',high:'High',show:'Planning envelope',hint:'Includes selected advertised supplier charges, if any. All other amounts are planning assumptions; unknown costs are excluded.',roads:'No road distance: fuel still missing.',fuel:'Calculated fuel',tolls:'Tolls not yet quoted',missing:'Excludes: possible tolls, return travel unless routed, unpriced transfers, availability and other unknown charges.',none:'Add at least one destination to your route.',invalid:'Check that each minimum does not exceed its maximum.',assumptions:'Budgeted lodging, meals and activities',quotes:'Selected advertised prices',note:'Avoid double-counting packages that include accommodation or meals. This range does not guarantee a travel price.',fuelparams:'If you have not entered fuel economy and pump price above, editable example values of 12 km/L and MXN 23.68/L are used.',fuelDefault:'Illustrative fuel economy 12 km/L; reference gasoline MXN 23.68/L (Profeco, Aug. 2026).',stops:'Municipalities on itinerary'},
 ja:{title:'料金未掲載でも旅行予算の目安を計算',explain:'これは旅行計画のための仮定で、各地域の実際の料金や予約見積ではありません。数値を変更できます。',mode:'想定する旅行費用',light:'節約',balanced:'標準',flexible:'余裕',activities:'有料アクティビティの想定回数',more:'仮定を編集（MXN）',room:'部屋/泊',food:'食費/人/日',activity:'活動費/人',low:'下限',high:'上限',show:'予算の目安',hint:'選択された公表価格を含みます。他の金額は計画上の仮定です。未確認費用は含みません。',roads:'道路距離未確認：燃料費未計上',fuel:'燃料費の計算値',tolls:'通行料未確認',missing:'通行料、ルートにない復路、未掲載の移動費、予約可否、その他の費用は含みません。',none:'目的地を追加してください。',invalid:'下限が上限を超えないようにしてください。',assumptions:'宿泊、食事、アクティビティの仮定',quotes:'選択した掲載価格',note:'宿泊・食事込みのパッケージを重複計上しないでください。',fuelparams:'燃費とガソリン代が未入力の場合、12km/Lと23.68 MXN/Lを参考値として使用します。',fuelDefault:'燃費12km/Lは仮定、ガソリン23.68 MXN/Lは2026年8月Profeco参考値です。',stops:'ルートの市町村'}
};
const el=(tag,cls,text)=>{let e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
const root=el('section','vxr-budget');root.id='vxr-budget';const headline=el('h4','vxr-title');const expl=el('p','vxr-note');root.append(headline,expl);
const row=el('div','vxr-row');const modeLabel=el('label','vxr-selectwrap');const modeText=el('span');const select=el('select');select.id='vxr-mode';for(const x of ['light','balanced','flexible','custom']){const opt=el('option');opt.value=x;opt.textContent=x;select.append(opt);}select.value='balanced';modeLabel.append(modeText,select);const actLabel=el('label','vxr-actwrap');const actText=el('span');const paid=el('input');paid.id='vxr-paid';paid.type='number';paid.min='0';paid.max='20';paid.step='1';paid.value='2';actLabel.append(actText,paid);row.append(modeLabel,actLabel);root.append(row);
const advanced=el('details','vxr-advanced'),advancedHead=el('summary');advanced.append(advancedHead);const edit=el('div','vxr-grid');advanced.append(edit);root.append(advanced);
const fields={};for(const key of ['room','food','activity']){fields[key]=[];for(const j of [0,1]){const lab=el('label','vxr-control');const title=el('span');const input=el('input');input.type='number';input.min='0';input.max='1000000';input.step='25';input.dataset.band=key+':'+j;lab.append(title,input);edit.append(lab);fields[key].push({input,title});}}
const output=el('div','vxr-output');output.setAttribute('role','status');output.setAttribute('aria-live','polite');const amount=el('p','vxr-total'),breakdown=el('p','vxr-breakdown'),warn=el('p','vxr-warning'),fuelHelp=el('p','vxr-foot');output.append(amount,breakdown,warn,fuelHelp);root.append(output);
const note=el('p','vxr-note vxr-bottom');root.append(note);
const sourceLine=el('p','vxr-note');
const profeco=el('a','', 'Profeco · gasolina');profeco.href='https://www.gob.mx/profeco/prensa/profeco-reporta-quien-es-quien-en-los-precios-de-la-gasolina-regular-y-el-diesel';profeco.target='_blank';profeco.rel='noopener noreferrer';
const sict=el('a','', 'SICT · casetas');sict.href='https://app.sct.gob.mx/sibuac_internet/ControllerUI?action=cmdEscogeRutaMovil';sict.target='_blank';sict.rel='noopener noreferrer';
sourceLine.append(profeco,document.createTextNode(' · '),sict);root.append(sourceLine);
const priceIntro=panel.querySelector('.vxp-intro'); if(priceIntro)priceIntro.insertAdjacentElement('afterend',root);else panel.prepend(root);
const language=()=>{const v=String(document.getElementById('language-select')?.value||document.documentElement.lang||'es').slice(0,2);return i18n[v]?v:'es';};
const t=()=>i18n[language()];
const money=x=>new Intl.NumberFormat(language()==='ja'?'ja-JP':language()==='en'?'en-US':'es-MX',{style:'currency',currency:'MXN',maximumFractionDigits:0}).format(x);
const val=(k)=>document.querySelector(`[data-price-input="${k}"]`)?.value??'';
const num=(v,fallback)=>v===''||v==null?fallback:Number(v);
const stops=()=>window.VeracruzItineraryV2?.getStops?.()||[];
const readBands=()=>Object.fromEntries(Object.keys(fields).map(k=>[k,fields[k].map(f=>Number(f.input.value))]));
const preset=(name)=>{const x=core.defaults[name]||core.defaults.balanced;for(const k of Object.keys(fields))fields[k].forEach((f,j)=>{f.input.value=x[k][j];});};
function quoteInfo(){const pricing=window.VeracruzTripPricing;if(!pricing)return {published:0,pricedActivities:0,lodgingIncluded:false};
 const e=pricing.getEstimate(),available=pricing.getOffers(),q=e.items.filter(x=>x.category==='published');let pricedActivities=0,lodgingIncluded=false;
 for(const item of q){const r=available.find(x=>x.offering===item.name&&x.provider===item.provider);if(!r)continue;
  const room=window.VeracruzPricingCore.isLodging(r)||/incluye (hospedaje|alojamiento)/i.test(r.terms_and_exclusions||'');
  if(room)lodgingIncluded=true;else pricedActivities++;
 }
 return {published:e.published,pricedActivities,lodgingIncluded};
}
function repaint(){const tt=t();headline.textContent=tt.title;expl.textContent=tt.explain;modeText.textContent=tt.mode;actText.textContent=tt.activities;advancedHead.textContent=tt.more;note.textContent=tt.note;
 for(const op of select.options){op.textContent=tt[op.value]||'Custom / Personalizado';}
 for(const k of Object.keys(fields))fields[k].forEach((f,j)=>{f.title.textContent=tt[k]+' · '+(j===0?tt.low:tt.high);});
 const s=stops();if(!s.length){amount.textContent=tt.none;breakdown.textContent='';warn.textContent='';fuelHelp.textContent='';return;}
 try{
  const pricing=window.VeracruzTripPricing?.getEstimate?.()||{};const q=quoteInfo();const km=pricing.roadKm??null;
  const b=core.compute({people:num(val('people'),2),days:num(val('days'),2),nights:num(val('nights'),1),rooms:num(val('rooms'),1),paidActivities:Number(paid.value),bands:readBands(),...q,km,efficiency:num(val('efficiency'),12),fuelPrice:num(val('fuelPrice'),23.68),tolls:val('tolls'),additional:val('additional')});
  amount.textContent=`${tt.show}: ${money(b.low)} – ${money(b.high)}`;
  breakdown.textContent=`${tt.assumptions}: ${money(b.assumed.room[0]+b.assumed.food[0]+b.assumed.activity[0])} – ${money(b.assumed.room[1]+b.assumed.food[1]+b.assumed.activity[1])} · ${tt.quotes}: ${money(b.published)}`;
  warn.textContent=(b.fuel===null?tt.roads:`${tt.fuel}: ${money(b.fuel)} (${b.km.toFixed(1)} km)`)+' · '+(b.tolls===null?tt.tolls:`${money(b.tolls)} casetas`)+'. '+tt.missing;
  fuelHelp.textContent=tt.fuelDefault+' '+tt.fuelparams;
 }catch(e){amount.textContent=tt.invalid;breakdown.textContent='';warn.textContent=e.message;fuelHelp.textContent='';}
}
select.addEventListener('change',()=>{if(select.value!=='custom')preset(select.value);repaint();});
paid.addEventListener('input',repaint);
for(const k of Object.keys(fields))for(const f of fields[k])f.input.addEventListener('input',()=>{select.value='custom';repaint();});
document.addEventListener('input',e=>{if(e.target?.dataset?.priceInput)repaint();});
document.addEventListener('change',e=>{if(e.target?.dataset?.priceInput||e.target?.closest?.('#vxp-prices .vxp-offers'))repaint();});
for(const name of ['vxw:stops-changed','vxw:route-calculated','vxw:route-cleared'])document.addEventListener(name,()=>queueMicrotask(repaint));
document.getElementById('language-select')?.addEventListener('change',repaint);
const offers=panel.querySelector('.vxp-offers');if(offers&&typeof MutationObserver!=='undefined'){new MutationObserver(repaint).observe(offers,{childList:true,subtree:true});}
preset('balanced');repaint();
window.VeracruzBudgetRange={getSummary:()=>({stops:stops().map(x=>x.name),style:select.value,paidActivities:Number(paid.value),bands:readBands()}),refresh:repaint};
})();
