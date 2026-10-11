"""S5: leakage-safe, one-month-ahead Veracruz hotel occupancy backtest.

Input: data/interim/datatur_veracruz_monthly.csv, created by existing S2 pipeline.
Outputs: outputs/ml/*.csv and figures/*.png; no invented observations.
"""
from pathlib import Path
import argparse
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def load_series(path):
    df = pd.read_csv(path)
    df = df.rename(columns={"fecha": "date"})
    required = {'date', 'ocupacion_pct'}
    if not required.issubset(df.columns):
        raise ValueError(f'Missing columns {required - set(df.columns)}; got {list(df.columns)}')
    # Existing S2 data may label the reporting center differently across exports.
    candidates = ['centro', 'centro_turistico', 'centro_nombre', 'nombre_centro', 'destino', 'nombre', 'centro_hotelero']
    center = next((c for c in candidates if c in df.columns), None)
    if center is None:
        raise ValueError(f'Cannot identify hotel-center column. Available: {list(df.columns)}. Pass --center-col.')
    return normalize(df, center)


def normalize(df, center):
    d = df[[center, 'date', 'ocupacion_pct']].copy()
    d.columns = ['center', 'date', 'occupancy']
    d['date'] = pd.to_datetime(d['date'])
    d['occupancy'] = pd.to_numeric(d['occupancy'], errors='raise')
    if d[['center', 'date', 'occupancy']].isna().any().any():
        raise ValueError('Null center/date/occupancy values')
    if not d['occupancy'].between(0, 100).all():
        raise ValueError('Occupancy outside 0..100')
    if d.duplicated(['center', 'date']).any():
        raise ValueError('Duplicate center-month rows; use the existing aggregated S2 input')
    d['date'] = d['date'].dt.to_period('M').dt.to_timestamp()
    if d.duplicated(['center', 'date']).any():
        raise ValueError('Duplicate monthly observations')
    for c, g in d.groupby('center'):
        g = g.sort_values('date')
        expected = pd.date_range(g.date.iloc[0], g.date.iloc[-1], freq='MS')
        if list(g.date) != list(expected):
            raise ValueError(f'Missing month or non-monthly dates in {c}; no synthetic fill applied')
    return d.sort_values(['center', 'date']).reset_index(drop=True)


def feature_row(history, target_month):
    # history ends at t-1; all features available before month t begins.
    vals = np.asarray(history, dtype=float)
    if len(vals) < 24:
        raise ValueError('24 prior months required')
    m = target_month.month
    return [np.sin(2*np.pi*m/12), np.cos(2*np.pi*m/12), vals[-1], vals[-2], vals[-3], vals[-12], vals[-24], vals[-3:].mean(), vals[-12:].mean()]


def model_for(name):
    if name == 'ridge':
        return make_pipeline(StandardScaler(), Ridge(alpha=10.0))
    if name == 'random_forest':
        return RandomForestRegressor(n_estimators=120, max_depth=5, min_samples_leaf=3, random_state=42, n_jobs=1)
    raise ValueError(name)


def evaluate(d, first_test_year=2023, min_train_rows=24):
    rows = []
    for center, g in d.groupby('center'):
        g = g.sort_values('date').reset_index(drop=True)
        y = g.occupancy.to_numpy(dtype=float)
        dates = g.date.to_list()
        feats = np.asarray([feature_row(y[:i], dates[i]) for i in range(24, len(g))])
        for i in range(24, len(g)):
            if dates[i].year < first_test_year:
                continue
            tr_count = i-24
            if tr_count < min_train_rows:
                raise ValueError(f'Insufficient training rows in {center} for {dates[i]:%Y-%m}: {tr_count}')
            prior = y[:i]
            # Three deterministic baselines + models fit ONLY to outcomes before test date.
            pred = {'last_month': prior[-1], 'seasonal_naive': prior[-12],
                    'historical_month_average': np.mean([y[j] for j in range(i) if dates[j].month == dates[i].month])}
            for name in ['ridge', 'random_forest']:
                mod = model_for(name)
                mod.fit(feats[:tr_count], y[24:i])
                pred[name] = mod.predict(feats[i-24:i-23])[0]
            for name, p in pred.items():
                p = float(np.clip(p, 0, 100))
                rows.append({'center': center, 'date': dates[i].strftime('%Y-%m-%d'),
                             'model': name, 'actual': y[i], 'predicted': p, 'error': y[i]-p,
                             'train_through': dates[i-1].strftime('%Y-%m-%d'), 'train_n': tr_count})
    if not rows:
        raise ValueError('No test months: check --test-year')
    predictions = pd.DataFrame(rows)
    metrics = predictions.groupby(['center','model'], as_index=False).agg(
        n_test=('error','size'), mae=('error',lambda x: float(np.abs(x).mean())),
        rmse=('error',lambda x: float(np.sqrt(np.mean(x*x)))), bias=('error','mean'))
    total = predictions.groupby('model',as_index=False).agg(
        n_test=('error','size'), mae=('error',lambda x: float(np.abs(x).mean())),
        rmse=('error',lambda x: float(np.sqrt(np.mean(x*x)))), bias=('error','mean'))
    total.insert(0, 'center', 'ALL_CENTERS')
    return predictions, pd.concat([metrics,total],ignore_index=True)


def next_month_forecast(d, best_models):
    out=[]
    for center, g in d.groupby('center'):
        g=g.sort_values('date').reset_index(drop=True)
        y=g.occupancy.to_numpy(dtype=float)
        next_date=g.date.iloc[-1]+pd.offsets.MonthBegin(1)
        name=best_models[center]
        if name=='last_month': p=y[-1]
        elif name=='seasonal_naive': p=y[-12]
        elif name=='historical_month_average': p=np.mean([v for v,dt in zip(y,g.date) if dt.month==next_date.month])
        else:
            X=np.asarray([feature_row(y[:i],g.date.iloc[i]) for i in range(24,len(g))])
            model=model_for(name)
            model.fit(X,y[24:])
            p=model.predict(np.asarray(feature_row(y,next_date)).reshape(1,-1))[0]
        out.append(dict(center=center,forecast_month=next_date.strftime('%Y-%m-%d'),model=name,
                        predicted_occupancy_pct=round(float(np.clip(p,0,100)),3),
                        last_observation=g.date.iloc[-1].strftime('%Y-%m-%d')))
    return pd.DataFrame(out)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',default='data/interim/datatur_veracruz_monthly.csv')
    ap.add_argument('--center-col',default=None)
    ap.add_argument('--output',default='outputs/ml')
    ap.add_argument('--test-year',type=int,default=2023)
    args=ap.parse_args()
    raw=pd.read_csv(args.input)
    if args.center_col:
        if args.center_col not in raw.columns: raise ValueError(f'Unknown center column {args.center_col}')
        d=normalize(raw,args.center_col)
    else: d=load_series(args.input)
    preds,metrics=evaluate(d,args.test_year)
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    preds.to_csv(out/'s5_backtest_predictions.csv',index=False)
    metrics.to_csv(out/'s5_backtest_metrics.csv',index=False)
    winner=(metrics[metrics.center!='ALL_CENTERS'].sort_values(['center','mae','rmse','model'])
            .drop_duplicates('center').set_index('center')['model'].to_dict())
    next_month_forecast(d,winner).to_csv(out/'s5_next_month_forecasts.csv',index=False)
    metadata={'target':'one-month-ahead hotel occupancy percentage, by DataTur hotel reporting center',
              'input':str(args.input),'source_coverage':{str(c):{'first':g.date.min().strftime('%Y-%m'),'last':g.date.max().strftime('%Y-%m'),'n':len(g)} for c,g in d.groupby('center')},
              'test_start_year':args.test_year,'evaluation':'expanding-window, re-fit at every target month, no future inputs',
              'selected_models':winner,'limitations':['Not tourist visitor counts','Not forecasts for the other 52 destinations','No independent cross-city extrapolation validation','Next-month projections are anchored at the last input month, not necessarily the present']}
    (out/'s5_metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    print(metrics.sort_values(['center','mae']).to_string(index=False))
    print('Saved:',out)

if __name__=='__main__': main()
