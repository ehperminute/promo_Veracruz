import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd

spec=importlib.util.spec_from_file_location('run_s6',Path(__file__).resolve().parents[1]/'scripts/run_s6.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_radius():
    assert m.conformal_radius([1]*24)==1
    assert m.conformal_radius(range(1,13))==12
    assert m.conformal_radius(range(1,25))==23

def test_periods_and_bounds(tmp_path):
    old=[];new=[]
    for center in ['A','B']:
        for dt in pd.date_range('2023-01-01',periods=24,freq='MS'):
            old.append((center,dt,'tuned_forest',52,50))
        for dt in pd.date_range('2025-01-01',periods=19,freq='MS'):
            new.append((center,dt,'tuned_forest',52,50))
    cols=['center','date','model','actual','predicted']
    pd.DataFrame(old,columns=cols).to_csv(tmp_path/'old.csv',index=False)
    pd.DataFrame(new,columns=cols).to_csv(tmp_path/'new.csv',index=False)
    r=m.run(tmp_path/'old.csv',tmp_path/'new.csv',tmp_path/'out')
    assert len(r)==4
    assert r['observed_coverage'].eq(1).all()
    assert (pd.read_csv(tmp_path/'out/s6_intervals.csv')['lower_pct']>=0).all()
