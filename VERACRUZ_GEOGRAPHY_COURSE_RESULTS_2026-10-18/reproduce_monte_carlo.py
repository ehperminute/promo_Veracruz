#!/usr/bin/env python3
"""Monte Carlo baseline: uniform random municipality selections (not tourism demand).
Run: python reproduce_monte_carlo.py path/to/veracruz_master_with_verified_evidence.sqlite [output_folder]
"""
import csv,random,statistics,sqlite3,sys
from collections import defaultdict
from pathlib import Path

def run(db,out):
 conn=sqlite3.connect(f'file:{Path(db).resolve()}?mode=ro',uri=True)
 m=defaultdict(set)
 for mid,fid in conn.execute('select municipality_id, feature_id from s4_statewide_evidence_pairs_v1'):m[mid].add(fid)
 candidates=sorted(m)
 if len(candidates)!=61:raise ValueError('Unexpected activity evidence cohort; refusing silent data version change')
 rows=conn.execute('select budget_mxn,number_promotions,exact_distinct_activities from or_statewide_scenario_results where scope=? order by budget_mxn',('statewide_212_registry_evidence_supported',)).fetchall()
 if len(rows)!=4:raise ValueError('Incomplete campaign optimization baseline')
 rng=random.Random(20261018); output=[]; stats=[]
 for budget,k,opt in rows:
  vals=[]
  for trial in range(1,5001):
   sample=rng.sample(candidates,k);coverage=len(set().union(*(m[x] for x in sample)))
   vals.append(coverage);output.append((budget,trial,k,coverage))
  sortedvals=sorted(vals)
  stats.append((budget,k,opt,round(statistics.mean(vals),2),round(statistics.stdev(vals),2),sortedvals[int(.025*(len(vals)-1))],sortedvals[int(.975*(len(vals)-1))],sum(v>=opt for v in vals)/len(vals)))
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 for fn,header,data in [('monte_carlo_draws.csv',['budget_mxn','simulation','selected_municipalities','distinct_activity_types'],output),('monte_carlo_summary.csv',['budget_mxn','promotions','exact_activity_coverage','random_mean','random_sd','random_p025','random_p975','fraction_at_least_optimum'],stats)]:
  with (out/fn).open('w',encoding='utf-8-sig',newline='') as f:w=csv.writer(f);w.writerow(header);w.writerows(data)
 for row in stats:print(row)
if __name__=='__main__':
 if len(sys.argv)<2:raise SystemExit(__doc__)
 run(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else '.');
