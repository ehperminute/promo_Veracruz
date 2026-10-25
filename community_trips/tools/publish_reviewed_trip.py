#!/usr/bin/env python3
"""Human-reviewed publication of traveler stories to a static GitHub Pages catalog.

Expected private input: a JSON file downloaded from the submission page OR extracted
from the private receiving service. Requires explicit approval flags. Never executes
untrusted data; re-encodes photo bytes with Pillow to discard metadata.
"""
import argparse
import base64
import hashlib
import io
import json
import re
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_PAYLOAD = 3_100_000
MAX_PHOTOS = 4
MAX_TOTAL_PIXELS = 12_000_000
CATEGORIES = {'food', 'accommodation', 'activity', 'transport', 'shopping', 'other'}
MUN_ID = re.compile(r'^municipality:\d{5}$')
ATTRACTION_ID = re.compile(r'^attraction:[^\s]{1,120}$')
MONTH = re.compile(r'^\d{4}-(0[1-9]|1[0-2])$')
DATA_URL = re.compile(r'^data:image/webp;base64,([A-Za-z0-9+/=]+)$')


def clean_text(s, max_length):
    if not isinstance(s, str):
        raise ValueError('Expected text field')
    return s.strip()[:max_length]


def validate(raw):
    if raw.get('schema_version') != 1 or raw.get('submission_type') != 'traveler_story':
        raise ValueError('Unknown submission schema')
    if raw.get('rights_confirmed') is not True:
        raise ValueError('No image and text sharing consent')
    title = clean_text(raw.get('title', ''), 90)
    story = clean_text(raw.get('story', ''), 1600)
    author = clean_text(raw.get('nickname', ''), 45)
    if not title or not story:
        raise ValueError('Story and title required')
    trip = raw.get('trip')
    if not isinstance(trip, dict) or trip.get('v') != 1:
        raise ValueError('Invalid trip version')
    people = trip.get('people')
    if not isinstance(people, int) or isinstance(people, bool) or not 1 <= people <= 30:
        raise ValueError('Invalid people')
    month = trip.get('month', '')
    if not isinstance(month, str) or (month and not MONTH.fullmatch(month)):
        raise ValueError('Use month and year only')
    stops = trip.get('stops')
    if not isinstance(stops, list) or not (1 <= len(stops) <= 12):
        raise ValueError('Invalid number of stops')
    for stop in stops:
        if not isinstance(stop, dict):
            raise ValueError('Invalid stop')
        stop['id'] = clean_text(stop.get('id', ''), 160)
        stop['name'] = clean_text(stop.get('name', ''), 100)
        if not stop['name']:
            raise ValueError('Empty stop name')
        if stop['id'] and not (MUN_ID.fullmatch(stop['id']) or ATTRACTION_ID.fullmatch(stop['id'])):
            raise ValueError('Unexpected stop id')
    expenses = trip.get('expenses', [])
    if not isinstance(expenses, list) or len(expenses) > 40:
        raise ValueError('Too many expense items')
    for item in expenses:
        if not isinstance(item, dict):
            raise ValueError('Invalid expense item')
        amount = item.get('amount')
        if not isinstance(amount, (float, int)) or isinstance(amount, bool) or not (0.01 <= amount <= 1_000_000):
            raise ValueError('Invalid expense value')
        if abs(round(amount * 100) - amount * 100) > 0.000001:
            raise ValueError('Invalid fractional amount')
        if not isinstance(item.get('stopIndex'), int) or not 0 <= item['stopIndex'] < len(stops):
            raise ValueError('Invalid expense location')
        if item.get('category') not in CATEGORIES:
            raise ValueError('Unexpected expense category')
        for field, maximum in [('label', 110), ('provider', 120), ('note', 200)]:
            item[field] = clean_text(item.get(field, ''), maximum)
    photos = raw.get('photos', [])
    if not isinstance(photos, list) or len(photos) > MAX_PHOTOS:
        raise ValueError('Too many images')
    for photo in photos:
        if not isinstance(photo, dict) or photo.get('mime') != 'image/webp' or not DATA_URL.fullmatch(photo.get('dataUrl', '')):
            raise ValueError('Invalid photo encoding')
        photo['alt'] = clean_text(photo.get('alt', ''), 140)
        stop_idx=photo.get('stopIndex')
        if stop_idx is not None and (not isinstance(stop_idx,int) or not 0<=stop_idx<len(stops)):
            raise ValueError('Photo stop index invalid')
    normalized_trip = {'v': 1, 'title': clean_text(trip.get('title', ''), 100) or title,
                       'month': month, 'people': people, 'stops': stops, 'expenses': expenses}
    return {'title': title, 'story': story, 'nickname': author, 'trip': normalized_trip, 'photos': photos, 'research_consent': raw.get('research_consent') is True}


def decode_photo(photo):
    match = DATA_URL.fullmatch(photo['dataUrl'])
    data = base64.b64decode(match.group(1), validate=True)
    if len(data) > 500_000 or data[:4] != b'RIFF' or data[8:12] != b'WEBP':
        raise ValueError('Invalid WebP photo data')
    try:
        im = Image.open(io.BytesIO(data))
        im.load()
        if im.width * im.height > MAX_TOTAL_PIXELS:
            raise ValueError('Too many photo pixels')
        im = ImageOps.exif_transpose(im).convert('RGB')
        im.thumbnail((1200, 1200))
        out = io.BytesIO()
        im.save(out, 'WEBP', quality=76, method=4)  # re-encode, strip metadata
        return out.getvalue()
    except (UnidentifiedImageError, OSError, ValueError) as e:
        raise ValueError('Unusable photo') from e


def publish(submission, site, dry_run=False):
    cleaned = validate(submission)
    unique_hash = hashlib.sha256(json.dumps(submission, sort_keys=True).encode()).hexdigest()[:14]
    name = 'traveler-' + unique_hash
    catalog_path = site / 'data' / 'community_trips.json'
    if catalog_path.exists():
        catalog = json.loads(catalog_path.read_text(encoding='utf8'))
    else:
        catalog = {'version': 1, 'trips': []}
    if any(x.get('id') == name for x in catalog.get('trips', [])):
        raise ValueError('Submission already published')
    photos = []
    for i, photo in enumerate(cleaned['photos'], 1):
        data = decode_photo(photo)
        relative = f'media/community-trips/{name}/{i}.webp'
        photos.append({'src': relative, 'alt': photo['alt'] or f'Traveler contributed photo {i}', 'source': 'traveler_contributed', 'stopIndex': photo.get('stopIndex')})
        if not dry_run:
            destination = site / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
    published = {
        'id': name, 'kind': 'traveler_reported',
        'title': cleaned['title'], 'summary': cleaned['story'][:260], 'story': cleaned['story'],
        'nickname': cleaned['nickname'], 'trip': cleaned['trip'], 'photos': photos,
        'price_source': 'self_reported_unverified', 'research_consent': cleaned['research_consent'], 'moderation_status': 'approved'
    }
    if not dry_run:
        catalog['trips'].append(published)
        catalog_path.parent.mkdir(parents=True, exist_ok=True)
        catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    return published


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('submission', type=Path)
    parser.add_argument('--site', type=Path, default=Path('site'))
    parser.add_argument('--approve', action='store_true')
    parser.add_argument('--content-reviewed', action='store_true')
    parser.add_argument('--rights-reviewed', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if not args.submission.exists() or args.submission.stat().st_size > MAX_PAYLOAD:
        parser.error('Submission missing or too large')
    if not args.dry_run and not (args.approve and args.content_reviewed and args.rights_reviewed):
        parser.error('Require --approve --content-reviewed --rights-reviewed before public posting')
    payload = json.loads(args.submission.read_text(encoding='utf8'))
    result = publish(payload, args.site.resolve(), dry_run=args.dry_run)
    print('DRY RUN:' if args.dry_run else 'PUBLISHED:', result['id'])
    print('Traveler story is unverified personal experience, not an observed population statistic.')

if __name__ == '__main__':
    main()
