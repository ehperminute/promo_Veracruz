"""Evaluate original and preselected S5 models on new observed 2025-2026 months.
Run from repository root: python scripts/evaluate_s5_25_26_data.py
No test-period model selection. Missing published months remain missing.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline

HIST = Path('data/interim/datatur_veracruz_monthly.csv')
NEW = Path('data/reference/datatur_veracruz_monthly_2025_2026.csv')
TUNED = Path('outputs/ml/s5_rf_tuning_test_metrics.csv')
OUT = Path('outputs/ml')
FIXED = dict(n_estimators=120, max_depth=5, min_samples_leaf=3, max_features=1.0)


def load_data(hist=HIST, new=NEW):
    a = pd.read_csv(hist).rename(columns={'fecha':'date', 'ocupacion_pct':'occupancy', 'centro':'center'})
    b = pd.read_csv(new).rename(columns={'fecha':'date', 'ocupacion_pct':'occupancy', 'centro':'center'})
    required = {'date','center','occupancy'}
    for label, frame in [('historical',a),('supplementary',b)]:
        if not required <= set(frame):
            raise ValueError(f'{label} missing {required-set(frame)}')
    a=a[['date','center','occupancy']].assign(origin='historical')
    b=b[['date','center','occupancy']].assign(origin='supplementary')
    data=pd.concat([a,b],ignore_index=True)
    data['date']=pd.to_datetime(data.date).dt.to_period('M').dt.to_timestamp()
    data['occupancy']=pd.to_numeric(data.occupancy,errors='raise')
    if data[['date','center','occupancy']].isna().any().any() or not data.occupancy.between(0,100).all():
        raise ValueError('Invalid dates, centers or occupancy values')
    if data.duplicated(['center','date']).any():
        raise ValueError('Overlapping or duplicate center/month rows: inspect input files')
    names=set(a.center.unique())
    if set(b.center.unique()) != names:
        raise ValueError(f'Center names differ between historical and new files: {names} vs {set(b.center.unique())}')
    if data.loc[data.origin=='supplementary','date'].min() < pd.Timestamp('2025-01-01'):
        raise ValueError('New observations overlap or predate the new evaluation window')
    return data.sort_values(['center','date']).reset_index(drop=True)


def feature(history, date):
    """Build month-t features using only observations strictly before t.
    Missing lags remain NaN and are imputed inside training pipeline.
    """
    if any(t >= date for t in history):
        raise ValueError('Future observation in history')
    lag=lambda k: history.get(date-pd.DateOffset(months=k), np.nan)
    last3=np.array([lag(k) for k in (1,2,3)],dtype=float)
    last12=np.array([lag(k) for k in range(1,13)],dtype=float)
    return np.array([np.sin(2*np.pi*date.month/12), np.cos(2*np.pi*date.month/12),
                     lag(1),lag(2),lag(3),lag(12),lag(24),
                     np.nanmean(last3) if np.isfinite(last3).any() else np.nan,
                     np.nanmean(last12) if np.isfinite(last12).any() else np.nan],dtype=float)


def choose_params(metrics_path=TUNED):
    chosen={}
    if Path(metrics_path).exists():
        table=pd.read_csv(metrics_path)
        for _,r in table.loc[table.model=='tuned_forest'].iterrows():
            chosen[r.center]=json.loads(r.params)
    return chosen


def evaluate(data, tuned):
    results=[]
    for center, df in data.groupby('center'):
        df=df.sort_values('date')
        observations={row.date:float(row.occupancy) for row in df.itertuples()}
        test_dates=[d for d in observations if d>=pd.Timestamp('2025-01-01')]
        if not test_dates: continue
        for date in sorted(test_dates):
            # Refit using past outcomes only; features use only dates before each target.
            history={dt:v for dt,v in observations.items() if dt<date}
            train_dates=[dt for dt in sorted(history) if dt>=pd.Timestamp('2018-01-01')]
            X=np.array([feature({k:v for k,v in history.items() if k<dt},dt) for dt in train_dates])
            y=np.array([history[dt] for dt in train_dates])
            if len(y)<36: raise ValueError('Not enough training history')
            pred={}
            models={'original_forest': FIXED, 'tuned_forest': tuned.get(center, FIXED)}
            for name,params in models.items():
                model=make_pipeline(SimpleImputer(strategy='median'),RandomForestRegressor(**params, random_state=42,n_jobs=1))
                model.fit(X,y)
                pred[name]=float(np.clip(model.predict(feature(history,date).reshape(1,-1))[0],0,100))
            prior=history.get(date-pd.DateOffset(months=1))
            if prior is not None: pred['last_month']=prior
            for label,value in pred.items():
                results.append(dict(center=center,date=date.strftime('%Y-%m-%d'),year=date.year,
                                    model=label,actual=observations[date],predicted=value,
                                    error=observations[date]-value,train_n=len(y),
                                    previous_month_observed=prior is not None))
    return pd.DataFrame(results)


def summarize(predictions):
    metrics=(predictions.groupby(['center','year','model'],as_index=False)
             .agg(n_test=('error','size'),mae=('error',lambda s:float(np.mean(abs(s)))),
                  rmse=('error',lambda s:float(np.sqrt(np.mean(s*s)))), bias=('error','mean')))
    aggregate=(predictions.groupby(['model'],as_index=False)
               .agg(n_test=('error','size'),mae=('error',lambda s:float(np.mean(abs(s)))),
                    rmse=('error',lambda s:float(np.sqrt(np.mean(s*s)))),bias=('error','mean')))
    aggregate.insert(0,'center','ALL_CENTERS');aggregate.insert(1,'year','2025-2026')
    return pd.concat([metrics,aggregate],ignore_index=True)


def main():
    data=load_data(); tuned=choose_params(); predicted=evaluate(data,tuned); metrics=summarize(predicted)
    OUT.mkdir(parents=True,exist_ok=True)
    predicted.to_csv(OUT/'s5_25_26_predictions.csv',index=False)
    metrics.to_csv(OUT/'s5_25_26_metrics.csv',index=False)
    (OUT/'s5_25_26_metadata.json').write_text(json.dumps({
        'evaluation':'rolling one-month-ahead with models refitted using prior observed outcomes',
        'test_period':'2025-01 through 2026-07',
        'fixed_models':'Original forest and tuned parameters chosen from 2021-2022 validation',
        'missing_data':'Missing center/month occupancy is never filled; missing lag features use training-only medians',
        'baseline':'last_month omitted when immediately preceding observation is missing',
        'center_counts':data[data.date>=pd.Timestamp('2025-01-01')].groupby('center').size().to_dict(),
        'limitations':['Official reports may be provisional','No destination-level demand extrapolation']},indent=2),encoding='utf-8')
    print(metrics.sort_values(['center','year','mae']).to_string(index=False))
    print('Saved to:',OUT)

if __name__=='__main__':main()
