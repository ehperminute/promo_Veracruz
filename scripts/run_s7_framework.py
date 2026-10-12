"""S7 demonstrator: state-wide destination × season promotion planning.
Inputs: project S4 profiles + optional 2025–26 DataTur table.
Costs and scores are scenario assumptions; this does not estimate ROI or demand.
Requires pandas, numpy, scipy.
"""
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
from scipy.optimize import milp, Bounds, LinearConstraint
from scipy.sparse import lil_matrix

PERIODS = {'spring_holiday': (3,4), 'summer': (7,8), 'autumn': (10,11), 'winter': (12,1)}
THEMES = ['theme_beach_coast','theme_nature','theme_culture_history','theme_archaeology','theme_adventure','theme_gastronomy_coffee','theme_wellness_spiritual','theme_urban_services']

def solve(profiles, occupancy, budget, package_cost=5000, high_occupancy=80):
    """Binary MILP. Reward distinct region-periods, theme-periods, and documented readiness.
    Assumptions: one promotion costs package_cost, at most one period per destination,
    and 3 spots per region per period (illustrative concentration cap).
    """
    profiles=profiles.copy().reset_index(drop=True)
    N=len(profiles); periods=list(PERIODS); T=len(periods)
    regions=sorted(profiles['region_turistica_preliminar'].dropna().unique())
    profiles['services']=pd.to_numeric(profiles['lodging_establishments'],errors='coerce').fillna(0)
    profiles['cards']=pd.to_numeric(profiles['official_product_card_count_295'],errors='coerce').fillna(0)
    # readiness is an evidence proxy (not demand/potential): logarithmic scale prevents largest cities dominating
    services=np.log1p(profiles['services'].to_numpy())
    cards=np.log1p(profiles['cards'].to_numpy())
    readiness=0.5*services/(services.max() or 1)+0.5*cards/(cards.max() or 1)
    # No extrapolation to towns without actual center-level occupancy measurements
    risks={}
    if occupancy is not None and len(occupancy):
        d=occupancy.copy();d['mes']=pd.to_numeric(d['mes'],errors='coerce');d['ocupacion_pct']=pd.to_numeric(d['ocupacion_pct'],errors='coerce')
        for c in d['centro'].dropna().unique():
            for t, months in PERIODS.items():
                v=d[(d['centro']==c)&(d['mes'].isin(months))]['ocupacion_pct'].dropna()
                risks[(str(c),t)]=float(v.max()) if len(v) else None
    pairs=[(i,t) for i in range(N) for t in periods]
    xN=len(pairs)
    rp=[(r,t) for r in regions for t in periods]
    tp=[(f,t) for f in THEMES for t in periods]
    yr={key:xN+j for j,key in enumerate(rp)}
    yt={key:xN+len(rp)+j for j,key in enumerate(tp)}
    M=xN+len(rp)+len(tp)
    c=np.zeros(M)
    for idx,(i,t) in enumerate(pairs):
        center=profiles.loc[i,'datatur_center'] if 'datatur_center' in profiles else None
        occ=risks.get((str(center),t)) if pd.notna(center) else None
        is_high = occ is not None and occ >= high_occupancy
        # Small readiness reward; explicit penalty for documented peak occupancy
        c[idx]=-(readiness[i]*0.15 - (0.3 if is_high else 0))
    for j in yr.values():c[j]=-3.0
    for j in yt.values():c[j]=-0.45
    constraints=[]
    def add(entries, lo=-np.inf, hi=np.inf): constraints.append((entries,lo,hi))
    add({i:float(package_cost) for i in range(xN)},hi=float(budget))
    for i in range(N): add({i*T+k:1.0 for k in range(T)},hi=1)
    for r,t in rp:
        ids=[i*T+periods.index(t) for i in range(N) if profiles.loc[i,'region_turistica_preliminar']==r]
        add({j:1. for j in ids},hi=3)
        add({yr[(r,t)]:1.,**{j:-1. for j in ids}},hi=0)
    for f,t in tp:
        ids=[i*T+periods.index(t) for i in range(N) if pd.to_numeric(profiles.loc[i,f],errors='coerce')==1]
        add({yt[(f,t)]:1.,**{j:-1. for j in ids}},hi=0)
    A=lil_matrix((len(constraints),M));lower=[];upper=[]
    for row,(entries,lo,hi) in enumerate(constraints):
        for col,val in entries.items(): A[row,col]=val
        lower.append(lo);upper.append(hi)
    res=milp(c=c,integrality=np.ones(M),bounds=Bounds(np.zeros(M),np.ones(M)),constraints=LinearConstraint(A.tocsr(),lower,upper),options={'time_limit':30,'mip_rel_gap':0.001})
    if res.x is None:raise RuntimeError(f'No feasible solution: {res.message}')
    selected=[]
    for ix,(i,t) in enumerate(pairs):
        if res.x[ix]>0.5:
            row=profiles.loc[i]
            center=row.get('datatur_center',None)
            occ=risks.get((str(center),t)) if pd.notna(center) else None
            selected.append({'destination':row['destination'],'region':row['region_turistica_preliminar'],'period':t,'assumed_cost_mxn':package_cost,'lodging_establishments':int(row['services']),'official_card_count':int(row['cards']),'datatur_center':center if pd.notna(center) else '', 'observed_period_peak_pct':occ,'demand_data_status':'observed_center_2025_26' if occ is not None else 'no_comparable_monthly_data','theme_count':sum(int(row[f]==1) for f in THEMES)})
    out=pd.DataFrame(selected)
    per_region=out.groupby('region').size().to_dict() if len(out) else {}
    indicators={'budget_mxn':budget,'assumed_cost_per_promotion_mxn':package_cost,'spent_mxn':int(len(out)*package_cost),'num_promotions':len(out),'distinct_destinations':out['destination'].nunique() if len(out) else 0,'regions_represented':len(per_region),'total_regions':len(regions),'region_period_cells':len(out[['region','period']].drop_duplicates()) if len(out) else 0,'theme_period_cells':int(sum(any((profiles.loc[profiles['destination']==s['destination'],f]==1).any() for s in selected if s['period']==t) for t in periods for f in THEMES)),'reported_solver_status':res.message,'peak_penalty_threshold_pct':high_occupancy,'selected_with_unknown_period_demand':int((out['demand_data_status']=='no_comparable_monthly_data').sum()) if len(out) else 0}
    return out,indicators

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--profiles',default='data/interim/destination_profiles_s4.csv');ap.add_argument('--occupancy',default='data/reference/datatur_veracruz_monthly_2025_2026.csv');ap.add_argument('--out',default='outputs/or');ap.add_argument('--budgets',nargs='+',type=int,default=[30000,60000,100000,200000]);ap.add_argument('--unit-cost',type=int,default=5000)
    a=ap.parse_args();profiles=pd.read_csv(a.profiles);occ=pd.read_csv(a.occupancy) if Path(a.occupancy).exists() else None
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True);metrics=[]
    for b in a.budgets:
        selected,info=solve(profiles,occ,b,a.unit_cost);selected.to_csv(out/f's7_calendar_budget_{b}.csv',index=False);metrics.append(info)
    tab=pd.DataFrame(metrics);tab.to_csv(out/'s7_scenario_comparison.csv',index=False);print(tab[['budget_mxn','spent_mxn','distinct_destinations','regions_represented','region_period_cells','theme_period_cells','selected_with_unknown_period_demand']].to_string(index=False))
if __name__=='__main__':main()
