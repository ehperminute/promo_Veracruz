#!/usr/bin/env python3
"""Repair Veracruz map overlay initialization after changing MapLibre basemap style.

Run at promo_Veracruz repository root, or pass that directory as first argument.
Only modifies site/js/map-explorer.js; backup is created before any change.
Never edits tourism data, the map GeoJSON, CSS, or website HTML.
"""
from pathlib import Path
from datetime import datetime
import sys

root = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd()
target = root/'site'/'js'/'map-explorer.js'
if not target.is_file():
    sys.exit(f'ERROR: Cannot find {target}. Run in the promo_Veracruz repo root.')
old = target.read_text(encoding='utf-8')
new = old

# 1. A remote vector style may render the basemap before all resources are idle.
# style.load is the MapLibre-supported point at which custom layers can be added.
needle = "mapObject.on('load',prepareMapLayers);"
replacement = """// Install our data layers as soon as the STYLE (not all remote tiles) is ready.
 // This event also fires after a future style change, when overlay layers need restoring.
 const onVeracruzStyleReady = () => {
   if (state.ready && mapObject.getSource('vx-locations')) return;
   state.ready = false;
   try { prepareMapLayers(); }
   catch (error) {
     console.error('[Veracruz map] Marker layer initialization failed:', error);
     const status = document.getElementById('vx-status');
     if (status) status.textContent = 'Map markers could not initialize: ' + error.message;
   }
 };
 mapObject.on('style.load', onVeracruzStyleReady);
 if (mapObject.isStyleLoaded()) onVeracruzStyleReady();"""
if needle in new:
    new = new.replace(needle, replacement, 1)
elif 'onVeracruzStyleReady' not in new:
    sys.exit('ERROR: Expected marker initializer not found. File left unchanged; send the current JS for inspection.')

# 2. Render a regular circle under each custom canvas badge, so places stay
# visible even if a sprite/image resource cannot render with the new basemap.
feature_needle = "const props={key:String(f.id),badge:badgeName(p.types),hit,focus:highlighting()?hit:0};"
feature_replacement = "const props={key:String(f.id),badge:badgeName(p.types),primary:p.types[0]||'other',hit,focus:highlighting()?hit:0};"
if feature_needle in new:
    new = new.replace(feature_needle, feature_replacement, 1)
elif 'primary:p.types[0]' not in new:
    sys.exit('ERROR: Expected feature mapper not found. File left unchanged; send current JS for inspection.')

layer_needle = "  mapObject.addLayer({id:'vx-places',type:'symbol',source:'vx-locations',"
layer_insert = """  // Independent geographic fallback: circles render even without custom icons.
  mapObject.addLayer({id:'vx-place-dot-fallback',type:'circle',source:'vx-locations',
    filter:['!', ['has','point_count']],
    paint:{'circle-radius':11,
      'circle-color':['match',['get','primary'],
        'adventure','#dc7d3d','water','#188ba8','nature','#35856c',
        'food','#c55e62','culture','#815caa','crafts','#a77b3c',
        'wellness','#35a09a','scenic','#5978bd','#7e8587'],
      'circle-opacity':['case',['==',['get','hit'],1],0.9,0.22],
      'circle-stroke-color':'#ffffff','circle-stroke-width':2}
  });
  mapObject.addLayer({id:'vx-places',type:'symbol',source:'vx-locations',"""
if "id:'vx-place-dot-fallback'" not in new:
    if layer_needle in new:
        new = new.replace(layer_needle, layer_insert, 1)
    else:
        sys.exit('ERROR: Expected marker layer not found. File left unchanged; send current JS for inspection.')

if new == old:
    print('Already patched; nothing changed.')
    sys.exit(0)
backup = target.with_name(f'map-explorer.js.before-marker-fix-{datetime.now():%Y%m%d-%H%M%S}')
backup.write_text(old, encoding='utf-8')
target.write_text(new, encoding='utf-8')
print('SUCCESS: Marker layer initialization and fallback fixed.')
print('Backup:', backup)
print('No changes to GeoJSON, SQLite, tourism records, guide files, or styling CSS.')
