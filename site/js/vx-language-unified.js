// Keeps the visual selector and language preference consistent without replacing
// the page-specific dictionaries/translations. V1, additive and idempotent.
(()=>{'use strict';
  const names={es:'Idioma',en:'Language',ja:'言語'};
  const ids=['language-select','tj-lang','vx-lang','vp-language','lang'];
  const sel=ids.map(x=>document.getElementById(x)).find(Boolean);
  if(!sel)return;
  const current=sel.value;
  ['es','en','ja'].forEach(v=>{const opt=[...sel.options].find(x=>x.value===v);if(opt)sel.append(opt)});
  sel.value=current;
  sel.classList.add('vx-language-select');
  sel.setAttribute('aria-label','Idioma / Language / 言語');
  const old=sel.closest('label, .language-control, .vp-lang-control');
  if(old)old.classList.add('vx-common-language');
  function updateLabel(){
    let l=sel.value;
    if(!names[l]){try{l=localStorage.getItem('veracruz_language')}catch(e){}};
    if(!names[l])l='es';
    const container=sel.closest('.vx-common-language');
    if(!container)return;
    const label=container.querySelector('label[for],span[data-vpi18n],span:not([class]),#tj-lang-label,#vx-lang-label');
    if(label&&label!==sel)label.textContent=names[l];
  }
  sel.addEventListener('change',()=>{try{localStorage.setItem('veracruz_language',sel.value)}catch(e){}updateLabel()});
  updateLabel();
  setTimeout(updateLabel,120);
})();
