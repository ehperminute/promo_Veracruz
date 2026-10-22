from pathlib import Path
import hashlib,json,re,sys
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd()
s=root/'site';html=(s/'index.html').read_text(encoding='utf-8')
for p in ['js/itinerary-router.js','js/discovery-scoring.js','js/interest-recommender.js','js/itinerary-pricing-core.js','js/itinerary-pricing.js']:
 assert (s/p).is_file(),f'missing {p}'
 assert html.count(f'src="{p}?')==1,(p,'missing/duplicate script tag')
assert html.index('js/discovery-scoring.js')<html.index('js/interest-recommender.js')
data=json.loads((s/'data/interest_evidence.json').read_text())
assert data['total_links']==216 and len(data['records'])==216
prices=json.loads((s/'data/provider_prices.json').read_text())
assert len(prices['entries'])==46
route=(s/'js/itinerary-router.js').read_text()
assert 'VeracruzItineraryV2' in route and 'vxw:route-calculated' in route
assert 'const novelty=window.VXDiscoveryScore' in (s/'js/interest-recommender.js').read_text()
assert 'panel.append(section);' in (s/'js/itinerary-pricing.js').read_text()
print('PASS: scripts unique and ordered, current 216-link source, 46 price records, route and price events intact')
