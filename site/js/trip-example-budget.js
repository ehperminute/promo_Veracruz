(() => {
  'use strict';
  const dataPath='data/trip_examples.json';
  const localeMap={es:'es-MX',en:'en-US',ja:'ja-JP'};
  const ui={
    es:{heading:'Presupuesto ilustrativo para esta ruta',summary:'Estos importes son supuestos para orientar la planificación; no representan compras reales, tarifas publicadas ni reservas.',group:'Total del ejemplo, para el grupo',person:'Si dos personas comparten todos los gastos',photo:'Foto de referencia; no es una imagen aportada por un viajero',credit:'Foto y licencia'},
    en:{heading:'Illustrative budget for this route',summary:'These amounts are planning assumptions. They are not actual purchases, published rates or reservations.',group:'Example total, entire group',person:'If two travelers share all expenses',photo:'Reference photograph, not a traveler-submitted image',credit:'Photo and license'},
    ja:{heading:'この旅程の参考予算',summary:'以下は計画用の仮の金額です。実際の支払い、公開料金、予約ではありません。',group:'グループの予算合計',person:'2人で均等に分担した場合',photo:'旅行者が投稿した写真ではなく参考写真です',credit:'写真とライセンス'}
  };
  let examples=[];
  const el=(tag,cl,txt)=>{const out=document.createElement(tag);if(cl)out.className=cl;if(txt!==undefined)out.textContent=String(txt);return out};
  const lang=()=>{let l='es';try{l=localStorage.getItem('veracruz_language')||'es'}catch{}return ui[l]?l:'es'};
  const localized=(obj,l)=>typeof obj==='string'?obj:(obj?.[l]||obj?.es||'');
  const money=(value,l)=>new Intl.NumberFormat(localeMap[l],{style:'currency',currency:'MXN',maximumFractionDigits:0}).format(value);
  function currentExample(){
    const id=new URLSearchParams(location.search).get('example');
    if(!id || !location.hash.startsWith('#trip=')) return null;
    const x=examples.find(t=>t.id===id && t.kind==='example');
    if(!x || !Array.isArray(x.exampleBudget?.items))return null;
    // Ensure this sample notice cannot be shown on a different route accidentally.
    try{
      const C=window.VXTripJournalCore;
      const opened=C.decode(location.hash.slice(6));
      if(opened.stops.length!==x.trip.stops.length || opened.stops.some((stop,i)=>stop.id!==x.trip.stops[i].id))return null;
      if(opened.expenses.length!==0)return null;
    }catch{return null}
    return x;
  }
  function render(){
    let panel=document.getElementById('vx-example-panel');
    if(!panel){
      const target=document.getElementById('tj-expenses-heading')?.closest('section');
      if(!target)return;
      panel=el('section','tj-card vx-example-panel');panel.id='vx-example-panel';target.before(panel);
    }
    panel.replaceChildren();
    const trip=currentExample();
    panel.hidden=!trip;
    if(!trip)return;
    const l=lang(), t=ui[l], b=trip.exampleBudget;
    panel.append(el('h2','',t.heading));panel.append(el('p','vx-budget-warning',t.summary));
    if(trip.coverPhoto){
      const p=trip.coverPhoto;
      if(/^https:\/\/commons\.wikimedia\.org\/wiki\/Special:FilePath\//.test(String(p.url||''))){
        const figure=el('figure','vx-sample-photo');const img=el('img','',localized(p.alt,l));img.src=p.url;img.alt=localized(p.alt,l);img.loading='lazy';img.referrerPolicy='no-referrer';figure.append(img);
        const caption=el('figcaption','',t.photo+' · ');
        const source=el('a','',t.credit+': '+String(p.credit||''));source.href=p.page;source.target='_blank';source.rel='noopener noreferrer';caption.append(source);figure.append(caption);panel.append(figure);
      }
    }
    const list=el('ul','vx-example-list');let total=0;
    b.items.forEach(item=>{
      const amount=Number(item.amount);
      if(!Number.isFinite(amount)||amount<0)return;
      total+=amount;
      const li=el('li','');li.append(el('span','',trip.trip.stops[item.stopIndex]?.name+' · '+localized(item.label,l)));
      li.append(el('strong','',money(amount,l)));list.append(li);
    });
    panel.append(list);
    const figures=el('div','vx-budget-figures');figures.append(el('p','',t.group+': '+money(total,l)));figures.append(el('p','',t.person+': '+money(total/(Number(b.people)||2),l)));panel.append(figures);
  }
  async function load(){
    try{const response=await fetch(dataPath,{cache:'no-store'});if(!response.ok)throw Error('not found');const obj=await response.json();examples=Array.isArray(obj.trips)?obj.trips:[]}catch{examples=[]}
    render();
  }
  window.addEventListener('hashchange',render);
  window.addEventListener('popstate',render);
  document.getElementById('tj-lang')?.addEventListener('change',()=>setTimeout(render,0));
  window.addEventListener('storage',ev=>{if(ev.key==='veracruz_language')render()});
  load();
})();
