(() => {
  'use strict';
  if (!window.VXTripJournalCore) return;
  const C=window.VXTripJournalCore;
  const L={es:'Compartir ruta y gastos',en:'Share route and spending',ja:'ルートと支出を共有'};
  const language=()=>{const val=document.getElementById('language-select')?.value||'es';return L[val]?val:'es'};
  function attach(){
    const planner=document.querySelector('#vxw-itinerary');
    if(!planner||document.getElementById('tj-planner-launch'))return false;
    const button=document.createElement('button');button.type='button';button.id='tj-planner-launch';button.className='vxw-subtle';button.textContent=L[language()];
    button.addEventListener('click',()=>{
      const stops=window.VeracruzItineraryV2?.getStops?.()||[];
      const trip={v:1,title:'Ruta por Veracruz',month:'',people:2,stops:stops.slice(0,C.MAX_STOPS).map(s=>({id:String(s.id||''),name:String(s.name||'')})),expenses:[]};
      if(!trip.stops.length){window.location.href='viajes.html';return;}
      const url=new URL('viajes.html',document.baseURI);url.hash='draft='+C.encode(trip);
      window.location.href=url.href;
    });
    const el=planner.querySelector('.vxw-buttons')||planner;el.append(button);
    const sel=document.getElementById('language-select');sel?.addEventListener('change',()=>{button.textContent=L[language()]});
    return true;
  }
  if(!attach()){
    let count=0;const timer=setInterval(()=>{count++;if(attach()||count>=35)clearInterval(timer)},300);
  }
})();
