"""2026-10-11 cumulative website content checks (no live network required)."""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
THEMES = ('beach_coast','nature','culture_history','archaeology','adventure','gastronomy_coffee','wellness_spiritual','urban_services')

def test_photo_manifest_and_attraction_evidence():
    photos = pd.read_csv(ROOT/'data/reference/destination_photo_manifest.csv').fillna('')
    checked = pd.read_csv(ROOT/'data/evidence/s4_atractivos_fuentes_v2.csv').fillna('')
    profiles = pd.read_csv(ROOT/'data/interim/destination_profiles_s4.csv')
    assert len(photos)==21
    assert photos.destination.is_unique
    assert set(photos.destination).issubset(set(profiles.destination))
    assert all(photos.file_page.str.startswith('https://commons.wikimedia.org/wiki/File:'))
    assert all(photos.image_url.str.startswith('https://commons.wikimedia.org/wiki/Special:FilePath/'))
    assert photos.author.str.len().min()>1
    assert photos.license.str.len().min()>1
    assert sum(checked.estado_cotejo_actual.eq('TEXTO_RESPALDADO_EN_FUENTE_OFICIAL')) == 114

def test_published_website_has_55_destinations_preserving_clusters_and_historical_features():
    data = json.loads((ROOT/'site/data/destinations.json').read_text('utf-8'))
    profiles = pd.read_csv(ROOT/'data/interim/destination_profiles_s4.csv').set_index('destination')
    membership = pd.read_csv(ROOT/'outputs/mining/clustering/cluster_membership.csv').set_index('destination')
    assert len(data)==55
    assert len({d['name'] for d in data})==55
    assert len({d['cluster']['id'] for d in data})==12
    assert sum(d['photo'] is not None for d in data)==21
    assert sum(len(d['attractions']) for d in data)==114
    assert sum(len(d['adventure_activities']) for d in data)==60
    assert sum('adventure' in d['themes'] for d in data)==37
    for dest in data:
        name=dest['name']
        assert dest['cluster']['id']==int(membership.loc[name,'cluster'])
        expected={k for k in THEMES if int(profiles.loc[name,f'theme_{k}'])==1}
        assert set(dest['model_themes'])==expected
        assert ('adventure' in dest['themes'])==bool(dest['adventure_activities'])
        if dest['photo']:
            assert dest['photo']['author']
            assert dest['photo']['license']
            assert set(dest['photo']['caption'])=={'en','es','ja'}
        for attraction in dest['attractions']:
            assert attraction['source_url'].startswith('https://')
        for activity in dest['adventure_activities']:
            assert activity['source_url'].startswith('https://')

def test_translations_cover_content_labels():
    keys={'reviewed_attractions_title','attraction_source','attraction_evidence_note','photo_by','photo_not_available'}
    for lang in ('en','es','ja'):
        content=json.loads((ROOT/f'site/i18n/{lang}.json').read_text('utf-8'))
        assert keys <= set(content)
        assert all(content[key] for key in keys)
