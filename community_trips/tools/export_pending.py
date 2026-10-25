#!/usr/bin/env python3
"""Export one private pending submission from local pilot receiver for manual review."""
import argparse,json,sqlite3
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('submission_id');p.add_argument('--database',type=Path,default=Path('.private_trip_submissions/pending.sqlite'))
p.add_argument('--out',type=Path,default=Path('/tmp/veracruz_trip_submission.json'))
a=p.parse_args()
with sqlite3.connect(a.database) as con:
    row=con.execute("SELECT document_json FROM submissions WHERE submission_id=? AND status='pending'",(a.submission_id,)).fetchone()
if not row:raise SystemExit('No pending record with this ID')
a.out.write_text(json.dumps(json.loads(row[0]),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Exported private review file:',a.out)
print('Review text and photos before publishing with publish_reviewed_trip.py')
