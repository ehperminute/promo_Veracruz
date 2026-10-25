(() => {
  'use strict';
  const C = window.VXTripJournalCore;
  if (!C) return;
  const $ = id => document.getElementById(id);
  const T = {
    es: {
      'tj-lang-label':'Idioma / Language','tj-kicker':'DIARIO DE RUTA','tj-headline':'Comparte tu viaje, no tus datos privados',
      'tj-lead':'Guarda paradas y gastos reales, crea un enlace y ayuda a otros a estimar cuánto podrían gastar.',
      'tj-title-heading':'Tu viaje','tj-title-label':'Nombre de la ruta','tj-month-label':'Mes aproximado (opcional)',
      'tj-people-label':'Viajeros','tj-stops-heading':'Paradas','tj-stops-help':'Trae las paradas del planificador o añade un lugar manualmente.',
      'tj-expenses-heading':'Gastos realizados','tj-expenses-help':'Indica lo que pagó el grupo en MXN, no el precio por persona.',
      'tj-stop-label':'Parada','tj-category-label':'Categoría','tj-item-label':'Compra o servicio','tj-amount-label':'Total pagado (MXN)',
      'tj-provider-label':'Proveedor o establecimiento (opcional)','tj-note-label':'Observación (opcional)',
      'tj-add-expense':'Registrar gasto','tj-add-stop':'Añadir parada','tj-summary-heading':'Resumen de gastos declarados',
      'tj-total-label':'Gastos registrados del grupo','tj-person-label':'Por viajero, si se repartió por igual',
      'tj-summary-note':'Los totales solo incluyen gastos registrados. No son precios verificados ni una cotización completa.',
      'tj-share-heading':'Compartir o reutilizar','tj-privacy':'Antes de compartir, revisa nombres, notas y proveedores. No incluyas teléfonos, direcciones personales, datos bancarios, tickets con identificadores ni fechas exactas.',
      'tj-consent-label':'Revisé la información y deseo incluirla en un enlace que cualquiera con él puede leer.',
      'tj-copy':'Copiar enlace para compartir','tj-edit':'Editar una copia','tj-back-map':'Volver al mapa','tj-open-route':'Abrir ruta en el mapa',
      'tj-public-note':'Los enlaces almacenan los datos en la propia dirección. No suben información a este sitio ni crean una publicación pública buscable.',
      draft:'Borrador privado', shared:'Viaje compartido · sin verificar', remove:'Quitar',
      stop:'Parada', records:'Registros', cats:{food:'Comida',accommodation:'Hospedaje',activity:'Actividades',transport:'Transporte',shopping:'Compras',other:'Otros'},
      saved:'Borrador guardado en este navegador.', needs:'Añade al menos una parada.', consent:'Marca la confirmación antes de compartir.',
      sharedOK:'Enlace copiado. Cualquiera que lo tenga podrá leer el viaje.', sharedFallback:'Copia la dirección que aparece a continuación:', tooLong:'Demasiados datos para un enlace. Quita detalles o divide el viaje.',
      newStop:'Ciudad o lugar', itemPlaceholder:'Comida, habitación, visita...', providerPlaceholder:'Nombre si deseas compartirlo',notePlaceholder:'Qué incluía el precio',titlePlaceholder:'Un fin de semana por Veracruz', invalid:'Revisa los campos del viaje.', shareLoaded:'Ruta compartida. Puedes copiarla para crear tu propia versión.',maxStop:'Máximo 12 paradas.', maxExpense:'Máximo 40 gastos.', empty:'Todavía no hay gastos registrados.',badLink:'Este enlace compartido está dañado o no es compatible.'
    },
    en: {
      'tj-lang-label':'Language','tj-kicker':'TRIP JOURNAL','tj-headline':'Share your trip, not your private details','tj-lead':'Record stops and real spending, share a link, and help others plan their budget.',
      'tj-title-heading':'Your trip','tj-title-label':'Trip title','tj-month-label':'Approximate month (optional)','tj-people-label':'Travelers',
      'tj-stops-heading':'Stops','tj-stops-help':'Bring your route from the planner or add a place manually.',
      'tj-expenses-heading':'Expenses paid','tj-expenses-help':'Enter the amount paid by the group in MXN, not a per-person price.',
      'tj-stop-label':'Stop','tj-category-label':'Category','tj-item-label':'Purchase or service','tj-amount-label':'Total paid (MXN)',
      'tj-provider-label':'Provider or business (optional)','tj-note-label':'Details (optional)','tj-add-expense':'Add expense','tj-add-stop':'Add stop','tj-summary-heading':'Traveler-reported spending',
      'tj-total-label':'Recorded group expenses','tj-person-label':'Per traveler, assuming equal split',
      'tj-summary-note':'Totals include recorded spending only. Not verified prices or a complete travel quote.',
      'tj-share-heading':'Share or reuse','tj-privacy':'Review names, notes and providers before sharing. Do not include phone numbers, home addresses, bank details, identifiable receipts or exact travel dates.',
      'tj-consent-label':'I reviewed this information and want it included in a link readable by anyone who has it.',
      'tj-copy':'Copy share link','tj-edit':'Edit a copy','tj-back-map':'Back to map','tj-open-route':'Open route in planner',
      'tj-public-note':'The data lives in the URL itself. Nothing is uploaded to the site and your trip is not listed in a public feed.',
      draft:'Private draft',shared:'Shared trip · unverified',remove:'Remove',stop:'Stop',records:'Records',cats:{food:'Food',accommodation:'Accommodation',activity:'Activities',transport:'Transport',shopping:'Shopping',other:'Other'},
      saved:'Draft saved in this browser.',needs:'Add at least one stop.',consent:'Check the confirmation box before sharing.',sharedOK:'Link copied. Anyone with it can read this trip.',sharedFallback:'Copy this link:',tooLong:'Trip too large for one link. Remove details or split the trip.',
      newStop:'Town or place',itemPlaceholder:'Meal, room, ticket...',providerPlaceholder:'Name if you want to share it',notePlaceholder:'What was included',titlePlaceholder:'A weekend in Veracruz',invalid:'Check the trip fields.',shareLoaded:'Shared trip. You can make your own editable copy.',maxStop:'Maximum 12 stops.',maxExpense:'Maximum 40 expenses.',empty:'No recorded expenses yet.',badLink:'This shared link is damaged or incompatible.'
    },
    ja: {
      'tj-lang-label':'言語','tj-kicker':'旅の記録','tj-headline':'旅行費用とルートを共有','tj-lead':'訪問先と実際の支出を記録し、リンクを共有して他の旅行者の計画に役立てます。',
      'tj-title-heading':'旅行の情報','tj-title-label':'旅のタイトル','tj-month-label':'旅行月（任意）','tj-people-label':'旅行者数','tj-stops-heading':'訪問先','tj-stops-help':'ルートプランナーから読み込むか手動で追加します。',
      'tj-expenses-heading':'実際の支出','tj-expenses-help':'一人当たりでなくグループ全体のメキシコペソでの支払額を入力してください。',
      'tj-stop-label':'訪問先','tj-category-label':'項目','tj-item-label':'購入・サービス','tj-amount-label':'支払総額（MXN）',
      'tj-provider-label':'事業者名（任意）','tj-note-label':'メモ（任意）','tj-add-expense':'支出を追加','tj-add-stop':'訪問先を追加','tj-summary-heading':'旅行者による支出記録','tj-total-label':'グループ支出','tj-person-label':'人数で均等割した場合','tj-summary-note':'記録済みの支出のみです。確認済み価格や旅行全体の見積もりではありません。',
      'tj-share-heading':'共有・再利用','tj-privacy':'共有前に氏名、メモ、事業者名を確認してください。電話番号、自宅住所、銀行情報、個人情報を含む領収書、正確な旅行日は載せないでください。',
      'tj-consent-label':'誰でも読める共有リンクにこの内容を含めることを確認しました。','tj-copy':'共有リンクをコピー','tj-edit':'コピーして編集','tj-back-map':'地図に戻る','tj-open-route':'ルートを開く',
      'tj-public-note':'データはリンク自体に含まれ、サイトにアップロードされず公開フィードにも表示されません。',
      draft:'個人の下書き',shared:'共有旅行・未検証',remove:'削除',stop:'訪問先',records:'記録数',cats:{food:'食事',accommodation:'宿泊',activity:'体験',transport:'交通',shopping:'買い物',other:'その他'},
      saved:'このブラウザーに下書きを保存しました。',needs:'訪問先を追加してください。',consent:'共有前に確認欄をチェックしてください。',sharedOK:'リンクをコピーしました。リンクを知る人は旅行情報を閲覧できます。',sharedFallback:'次のリンクをコピーしてください：',tooLong:'共有リンクには情報が多すぎます。詳細を減らしてください。',
      newStop:'市町村・場所',itemPlaceholder:'食事、宿泊、入場料など',providerPlaceholder:'任意の事業者名',notePlaceholder:'料金に含まれるもの',titlePlaceholder:'ベラクルスの旅行',invalid:'入力内容を確認してください。',shareLoaded:'共有旅行です。自分用にコピーして編集できます。',maxStop:'最大12地点です。',maxExpense:'最大40件の支出です。',empty:'支出の記録はありません。',badLink:'共有リンクが壊れているか、対応していません。'
    }
  };
  let lang='es', shared=false, current={v:1,title:'Mi viaje por Veracruz',month:'',people:2,stops:[],expenses:[]};
  const money = x => new Intl.NumberFormat(lang==='ja'?'ja-JP':lang==='en'?'en-US':'es-MX',{style:'currency',currency:'MXN',maximumFractionDigits:2}).format(x);
  const t=()=>T[lang];
  function announce(message,err=false){$('tj-status').textContent=message; $('tj-status').classList.toggle('error',err);}
  function getRaw(){return {...current,title:$('tj-title').value.trim(),month:$('tj-month').value,people:Number($('tj-people').value)};}
  function persist(){if(shared)return;try{localStorage.setItem('vx_trip_diary_draft_v1',JSON.stringify(current));}catch(e){} }
  function sync(){if(shared)return;try{const candidate=getRaw();if(candidate.stops.length) current=C.normalize(candidate);else {if(!Number.isInteger(candidate.people)||candidate.people<1||candidate.people>30)throw Error('Invalid party size');if(candidate.month&&!/^\d{4}-(?:0[1-9]|1[0-2])$/.test(candidate.month))throw Error('Invalid month');current.title=candidate.title||current.title;current.month=candidate.month;current.people=candidate.people;}persist();}catch(e){announce(t().invalid,true);}render();}
  function item(tag,cls,str){const el=document.createElement(tag);if(cls)el.className=cls;if(str!==undefined)el.textContent=str;return el;}
  function render(){
    document.documentElement.lang=lang;document.body.classList.toggle('tj-viewonly',shared);
    for(const [id,str] of Object.entries(t()))if(id.startsWith('tj-')&&typeof str==='string'&&$(id)&&!['tj-title','tj-month','tj-people'].includes(id))$(id).textContent=str;
    $('tj-title').value=current.title;$('tj-month').value=current.month;$('tj-people').value=current.people;
    $('tj-title').placeholder=t().titlePlaceholder;
    $('tj-stop-name').placeholder=t().newStop;
    $('tj-item').placeholder=t().itemPlaceholder;
    $('tj-provider').placeholder=t().providerPlaceholder;
    $('tj-note').placeholder=t().notePlaceholder;
    $('tj-mode').textContent=shared?t().shared:t().draft;
    $('tj-edit').hidden=!shared;
    $('tj-copy').hidden=shared;
    $('tj-lang').value=lang;
    const stopList=$('tj-stops'),stopSelect=$('tj-expense-stop'),category=$('tj-category');
    stopList.replaceChildren();stopSelect.replaceChildren();category.replaceChildren();
    current.stops.forEach((s,i)=>{
      const li=item('li','tj-entry'),left=item('div','');left.append(item('strong','',s.name));
      if(s.id)left.append(item('small','',s.id.startsWith('municipality:')?'Municipio / Municipality':'Mapa / Map'));
      li.append(left);
      if(!shared){const b=item('button','tj-button secondary',t().remove);b.type='button';b.onclick=()=>{current.stops.splice(i,1);current.expenses=current.expenses.filter(e=>e.stopIndex!==i).map(e=>({...e,stopIndex:e.stopIndex>i?e.stopIndex-1:e.stopIndex}));persist();render();};li.append(b)}
      stopList.append(li);const o=item('option','',s.name);o.value=String(i);stopSelect.append(o);
    });
    C.CATEGORIES.forEach(c=>{const o=item('option','',t().cats[c]);o.value=c;category.append(o)});
    const expenses=$('tj-expenses');expenses.replaceChildren();
    if(!current.expenses.length)expenses.append(item('p','tj-muted',t().empty));
    current.expenses.forEach((e,i)=>{const row=item('div','tj-entry');const content=item('div','');content.append(item('strong','',e.label+' · '+money(e.amount)));content.append(item('small','',[current.stops[e.stopIndex]?.name,t().cats[e.category],e.provider,e.note].filter(Boolean).join(' · ')));row.append(content);if(!shared){const b=item('button','tj-button secondary',t().remove);b.type='button';b.onclick=()=>{current.expenses.splice(i,1);persist();render()};row.append(b)}expenses.append(row)});
    const {total,perPerson,byStop}= current.stops.length?C.summary(current):{total:0,perPerson:0,byStop:[]};
    $('tj-total').textContent=money(total);$('tj-person-total').textContent=money(perPerson);
    $('tj-breakdown').replaceChildren(...byStop.filter(x=>x.total>0).map(x=>item('p','tj-muted',x.name+': '+money(x.total))));
    const route=C.routeURL.bind(null);
    const link=current.stops.length?route(current):null;
    $('tj-open-route').hidden=!link;
    if(link)$('tj-open-route').href=link;
  }
  $('tj-lang').onchange=e=>{lang=e.target.value;try{localStorage.setItem('veracruz_language',lang)}catch{}render()};
  ['tj-title','tj-month','tj-people'].forEach(id=>$(id).addEventListener('change',sync));
  $('tj-add-stop').onclick=()=>{if(shared)return;const name=$('tj-stop-name').value.trim();if(!name)return;if(current.stops.length>=C.MAX_STOPS){announce(t().maxStop,true);return}if(current.stops.some(s=>s.name.toLocaleLowerCase()===name.toLocaleLowerCase()))return;current.stops.push({id:'',name:name.slice(0,100)});$('tj-stop-name').value='';persist();render()};
  $('tj-expense-form').onsubmit=e=>{e.preventDefault();if(shared)return;if(current.expenses.length>=C.MAX_EXPENSES){announce(t().maxExpense,true);return}try{const expense={stopIndex:Number($('tj-expense-stop').value),category:$('tj-category').value,label:$('tj-item').value,amount:Number($('tj-amount').value),provider:$('tj-provider').value,note:$('tj-note').value};const next=C.normalize({...getRaw(),expenses:[...current.expenses,expense]});current=next;persist();$('tj-item').value='';$('tj-amount').value='';$('tj-provider').value='';$('tj-note').value='';render();}catch(e){announce(t().invalid+': '+e.message,true)}};
  $('tj-edit').onclick=()=>{shared=false;try{history.replaceState(null,'',location.pathname+location.search)}catch(e){location.hash=''}persist();$('tj-consent').checked=false;render();announce(t().saved)};
  $('tj-copy').onclick=async()=>{if(!$('tj-consent').checked){announce(t().consent,true);return}try{current=C.normalize(getRaw());const payload=C.encode(current);const link=new URL('viajes.html',document.baseURI);link.search='';link.hash='trip='+payload;const url=link.toString();if(navigator.clipboard?.writeText){await navigator.clipboard.writeText(url);announce(t().sharedOK)}else{window.prompt(t().sharedFallback,url)}persist()}catch(e){announce((String(e.message).includes('large')?t().tooLong:t().invalid)+': '+e.message,true)}};
  function start(){
    try{const savedLang=localStorage.getItem('veracruz_language');if(T[savedLang])lang=savedLang;}catch(e){}
    const hash=location.hash.replace(/^#/,'');
    if(hash.startsWith('trip=')||hash.startsWith('draft=')){
      try{current=C.decode(hash.slice(hash.indexOf('=')+1));shared=hash.startsWith('trip=');}catch(e){announce(t().badLink,true);current={v:1,title:'Mi viaje por Veracruz',month:'',people:2,stops:[],expenses:[]};}
    }else try{const saved=localStorage.getItem('vx_trip_diary_draft_v1');if(saved)current=C.normalize(JSON.parse(saved))}catch(e){}
    render();if(shared)announce(t().shareLoaded);
  }
  start();
})();
