"""Reproducible processing benchmark on real DataTur records and labelled replicas.

This IS NOT evidence of new observations or distributed execution. Replication is a
synthetic load test measuring throughput, storage/query scaling and index behavior.
"""
from __future__ import annotations
import argparse
import csv
import json
import os
import resource
import sqlite3
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/raw/Base70centros.csv'
OUTPUT = ROOT / 'outputs/bigdata/data_processing_benchmark.json'
REQUIRED = ('anio','mes','centro','cuartos_disponibles','llegada_turistas_residentes')


def worker(scale: int):
    start = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix='veracruz_bd_') as temp:
        db_path=Path(temp)/'benchmark.sqlite'
        db=sqlite3.connect(db_path)
        db.execute('PRAGMA journal_mode=OFF')
        db.execute('PRAGMA synchronous=OFF')
        db.execute('CREATE TABLE datatur (replica INTEGER, report_year INTEGER, month INTEGER, center TEXT, rooms_available INTEGER, arrivals_residents INTEGER)')
        source_rows=0
        sum_base=0
        one_row_groups={}
        inserted=0
        batch=[]
        for replica in range(scale):
            with DATA.open(encoding='utf-8-sig',newline='') as f:
                reader=csv.DictReader(f,delimiter='\t')
                missing=set(REQUIRED)-set(reader.fieldnames or [])
                if missing:raise AssertionError(f'Missing fields: {missing}')
                for row in reader:
                    year=int(row['anio']);month=int(row['mes'])
                    rooms=int(float(row['cuartos_disponibles'] or '0'))
                    arrivals=int(float(row['llegada_turistas_residentes'] or '0'))
                    center=row['centro']
                    batch.append((replica,year,month,center,rooms,arrivals))
                    inserted+=1
                    if replica==0:
                        source_rows+=1;sum_base+=rooms
                        if year==2024:
                            k=(center,month);one_row_groups[k]=one_row_groups.get(k,0)+rooms
                    if len(batch)>=4000:
                        db.executemany('INSERT INTO datatur VALUES (?,?,?,?,?,?)',batch)
                        batch.clear()
            if batch:
                db.executemany('INSERT INTO datatur VALUES (?,?,?,?,?,?)',batch);batch.clear()
        db.commit()
        ingest=time.perf_counter()-start
        assert inserted == source_rows*scale
        total=db.execute('SELECT COUNT(*),SUM(rooms_available) FROM datatur').fetchone()
        assert total==(inserted,sum_base*scale),f'Ingest mismatch {total}'
        # Index-vs-scan test on identical aggregate query.
        query='SELECT center,month,SUM(rooms_available) FROM datatur WHERE report_year=2024 GROUP BY center,month ORDER BY center,month'
        t=time.perf_counter();baseline=db.execute(query).fetchall();scan_seconds=time.perf_counter()-t
        assert len(baseline)==len(one_row_groups)
        assert all(v==one_row_groups[(c,m)]*scale for c,m,v in baseline)
        t=time.perf_counter();db.execute('CREATE INDEX idx_year_center_month ON datatur(report_year,center,month)');db.commit();index_seconds=time.perf_counter()-t
        t=time.perf_counter();indexed=db.execute(query).fetchall();indexed_seconds=time.perf_counter()-t
        assert baseline==indexed
        bytes_used=db_path.stat().st_size
        db.close()
    return {'scale_factor_synthetic':scale,'source_records':source_rows,
        'test_records':inserted,'input_file':str(DATA.relative_to(ROOT)),
        'input_bytes':DATA.stat().st_size,'insert_seconds':round(ingest,5),
        'scan_query_seconds':round(scan_seconds,5),'index_seconds':round(index_seconds,5),
        'indexed_query_seconds':round(indexed_seconds,5),
        'sqlite_file_bytes':bytes_used,
        'query_groups':len(baseline),
        'verification':'COUNT and SUM scale exactly; indexed aggregation matches full scan',
        'max_rss_kib_process':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--worker',type=int)
    parser.add_argument('--scales',type=int,nargs='+',default=[1,8,16,64])
    a=parser.parse_args()
    if a.worker is not None:
        print(json.dumps(worker(a.worker)))
        return
    outputs=[]
    for n in a.scales:
        if n<1 or n>64:raise ValueError('scale 1 to 64 only')
        r=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--worker',str(n)],capture_output=True,text=True,check=True)
        d=json.loads(r.stdout);outputs.append(d)
        print(f"{n}x {d['test_records']:,} rows: ingest {d['insert_seconds']:.2f}s, "
              f"scan {d['scan_query_seconds']:.3f}s, indexed {d['indexed_query_seconds']:.3f}s")
    result={
      'study':'Bounded scalability and index benchmark on DataTur real source rows plus declared synthetic replicas',
      'synthetic_not_new_tourist_observations':True,
      'distributed_framework_tested':False,
      'production_capability_claim':'none',
      'interpretation':'Measures local throughput, disk space, indexing and aggregate query correctness; not an actual distributed Big Data cluster or evidence of added tourist sample size.',
      'runs':outputs,
    }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('Wrote',OUTPUT.relative_to(ROOT))
if __name__=='__main__':main()
