/* Pure estimation engine. Browser global and Node module. No provider availability is inferred. */
(function(global,factory){
 const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;
 global.VeracruzPricingCore=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 const norm=s=>String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9 ]/g,' ').replace(/\s+/g,' ').trim();
 const bounded=(v,lo,hi)=>{if(v===''||v==null)return null;const n=Number(v);return Number.isFinite(n)&&n>=lo&&n<=hi?n:null;};
 const isLodging=r=>/habitaci[oó]n por noche/i.test(r.unit||'');
 const isRegional=r=>!/^[^/]+$/.test(r.municipality_or_area||'')||/circuito/i.test(r.municipality_or_area||'');
 function matching(stops,rows){
   const cities=new Set(stops.map(p=>norm(p.kind==='municipality'?p.name:p.municipality)).filter(Boolean));
   return rows.filter(r=>!isRegional(r)&&cities.has(norm(r.municipality_or_area)));
 }
 function quote(r,people,days,nights,rooms){
   const unit=norm(r.unit),base=bounded(r.price_mxn,0,1e8),notes=[];
   if(base===null||String(r.can_auto_total).toUpperCase()==='NO')return {usable:false,amount:null,notes:['Unconfirmed selling unit or price. Reference only.']};
   let quantity;
   if(/habitacion por noche/.test(unit)){
     const capacity=/hasta cuatro huespedes|hasta 4 huespedes/.test(norm(r.terms_and_exclusions))?4:null;
     const needed=capacity?Math.ceil(people/capacity):rooms;
     const billedRooms=Math.max(rooms,needed);
     quantity=billedRooms*nights;
     if(billedRooms>rooms)notes.push('Room capacity requires at least '+billedRooms+' rooms for this party.');
     if(!nights)notes.push('No nights selected.');
   }
   else if(/por persona|por huesped|por visitante/.test(unit)){quantity=people;
      const terms=norm(r.terms_and_exclusions);
      if(/minimo cuatro|minimum four/.test(terms)&&people<4){quantity=4;notes.push('Minimum billing: 4 people.');}
      if(/minimo tres|minimum three/.test(terms)&&people<3){quantity=3;notes.push('Minimum billing: 3 people.');}
      if(/minimo 20|minimo veinte/.test(terms)&&people<20){quantity=20;notes.push('Minimum billing: 20 people.');}
      if(/habitacion doble/.test(unit))notes.push('Double-occupancy package: confirm room allocation.');
   }else return {usable:false,amount:null,notes:['Unknown unit.']};
   const taxExtra=/iva adicional/i.test(r.terms_and_exclusions||'');
   const tax=taxExtra?base*quantity*.16:0;
   if(taxExtra)notes.push('Illustrative 16% VAT added: confirm applicable taxes.');
   if(/desde|from|FROM_/i.test((r.price_basis||'')+' '+(r.terms_and_exclusions||'')))notes.push('Advertised starting price: actual date may cost more.');
   if(/incluye hospedaje|incluye alojamiento|algunos traslados/i.test(r.terms_and_exclusions||''))notes.push('Package may include lodging or transfers; avoid double counting.');
   return {usable:true,quantity,base:base*quantity,tax,amount:Math.round((base*quantity+tax)*100)/100,notes};
 }
 function estimate({offers=[],party=2,days=2,nights=1,rooms=1,roadKm=null,manualKm=null,efficiency=null,fuelPrice=null,tolls=null,mealsPerPersonDay=null,manualLodgingRoomNight=null,additional=null}={}){
  const p=bounded(party,1,100)||1,d=bounded(days,1,100)||1,n=bounded(nights,0,100)??0,r=bounded(rooms,1,50)||1;
  const items=[],warnings=[];let published=0,assumptions=0,hotelIncluded=false;
  for(const x of offers){const q=quote(x,p,d,n,r);if(!q.usable){warnings.push(x.offering+': selling unit unverified; excluded.');continue;}
    if(isLodging(x)||/incluye hospedaje|incluye alojamiento/i.test(x.terms_and_exclusions||''))hotelIncluded=true;
    for(const note of q.notes)warnings.push(x.offering+': '+note);
    published+=q.amount;items.push({category:'published',name:x.offering,provider:x.provider,amount:q.amount,quantity:q.quantity,notes:q.notes,source_url:x.source_url});
  }
  if(offers.length>1&&offers.some(o=>/paquete|package|tour.*noche|incluye hospedaje|incluye alojamiento/i.test((o.offering||'')+' '+(o.terms_and_exclusions||''))))warnings.push('Combined selections may overlap in included lodging, meals, transfers or entrances. Confirm inclusions before booking.');
  const km=bounded(roadKm,0,100000)??bounded(manualKm,0,100000);
  let fuel=null;
  if(km!==null&&bounded(efficiency,1,100)!==null&&bounded(fuelPrice,0,1000)!==null){fuel=Math.round(km/Number(efficiency)*Number(fuelPrice)*100)/100;assumptions+=fuel;items.push({category:'assumption',name:'Fuel',amount:fuel});}
  if(bounded(tolls,0,1e6)!==null){assumptions+=Number(tolls);items.push({category:'assumption',name:'Tolls (user supplied)',amount:Number(tolls)});}
  if(bounded(mealsPerPersonDay,0,1e6)!==null){const v=Number(mealsPerPersonDay)*p*d;assumptions+=v;items.push({category:'assumption',name:'Meals (user estimate)',amount:v});}
  if(!hotelIncluded&&n>0&&bounded(manualLodgingRoomNight,0,1e6)!==null){const v=Number(manualLodgingRoomNight)*r*n;assumptions+=v;items.push({category:'assumption',name:'Lodging (user estimate)',amount:v});}
  if(hotelIncluded&&bounded(manualLodgingRoomNight,0,1e6)!==null)warnings.push('User lodging estimate excluded because a published room rate is selected.');
  if(bounded(additional,0,1e6)!==null){assumptions+=Number(additional);items.push({category:'assumption',name:'Other (user supplied)',amount:Number(additional)});}
  const missing=[];
  if(!offers.length)missing.push('Activity and entrance fees');
  if(n>0&&!hotelIncluded&&bounded(manualLodgingRoomNight,0,1e6)===null)missing.push('Accommodation');
  if(km===null)missing.push('Driving distance (calculate a route or enter road kilometres)');
  else if(fuel===null)missing.push('Fuel (vehicle consumption / fuel price)');
  if(bounded(tolls,0,1e6)===null)missing.push('Tolls');
  if(bounded(mealsPerPersonDay,0,1e6)===null)missing.push('Meals');
  return {published:Math.round(published*100)/100,assumptions:Math.round(assumptions*100)/100,subtotal:Math.round((published+assumptions)*100)/100,items,missing,warnings,roadKm:km,roadKmSource:bounded(roadKm,0,100000)!==null?'routing response':km!==null?'user supplied':null};
 }
 return {norm,bounded,isLodging,isRegional,matching,quote,estimate};
});
