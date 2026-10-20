from run_markov import predict_test
import pandas as pd
c=['Coatzacoalcos','Veracruz-Boca del Río','Xalapa']
rows=[]
for thr in [(35,45),(40,50),(45,55)]:
 total=[]
 for center in c:
  counts,P,pred,sim,freq=predict_test(center,thr)
  rows.append({'umbrales':f'{thr[0]}/{thr[1]}','centro':center,'n':len(pred),'aciertos_markov':int(pred.markov_correct.sum()),'aciertos_persistencia':int(pred.persistence_correct.sum()),'brier_markov':round(float(pred.markov_brier.mean()),4),'brier_marginal':round(float(pred.marginal_brier.mean()),4)})
  total.append(pred)
 combo=pd.concat(total)
 rows.append({'umbrales':f'{thr[0]}/{thr[1]}','centro':'TODOS','n':len(combo),'aciertos_markov':int(combo.markov_correct.sum()),'aciertos_persistencia':int(combo.persistence_correct.sum()),'brier_markov':round(float(combo.markov_brier.mean()),4),'brier_marginal':round(float(combo.marginal_brier.mean()),4)})
df=pd.DataFrame(rows)
df.to_csv('outputs/sensibilidad_umbrales.csv',index=False)
print(df.to_string(index=False))
