/* Non-invasive official-source excerpts for the existing Veracruz explorer.
   Independent of map-explorer.js internal functions; safe with versioned map code.
   Every excerpt is extracted from site/data/map_guide_notes.json, NOT invented. */
(() => {
  'use strict';
  const root = document.getElementById('veracruz-map-section');
  if (!root) return;
  const normalize = value => String(value || '').normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  const langs = {
    en: { title:'Original tourism listings', source:'Read the original listing ↗',
      note:'Excerpt from the original Spanish source. This listing may cover more than one municipality.' },
    es: { title:'Fichas originales de turismo', source:'Leer ficha original ↗',
      note:'Extracto de la fuente original en español. Esta ficha puede abarcar más de un municipio.' },
    ja: { title:'公式観光情報の原文', source:'公式情報を読む ↗',
      note:'スペイン語の原文からの抜粋。複数の自治体に関する情報を含む場合があります。' }
  };
  const safeUrl = value => {
    try { const u = new URL(value); return u.protocol === 'https:' ? u.href : null; }
    catch { return null; }
  };
  const el = (tag, cls, text) => {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = String(text);
    return node;
  };
  let features = [], notes = {}, scheduled = false;
  let detailObserver;
  const whenReady = async () => {
    try {
      const requests = await Promise.all([
        fetch('data/map_points.geojson', {cache:'no-store'}),
        fetch('data/map_guide_notes.json', {cache:'no-store'})
      ]);
      if (!requests.every(r => r.ok)) throw new Error('map geographic or guide data not found');
      const [geo, guide] = await Promise.all(requests.map(r => r.json()));
      features = (geo.features || []);
      notes = guide;
      sync();
    } catch (err) { console.warn('Veracruz original-source guide add-on:', err); }
  };
  const currentLanguage = () => {
    const lang = document.getElementById('language-select')?.value || document.documentElement.lang || 'en';
    return langs[String(lang).toLowerCase().slice(0,2)] ? String(lang).toLowerCase().slice(0,2) : 'en';
  };
  function sync() {
    scheduled = false;
    const detail = root.querySelector('#vx-detail:not([hidden])');
    const h = detail?.querySelector('.vx-detail-top h3, h3');
    const g = detail?.querySelector('.vx-guide-title h4, .vx-guide-title');
    if (!h || !g || !features.length) return;
    const municipality = normalize(h.textContent);
    const title = normalize(g.textContent);
    const f = features.find(v => normalize(v.properties?.name) === municipality);
    if (!f) return;
    const options = [...(root.querySelector('#vx-activity')?.options || [])];
    const a = (f.properties?.activities || []).find(act => {
      const names = [act.id, act.name_es, act.name_en, String(act.id || '').replace(/_/g,' ')];
      const selected = options.find(opt => opt.value === act.id);
      if (selected) names.push(selected.textContent);
      return names.some(n => normalize(n) === title);
    });
    if (!a) return;
    const key = String(f.properties.municipality_id) + '::' + a.id;
    const products = (notes[key]?.official_products || []).filter(p => p.original_preview_es && safeUrl(p.source_url));
    const existing = detail.querySelector('.vx-restored-product-sources');
    if (existing?.dataset.key === key && existing.dataset.lang === currentLanguage()) return;
    if (existing) existing.remove();
    if (!products.length) return;
    const lang = currentLanguage(); const words = langs[lang];
    const wrap = el('section','vx-restored-product-sources');
    wrap.dataset.key=key; wrap.dataset.lang=lang;
    wrap.append(el('h4','',words.title));
    for (const [idx,product] of products.entries()) {
      const exp=el('details','vx-original-product'); if (idx===0) exp.open=true;
      exp.append(el('summary','',product.title));
      const p=el('p','vx-original-preview',product.original_preview_es);p.lang='es';exp.append(p);
      exp.append(el('p','vx-note',words.note));
      const link=el('a','vx-source-link',words.source);
      link.href=safeUrl(product.source_url);link.target='_blank';link.rel='noopener noreferrer';
      exp.append(link);wrap.append(exp);
    }
    g.insertAdjacentElement('afterend',wrap);
  }
  const schedule = () => {
    if (!scheduled) {scheduled=true; requestAnimationFrame(sync);}
  };
  const start = () => {
    const detail = root.querySelector('#vx-detail');
    if (!detail) return false;
    if (detailObserver) detailObserver.disconnect();
    detailObserver = new MutationObserver(schedule);
    detailObserver.observe(detail,{subtree:true,childList:true,attributes:true,attributeFilter:['hidden']});
    document.addEventListener('change',schedule);
    new MutationObserver(schedule).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
    whenReady();
    return true;
  };
  if (!start()) {
    const wait = new MutationObserver(() => {if (start()) wait.disconnect();});
    wait.observe(root,{childList:true,subtree:true});
  }
})();
