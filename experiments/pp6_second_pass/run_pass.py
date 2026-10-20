"""PP6 second pass (read-only source access). Requires numpy, pandas, scipy.
Run from repo root: python experiments/pp6_second_pass/run_pass.py
Preserves all existing source/analysis/site files; writes only to this script's results/.
"""
from __future__ import annotations
import csv
import hashlib
import json
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix, vstack

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DB = ROOT / 'data/recovered_source_descriptions/veracruz_pp3_master_with_originals.sqlite'
AUDITED_14_DB = ROOT / 'VERACRUZ_GEOGRAPHY_COURSE_RESULTS_2026-10-18/research/veracruz_master_with_verified_evidence.sqlite'
FORECAST = ROOT / 'outputs/ml/s5_25_26_predictions.csv'
HIST = ROOT / 'data/interim/datatur_veracruz_monthly.csv'
RECENT = ROOT / 'data/reference/datatur_veracruz_monthly_2025_2026.csv'
OUT = HERE / 'results'
CAMPAIGN = ['Atlahuilco','Catemaco','Coatepec','Fortín','Papantla','San Andrés Tuxtla']


def ro_conn(path: Path):
    if not path.is_file():
        raise FileNotFoundError(f'Required input missing: {path}')
    return sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + '\n', encoding='utf-8')


def database_audit():
    with ro_conn(DB) as db:
        integrity = db.execute('pragma integrity_check').fetchone()[0]
        assert integrity == 'ok', integrity
        count = db.execute('SELECT count(*), count(distinct municipality_id), count(distinct feature_id), sum(original_text_support_count>0) FROM s4_statewide_evidence_pairs_v1').fetchone()
        restored = db.execute("SELECT count(*) FROM original_product_description_recovery WHERE status='original_restored' AND length(description_text_original)>0").fetchone()[0]
        products = db.execute('SELECT count(*) FROM catalog_product_cards').fetchone()[0]
        municipalities = db.execute('SELECT count(*) FROM municipalities').fetchone()[0]
        snapshots = db.execute('SELECT snapshot_sha256, archived_file, original_size_bytes FROM original_source_snapshots').fetchall()
        audited_snapshots = []
        for sha, relpath, byte_length in snapshots:
            source = ROOT / 'data/recovered_source_descriptions/restoration_audit' / relpath
            actual_sha = hashlib.sha256(source.read_bytes()).hexdigest() if source.exists() else None
            audited_snapshots.append(dict(name=source.name, accessible=source.exists(), valid_hash=(actual_sha == sha), byte_count=source.stat().st_size if source.exists() else None, recorded_byte_count=byte_length))
        assert restored == products == 295
        assert all(row['valid_hash'] for row in audited_snapshots)
    external14 = None
    if AUDITED_14_DB.exists():
        with ro_conn(AUDITED_14_DB) as db:
            assert db.execute('pragma integrity_check').fetchone()[0]=='ok'
            external14 = db.execute('select count(*), count(distinct municipality_id) from external_14_tourism_evidence_reviewed').fetchone()
    return {'db':DB.relative_to(ROOT).as_posix(), 'integrity':integrity, 'municipalities':municipalities, 'accepted_specific_activity_pairs':count[0], 'municipalities_with_specific_activity_pairs':count[1], 'specific_activity_types':count[2], 'pairs_with_recorded_original_text_support':count[3], 'original_product_descriptions_restored':restored, 'catalog_product_cards':products, 'verified_html_snapshots':audited_snapshots, 'external_14_review_records_in_separate_database':external14[0] if external14 else None, 'external_14_distinct_municipalities':external14[1] if external14 else None, 'note':'The external 14-municipality review is not merged into the original 216 homogeneous activity-pair observations. Archived source support is not proof of current opening/availability.'}


def evidence_rows():
    with ro_conn(DB) as db:
        return pd.read_sql_query('''SELECT p.municipality_id, m.name_official AS municipality, p.feature_id, p.family,
                                   p.claim_count,p.claim_ids,p.source_ids,p.source_urls,
                                   p.original_text_support_count,p.summary_only_evidence_count
                            FROM s4_statewide_evidence_pairs_v1 AS p
                            JOIN municipalities AS m ON p.municipality_id=m.municipality_id''', db)


def recommend(rows, requested, require_all=True, original_only=False):
    requested=sorted(set(requested))
    if not requested:
        raise ValueError('Specify at least one feature_id')
    r=rows[rows.feature_id.isin(requested)]
    if original_only:
        r=r[r.original_text_support_count>0]
    matched=[]
    for (municipality_id,name),subset in r.groupby(['municipality_id','municipality']):
        features=set(subset.feature_id)
        if require_all and not set(requested).issubset(features):
            continue
        matches=[]
        for record in subset.sort_values('feature_id').itertuples(index=False):
            matches.append({'activity':record.feature_id,'family':record.family, 'original_text_support_count':int(record.original_text_support_count),'claim_ids':record.claim_ids.split('|') if record.claim_ids else [],'source_ids':record.source_ids.split('|') if record.source_ids else [],'source_urls':record.source_urls.split('|') if isinstance(record.source_urls,str) and record.source_urls else []})
        matched.append({'municipality_id':municipality_id,'municipality':name,'matched_count':len(features),'original_text_supported_matches':int(sum(t['original_text_support_count']>0 for t in matches)),'matches':matches})
    matched.sort(key=lambda d:(-d['matched_count'],-d['original_text_supported_matches'],d['municipality']))
    return matched


def s4_audit(rows):
    claim_names = rows[rows.municipality.isin(CAMPAIGN)]
    assert len(claim_names)==66, 'Portfolio feature count unexpected: review changes before interpreting historical reports.'
    with ro_conn(DB) as db:
        history=pd.read_sql_query('SELECT view,k,silhouette,sizes,singletons,penalized_score FROM s4_experiment_metrics',db)
    view_summary=[]
    for name,group in history.groupby('view'):
        best=group.sort_values('penalized_score',ascending=False).iloc[0]
        view_summary.append({'view':name,'top_k_by_stored_penalized_score':int(best.k),'silhouette':float(best.silhouette),'singletons':int(best.singletons),'historical_only':True})
    result={'documented_activity_pair_count':len(rows),'campaign_distinct_feature_links':len(claim_names),'campaign_links_with_original_text_support':int((claim_names.original_text_support_count>0).sum()),'campaign_links_without_original_text_support':claim_names.loc[claim_names.original_text_support_count<=0,['municipality','feature_id']].to_dict('records'), 'stored_exploratory_clustering_views':view_summary,'recommendations_any_evidence':recommend(rows,['kayaking','birdwatching'],require_all=True),'recommendations_with_original_text':recommend(rows,['kayaking','birdwatching'],require_all=True,original_only=True), 'interpretation':'Recommendations are exact documented activity intersections, not predicted tourist tastes; unlisted activities have unknown status, not established absence.'}
    return result


def solve_coverage(rows, original_only=False):
    r=rows[rows.original_text_support_count>0] if original_only else rows
    cities=sorted(rows.municipality_id.unique())
    features=sorted(r.feature_id.unique())
    nc,nf=len(cities),len(features)
    ci={city:i for i,city in enumerate(cities)}
    fi={f:i for i,f in enumerate(features)}
    coverage=lil_matrix((nf,nc+nf))
    for j in range(nf):
        coverage[j,nc+j]=1.0
    for row in r.itertuples(index=False):
        coverage[fi[row.feature_id],ci[row.municipality_id]]=-1.0
    limit=lil_matrix((1,nc+nf)); limit[0,:nc]=1.0
    matrix=vstack([coverage.tocsr(),limit.tocsr()]); lower=np.r_[np.full(nf,-np.inf),0.0]; upper=np.r_[np.zeros(nf),6.0]
    # Tiny deterministic tie-break on municipality order does not change integer coverage objective.
    objective=np.r_[np.arange(nc)*1e-5,-np.ones(nf)]
    result=milp(objective,integrality=np.ones(nc+nf),bounds=Bounds(0,1),constraints=LinearConstraint(matrix,lower,upper),options={'time_limit':30,'mip_rel_gap':1e-6})
    if result.x is None or result.status!=0:
        raise RuntimeError(f'MILP not proven optimal: {result.message}')
    selected=set(cities[i] for i in range(nc) if result.x[i]>.5)
    chosen=rows[rows.municipality_id.isin(selected)]
    names=sorted(chosen.municipality.unique())
    total=len(set(chosen.feature_id))
    supported=len(set(chosen[chosen.original_text_support_count>0].feature_id))
    modeled=len(set(r[r.municipality_id.isin(selected)].feature_id))
    assert modeled == round(sum(result.x[nc:])), 'Coverage variables differ from actual selected set'
    return {'strict_original_text_constraint':original_only,'proof':'scipy.optimize.milp solved to optimality', 'candidate_municipalities':nc,'activity_types_eligible':nf,'selected_municipalities':names,'selected_n':len(names),'accepted_activity_types_covered':total,'original_text_supported_types_covered':supported,'objective_types_covered':modeled,'assumed_cost_mxn':len(names)*5000,'budget_mxn':30000}


def s5_comparison(bootstrap_n=2000):
    predictions=pd.read_csv(FORECAST,parse_dates=['date'])
    wide=predictions.pivot(index=['center','date'],columns='model',values='error').reset_index()
    common=wide.dropna(subset=['tuned_forest','last_month']).copy()
    history=pd.read_csv(HIST).rename(columns={'fecha':'date','centro':'center','ocupacion_pct':'occupancy'})[['center','date','occupancy']]
    recent=pd.read_csv(RECENT).rename(columns={'fecha':'date','centro':'center','ocupacion_pct':'occupancy'})[['center','date','occupancy']]
    all_series=pd.concat([history,recent],ignore_index=True)
    all_series['date']=pd.to_datetime(all_series.date).dt.to_period('M').dt.to_timestamp()
    if all_series.duplicated(['center','date']).any():
        raise ValueError('Overlapping center/month data')
    values={(r.center,r.date):float(r.occupancy) for r in all_series.itertuples(index=False)}
    actual=[];season=[];three=[];monthmean=[]
    for row in common.itertuples(index=False):
        target=(row.center,row.date)
        actual.append(values[target])
        subset=all_series[(all_series.center==row.center)&(all_series.date<row.date)]
        previous_year=subset.loc[subset.date==row.date-pd.DateOffset(months=12),'occupancy']
        trailing=subset.loc[subset.date>=row.date-pd.DateOffset(months=3),'occupancy']
        historical_month=subset.loc[subset.date.dt.month==row.date.month,'occupancy']
        season.append(float(previous_year.iloc[0]) if len(previous_year) else np.nan)
        three.append(float(trailing.mean()) if len(trailing) else np.nan)
        monthmean.append(float(historical_month.mean()) if len(historical_month) else np.nan)
    if not(np.isfinite(season).all() and np.isfinite(three).all() and np.isfinite(monthmean).all()):
        raise ValueError('Additional baselines not available for every shared test observation')
    common['actual']=actual
    common['seasonal_naive_abs_error']=abs(common.actual-season)
    common['three_month_mean_abs_error']=abs(common.actual-three)
    common['historical_month_mean_abs_error']=abs(common.actual-monthmean)
    common['last_month_abs_error']=abs(common.last_month)
    common['tuned_forest_abs_error']=abs(common.tuned_forest)
    common['original_forest_abs_error']=abs(common.original_forest)
    metrics=[]
    for model in ['tuned_forest','original_forest','last_month','seasonal_naive','three_month_mean','historical_month_mean']:
        metrics.append({'model':model,'n_paired':len(common),'mae':float(common[model+'_abs_error'].mean())})
    # Circular 4-month block resampling. Cluster all 3 centers in each month together.
    months=sorted(common.date.unique()); length=len(months); block=4
    comparison=[]
    for baseline in ['last_month','seasonal_naive','three_month_mean','historical_month_mean']:
        common[baseline+'_gain_pp']=common[baseline+'_abs_error']-common.tuned_forest_abs_error
        per_month={t:common.loc[common.date==t,baseline+'_gain_pp'].to_numpy() for t in months}
        rng=np.random.default_rng(20261020); samples=[]
        for _ in range(bootstrap_n):
            ix=[]
            while len(ix)<length:
                start=int(rng.integers(length)); ix.extend((start+i)%length for i in range(block))
            sampled=np.concatenate([per_month[months[j]] for j in ix[:length]])
            samples.append(float(sampled.mean()))
        low,high=np.percentile(samples,[2.5,97.5])
        comparison.append({'baseline':baseline,'paired_n':len(common),'months_n':length,'forest_mae_pp':float(common.tuned_forest_abs_error.mean()),'baseline_mae_pp':float(common[baseline+'_abs_error'].mean()),'improvement_pp':float(common[baseline+'_gain_pp'].mean()),'block_bootstrap_95pct_lower_pp':float(low),'block_bootstrap_95pct_upper_pp':float(high),'resampling_note':'Illustrative circular 4-calendar-month block bootstrap with all centers grouped per month; 19 months is a short series; no formal superiority claim against all baselines.'})
    common[['center','date','actual','tuned_forest_abs_error','original_forest_abs_error','last_month_abs_error','seasonal_naive_abs_error','three_month_mean_abs_error','historical_month_mean_abs_error']].to_csv(OUT/'s5_paired_errors.csv',index=False,date_format='%Y-%m-%d',float_format='%.10f')
    pd.DataFrame(metrics).to_csv(OUT/'s5_paired_metrics.csv',index=False,float_format='%.8f')
    pd.DataFrame(comparison).to_csv(OUT/'s5_baseline_comparison.csv',index=False,float_format='%.8f')
    return {'total_forest_predictions':int((predictions.model=='tuned_forest').sum()),'paired_predictions':len(common),'paired_months':length,'centers':int(common.center.nunique()),'comparison':comparison,'conclusion':'The forest improves on last_month persistence, but its advantage over the three-month mean and seasonal-naive baselines is too small/uncertain here to justify an operational forecast feature.'}



def s6_interval_audit():
    path = ROOT / 'outputs/stochastic/s6_rolling_comparison_predictions.csv'
    stated = ROOT / 'outputs/stochastic/s6_rolling_comparison_metrics.csv'
    p = pd.read_csv(path)
    m = pd.read_csv(stated)
    assert len(p) > 0 and len(m) == 12
    p['covered'] = p['covered'].astype(bool)
    assert np.isclose(p['width'].to_numpy(),(p['upper']-p['lower']).to_numpy(),atol=1e-8).all()
    for summary in m.itertuples(index=False):
        part=p[(p.center==summary.center)&(p.method==summary.method)]
        assert len(part)==summary.months
        assert int(part.covered.sum()) == summary.covered
        assert np.isclose(part.width.mean(),summary.mean_width,atol=1e-8)
        assert np.isclose(part.covered.mean(),summary.coverage,atol=1e-8)
    records=[]
    for center,group in m.groupby('center'):
        fixed=group[group.method=='fixed_2023_2024'].iloc[0]
        rolling=group[group.method=='rolling_12'].iloc[0]
        records.append({'center':center,'n_evaluated':int(fixed.months),
                        'fixed_coverage':float(fixed.coverage),'fixed_width_pp':float(fixed.mean_width),
                        'rolling12_coverage':float(rolling.coverage),'rolling12_width_pp':float(rolling.mean_width),
                        'coverage_change':float(rolling.coverage-fixed.coverage),
                        'width_change_pp':float(rolling.mean_width-fixed.mean_width)})
    return {'prediction_rows_checked':len(p),'metric_rows_checked':len(m),'by_center':records,
            'interpretation':'Recomputed historical interval metrics are internally consistent. Wider intervals can yield higher coverage; neither predictive calibration for new locations nor tourist demand estimates follow.'}

def main():
    OUT.mkdir(exist_ok=True,parents=True)
    data=database_audit(); rows=evidence_rows(); s4=s4_audit(rows)
    or_all=solve_coverage(rows,False);or_strict=solve_coverage(rows,True)
    s5=s5_comparison(); s6=s6_interval_audit()
    if or_all['objective_types_covered']!=47 or or_strict['objective_types_covered']!=47:
        raise AssertionError('Historical 47-activity optimum not reproduced; investigate changed inputs')
    write_json(OUT/'database_audit.json',data)
    write_json(OUT/'s4_evidence_discovery.json',s4)
    write_json(OUT/'s7_evidence_sensitive_optimization.json',{'all_documented':or_all,'strict_original_text':or_strict})
    write_json(OUT/'s5_paired_interpretation.json',s5)
    write_json(OUT/'s6_interval_audit.json',s6)
    queue=rows[rows.municipality.isin(CAMPAIGN)].sort_values(['municipality','feature_id'])
    queue.to_csv(OUT/'s8_campaign_claims_evidence.csv',index=False)
    gates={
     'S0_S3':{'state':'PARTIAL','reason':'Recovered SQLite and archived HTML pass checks; full frozen-source rebuild cannot be verified because original raw ZIPs/PDFs were intentionally excluded.'},
     'S4_activity_discovery':{'state':'PASS','reason':'Exact source-linked activity intersections; no segmentation claims or imputed tourism absence.'},
     'S4_clusters':{'state':'HISTORICAL_ONLY','reason':'Old cluster views have exploratory diagnostics but no validated current recommendation benefit.'},
     'S5_forecasting':{'state':'RESEARCH_PASS_DEPLOYMENT_HOLD','reason':'Paired 52-month-center test plus additional baselines; no decisive improvement over rolling average.'},
     'S6_stochastic':{'state':'RESEARCH_PASS_DEPLOYMENT_HOLD','reason':'12 saved interval comparison metrics reproduced from 212 predictions; live predictive calibration and separate Markov experiment integration remain unavailable.'},
     'S7_coverage_optimization':{'state':'PASS_ASSUMPTION_DEPENDENT','reason':'Independent exact MILP solves reproduce 47 types under both evidence criteria; costs assumed.'},
     'S8_marketing':{'state':'PARTIAL','reason':'Archival campaign claim ledger exported; live access, audience performance, prices unverified.'},
     'S9_final':{'state':'PENDING','reason':'Need stage-by-stage integration and rubric-specific submissions.'}}
    write_json(OUT/'GATE_STATE.json',gates)
    print('SQLite integrity, 295 source restorations: PASS')
    print('S4 activity discovery: PASS; six-municipality supported pairs:',s4['campaign_links_with_original_text_support'],'/',s4['campaign_distinct_feature_links'])
    print('S7 optimal coverage:',or_all['objective_types_covered'],'strict:',or_strict['objective_types_covered'])
    print('S5 paired MAE:',[(a['baseline'],round(a['baseline_mae_pp'],3),round(a['forest_mae_pp'],3)) for a in s5['comparison']])
    print('Saved results to:',OUT)

if __name__=='__main__':
    main()
