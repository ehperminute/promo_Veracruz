"""Tests for additive PP6 second pass; run from repo root with pytest."""
from pathlib import Path
import importlib.util
import hashlib
import json

HERE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('pp6_pass',HERE/'run_pass.py')
p=importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


def test_db_integrity_and_restored_source():
    d=p.database_audit()
    assert d['integrity']=='ok'
    assert d['municipalities']==212
    assert d['accepted_specific_activity_pairs']==216
    assert d['original_product_descriptions_restored']==295
    assert d['pairs_with_recorded_original_text_support']==173
    assert all(x['valid_hash'] for x in d['verified_html_snapshots'])


def test_separate_external_review_does_not_change_pair_count():
    assert p.database_audit()['external_14_review_records_in_separate_database']==40
    assert len(p.evidence_rows())==216


def test_documented_activity_intersection_only():
    rows=p.evidence_rows()
    selected=p.recommend(rows,['kayaking','birdwatching'],True,True)
    assert [r['municipality'] for r in selected]==['Catemaco','San Andrés Tuxtla']
    for item in selected:
        assert {m['activity'] for m in item['matches']}=={'kayaking','birdwatching'}
        assert all(m['claim_ids'] and m['source_ids'] and m['source_urls'] for m in item['matches'])
        assert all(m['original_text_support_count']>0 for m in item['matches'])


def test_missing_evidence_is_not_zero_claim():
    assert p.recommend(p.evidence_rows(),['made_up_specific_activity'],True)==[]


def test_no_partial_all_required_matches():
    rows=p.evidence_rows()
    results=p.recommend(rows,['kayaking','birdwatching','made_up_specific_activity'],True)
    assert results==[]
    assert p.recommend(rows,['kayaking','birdwatching'],True)==p.recommend(rows,['birdwatching','kayaking','kayaking'],True)


def test_campaign_evidence_coverage():
    rows=p.evidence_rows();audit=p.s4_audit(rows)
    assert audit['campaign_distinct_feature_links']==66
    assert audit['campaign_links_with_original_text_support']==65
    assert audit['campaign_links_without_original_text_support']==[{'municipality':'Coatepec','feature_id':'canyoning'}] or audit['campaign_links_without_original_text_support']==[{'feature_id':'canyoning','municipality':'Coatepec'}]


def test_exact_milp_reproduces_demand_diversity_optimum():
    result=p.solve_coverage(p.evidence_rows())
    assert result['objective_types_covered']==47
    assert result['selected_n']==6
    assert sorted(result['selected_municipalities'])==sorted(p.CAMPAIGN)
    assert result['budget_mxn']==30000


def test_text_supported_milp_robustness():
    result=p.solve_coverage(p.evidence_rows(),True)
    assert result['objective_types_covered']==47
    assert result['original_text_supported_types_covered']==47
    assert sorted(result['selected_municipalities'])==sorted(p.CAMPAIGN)


def test_paired_forecast_and_extra_baselines():
    result=p.s5_comparison(bootstrap_n=200)
    assert result['paired_predictions']==52
    assert result['total_forest_predictions']==53
    by={row['baseline']:row for row in result['comparison']}
    assert set(by)=={'last_month','seasonal_naive','three_month_mean','historical_month_mean'}
    assert abs(by['last_month']['forest_mae_pp']-5.5935)<0.02
    assert by['last_month']['improvement_pp']>0
    assert 0<by['three_month_mean']['improvement_pp']<0.2


def test_stochastic_metrics_recomputed():
    r=p.s6_interval_audit()
    assert r['prediction_rows_checked']==212
    assert r['metric_rows_checked']==12
    assert {x['center'] for x in r['by_center']}=={'Coatzacoalcos','Veracruz-Boca del Río','Xalapa'}
    assert next(x for x in r['by_center'] if x['center']=='Coatzacoalcos')['rolling12_coverage']>next(x for x in r['by_center'] if x['center']=='Coatzacoalcos')['fixed_coverage']
