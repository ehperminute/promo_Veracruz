import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run_s5 import normalize,feature_row,evaluate,next_month_forecast

def fixture():
    months=pd.date_range('2016-01-01',periods=108,freq='MS')
    return pd.DataFrame([{'centro':c,'date':dt,'ocupacion_pct':float(45+6*np.sin(i*2*np.pi/12)+v)}
                        for c,v in [('A',0),('B',4),('C',-4)] for i,dt in enumerate(months)])

def test_data_shape_and_backtest():
    d=normalize(fixture(),'centro')
    p,m=evaluate(d)
    assert len(p)==3*24*5
    assert set(p.model)=={'last_month','seasonal_naive','historical_month_average','ridge','random_forest'}
    assert (pd.to_datetime(p.train_through)<pd.to_datetime(p.date)).all()
    assert (m.mae>=0).all()
    nxt=next_month_forecast(d,{c:'seasonal_naive' for c in ['A','B','C']})
    assert set(nxt.forecast_month)=={'2025-01-01'}

def test_reject_gaps_and_duplicates():
    f=fixture()
    with pytest.raises(ValueError):normalize(f.drop(10),'centro')
    with pytest.raises(ValueError):normalize(pd.concat([f,f.iloc[[0]]]),'centro')

def test_features_use_only_history():
    a=list(range(24))
    assert feature_row(a,pd.Timestamp('2020-01-01'))[2]==23
    assert feature_row(a,pd.Timestamp('2020-01-01'))[5]==12
