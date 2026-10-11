"""S6: held-out occupancy uncertainty evaluation. Run at repository root."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import numpy as np
import pandas as pd

OLD = 'outputs/ml/s5_rf_tuning_test_predictions.csv'
NEW = 'outputs/ml/s5_new_period_predictions.csv'
MODEL = 'tuned_forest'
ALPHA = .10


def conformal_radius(errors, alpha=ALPHA):
    """Finite sample absolute-residual conformal quantile; no interpolation."""
    errors = np.sort(np.abs(np.asarray(errors, dtype=float)))
    errors = errors[np.isfinite(errors)]
    n = len(errors)
    if n == 0:
        raise ValueError('No calibration errors')
    k = math.ceil((n + 1) * (1-alpha))
    if k > n:
        return float('inf')
    return float(errors[k-1])


def load(p):
    df = pd.read_csv(p)
    required = {'center','date','model','actual','predicted'}
    if not required.issubset(df.columns):
        raise ValueError(f'{p}: missing {sorted(required-set(df.columns))}')
    df['date'] = pd.to_datetime(df['date'])
    for col in ['actual','predicted']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.loc[df['model'] == MODEL].copy()
    if df.empty: raise ValueError(f'{p}: no {MODEL} rows')
    if df.duplicated(['center','date']).any(): raise ValueError(f'{p}: duplicate center dates')
    if df[['actual','predicted']].isna().any().any(): raise ValueError(f'{p}: nonnumeric outcomes')
    if not (df['actual'].between(0,100).all() and df['predicted'].between(0,100).all()):
        raise ValueError(f'{p}: occupancy should be 0..100 percent')
    df['abs_error'] = (df['actual']-df['predicted']).abs()
    return df


def run(old_path, new_path, output):
    old, new = load(old_path), load(new_path)
    assert old['date'].max() < new['date'].min(), 'Overlapping evaluation periods'
    all_rows=[]; metrics=[]
    for center in sorted(new['center'].unique()):
        old_c = old[old.center==center]
        new_c = new[new.center==center]
        if old_c.empty: raise ValueError(f'No old calibration data for {center}')
        splits = [
            ('2024_check', old_c[old_c.date.dt.year==2023], old_c[old_c.date.dt.year==2024]),
            ('2025_2026_check', old_c[old_c.date.dt.year.isin([2023,2024])], new_c),
        ]
        for label, calib, evaluation in splits:
            if calib.empty or evaluation.empty: raise ValueError(f'Empty split: {center}, {label}')
            if calib.date.max() >= evaluation.date.min(): raise ValueError('Calibration must precede evaluation')
            radius=conformal_radius(calib.abs_error)
            # Occupancy is bounded, so truncate symmetric ranges at physical limits.
            df=evaluation[['center','date','actual','predicted','abs_error']].copy()
            df['period']=label
            df['calibration_n']=len(calib)
            df['radius_pp']=radius
            df['lower_pct']=(df.predicted-radius).clip(lower=0)
            df['upper_pct']=(df.predicted+radius).clip(upper=100)
            df['covered']=(df.actual >= df.lower_pct) & (df.actual <= df.upper_pct)
            df['interval_width_pp']=df.upper_pct-df.lower_pct
            all_rows.append(df)
            metrics.append({'center':center,'period':label,'calibration_n':len(calib),
                            'n_evaluated':len(df),'nominal_coverage':1-ALPHA,
                            'radius_pp':radius,'covered_n':int(df.covered.sum()),
                            'observed_coverage':float(df.covered.mean()),
                            'mean_interval_width_pp':float(df.interval_width_pp.mean()),
                            'point_mae_pp':float(df.abs_error.mean())})
    intervals=pd.concat(all_rows,ignore_index=True).sort_values(['period','center','date'])
    scores=pd.DataFrame(metrics).sort_values(['period','center'])
    output.mkdir(parents=True, exist_ok=True)
    intervals.to_csv(output/'s6_intervals.csv',index=False,date_format='%Y-%m-%d')
    scores.to_csv(output/'s6_coverage_metrics.csv',index=False)
    (output/'s6_method.json').write_text(json.dumps({
        'model':MODEL,'alpha':ALPHA,'description':'Absolute-error split conformal intervals, calibrated separately per center on earlier out-of-sample errors.',
        'test_2024':'2023 calibration (12 errors per center) -> 2024 evaluation',
        'test_2025_2026':'2023-2024 calibration (24 errors per center) -> Jan 2025-Jul 2026 evaluation',
        'cautions':['Conformal nominal coverage needs exchangeability; time series shifts violate this assumption.',
                    'Small calibration samples; these intervals are empirical checks, not assured 90% coverage.',
                    'Missing new-period observations have not been imputed.',
                    'Only three measured hotel centers; not tourism visitation forecasts for other destinations.',
                    'Rolling S5 models update training, so intervals refer to one-step rolling predictions, not a frozen 2024 model.']
    },indent=2),encoding='utf-8')
    print(scores.to_string(index=False,float_format=lambda x:f'{x:.3f}'))
    print(f'\nSaved: {output}')
    return scores


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--old',default=OLD)
    parser.add_argument('--new',default=NEW)
    parser.add_argument('--out',default='outputs/stochastic')
    a=parser.parse_args()
    run(Path(a.old),Path(a.new),Path(a.out))

if __name__=='__main__': main()
