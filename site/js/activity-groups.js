/* Current source-backed experience browser: eight groups (all >=2), 78 named experiences.
   Real Commons photographs illustrate ONE representative example per group, not every stop. */
(() => {
  'use strict';
  const host=document.getElementById('vx-activities');
  if (!host || host.dataset.groupsLoaded) return;
  host.dataset.groupsLoaded='1';
  const T={
    es:{title:'Explora experiencias en Veracruz',intro:'Ocho colecciones temáticas para navegar 78 actividades concretas y sus municipios documentados. No son clústeres estadísticos.',search:'Buscar experiencia o municipio...',units:'experiencias',places:'Municipios documentados',sources:'Fuente ↗',add:'Añadir a ruta',map:'Ver en mapa',more:'Ver lugares y fuentes',none:'Sin resultados.',photo:'Fotografía de ejemplo, no de todas las actividades',loading:'Cargando actividades...',error:'No se pudo cargar el catálogo. Comprueba site/data/activity_sections.json.',done:'Municipio añadido:',err:'No se pudo añadir; abre el planificador y vuelve a intentarlo.',warning:'La evidencia documental no garantiza acceso, horario, precio ni disponibilidad actual.'},
    en:{title:'Explore Veracruz experiences',intro:'Eight thematic sections for 78 specific activities and their documented municipalities. These are not statistical clusters.',search:'Search activity or municipality...',units:'activities',places:'Documented municipalities',sources:'Source ↗',add:'Add to route',map:'Show on map',more:'Places and evidence',none:'No results.',photo:'Example photograph, not of every listed activity',loading:'Loading activities...',error:'Could not load the activity catalog. Check site/data/activity_sections.json.',done:'Added municipality:',err:'Could not add stop; open planner and try again.',warning:'Documentary evidence does not guarantee current access, hours, pricing or availability.'},
    ja:{title:'ベラクルスの体験を探す',intro:'78の具体的な体験を8つのテーマで紹介します。統計的クラスタではありません。',search:'体験・市町村を検索…',units:'体験',places:'資料で確認された市町村',sources:'出典 ↗',add:'ルートに追加',map:'地図で見る',more:'場所と出典',none:'該当なし',photo:'この写真はテーマの一例で、全活動の写真ではありません',loading:'読み込み中…',error:'活動データを読み込めませんでした。',done:'追加しました：',err:'ルートに追加できませんでした。',warning:'資料の記載は現在の営業・価格・予約を保証しません。'}
  };
  let data=null, query='';
  const locale=()=>{const v=document.querySelector('#language-select')?.value||'es';return T[v]?v:'es';};
  const lang=()=>T[locale()];
  const el=(type,cls,text)=>{const n=document.createElement(type);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
  const clean=x=>String(x||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  const external=x=>{try{const u=new URL(x);return u.protocol==='https:'?u.href:null;}catch{return null;}};
  const header=el('div','vxg-header');
  const heading=el('h2'); const intro=el('p');header.append(heading,intro);
  const search=el('input','vxg-search');search.type='search';search.autocomplete='off';search.setAttribute('aria-label','Search experiences and municipalities');
  const count=el('p','vxg-count');const sections=el('div','vxg-list');const alert=el('p','vxg-feedback');alert.setAttribute('role','status');
  const caveat=el('p','vxg-caveat');host.replaceChildren(header,search,count,sections,caveat,alert);
  function useRoute(m){const ok=window.VeracruzItineraryV2?.addStopById?.('municipality:'+m.municipality_id);alert.textContent=ok?lang().done+' '+m.name:lang().err; if(ok)document.getElementById('vxw-itinerary')?.scrollIntoView({behavior:'smooth',block:'start'});}
  function mapFilter(feature){const sel=document.getElementById('vx-activity');if(!sel)return;const opts=Array.from(sel.options);if(!opts.some(o=>o.value===feature))return;sel.value=feature;sel.dispatchEvent(new Event('change',{bubbles:true}));document.getElementById('veracruz-map-section')?.scrollIntoView({behavior:'smooth',block:'start'});}
  function activityRow(a){const block=el('details','vxg-activity');const summary=el('summary','vxg-activity-head');
    const itemTitle=el('strong','',locale()==='en'?(a.label_en||a.label_es):a.label_es);
    const itemCount=el('span','vxg-chip',a.municipality_count+' '+lang().places);summary.append(itemTitle,itemCount);block.append(summary);
    const desc=el('p','vxg-description',locale()==='en'?(a.description_en||a.description_es):a.description_es);block.append(desc);
    const control=el('button','vxg-map',lang().map);control.type='button';control.addEventListener('click',()=>mapFilter(a.feature_id));block.append(control);
    const list=el('div','vxg-municipalities');
    for(const m of a.municipalities){const row=el('div','vxg-municipality');const add=el('button','',lang().add+' · '+m.name);add.type='button';add.addEventListener('click',()=>useRoute(m));row.append(add);
      for(const link of [...new Set(m.source_urls)].slice(0,1)){const url=external(link);if(url){const aLink=el('a','',lang().sources);aLink.href=url;aLink.rel='noopener noreferrer';aLink.target='_blank';row.append(aLink);}}
      list.append(row);}
    block.append(list);return block;}
  function sectionCard(s, activities, open){const section=el('section','vxg-section');const top=el('div','vxg-section-top');
    const photo=el('div','vxg-photo');const image=el('img');image.loading='lazy';image.alt=(s.photo.caption_es||s.id);image.src=s.photo.url;
    image.addEventListener('error',()=>{image.hidden=true;photo.classList.add('vxg-photo-failed');});photo.append(image);
    const photoCredit=el('a','vxg-photo-credit',s.photo.credit+' ↗');photoCredit.href=s.photo.source_url;photoCredit.target='_blank';photoCredit.rel='noopener noreferrer';photo.append(photoCredit);top.append(photo);
    const meta=el('div','vxg-meta');const label=el('h3','',s.labels[locale()==='es'?0:locale()==='ja'?2:1]);meta.append(label,el('p','vxg-counter',activities.length+' '+lang().units));meta.append(el('p','vxg-caption',s.photo.caption_es));meta.append(el('small','vxg-disclaimer',lang().photo));top.append(meta);section.append(top);
    const box=el('div','vxg-activity-list');for(const activity of activities)box.append(activityRow(activity));section.append(box);
    return section;}
  function render(){const l=lang();heading.textContent=l.title;intro.textContent=l.intro;search.placeholder=l.search;caveat.textContent=l.warning;
    if(!data)return;const q=clean(query);const groups=[];let matched=0;
    for(const s of data.sections){const matches=s.activities.filter(a=>!q || clean([a.label_es,a.label_en,...a.municipalities.map(m=>m.name)].join(' ')).includes(q));
      if(matches.length){groups.push([s,matches]);matched+=matches.length;}}
    sections.replaceChildren();for(const [s,activities] of groups)sections.append(sectionCard(s,activities,!!q));
    if(!matched)sections.append(el('p','vxg-empty',l.none));
    count.textContent=groups.length+' '+(locale()==='es'?'secciones':locale()==='ja'?'分類':'sections')+' · '+matched+' '+l.units;
  }
  search.addEventListener('input',()=>{query=search.value;render();});
  document.getElementById('language-select')?.addEventListener('change',render);
  alert.textContent=lang().loading;
  fetch('data/activity_sections.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error(String(r.status));return r.json();}).then(d=>{
     if(d.counts?.activities!==78||d.counts?.sections!==8||d.counts?.links!==216)throw Error('Current data version mismatch');data=d;alert.textContent='';render();
  }).catch(e=>{alert.textContent=lang().error;console.error('Activity groups',e);});
})();
