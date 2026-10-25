#!/usr/bin/env python3
"""Synthetic metadata workload only. Not a real traveler data experiment."""
import argparse,random,sqlite3,tempfile,time,statistics
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--rows',type=int,default=100_000);a=p.parse_args()
if a.rows<1 or a.rows>2_000_000:raise SystemExit('rows must be between 1 and 2,000,000')
rng=random.Random(2026)
places=['30038','30092','30088','30124','30032','30141','30112','30203']
cats=['food','accommodation','activity','transport']
with tempfile.TemporaryDirectory() as d:
    db=Path(d)/'synthetic_trip_events.sqlite'; con=sqlite3.connect(db)
    con.execute('CREATE TABLE expense_events(event_id INTEGER PRIMARY KEY, municipality TEXT, category TEXT, amount_cents INTEGER, period TEXT)')
    start=time.perf_counter()
    for i in range(0,a.rows,2000):
        batch=[(j,rng.choice(places),rng.choice(cats),rng.randint(3000,90000),f'2026-{rng.randint(1,12):02d}') for j in range(i,min(i+2000,a.rows))]
        con.executemany('INSERT INTO expense_events VALUES (?,?,?,?,?)',batch)
    con.commit();loaded=time.perf_counter()-start
    q='SELECT municipality, category, COUNT(*), AVG(amount_cents) FROM expense_events GROUP BY municipality,category'
    start=time.perf_counter();v1=con.execute(q).fetchall();scan=time.perf_counter()-start
    con.execute('CREATE INDEX idx_region_category ON expense_events(municipality,category)')
    start=time.perf_counter();v2=con.execute(q).fetchall();indexed=time.perf_counter()-start
    assert len(v1)==len(v2) and all(x[:3]==y[:3] and abs(x[3]-y[3])<1e-6 for x,y in zip(v1,v2))
    con.close()
print(f'Only SYNTHETIC records: {a.rows}, ingest {loaded:.3f}s, unindexed agg {scan:.3f}s, indexed agg {indexed:.3f}s')
print('Never report as observed traveler expenditure. This is not a distributed-systems benchmark.')
