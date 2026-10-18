#!/usr/bin/env python3
"""Replace blocked public OSM raster basemap with OpenFreeMap Positron in map-explorer.js.

Runs from the promo_Veracruz repository root, or accepts that directory as its first argument.
Edits only site/js/map-explorer.js and creates a backup.
"""
from pathlib import Path
import sys
import re
from datetime import datetime

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
target = root / "site" / "js" / "map-explorer.js"
if not target.is_file():
    raise SystemExit(f"Cannot find {target}. Run this from the promo_Veracruz root.")

source = target.read_text(encoding="utf-8")
style_url = "https://tiles.openfreemap.org/styles/positron"
if style_url in source:
    print("Already using OpenFreeMap Positron. No changes needed.")
    raise SystemExit(0)

# Match only the old hard-coded OSM raster style, not unrelated basemap/overlay code.
old = re.compile(
    r"style\s*:\s*\{\s*version\s*:\s*8\s*,\s*sources\s*:\s*\{\s*osm\s*:\s*\{"
    r"[^{}]*?https://tile\.openstreetmap\.org/\{z\}/\{x\}/\{y\}\.png"
    r"[^{}]*?\}\s*\}\s*,\s*layers\s*:\s*\[\s*\{"
    r"[^{}]*?\}\s*\]\s*\}",
    flags=re.S,
)
updated, replacements = old.subn(f"style:'{style_url}'", source, count=1)
if replacements != 1:
    raise SystemExit(
        "Could not find exactly the expected public OSM style block. No changes made. "
        "Please share the current site/js/map-explorer.js for inspection."
    )
backup = target.with_name(f"map-explorer.js.before-basemap-{datetime.now():%Y%m%d-%H%M%S}")
backup.write_text(source, encoding="utf-8")
target.write_text(updated, encoding="utf-8")
print(f"Basemap updated to OpenFreeMap Positron. Backup: {backup}")
print("Your tourism GeoJSON, region data, activity guides and CSS were not modified.")
