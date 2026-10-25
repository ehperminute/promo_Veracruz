#!/usr/bin/env python3
"""Manually review a supplier submission and publish only public fields.

Usage:
python veracruz_provider_marketplace_mvp/scripts/review_offer.py \
  solicitud-proveedor.json --repo . --approve --contact-verified

Do not commit input submission JSON: it contains a private administrative email.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

FIELDS = ('provider_name', 'municipality_id', 'municipality_name', 'category',
          'service_name', 'description', 'price_mxn', 'price_unit', 'tax_status',
          'capacity_note', 'valid_until', 'public_url', 'conditions',
          'tourism_registration')
CATS = {'accommodation', 'activity', 'guide', 'transport'}
UNITS = {'person', 'room_night', 'group', 'service', 'quote'}
TAXES = {'included', 'excluded', 'unknown'}
MAXLEN = {'provider_name':120, 'municipality_name':120, 'service_name':120,
          'description':1200,'capacity_note':150,'conditions':1000,
          'tourism_registration':80,'public_url':600}


def validate_url(raw):
    if not raw:
        return ''
    parsed = urlsplit(str(raw))
    if parsed.scheme not in ('https','http') or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError('Invalid public URL: only ordinary http(s) URLs permitted')
    return str(raw)


def read_municipalities(root):
    geo = json.loads((root/'site/data/map_points.geojson').read_text(encoding='utf-8'))
    return {str(f['properties']['municipality_id']):str(f['properties']['name'])
            for f in geo['features']}


def validate(submission, root):
    if submission.get('schema_version') != 1:
        raise ValueError('Unsupported submission schema')
    if submission.get('consent_public') is not True:
        raise ValueError('Missing permission to publish business data')
    municipality = read_municipalities(root)
    code = str(submission.get('municipality_id') or '')
    if code not in municipality or submission.get('municipality_name')!=municipality[code]:
        raise ValueError('Municipality name/code mismatch with source GeoJSON')
    if submission.get('category') not in CATS:
        raise ValueError('Unknown service category')
    if submission.get('price_unit') not in UNITS or submission.get('tax_status') not in TAXES:
        raise ValueError('Invalid price units or tax status')
    price = submission.get('price_mxn')
    if price is not None:
        if type(price) not in (int,float) or price<0 or price>10000000:
            raise ValueError('Invalid price')
        if submission['price_unit']=='quote':
            raise ValueError('A numeric price requires a non-quote unit')
    elif submission['price_unit']!='quote':
        raise ValueError('Unpriced offer requires quote unit')
    for name in ('provider_name','service_name','description','private_contact_email'):
        if not str(submission.get(name) or '').strip():
            raise ValueError('Missing: '+name)
    for key,limit in MAXLEN.items():
        if len(str(submission.get(key) or ''))>limit:
            raise ValueError('Too long: '+key)
    if not str(submission.get('public_url') or '').strip():
        raise ValueError('A public provider contact URL is required')
    validate_url(submission.get('public_url'))
    if submission.get('valid_until'):
        try:
            expiry=dt.date.fromisoformat(submission['valid_until'])
        except ValueError as exc:
            raise ValueError('Invalid offer expiration date') from exc
        if expiry < dt.date.today():
            raise ValueError('Expired offer')
    if len(str(submission['private_contact_email']))>180 or '@' not in submission['private_contact_email']:
        raise ValueError('Private contact email invalid')
    result = {k:submission.get(k) for k in FIELDS}
    result['public_url']=validate_url(result['public_url'])
    result['status']='approved'
    result['review_level']='operator_submission_reviewed'
    result['approved_at']=dt.datetime.now(dt.timezone.utc).isoformat()
    id_input='|'.join(str(result[k]) for k in ('provider_name','municipality_id','service_name','category'))
    result['offer_id']='offer-'+hashlib.sha256(id_input.encode('utf-8')).hexdigest()[:14]
    return result


def publish(submission_path,root):
    if not submission_path.exists():
        raise ValueError('Submission file does not exist')
    submission=json.loads(submission_path.read_text(encoding='utf-8'))
    offer=validate(submission,root)
    target=root/'site/data/provider_offers.json'
    if not target.exists():
        raise ValueError('Site provider_offers.json missing; run installer first')
    data=json.loads(target.read_text(encoding='utf-8'))
    offers=data.get('offers',[])
    offers=[o for o in offers if o.get('offer_id')!=offer['offer_id']]
    offers.append(offer)
    offers.sort(key=lambda o:(o['municipality_name'],o['provider_name'],o['service_name']))
    data={'schema_version':1,'updated_at':dt.datetime.now(dt.timezone.utc).isoformat(),'offers':offers}
    raw=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
    if submission['private_contact_email'].lower() in raw.lower():
        raise ValueError('Private data leak detected; refusing to publish')
    target.write_text(raw,encoding='utf-8')
    return offer


def main():
    ap=argparse.ArgumentParser(description='Publish a manually verified provider offer to static website.')
    ap.add_argument('submission',type=Path)
    ap.add_argument('--repo',type=Path,default=Path.cwd())
    ap.add_argument('--approve',action='store_true',help='Explicit manual approval required')
    ap.add_argument('--contact-verified',action='store_true',help='I verified that the submitter is authorized to represent the business')
    args=ap.parse_args()
    if not args.approve or not args.contact_verified:
        ap.error('No publication: both --approve and --contact-verified are required')
    offer=publish(args.submission,args.repo.resolve())
    print('APPROVED: '+offer['offer_id']+' · '+offer['service_name']+' · '+offer['municipality_name'])
    print('Published static listing to site/data/provider_offers.json. Commit and deploy only after inspecting changes.')

if __name__=='__main__': main()
