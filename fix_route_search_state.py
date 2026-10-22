from pathlib import Path
import re, shutil, sys, json
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path.cwd()
site=root/'site'
js=site/'js/itinerary-router.js'; html=site/'index.html'
if not js.is_file() or not html.is_file(): raise SystemExit('STOP: Run this from the promo_Veracruz repository root.')
data={}
for name in ('map_points.geojson','attractions.geojson'):
    path=site/'data'/name
    data[name]=json.loads(path.read_text(encoding='utf-8'))
    if data[name].get('type')!='FeatureCollection':raise SystemExit('STOP: Invalid '+name)
print('Data:',len(data['map_points.geojson']['features']),'municipalities,',len(data['attractions.geojson']['features']),'attractions.')
a=js.read_text(encoding='utf-8'); h=html.read_text(encoding='utf-8')
if 'PP6-SEARCH-STATE-V4' in a: print('ALREADY INSTALLED: v4 search-state fix'); sys.exit(0)
if "const searchWrap=make('div','vxw-search-wrap');" not in a or "places=[...towns,...mapped];" not in a:
    raise SystemExit('STOP: Installed planner differs from expected V3. No files modified.')
if "const responses=await Promise.all([fetch('data/attractions.geojson'),fetch('data/map_points.geojson')]);" not in a:
    raise SystemExit('STOP: The catalog loader differs from V3. No files modified.')
if 'js/itinerary-router.js?v=3' not in h:
    raise SystemExit('STOP: Expected V3 script tag missing. No files modified.')
backup=root/'.local-site-backup-before-search-v4';backup.mkdir(exist_ok=True)
for source,name in ((js,'itinerary-router.js'),(html,'index.html')):
    dest=backup/name
    if not dest.exists():shutil.copy2(source,dest)
a=a.replace("const searchWrap=make('div','vxw-search-wrap');", """/* PP6-SEARCH-STATE-V4: report catalog status and refresh pending searches. */
  const searchWrap=make('div','vxw-search-wrap');""",1)
a=a.replace("searchWrap.append(search,suggestionBox);panel.append(searchWrap);", """searchWrap.append(search,suggestionBox);panel.append(searchWrap);
  const catalogState=make('p','vxw-catalog-state','Loading municipalities and attractions…');
  panel.append(catalogState);""",1)
a=a.replace("fetch('data/attractions.geojson'),fetch('data/map_points.geojson')", "fetch('data/attractions.geojson',{cache:'no-store'}),fetch('data/map_points.geojson',{cache:'no-store'})",1)
a=a.replace("if(!found.length)suggestionBox.append(make('p','vxw-no-matches',tx().notFound));", "if(!found.length)suggestionBox.append(make('p','vxw-no-matches',places.length?tx().notFound:'Cargando municipios y atractivos…'));",1)
a=a.replace("places=[...towns,...mapped];", """places=[...towns,...mapped];
      catalogState.textContent=`${towns.length} municipalities / municipios · ${mapped.length} attractions / atractivos`;
      // A user can search before the asynchronous files finish loading.
      if(search.value.trim())showSearch();""",1)
a=a.replace("}catch(e){setStatus(`Could not load mapped attractions: ${e.message}`,true);", "}catch(e){catalogState.textContent=`Catalog failed to load: ${e.message}`;setStatus(`Could not load mapped attractions: ${e.message}`,true);",1)
a=a.replace("notFound:'No se encontraron atractivos.'", "notFound:'No hay coincidencias con la búsqueda. Comprueba el nombre del municipio o atractivo.'",1)
a=a.replace("notFound:'No matching attractions.'", "notFound:'No matching municipalities or attractions.'",1)
a=a.replace("notFound:'該当する観光地がありません。'", "notFound:'該当する市町村・観光地がありません。'",1)
h=h.replace('js/itinerary-router.js?v=3','js/itinerary-router.js?v=4',1)
js.write_text(a,encoding='utf-8');html.write_text(h,encoding='utf-8')
ignore=root/'.gitignore'
old=ignore.read_text(encoding='utf-8') if ignore.exists() else ''
if '.local-site-backup-before-search-v4/' not in old:
    ignore.write_text(old.rstrip()+'\n\n# Local rollback backups\n.local-site-backup-before-search-v4/\n',encoding='utf-8')
print('PASS: added visible catalog count, no-store fetch, pending-query refresh, clear no-match text, cache-busting v4.')
