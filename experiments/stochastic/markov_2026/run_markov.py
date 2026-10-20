#!/usr/bin/env python3
"""Reproducible first-order Markov experiment: Veracruz DataTur hotel occupancy.
Source: verified repository snapshot data/reference/datatur_veracruz_monthly_2025_2026.csv.
Train: observed 2025 adjacent months. Holdout: 2026 Jan-Jul, requiring observed t-1.
"""
import csv, json, math, random
from pathlib import Path
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
OUT=HERE/'outputs'
OUT.mkdir(exist_ok=True)
# Versioned copy of the project reference DataTur data, not code-generated observations.
# Source columns and original source_archive are preserved in source_data/.
source_file=HERE/'source_data'/'datatur_2025_2026_snapshot.csv'
obs=pd.read_csv(source_file).sort_values(['centro','fecha'])
expected={'centro','fecha','anio','mes','ocupacion_pct'}
if not expected.issubset(obs.columns):
    raise ValueError(f'Missing columns in source: {expected-set(obs.columns)}')
if len(obs)!=53: raise ValueError(f'Expected 53 source observations; found {len(obs)}')
obs.to_csv(OUT/'datatur_2025_2026_observado.csv',index=False)
TH=(40.0,50.0)
LABELS=['Baja','Media','Alta']
def state(x,t=TH):
    return int(x>=t[0])+int(x>=t[1])
def transitions(center,year=2025,t=TH):
    c=obs[(obs.centro==center)&(obs.anio==year)].copy().sort_values('fecha')
    seen={pd.Period(d,freq='M'):float(o) for d,o in zip(c.fecha,c.ocupacion_pct)}
    trans=[]
    for p,val in seen.items():
        prev=p-1
        if prev in seen: trans.append((int(state(seen[prev],t)),int(state(val,t))))
    return trans

def predict_test(center,t=TH):
    c=obs[obs.centro==center].copy()
    seen={pd.Period(d,freq='M'):float(o) for d,o in zip(c.fecha,c.ocupacion_pct)}
    train=transitions(center,2025,t)
    count=np.zeros((3,3),dtype=int)
    for a,b in train: count[a,b]+=1
    # Laplace add-one probability smoothing, predeclared (not tuned on test).
    P=(count+1)/(count.sum(axis=1,keepdims=True)+3)
    train_state=[state(v,t) for p,v in seen.items() if p.year==2025]
    freq=np.bincount(train_state,minlength=3)
    marginal=(freq+1)/(freq.sum()+3)
    recs=[]
    for p,val in seen.items():
        if p.year!=2026 or p.month>7 or p-1 not in seen:continue
        fr=state(seen[p-1],t);actual=state(val,t); pred=int(np.argmax(P[fr])); persistence=fr
        record={'centro':center,'fecha':str(p),'prev_state':LABELS[fr], 'observed_state':LABELS[actual],
         'markov_state':LABELS[pred],'persistence_state':LABELS[persistence],
         'markov_correct':int(pred==actual),'persistence_correct':int(fr==actual),
         'markov_prob_true':float(P[fr,actual]),'marginal_prob_true':float(marginal[actual]),
         'markov_brier':float(np.sum((P[fr]-np.eye(3)[actual])**2)),
         'marginal_brier':float(np.sum((marginal-np.eye(3)[actual])**2)),
         'markov_log_loss':float(-math.log(P[fr,actual])),'marginal_log_loss':float(-math.log(marginal[actual]))}
        recs.append(record)
    # simulated chain from last known 2025 state (or most recent at start)
    local=random.Random(20261018 + {'Coatzacoalcos':1,'Veracruz-Boca del Río':2,'Xalapa':3}[center])
    start=state(seen[pd.Period('2025-12')],t) if pd.Period('2025-12') in seen else state(seen[max(p for p in seen if p.year==2025)],t)
    sim=np.zeros(3,int)
    for run in range(1000):
        cur=start
        for _ in range(12):
            v=local.random();new=int(np.searchsorted(np.cumsum(P[cur]),v,side='right'));cur=min(new,2);sim[cur]+=1
    return count,P,pd.DataFrame(recs), sim/(1000*12),freq

all_pred=[];summary=[];matrix_rows=[];count_rows=[];sim_rows=[]
for center in ['Coatzacoalcos','Veracruz-Boca del Río','Xalapa']:
    counts,P,preds,sim,freq=predict_test(center)
    all_pred.append(preds)
    summary.append({'centro':center,'2025_train_transitions':int(counts.sum()),'2025_train_observations':int(freq.sum()),'2026_test_transitions':len(preds),
        'markov_correct':int(preds.markov_correct.sum()),'markov_accuracy':float(preds.markov_correct.mean()),
        'persistence_correct':int(preds.persistence_correct.sum()),'persistence_accuracy':float(preds.persistence_correct.mean()),
        'markov_brier':float(preds.markov_brier.mean()), 'baseline_marginal_brier':float(preds.marginal_brier.mean()),
        'markov_log_loss':float(preds.markov_log_loss.mean()),'baseline_marginal_log_loss':float(preds.marginal_log_loss.mean())})
    for i in range(3):
        for j in range(3):
            matrix_rows.append({'centro':center,'estado_origen':LABELS[i],'estado_destino':LABELS[j], 'conteo_2025':int(counts[i,j]),'probabilidad_suavizada':round(float(P[i,j]),5)})
        sim_rows.append({'centro':center,'estado':LABELS[i],'fraccion_simulada_12_pasos':round(float(sim[i]),5)})
summary=pd.DataFrame(summary)
summary.to_csv(OUT/'resumen_validacion_markov.csv',index=False)
pd.concat(all_pred).to_csv(OUT/'predicciones_fuera_muestra_2026.csv',index=False)
pd.DataFrame(matrix_rows).to_csv(OUT/'matrices_transicion_2025.csv',index=False)
pd.DataFrame(sim_rows).to_csv(OUT/'simulacion_markov_12_meses.csv',index=False)
summary_total={
 'train_transitions':int(summary['2025_train_transitions'].sum()),
 'test_n':int(summary['2026_test_transitions'].sum()),
 'markov_correct':int(summary.markov_correct.sum()),
 'persistence_correct':int(summary.persistence_correct.sum()),
 'markov_accuracy':float(summary.markov_correct.sum()/summary['2026_test_transitions'].sum()),
 'persistence_accuracy':float(summary.persistence_correct.sum()/summary['2026_test_transitions'].sum()),
 'markov_brier':float(np.average(summary.markov_brier, weights=summary['2026_test_transitions'])),
 'baseline_marginal_brier':float(np.average(summary.baseline_marginal_brier,weights=summary['2026_test_transitions']))}
(OUT/'metadata.json').write_text(json.dumps({'source':'DataTur monthly Veracruz published archive; repo reference file data/reference/datatur_veracruz_monthly_2025_2026.csv','training':'2025','test':'2026-01 through 2026-07, consecutive months only','state_thresholds':{'low':'<40%','medium':'40%-<50%','high':'>=50%'},'smoothing':'Laplace alpha=1','simulation':'1000 trajectories x 12 steps; no forecasting validity claim','overall':summary_total},indent=2,ensure_ascii=False))
print(summary.round(3).to_string(index=False));print('TOTAL',summary_total);print(pd.DataFrame(matrix_rows).pivot_table(index=['centro','estado_origen'],columns='estado_destino',values='conteo_2025'))
