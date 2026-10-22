#!/usr/bin/env python3
import argparse
import hashlib
import html
import os
import sqlite3
from datetime import datetime, timezone
from textwrap import wrap


def seeded_palette(seed_text):
    digest = hashlib.sha256(seed_text.encode('utf-8')).hexdigest()
    palettes = [
        ('#174A7E', '#2B7CB9', '#D9F1FF'),
        ('#265D3B', '#4C9A5E', '#E8F8EA'),
        ('#6B3E8E', '#A463D8', '#F2E7FF'),
        ('#8B4A2B', '#D07A45', '#FFF1E7'),
        ('#265A6A', '#40A3B8', '#E6FBFF'),
        ('#7A2230', '#C05369', '#FFE8ED'),
    ]
    idx = int(digest[:2], 16) % len(palettes)
    return palettes[idx]


def make_svg(title, subtitle, badge, footer, seed_text):
    c1, c2, c3 = seeded_palette(seed_text)
    title_lines = wrap(title, width=18)[:3]
    subtitle_lines = wrap(subtitle or '', width=52)[:3]

    title_tspans = ''.join(
        f'<tspan x="90" dy="{76 if i == 0 else 68}">{html.escape(line)}</tspan>'
        for i, line in enumerate(title_lines)
    )
    subtitle_tspans = ''.join(
        f'<tspan x="90" dy="{34 if i == 0 else 30}">{html.escape(line)}</tspan>'
        for i, line in enumerate(subtitle_lines)
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="675" viewBox="0 0 1200 675" role="img" aria-label="{html.escape(title)}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{c1}"/>
      <stop offset="100%" stop-color="{c2}"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="675" fill="url(#bg)"/>
  <circle cx="1080" cy="90" r="170" fill="rgba(255,255,255,0.12)"/>
  <circle cx="120" cy="610" r="160" fill="rgba(255,255,255,0.10)"/>
  <rect x="48" y="48" width="1104" height="579" rx="34" ry="34" fill="none" stroke="rgba(255,255,255,0.6)" stroke-width="2"/>
  <rect x="90" y="82" width="230" height="52" rx="18" fill="{c3}"/>
  <text x="108" y="116" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="700" fill="#17202A">{html.escape(badge)}</text>
  <text x="90" y="165" font-family="Arial, Helvetica, sans-serif" font-size="68" font-weight="700" fill="#FFFFFF">{title_tspans}</text>
  <text x="90" y="380" font-family="Arial, Helvetica, sans-serif" font-size="28" fill="#F8FBFF">{subtitle_tspans}</text>
  <line x1="90" y1="560" x2="1110" y2="560" stroke="rgba(255,255,255,0.75)" stroke-width="2"/>
  <text x="90" y="600" font-family="Arial, Helvetica, sans-serif" font-size="24" fill="#F8FBFF">{html.escape(footer)}</text>
</svg>'''
    return svg.encode('utf-8'), 'image/svg+xml'


def column_exists(cur, table, column):
    return any(r[1] == column for r in cur.execute(f'PRAGMA table_info({table})').fetchall())


def ensure_columns(cur, table, defs):
    for col_name, col_type in defs:
        if not column_exists(cur, table, col_name):
            cur.execute(f'ALTER TABLE {table} ADD COLUMN {col_name} {col_type}')


def build_municipality_images(con):
    cur = con.cursor()
    ensure_columns(cur, 'municipalities', [
        ('hero_image_blob', 'BLOB'),
        ('hero_image_mime', 'TEXT'),
        ('hero_image_kind', 'TEXT'),
        ('hero_image_note', 'TEXT'),
        ('hero_image_updated_at', 'TEXT'),
    ])
    rows = cur.execute('SELECT municipality_id, name_official, COALESCE(tourism_region, "") FROM municipalities ORDER BY name_official COLLATE NOCASE').fetchall()
    now = datetime.now(timezone.utc).isoformat()
    count = 0
    for municipality_id, name, region in rows:
        subtitle = f'Región turística: {region}' if region else 'Referencia municipal para el prototipo turístico de Veracruz'
        footer = 'Representación visual generada. Sustituible por foto o arte final.'
        data, mime = make_svg(name, subtitle, 'Municipio', footer, f'municipality::{municipality_id}::{name}')
        cur.execute('''UPDATE municipalities
                       SET hero_image_blob=?, hero_image_mime=?, hero_image_kind=?, hero_image_note=?, hero_image_updated_at=?
                       WHERE municipality_id=?''',
                    (data, mime, 'generated_placeholder', 'Representational hero image generated locally for UI/media prototyping.', now, municipality_id))
        count += 1
    return count


def build_activity_images(con):
    cur = con.cursor()
    ensure_columns(cur, 'activities', [
        ('illustration_blob', 'BLOB'),
        ('illustration_mime', 'TEXT'),
        ('illustration_kind', 'TEXT'),
        ('illustration_note', 'TEXT'),
        ('illustration_updated_at', 'TEXT'),
    ])
    fam = {aid: fam for aid, fam in cur.execute('SELECT activity_id, activity_family FROM activity_taxonomy_family').fetchall()}
    rows = cur.execute('SELECT activity_id, name_es, name_en, COALESCE(activity_level, ""), COALESCE(definition, "") FROM activities ORDER BY name_es COLLATE NOCASE').fetchall()
    now = datetime.now(timezone.utc).isoformat()
    count = 0
    for activity_id, name_es, name_en, level, definition in rows:
        parts = []
        family = fam.get(activity_id, '')
        if family:
            parts.append(f'Familia: {family}')
        if level:
            parts.append(f'Nivel: {level}')
        if name_en and name_en != name_es:
            parts.append(f'EN: {name_en}')
        subtitle = ' · '.join(parts) if parts else (definition[:120] or 'Actividad del catálogo turístico de Veracruz')
        footer = 'Marcador visual generado. Reemplazable por imagen editorial.'
        data, mime = make_svg(name_es, subtitle, 'Actividad', footer, f'activity::{activity_id}::{name_es}')
        cur.execute('''UPDATE activities
                       SET illustration_blob=?, illustration_mime=?, illustration_kind=?, illustration_note=?, illustration_updated_at=?
                       WHERE activity_id=?''',
                    (data, mime, 'generated_placeholder', 'Representational activity image generated locally for UI/media prototyping.', now, activity_id))
        count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description='Add and populate BLOB image columns in the Veracruz SQLite database.')
    parser.add_argument('db_path', help='Path to SQLite database')
    args = parser.parse_args()
    if not os.path.exists(args.db_path):
        raise SystemExit(f'Database not found: {args.db_path}')
    con = sqlite3.connect(args.db_path)
    try:
        m = build_municipality_images(con)
        a = build_activity_images(con)
        con.commit()
        cur = con.cursor()
        m_count = cur.execute('SELECT COUNT(*) FROM municipalities WHERE hero_image_blob IS NOT NULL').fetchone()[0]
        a_count = cur.execute('SELECT COUNT(*) FROM activities WHERE illustration_blob IS NOT NULL').fetchone()[0]
        print(f'Updated municipalities: {m}')
        print(f'Updated activities: {a}')
        print(f'Blob coverage -> municipalities: {m_count}, activities: {a_count}')
    finally:
        con.close()

if __name__ == '__main__':
    main()
