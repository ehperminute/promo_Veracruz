from pathlib import Path
from playwright.sync_api import sync_playwright
asset=Path(__file__).resolve().parents[1]/'assets'
with sync_playwright() as p:
    b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
    page=b.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content('''<html lang="es"><body><select id="language-select"><option value="es" selected>ES</option><option value="en">EN</option><option value="ja">JA</option></select><details id="vxp-prices" open><summary>Estimar costos</summary><p class="vxp-intro">Publicado y estimado</p><div class="vxp-fields"><input data-price-input="people" value="2"/><input data-price-input="days" value="2"/><input data-price-input="nights" value="1"/><input data-price-input="rooms" value="1"/><input data-price-input="tolls" value=""/><input data-price-input="efficiency" value=""/><input data-price-input="fuelPrice" value=""/><input data-price-input="additional" value=""/></div><div class="vxp-offers"></div></details></body></html>''')
    page.evaluate('''() => {
      window.testKm=null;
      window.VeracruzTripPricing={getEstimate:()=>({roadKm:window.testKm,published:0,items:[]}),getOffers:()=>[]};
      window.VeracruzPricingCore={isLodging:()=>false};
      window.VeracruzItineraryV2={getStops:()=>[{name:'Xalapa',kind:'municipality'},{name:'Córdoba',kind:'municipality'},{name:'Tamiahua',kind:'municipality'}]};
    }''')
    page.add_style_tag(path=str(asset/'budget-range.css'))
    page.add_script_tag(path=str(asset/'budget-range-core.js'))
    page.add_script_tag(path=str(asset/'budget-range.js'))
    root=page.locator('#vxr-budget'); assert root.count()==1
    assert 'Presupuesto de referencia' in root.inner_text()
    assert 'gasolina pendiente' in root.inner_text()
    initial=root.locator('.vxr-total').inner_text()
    page.evaluate('window.testKm=120;document.dispatchEvent(new CustomEvent("vxw:route-calculated"))')
    after=root.locator('.vxr-total').inner_text()
    assert initial!=after,(initial,after)
    assert '237' in root.locator('.vxr-warning').inner_text()
    page.locator('#vxr-mode').select_option('light')
    low=root.locator('.vxr-total').inner_text();assert low!=after
    page.locator('[data-price-input="people"]').fill('4')
    high=root.locator('.vxr-total').inner_text();assert high!=low
    page.locator('#language-select').select_option('en')
    assert 'Planning envelope' in root.inner_text()
    page.locator('#language-select').select_option('ja')
    assert '予算' in root.inner_text()
    page.locator('#language-select').select_option('es')
    page.screenshot(path='/mnt/data/veracruz_budget_range_test/preview.png',full_page=True)
    assert not errors, errors
    print('PASS: browser cost range displayed with three unpriced stops, fuel update, editable assumptions, party changes, ES/EN translations')
    b.close()
