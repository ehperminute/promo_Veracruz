/* Reference spending envelope; NOT locally sampled rates, supplier quotes or confidence bounds. */
(function(global,factory){
 const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 global.VeracruzBudgetRangeCore=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 const bounded=(x,lo,hi)=>{if(x===''||x===null||x===undefined)return null;const v=Number(x);return Number.isFinite(v)&&v>=lo&&v<=hi?v:null;};
 const defaults={
  light:{room:[450,900],food:[150,300],activity:[0,250]},
  balanced:{room:[700,1600],food:[220,500],activity:[100,500]},
  flexible:{room:[1200,2600],food:[350,850],activity:[250,1000]}
 };
 function compute(o={}){
  const people=bounded(o.people,1,100), days=bounded(o.days,1,100),nights=bounded(o.nights,0,100),rooms=bounded(o.rooms,1,50),paidActivities=bounded(o.paidActivities,0,100);
  const required={people,days,nights,rooms,paidActivities};
  for(const [k,v] of Object.entries(required))if(v===null)throw Error('Invalid '+k);
  const bands=o.bands||defaults.balanced;
  for(const key of ['room','food','activity']){
   const b=bands[key];if(!Array.isArray(b)||b.length!==2||bounded(b[0],0,1e6)===null||bounded(b[1],0,1e6)===null||Number(b[0])>Number(b[1]))throw Error('Invalid assumption band: '+key);
  }
  const pricedActivities=bounded(o.pricedActivities??0,0,100);
  if(pricedActivities===null)throw Error('Invalid priced activity count');
  const unknownActivityCount=Math.max(0,paidActivities-pricedActivities);
  const roomCount=(o.lodgingIncluded||nights===0)?0:rooms*nights;
  const prices={room:[roomCount*bands.room[0],roomCount*bands.room[1]],food:[people*days*bands.food[0],people*days*bands.food[1]],activity:[people*unknownActivityCount*bands.activity[0],people*unknownActivityCount*bands.activity[1]]};
  const published=bounded(o.published??0,0,1e8);
  if(published===null)throw Error('Invalid published subtotal');
  const km=bounded(o.km,0,100000);
  const efficiency=bounded(o.efficiency,1,100), fuelPrice=bounded(o.fuelPrice,0,1000);
  const fuel=(km!==null&&efficiency!==null&&fuelPrice!==null)?Math.round(km/efficiency*fuelPrice*100)/100:null;
  const tolls=bounded(o.tolls,0,1e7),additional=bounded(o.additional,0,1e7);
  const extra=(fuel??0)+(tolls??0)+(additional??0)+published;
  const lo=Math.round((Object.values(prices).reduce((s,b)=>s+b[0],0)+extra)*100)/100;
  const hi=Math.round((Object.values(prices).reduce((s,b)=>s+b[1],0)+extra)*100)/100;
  const missing=[];
  if(km===null)missing.push('road distance / fuel');
  else if(fuel===null)missing.push('fuel parameters');
  if(tolls===null)missing.push('tolls');
  missing.push('supplier availability and unlisted expenses');
  return {low:lo,high:hi,assumed:prices,published,fuel,tolls,km,unknownActivityCount,roomCount,missing};
 }
 return {compute,defaults,bounded};
});
