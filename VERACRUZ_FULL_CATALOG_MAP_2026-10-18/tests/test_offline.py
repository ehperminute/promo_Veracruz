from pathlib import Path
from playwright.sync_api import sync_playwright
import json,tempfile,shutil,subprocess
P=Path('/mnt/data/VERACRUZ_FULL_CATALOG_MAP_2026-10-18')
root=Path(tempfile.mkdtemp());shutil.copytree('/mnt/data/veracruz_attractions_v2_patch/testrepo/site',root/'site');shutil.copytree('/mnt/data/veracruz_attractions_v2_patch/tools',root/'tools');shutil.copy2('/mnt/data/veracruz_attractions_v2_patch/assets/attractions.csv',root/'site/data/attractions.csv')
subprocess.run(['python',str(root/'tools/build_attractions.py'),str(root)],check=True)
subprocess.run(['python',str(P/'install_full_catalog.py'),str(root)],check=True)
site=root/'site'
fake=(Path('/mnt/data/attraction_integration_work/test_browser_offline.py').read_text()).split("fake='''",1)[1].split("'''",1)[0]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1400,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content('<html lang="en"><body><section id="veracruz-map-section"></section></body></html>')
 data={file.name:json.loads(file.read_text()) for file in (site/'data').glob('*.json')}
 data.update({file.name:json.loads(file.read_text()) for file in (site/'data').glob('*.geojson')})
 page.evaluate('''p=>{window.fetch=(uri)=>{let x=uri.split('/').at(-1).split('?')[0],o=p[x];return Promise.resolve({ok:!!o,status:o?200:404,json:()=>Promise.resolve(o)});};}''',data)
 page.add_script_tag(content=fake)
 page.add_style_tag(content=(site/'css/map-explorer.css').read_text())
 page.add_style_tag(content=(site/'css/map-attractions.css').read_text())
 page.add_script_tag(content=(site/'js/map-explorer.js').read_text())
 page.add_script_tag(content=(site/'js/map-attractions.js').read_text())
 page.wait_for_function('document.querySelectorAll(".vxa-marker").length===35',timeout=15000)
 page.locator('#vx-search').fill('Cuyuxquihui')
 page.wait_for_function('document.querySelectorAll(".vxc-record").length>=1')
 page.locator('.vxc-record').first.click()
 assert 'Cuyuxquihui' in page.locator('.vxc-title').inner_text()
 page.locator('.vxc-back').click()
 page.locator('#vx-search').fill('Finca Siete Lunas')
 page.locator('.vxc-record').first.click()
 assert 'Finca Siete Lunas' in page.locator('.vxc-title').inner_text()
 assert 'municipality' in page.locator('.vxc-disclaimer').inner_text().lower()
 page.locator('.vxc-back').click()
 page.locator('#vx-search').fill('Todo Veracruz es Bello')
 page.locator('.vxc-record').first.click()
 assert 'Todo Veracruz' in page.locator('.vxc-title').inner_text()
 assert 'not one geographic point' in page.locator('.vxc-disclaimer').inner_text()
 page.locator('.vxc-back').click();page.locator('#vx-search').fill('El Tajin')
 page.locator('.vxc-record').first.click()
 assert 'El Tajín' in page.locator('.vxc-title').inner_text()
 print('PASS: 35 markers; mapped attraction, municipal lead and multi-town tourism product searches; guide panel; no script errors')
 print('errors',errors);assert not errors
 browser.close()
shutil.rmtree(root)
