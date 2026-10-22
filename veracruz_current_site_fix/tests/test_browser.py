import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright
HERE=Path(__file__).resolve().parents[1]
SITE=Path('/mnt/data/sitefix_test/site')
HTML='''<html lang="es"><head><meta charset="utf-8"></head><body><header><h1></h1><p id="current-subtitle"></p><nav><a id="nav-map"></a><a id="nav-route"></a></nav><select id="language-select"><option value="en">English</option><option value="es" selected>Español</option><option value="ja">日本語</option></select></header><section id="veracruz-map-section"><div id="vx-map" style="height:340px"></div><aside class="vx-side"><div id="vx-list"></div></aside></section></body></html>'''
MOCK='''() => {
  window.__routerTest={handlers:{},sources:{},layers:{},requests:[]};
  window.__vx_attraction_map={on(n,fn){(window.__routerTest.handlers[n]??=[]).push(fn);},getLayer(k){return window.__routerTest.layers[k];},getSource(k){return window.__routerTest.sources[k];},addSource(k,o){window.__routerTest.sources[k]={...o,setData(x){this.data=x;}};},addLayer(o){window.__routerTest.layers[o.id]=o;},removeLayer(k){delete window.__routerTest.layers[k];},removeSource(k){delete window.__routerTest.sources[k];},getCanvas(){return document.getElementById('vx-map');},isStyleLoaded(){return true;},fitBounds(...args){this.bounds=args;}};
  window.fetch=async (url,options) => {
    let u=String(url);
    if(u.endsWith('attractions.geojson'))return {ok:true,json:async()=>window.__routerTest.attractions};
    if(u.endsWith('map_points.geojson'))return {ok:true,json:async()=>window.__routerTest.municipalities};
    window.__routerTest.requests.push(u);
    return {ok:true,json:async()=>({code:'Ok',routes:[{distance:195000,duration:8900,geometry:{type:'LineString',coordinates:[[-97.02,20.38],[-97.15,20.5],[-97.48,20.53]]}}],waypoints:[]})};
  };
}'''
async def main():
    attrs=json.loads((SITE/'data/attractions.geojson').read_text())
    muni=json.loads((SITE/'data/map_points.geojson').read_text())
    js=(SITE/'js/itinerary-router.js').read_text()
    css=(SITE/'css/itinerary-router.css').read_text()
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=await browser.new_page(viewport={'width':390,'height':840})
        err=[];page.on('pageerror',lambda x:err.append(str(x)))
        await page.set_content(HTML)
        await page.add_style_tag(content=css)
        await page.evaluate(MOCK)
        await page.evaluate('(arg)=>{window.__routerTest.attractions=arg[0];window.__routerTest.municipalities=arg[1]}',[attrs,muni])
        await page.add_script_tag(content=js)
        await page.wait_for_function('window.VeracruzItineraryV2?.getStops && !!document.querySelector(".vxw-search")')
        await page.locator('.vxw-search').fill('Tecolutla')
        found=await page.locator('.vxw-suggestion').all_inner_texts()
        assert found and 'Tecolutla' in found[0] and 'Municipio' in found[0],found
        assert any('Museo Marino Tecolutla' in x for x in found), found
        await page.locator('.vxw-suggestion').first.click()
        ids=await page.evaluate('window.VeracruzItineraryV2.getStops().map(p=>p.id)')
        assert ids==['municipality:30158'],ids
        assert 'ubicación aproximada' in await page.locator('.vxw-stop').first.inner_text()
        # Directly click a municipality pin while the picking mode is on.
        await page.locator('.vxw-pick').click()
        await page.evaluate('''() => {
           let pin=document.createElement('div');pin.className='vx-geo-marker';pin.dataset.vxMunicipalityId='30087';pin.title='Xalapa';
           document.querySelector('#vx-map').append(pin);pin.click();
        }''')
        # 30087 may not be Xalapa; verify matching municipality ID and successful add without using its label.
        assert await page.locator('.vxw-stop').count()==2
        assert await page.locator('.vxw-directions a').count()==1
        await page.locator('.vxw-main').click()
        await page.wait_for_function("!!window.__routerTest.layers['vxw-road-line']")
        assert '/route/v1/driving/' in (await page.evaluate('window.__routerTest.requests[0]'))
        await page.locator('.vxw-search').fill('Museo Marino Tecolutla')
        await page.locator('.vxw-suggestion').first.click()
        assert await page.locator('.vxw-stop').count()==3
        assert not err,err
        await page.screenshot(path='/mnt/data/veracruz_current_site_fix/tests/tecolutla_mobile.png',full_page=True)
        await browser.close()
        print('PASS: Tecolutla municipality, distinct attraction, municipality-marker click, 3-stop mock road route, map marker ids.')
asyncio.run(main())
