#!/usr/bin/env python3
"""Offline tests for supplier listing MVP, no external bookings or services."""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PKG=Path(__file__).resolve().parents[1]
SRC=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else None

spec=importlib.util.spec_from_file_location('provider_review', PKG/'scripts/review_offer.py')
rev=importlib.util.module_from_spec(spec)
spec.loader.exec_module(rev)


def check(cond,msg):
    if not cond: raise AssertionError(msg)
    print('PASS:',msg)


def fixture():
    return dict(schema_version=1,submitted_at='2026-10-25T12:00:00Z',provider_name='NEGOCIO FICTICIO DE PRUEBA',
                municipality_id='30001',municipality_name='Acajete',category='accommodation',
                service_name='Habitación de prueba',description='Oferta inventada solo para pruebas locales',
                price_mxn=800,price_unit='room_night',tax_status='included',capacity_note='2 personas',
                valid_until='2099-01-01',public_url='https://example.org/test',conditions='Sujeto a confirmación',
                private_contact_email='private-person@example.org',tourism_registration='',consent_public=True)


def main():
    with tempfile.TemporaryDirectory() as t:
        root=Path(t)
        (root/'site/data').mkdir(parents=True)
        (root/'site/index.html').write_text('<!DOCTYPE html><html><head><title>Demo</title></head><body><nav>Map</nav><main><section id="veracruz-map-section"></section></main></body></html>',encoding='utf-8')
        (root/'site/data/map_points.geojson').write_text(json.dumps({'type':'FeatureCollection','features':[{'type':'Feature','properties':{'municipality_id':'30001','name':'Acajete'},'geometry':{'type':'Point','coordinates':[-97.0,19.0]}}]}),encoding='utf-8')
        for i in range(2):
            subprocess.check_call([sys.executable,str(PKG/'install.py'),str(root)],stdout=subprocess.DEVNULL)
        html=(root/'site/index.html').read_text(encoding='utf-8')
        check(html.count('<!-- PROVIDER-MARKET-MVP -->')==1,'Idempotent installation, one public offer section')
        check(html.count('js/provider-market.js')==1,'Only one offer-display script')
        check((root/'site/proveedores.html').exists(),'Provider submission form installed')
        check(len(json.loads((root/'site/data/provider_offers.json').read_text())['offers'])==0,'Release starts with zero fictional business listings')
        sub=fixture()
        private_file=root/'private_provider.json'
        private_file.write_text(json.dumps(sub),encoding='utf-8')
        offer=rev.publish(private_file,root)
        ledger=root/'site/data/provider_offers.json'
        raw=ledger.read_text(encoding='utf-8')
        check('private-person@example.org' not in raw,'Private administrative contact not published')
        check(offer['price_mxn']==800 and offer['price_unit']=='room_night','Price and unit preserved')
        check(json.loads(raw)['offers'][0]['municipality_id']=='30001','Stable municipality ID retained for route matching')
        rev.publish(private_file,root)
        check(len(json.loads(ledger.read_text(encoding='utf-8'))['offers'])==1,'Republishing replaces same offer, no duplication')
        subprocess.check_call([sys.executable,str(PKG/'install.py'),str(root)],stdout=subprocess.DEVNULL)
        check(len(json.loads(ledger.read_text(encoding='utf-8'))['offers'])==1,'Reinstall preserves approved listings')
        bad=fixture();bad['consent_public']=False
        try:rev.validate(bad,root);raise AssertionError('Missing consent accepted')
        except ValueError:print('PASS: Missing consent rejected')
        bad=fixture();bad['municipality_name']='Orizaba'
        try:rev.validate(bad,root);raise AssertionError('Invalid municipality accepted')
        except ValueError:print('PASS: Municipality mismatch rejected')
        bad=fixture();bad['public_url']='javascript:alert(1)'
        try:rev.validate(bad,root);raise AssertionError('Unsafe URL accepted')
        except ValueError:print('PASS: Unsafe URL rejected')
        bad=fixture();bad['price_unit']='quote'
        try:rev.validate(bad,root);raise AssertionError('Misrepresented units accepted')
        except ValueError:print('PASS: Numeric price without unit rejected')
        bad=fixture();bad['valid_until']='2020-01-01'
        try:rev.validate(bad,root);raise AssertionError('Expired listing accepted')
        except ValueError:print('PASS: Expired listing rejected')
        if shutil.which('node'):
            for name in ['provider-form.js','provider-market.js']:
                subprocess.check_call(['node','--check',str(PKG/'site/js'/name)],stdout=subprocess.DEVNULL)
            print('PASS: Both JavaScript modules pass syntax check')
        print('\nALL CHECKS PASSED')

if __name__=='__main__':main()
