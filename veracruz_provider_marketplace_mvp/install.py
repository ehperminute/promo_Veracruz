#!/usr/bin/env python3
"""Non-destructive additive installer for a provider-offer MVP on static Veracruz site."""
from __future__ import annotations
import re
import shutil
import sys
from pathlib import Path

SOURCE=Path(__file__).resolve().parent
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd()
SITE=ROOT/'site'
INDEX=SITE/'index.html'
if not INDEX.is_file() or not (SITE/'data/map_points.geojson').is_file():
    raise SystemExit('Run from promo_Veracruz root; expected site/index.html and site/data/map_points.geojson')

assets=[('site/proveedores.html','site/proveedores.html'),('site/js/provider-form.js','site/js/provider-form.js'),('site/js/provider-market.js','site/js/provider-market.js'),('site/css/provider-market.css','site/css/provider-market.css'),('site/data/provider_submission_config.json','site/data/provider_submission_config.json')]
for src,dst in assets:
    dest=ROOT/dst
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dst=='site/data/provider_submission_config.json' and dest.exists():
        continue  # preserve a configured private submission service endpoint
    shutil.copy2(SOURCE/src,dest)

# IMPORTANT: Do not destroy a real, previously approved offers ledger on reinstallation.
offers=SITE/'data/provider_offers.json'
if not offers.exists():
    shutil.copy2(SOURCE/'site/data/provider_offers.json',offers)

html=INDEX.read_text(encoding='utf-8')
if '<!-- PROVIDER-MARKET-MVP -->' not in html:
    if '</main>' not in html or '</head>' not in html or '</body>' not in html:
        raise SystemExit('Unexpected site/index.html structure: no files modified except additive assets')
    block='''
<!-- PROVIDER-MARKET-MVP -->
<section id="provider-offers" class="vp-market" aria-labelledby="vp-title">
  <div class="vp-market-head">
    <div><p class="vp-eyebrow">Red turística de Veracruz · prototipo</p><h2 id="vp-title">Servicios para tu itinerario</h2>
    <p id="vp-intro">Consulta las ofertas revisadas que los prestadores de servicios publican para tus destinos. La disponibilidad debe confirmarse.</p></div>
    <a class="vp-button secondary" href="proveedores.html">¿Ofreces servicios? Publica tu propuesta</a>
  </div>
  <div class="vp-route-summary" id="vp-route-summary" aria-live="polite"></div>
  <p id="vp-offers-status" class="vp-muted" role="status"></p>
  <div id="vp-offers-grid" class="vp-offers" aria-live="polite"></div>
  <button id="vp-show-all" class="vp-button secondary" type="button" aria-pressed="false">Ver todos los servicios publicados</button>
  <p id="vp-disclaimer" class="vp-disclaimer">Las reservas y pagos se realizan con cada proveedor. Esta plataforma no confirma disponibilidad.</p>
</section>
'''
    html=html.replace('</main>',block+'</main>',1)
    html=html.replace('</head>','<link rel="stylesheet" href="css/provider-market.css?v=1">\n</head>',1)
    html=html.replace('</body>','<script defer src="js/provider-market.js?v=1"></script>\n</body>',1)
    # Add one discoverable nav link, rather than replacing any existing menu.
    m=re.search(r'</nav>',html,flags=re.I)
    if m:html=html[:m.start()]+'<a href="proveedores.html">Prestadores / Providers</a>\n'+html[m.start():]
    INDEX.write_text(html,encoding='utf-8')

# Add admin script in repo for recurring manual review. Do not create public submission inbox.
admin=ROOT/'scripts/pp6/review_provider_offer.py'
admin.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(SOURCE/'scripts/review_offer.py',admin)

ignore=ROOT/'.gitignore'
addition='\n# Private provider requests: do not commit contact email submissions\nprovider_submissions/\n*solicitud-proveedor*.json\n'
if ignore.exists():
    old=ignore.read_text(encoding='utf-8')
    if 'provider_submissions/' not in old:
        ignore.write_text(old+addition,encoding='utf-8')
else:ignore.write_text(addition,encoding='utf-8')
print('Installed provider MVP: site/proveedores.html; public route-linked offers; manual review CLI.')
print('No provider submissions endpoint is configured. Initial approved offer count is preserved.')
