/* Pure validation and serialization helpers. No network, accounts or analytics. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.VXTripJournalCore = factory();
})(typeof window !== 'undefined' ? window : this, function () {
  'use strict';
  const VERSION = 1;
  const MAX_STOPS = 12, MAX_EXPENSES = 40, MAX_CHARS = 8000;
  const CATEGORIES = ['food','accommodation','activity','transport','shopping','other'];
  const ascii = s => String(s == null ? '' : s).trim();
  const text = (s, max = 150) => ascii(s).slice(0, max);
  function normalize(raw) {
    if (!raw || typeof raw !== 'object') throw Error('Invalid trip');
    const people = Number(raw.people);
    if (!Number.isInteger(people) || people < 1 || people > 30) throw Error('Invalid party size');
    const month = ascii(raw.month);
    if (month && !/^\d{4}-(?:0[1-9]|1[0-2])$/.test(month)) throw Error('Invalid month');
    const stops = (Array.isArray(raw.stops) ? raw.stops : []).slice(0, MAX_STOPS).map(s => ({
      id: text(s.id, 160), name: text(s.name, 100)
    })).filter(s => s.name);
    if (stops.length < 1) throw Error('At least one stop is required');
    if (Array.isArray(raw.stops) && raw.stops.length > MAX_STOPS) throw Error('Too many stops');
    if (new Set(stops.map(s => s.id || s.name.toLowerCase())).size !== stops.length) throw Error('Duplicate stops');
    const expenses = (Array.isArray(raw.expenses) ? raw.expenses : []).map(e => {
      const amount = Number(e.amount);
      if (!Number.isFinite(amount) || amount < 0.01 || amount > 1000000 || Math.abs(Math.round(amount * 100) - amount * 100) > 0.000001) throw Error('Invalid expense');
      const stopIndex = Number(e.stopIndex);
      if (!Number.isInteger(stopIndex) || stopIndex < 0 || stopIndex >= stops.length) throw Error('Expense stop missing');
      if (!CATEGORIES.includes(e.category)) throw Error('Invalid category');
      return {
        stopIndex, category: e.category, label: text(e.label, 110), amount,
        provider: text(e.provider, 120), note: text(e.note, 200)
      };
    });
    if (expenses.length > MAX_EXPENSES) throw Error('Too many expenses');
    return {v:VERSION, title:text(raw.title, 100) || 'Mi viaje por Veracruz', month, people, stops, expenses};
  }
  function toBase64Url(rawText) {
    const bytes = new TextEncoder().encode(rawText);
    let str = '';
    for (const b of bytes) str += String.fromCharCode(b);
    return btoa(str).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/,'');
  }
  function fromBase64Url(payload) {
    if (!/^[A-Za-z0-9_-]+$/.test(payload) || payload.length > MAX_CHARS) throw Error('Invalid shared link');
    const ascii = atob(payload.replace(/-/g,'+').replace(/_/g,'/'));
    return new TextDecoder('utf-8',{fatal:true}).decode(Uint8Array.from(ascii, c=>c.charCodeAt(0)));
  }
  function encode(data) {
    const normalized = normalize(data);
    const coded = toBase64Url(JSON.stringify(normalized));
    if (coded.length > MAX_CHARS) throw Error('Trip too large for a single link');
    return coded;
  }
  function decode(payload) {
    const raw = JSON.parse(fromBase64Url(payload));
    if (raw.v !== VERSION) throw Error('Unsupported trip version');
    return normalize(raw);
  }
  function summary(data) {
    const trip=normalize(data);
    const total = Math.round(trip.expenses.reduce((s,e)=>s+e.amount,0)*100)/100;
    const byStop = trip.stops.map((s,i)=>({name:s.name, total:Math.round(trip.expenses.filter(e=>e.stopIndex===i).reduce((a,e)=>a+e.amount,0)*100)/100}));
    return {total, perPerson: Math.round(total/trip.people*100)/100, byStop, count:trip.expenses.length};
  }
  function routeURL(data) {
    const trip = normalize(data);
    const validIDs = trip.stops.map(s=>s.id).filter(s=>/^(municipality:|attraction:)/.test(s));
    if (validIDs.length !== trip.stops.length) return null;
    return 'index.html?vxroute='+encodeURIComponent(validIDs.join(','));
  }
  return {VERSION,MAX_STOPS,MAX_EXPENSES,CATEGORIES,normalize,encode,decode,summary,routeURL};
});
