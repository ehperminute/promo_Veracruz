import sqlite3,sys,pandas as pd
from itertools import combinations
from scipy.stats import fisher_exact
from statsmodels.stats.multitest import multipletests
from pathlib import Path
p=Path(sys.argv[1])
con=sqlite3.connect(p)
r=pd.read_sql('SELECT DISTINCT municipality_id, family FROM s4_statewide_evidence_pairs_v1',con)
x=pd.crosstab(r.municipality_id,r.family).gt(0)
rows=[]
for a,b in combinations(x.columns,2):
  aa=x[a];bb=x[b];co=int((aa&bb).sum());n=len(x)
  t=[[co,int((aa&~bb).sum())],[int((~aa&bb).sum()),int((~aa&~bb).sum())]]
  _,p=fisher_exact(t,alternative='greater')
  rows.append(dict(category_1=a,category_2=b,municipalities_both=co,support=co/n,confidence_given_1=co/aa.sum(),lift=co*n/(aa.sum()*bb.sum()),p_one_sided=p))
d=pd.DataFrame(rows);d['q_BH_36_tests']=multipletests(d.p_one_sided,method='fdr_bh')[1]
d.sort_values('p_one_sided').to_csv('category_pair_audit.csv',index=False)
print('municipalities',len(x),'pairs tested',len(d),'significant after BH',sum(d.q_BH_36_tests<0.05))
