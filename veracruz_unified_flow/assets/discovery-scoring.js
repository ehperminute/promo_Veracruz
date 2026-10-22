/* Documented novelty, not measured crowd levels, search popularity or visitor demand. */
(function(root,factory){const lib=factory();if(typeof module==='object'&&module.exports)module.exports=lib;if(root)root.VXDiscoveryScore=lib;})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 // Auto-suggestions must not advertise access to ceremonies or professional fieldwork
 // without community/operator permission. Records stay available for manual exploration.
 const autoSuitable=r=>r && !/(ritual|ceremony|research_expedition|research_fieldwork)/i.test(String(r.feature_id||''));
 const credible=r=>r&&r.original_text_support===true&&Array.isArray(r.source_urls)&&r.source_urls.some(u=>typeof u==='string'&&/^https:\/\//.test(u));
 function frequency(rows){const links=new Map();for(const r of rows){if(!r||!r.feature_id||!r.municipality_id)continue;let set=links.get(r.feature_id);if(!set){set=new Set();links.set(r.feature_id,set);}set.add(r.municipality_id);}return new Map([...links].map(([k,v])=>[k,v.size]));}
 function rarity(r,freq){return 1/Math.sqrt(Math.max(1,freq.get(r.feature_id)||1));}
 function candidate(c,freq){const verified=c.rows.filter(r=>credible(r)&&autoSuitable(r));if(!verified.length)return -Infinity;
  const unique=new Map();for(const r of verified)if(!unique.has(r.feature_id))unique.set(r.feature_id,r);
  const distinctive=[...unique.values()].map(r=>rarity(r,freq)).sort((a,b)=>b-a);
  // Up to three uncommon documented activities; don't reward bulk catalog entries without limit.
  return distinctive.slice(0,3).reduce((v,x)=>v+15*x,0)+3*Math.min(3,verified.length)-Math.max(0,c.rows.length-3)*2.0;
 }
 function portfolio(chosen,freq,distanceKm,rng=Math.random){const unique=new Map(),families=new Set();let sourceCount=0;for(const c of chosen){let hasProof=false;for(const r of c.rows){if(!credible(r)||!autoSuitable(r))continue;hasProof=true;families.add(r.family);if(!unique.has(r.feature_id))unique.set(r.feature_id,r);sourceCount++;}if(!hasProof)return -Infinity;}
 const uncommon=[...unique.values()].map(r=>rarity(r,freq)).sort((a,b)=>b-a);
 const rareBonus=uncommon.slice(0,8).reduce((acc,x)=>acc+10*x,0);
 const distinctPlaces=new Set(chosen.map(c=>c.id)).size;
 // Reward distinct activities and families across a practical trip, not most records per city.
 return rareBonus+4*families.size+2*distinctPlaces+Math.min(5,sourceCount)*0.5
   -chosen.reduce((sum,c)=>sum+Math.max(0,c.rows.length-4)*3.0,0)
   -Math.max(0,distanceKm)*0.025+(rng()-0.5)*11;
 }
 function reasons(c,freq){return c.rows.filter(r=>credible(r)&&autoSuitable(r)).slice().sort((a,b)=>rarity(b,freq)-rarity(a,freq)).slice(0,2).map(r=>({feature_id:r.feature_id,label_es:r.label_es,label_en:r.label_en,municipalities:freq.get(r.feature_id)||1,source_url:r.source_urls.find(u=>/^https:\/\//.test(u))}));}
 return {credible,autoSuitable,frequency,rarity,candidate,portfolio,reasons};
});
