"""Tune S5 Random Forest without selecting hyperparameters on the final test years.

Usage: python scripts/tune_s5.py
Uses data/interim/datatur_veracruz_monthly.csv (project S2 output).
Tuning window 2021-2022; untouched evaluation window 2023-2024.
"""
import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from run_s5 import load_series, feature_row


def make_features(group):
    group = group.sort_values('date').reset_index(drop=True)
    y = group['occupancy'].to_numpy(dtype=float)
    dates = group['date'].tolist()
    X = np.asarray([feature_row(y[:i], dates[i]) for i in range(24, len(y))])
    return dates, y, X


def predict_at(X, y, i, params):
    # Feature row j corresponds to target y[j+24]. Train strictly before month i.
    model = RandomForestRegressor(**params, random_state=42, n_jobs=1)
    model.fit(X[:i-24], y[24:i])
    return float(np.clip(model.predict(X[i-24:i-23])[0], 0, 100))


def score_window(group, params, start_year, end_year, refit_stride=1):
    dates, y, X = make_features(group)
    indices = [i for i in range(24, len(y)) if start_year <= dates[i].year <= end_year]
    if not indices:
        raise ValueError(f'No rows for {start_year}-{end_year}')
    errors = []
    predictions = []
    for i in indices:
        if i-24 < 24:
            raise ValueError(f'Insufficient historical training data for {dates[i]}')
        p = predict_at(X, y, i, params)
        errors.append(abs(y[i]-p))
        predictions.append({'date':dates[i].strftime('%Y-%m-%d'), 'actual':y[i], 'predicted':p,
                            'error':y[i]-p})
    return float(np.mean(errors)), predictions


def grid():
    # 24 combinations. Keep modest; 108 months per city cannot support huge trees reliably.
    for trees, depth, leaf, features in itertools.product(
        [100, 200], [3, 5, None], [2, 5], [0.7, 1.0]
    ):
        yield dict(n_estimators=trees, max_depth=depth,
                   min_samples_leaf=leaf, max_features=features)


def run(d, validation=(2021, 2022), test=(2023, 2024)):
    tuning, predictions, summary = [], [], []
    fixed = dict(n_estimators=120, max_depth=5, min_samples_leaf=3, max_features=1.0)
    for center, group in d.groupby('center'):
        best = None
        for params in grid():
            mae, _ = score_window(group, params, *validation)
            tuning.append({'center': center, 'validation_mae':mae, **params})
            if best is None or mae < best[0]:
                best = (mae, params)
        chosen = best[1]
        for label, params in [('original_forest', fixed), ('tuned_forest', chosen)]:
            test_mae, records = score_window(group, params, *test)
            for r in records:
                predictions.append({'center':center, 'model':label, **r})
            summary.append({'center':center, 'model':label, 'test_mae':test_mae,
                            'validation_mae_of_chosen':best[0] if label=='tuned_forest' else np.nan,
                            'params':json.dumps(params, sort_keys=True)})
        # Simple, existing last-month baseline, same test rows.
        dates, y, _ = make_features(group)
        vals=[{'date':dates[i].strftime('%Y-%m-%d'), 'actual':y[i],
               'predicted':y[i-1], 'error':y[i]-y[i-1]}
              for i in range(24,len(y)) if test[0]<=dates[i].year<=test[1]]
        for r in vals:
            predictions.append({'center':center, 'model':'last_month', **r})
        summary.append({'center':center, 'model':'last_month',
                        'test_mae':float(np.mean([abs(r['error']) for r in vals])),
                        'validation_mae_of_chosen':np.nan, 'params':'{}'})
    return pd.DataFrame(tuning), pd.DataFrame(predictions), pd.DataFrame(summary)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', default='data/interim/datatur_veracruz_monthly.csv')
    parser.add_argument('--output', default='outputs/ml')
    args=parser.parse_args()
    d=load_series(args.input)
    tuning, preds, metrics=run(d)
    out=Path(args.output); out.mkdir(parents=True,exist_ok=True)
    tuning.to_csv(out/'s5_rf_tuning_validation.csv',index=False)
    preds.to_csv(out/'s5_rf_tuning_test_predictions.csv',index=False)
    metrics.to_csv(out/'s5_rf_tuning_test_metrics.csv',index=False)
    print(metrics[['center','model','test_mae']].to_string(index=False))
    print('Parameters selected ONLY on 2021-2022. Final testing ONLY on 2023-2024.')
    print('Saved:',out)

if __name__=='__main__':
    main()
