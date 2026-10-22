#!/usr/bin/env python3
import argparse
import sqlite3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('db_path')
    args = ap.parse_args()

    con = sqlite3.connect(args.db_path)
    cur = con.cursor()
    total_m = cur.execute('SELECT COUNT(*) FROM municipalities').fetchone()[0]
    blob_m = cur.execute('SELECT COUNT(*) FROM municipalities WHERE hero_image_blob IS NOT NULL').fetchone()[0]
    total_a = cur.execute('SELECT COUNT(*) FROM activities').fetchone()[0]
    blob_a = cur.execute('SELECT COUNT(*) FROM activities WHERE illustration_blob IS NOT NULL').fetchone()[0]
    print({'municipalities_total': total_m, 'municipalities_with_blob': blob_m, 'activities_total': total_a, 'activities_with_blob': blob_a})
    con.close()

if __name__ == '__main__':
    main()
