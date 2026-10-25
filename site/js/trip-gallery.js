(() => {
  'use strict';
  const core = window.VXTripJournalCore;
  const $ = id => document.getElementById(id);
  const section = $('vx-trip-gallery');
  if (!section || !core) return;
  const strings = {
    es: { heading:'Rutas para inspirarte', introduction:'Ideas basadas en experiencias documentadas; no son reseñas de viajeros ni contienen gastos reales.', demo:'Ruta sugerida · sin gastos observados', published:'Relato de viajero · precios declarados', view:'Ver ruta', copy:'Usar como plantilla', submit:'Compartir mi experiencia y fotos', unavailable:'No se pudieron cargar las rutas de ejemplo.', details:'Experiencias destacadas', story:'Ver relato y fotos', expenses:'Gastos declarados', empty:'Aún no hay relatos de viajeros aprobados.', exampleBudget:'Gastos de ejemplo para 2 personas (no son compras reales)', sampleCosts:'Ver conceptos del ejemplo', photoCredit:'Foto y licencia' },
    en: { heading:'Routes to inspire you', introduction:'Ideas based on documented activities; these are not traveler reviews or observed expenses.', demo:'Suggested route · no observed spending', published:'Traveler story · self-reported prices', view:'View itinerary', copy:'Use as template', submit:'Share my experience and photos', unavailable:'Could not load example routes.', details:'Highlights', story:'Read story and see photos', expenses:'Reported spending', empty:'No approved traveler stories yet.', exampleBudget:'Example allowance for 2 travelers (not real purchases)', sampleCosts:'See example items', photoCredit:'Photo and license' },
    ja: { heading:'旅のアイデア', introduction:'記録された体験を基にしたルート例。実際の旅行体験談や支出データではありません。', demo:'おすすめ例・実際の支出ではありません', published:'旅行者の記録・自己申告の金額', view:'旅程を見る', copy:'雛形として使う', submit:'旅の体験と写真を共有', unavailable:'ルート例を読み込めませんでした。', details:'主な体験', story:'体験談と写真を見る', expenses:'申告された支出', empty:'承認された旅行体験談はまだありません。', exampleBudget:'2人分の仮の予算（実際の購入ではありません）', sampleCosts:'予算内訳を見る', photoCredit:'写真・ライセンス' }
  };
  let examples = [], published = [], loaded=false;
  const node=(tag,cl,txt)=>{const el=document.createElement(tag);if(cl)el.className=cl;if(txt!==undefined)el.textContent=txt;return el;};
  function lang(){let l='es';try{l=localStorage.getItem('veracruz_language')||'es';}catch(e){}return strings[l]?l:'es';}
  function label(obj,l){return typeof obj==='string'?obj:obj?.[l]||obj?.es||'';}
  function entry(trip,l){
    const s=strings[l];const isExample=trip.kind==='example';
    const card=node('article','vx-trip-card');
    if(isExample && trip.coverPhoto){
      const p=trip.coverPhoto;
      if(/^https:\/\/commons\.wikimedia\.org\/wiki\/Special:FilePath\//.test(String(p.url||''))){
        const im=node('img','vx-trip-cover');im.src=p.url;im.loading='lazy';im.alt=label(p.alt,l);im.referrerPolicy='no-referrer';card.append(im);
        const credit=node('a','vx-example-credit',s.photoCredit+': '+String(p.credit||''));credit.href=p.page;credit.target='_blank';credit.rel='noopener noreferrer';card.append(credit);
      }
    }
    if(!isExample&&Array.isArray(trip.photos)&&trip.photos.length){
      const photo=trip.photos[0];const url=String(photo.src||'');
      if(/^media\/community-trips\/[a-z0-9_-]+\/[a-z0-9_-]+\.webp$/.test(url)){
        const img=node('img','vx-trip-cover');img.src=url;img.loading='lazy';img.alt=String(photo.alt||'Imagen compartida por viajero').slice(0,140);card.append(img);
      }
    }
    card.append(node('span','vx-trip-kicker',isExample?s.demo:s.published));
    card.append(node('h3','',label(trip.title,l)));
    card.append(node('p','vx-trip-description',label(trip.summary||trip.story,l)));
    const stops=(trip.trip?.stops||[]).map(x=>x.name).join(' → ');
    card.append(node('p','vx-trip-route',stops));
    if(isExample&&trip.activities?.length){card.append(node('p','vx-trip-meta',s.details+': '+label(trip.highlights,l)));}
    if(isExample && trip.exampleBudget?.items?.length){
      const items=trip.exampleBudget.items;
      const total=items.reduce((sum,item)=>sum+Number(item.amount||0),0);
      const fmt=new Intl.NumberFormat(l==='ja'?'ja-JP':l==='en'?'en-US':'es-MX',{style:'currency',currency:'MXN',maximumFractionDigits:0});
      card.append(node('p','vx-example-budget',s.exampleBudget+': '+fmt.format(total)));
      const detail=node('details','vx-example-spending');detail.append(node('summary','',s.sampleCosts));
      const list=node('ul','');items.forEach(it=>{const stop=trip.trip?.stops?.[it.stopIndex]?.name||'';list.append(node('li','',stop+' · '+label(it.label,l)+' · '+fmt.format(it.amount)))});
      detail.append(list);card.append(detail);
    }
    if(!isExample && trip.trip?.expenses?.length){const summary=core.summary(trip.trip);card.append(node('p','vx-trip-meta',s.expenses+': '+summary.total.toLocaleString(l==='ja'?'ja-JP':l==='en'?'en-US':'es-MX',{style:'currency',currency:'MXN'})));}
    if(!isExample){
      const detail=node('details','vx-trip-story');detail.append(node('summary','',s.story));
      detail.append(node('p','vx-trip-story-text',trip.story||''));
      if(Array.isArray(trip.photos)&&trip.photos.length){
        const photos=node('div','vx-trip-photos');
        trip.photos.forEach(photo=>{
          const path=String(photo.src||'');
          if(!/^media\/community-trips\/[a-z0-9_-]+\/[a-z0-9_-]+\.webp$/.test(path))return;
          const figure=node('figure','');const im=node('img','');im.src=path;im.loading='lazy';im.alt=String(photo.alt||'Fotografía de un viajero').slice(0,140);figure.append(im);
          const stop=trip.trip?.stops?.[photo.stopIndex]?.name || '';
          const caption=[photo.alt,stop].filter(Boolean).join(' · ');
          if(caption)figure.append(node('figcaption','',caption));
          photos.append(figure);
        });
        detail.append(photos);
      }
      card.append(detail);
    }
    const actions=node('div','vx-trip-actions');
    const v=node('a','tj-button secondary',s.view);v.href=(isExample?'viajes.html?example='+encodeURIComponent(trip.id):'viajes.html')+'#trip='+core.encode(trip.trip);// VX-TRIP-GALLERY-SAME-HASH-FIX-V1: refresh when same example is clicked twice.
    v.addEventListener('click',ev=>{
      if(location.hash===new URL(v.href,location.href).hash && window.VXTripJournalOpenHash){ev.preventDefault();window.VXTripJournalOpenHash();}
    });
    actions.append(v);
    if(isExample){const c=node('a','tj-button',s.copy);c.href='viajes.html#draft='+core.encode(trip.trip);c.addEventListener('click',()=>{try{localStorage.setItem('vx_trip_diary_draft_v1',JSON.stringify(core.normalize(trip.trip)))}catch(e){}});actions.append(c);}
    card.append(actions);
    return card;
  }
  function render(){
    const l=lang(), s=strings[l];section.replaceChildren();
    const bar=node('div','vx-trip-heading');bar.append(node('h2','',s.heading));const a=node('a','tj-button',s.submit);a.href='enviar-viaje.html';bar.append(a);section.append(bar);
    section.append(node('p','vx-trip-intro',s.introduction));
    if(!loaded){section.append(node('p','tj-muted',s.unavailable));return;}
    const grid=node('div','vx-trip-grid');
    [...examples,...published].forEach(trip=>{try{grid.append(entry(trip,l));}catch(e){}});
    section.append(grid);
    if(!published.length)section.append(node('p','tj-muted',s.empty));
  }
  async function load(){
    try{
      const [a,b]=await Promise.all([
        fetch('data/trip_examples.json',{cache:'no-store'}),
        fetch('data/community_trips.json',{cache:'no-store'})
      ]);
      if(!a.ok||!b.ok)throw Error('Data unavailable');
      const d=await a.json(), e=await b.json();
      examples=(Array.isArray(d.trips)?d.trips:[]).filter(x=>x.kind==='example');
      published=(Array.isArray(e.trips)?e.trips:[]).filter(x=>x.kind==='traveler_reported');
      loaded=true;
    }catch(e){loaded=false;}
    render();
  }
  const select=$('tj-lang');if(select)select.addEventListener('change',()=>setTimeout(render,0));
  window.addEventListener('storage',ev=>{if(ev.key==='veracruz_language')render();});
  load();
})();
