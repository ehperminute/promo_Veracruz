#!/usr/bin/env python3
import argparse
import os
import sqlite3


def safe_slug(text):
    import re, unicodedata
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^a-zA-Z0-9]+', '-', text.strip().lower()).strip('-')
    return text or 'item'


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def main():
    ap = argparse.ArgumentParser(description='Export municipality/activity BLOB images to files.')
    ap.add_argument('db_path')
    ap.add_argument('out_dir')
    args = ap.parse_args()

    con = sqlite3.connect(args.db_path)
    cur = con.cursor()
    mun_dir = os.path.join(args.out_dir, 'municipalities')
    act_dir = os.path.join(args.out_dir, 'activities')
    ensure_dir(mun_dir)
    ensure_dir(act_dir)

    mun_count = 0
    for municipality_id, name, blob in cur.execute('SELECT municipality_id, name_official, hero_image_blob FROM municipalities WHERE hero_image_blob IS NOT NULL'):
        fn = f"{safe_slug(name)}__{safe_slug(municipality_id)}.svg"
        with open(os.path.join(mun_dir, fn), 'wb') as f:
            f.write(blob)
        mun_count += 1

    act_count = 0
    for activity_id, name, blob in cur.execute('SELECT activity_id, name_es, illustration_blob FROM activities WHERE illustration_blob IS NOT NULL'):
        fn = f"{safe_slug(name)}__{safe_slug(activity_id)}.svg"
        with open(os.path.join(act_dir, fn), 'wb') as f:
            f.write(blob)
        act_count += 1

    print(f'Exported municipality images: {mun_count}')
    print(f'Exported activity images: {act_count}')

if __name__ == '__main__':
    main()
