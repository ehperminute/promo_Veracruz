/* Labels for the current map page. Legacy 55-destination app.js is intentionally not loaded. */
(() => {
  const labels={
    en:{title:'Veracruz Tourism Intelligence',subtitle:'Explore documented activities and mapped attractions; locations and access may be approximate.',map:'Explore the map',route:'Plan a route'},
    es:{title:'Veracruz: información turística',subtitle:'Explora actividades documentadas y atractivos cartografiados; las ubicaciones y accesos pueden ser aproximados.',map:'Explorar mapa',route:'Planear ruta'},
    ja:{title:'ベラクルス観光情報',subtitle:'資料に基づく体験と観光地点。位置やアクセスは概略情報を含みます。',map:'地図を探索',route:'旅行ルートを計画'}
  };
  const select=document.getElementById('language-select');
  if(!select)return;
  function translate(){
    const lang=labels[select.value]?select.value:'en',t=labels[lang];
    document.documentElement.lang=lang;
    const title=document.querySelector('header h1'),subtitle=document.getElementById('current-subtitle'),map=document.getElementById('nav-map'),route=document.getElementById('nav-route');
    if(title)title.textContent=t.title;if(subtitle)subtitle.textContent=t.subtitle;
    if(map)map.textContent=t.map;if(route)route.textContent=t.route;
    document.title=t.title;
    try{localStorage.setItem('veracruz_language',lang);}catch(e){}
  }
  let saved=null;try{saved=localStorage.getItem('veracruz_language');}catch(e){}
  if(labels[saved])select.value=saved;
  select.addEventListener('change',translate);
  translate();
})();
