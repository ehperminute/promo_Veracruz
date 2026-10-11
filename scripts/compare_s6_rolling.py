import pandas as pd,numpy as np,math
from pathlib import Path
Path("outputs/stochastic").mkdir(parents=True,exist_ok=True)
old=pd.read_csv('outputs/ml/s5_rf_tuning_test_predictions.csv',parse_dates=['date'])
new=pd.read_csv('outputs/ml/s5_25_26_predictions.csv',parse_dates=['date'])
old=old[old.model=='tuned_forest'];new=new[new.model=='tuned_forest']

def rad(a):
 a=np.sort(np.abs(np.asarray(a)));k=math.ceil((len(a)+1)*.9);return float(a[min(k,len(a))-1]) if len(a) else float('nan')
records=[]
for center in new.center.unique():
 history=old[old.center==center].sort_values('date').copy(); history['abs_error']=(history.actual-history.predicted).abs()
 upcoming=new[new.center==center].sort_values('date').copy()
 for _,r in upcoming.iterrows():
  for scheme in ['fixed_2023_2024','rolling_12','rolling_24','expanding']:
   past=history.abs_error.to_numpy()
   if scheme=='fixed_2023_2024': past=old[old.center==center].assign(a=lambda x:(x.actual-x.predicted).abs()).a.to_numpy()
   elif scheme=='rolling_12': past=past[-12:]
   elif scheme=='rolling_24': past=past[-24:]
   q=rad(past); lo=max(0,r.predicted-q);hi=min(100,r.predicted+q)
   records.append(dict(center=center,date=r.date,method=scheme,actual=r.actual,predicted=r.predicted,lower=lo,upper=hi,radius=q,covered=lo<=r.actual<=hi,width=hi-lo))
  history=pd.concat([history,pd.DataFrame([dict(date=r.date,abs_error=abs(r.actual-r.predicted))])],ignore_index=True)
out=pd.DataFrame(records)
summary=out.groupby(['center','method']).agg(months=('covered','size'),covered=('covered','sum'),coverage=('covered','mean'),mean_width=('width','mean'),mean_radius=('radius','mean')).reset_index();print(summary.to_string(index=False,float_format=lambda x:f'{x:.3f}'))
out.to_csv('outputs/stochastic/s6_rolling_comparison_predictions.csv',index=False);summary.to_csv('outputs/stochastic/s6_rolling_comparison_metrics.csv',index=False)
