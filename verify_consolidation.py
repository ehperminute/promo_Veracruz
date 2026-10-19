from pathlib import Path
import csv,sqlite3
root=Path(__file__).resolve().parent
p=root/'experiments/marketing/2026-10-19/sources/veracruz_pp3_master_RECOVERED.sqlite'
with sqlite3.connect(f'file:{p}?mode=ro',uri=True) as c:
 assert c.execute('pragma integrity_check').fetchone()[0]=='ok'
 assert c.execute('select count(*) from s4_statewide_evidence_pairs_v1').fetchone()[0]==216
for f,n in [('docs/mining/category_pair_audit.csv',36),('experiments/marketing/2026-10-19/results/coverage_212_before_after.csv',212),('experiments/marketing/2026-10-19/sources/verification_40.csv',40),('experiments/or/infrastructure_tradeoff_2026-10-19/comparison.csv',6)]:
 with (root/f).open(encoding='utf-8-sig',newline='') as src:
  assert sum(1 for _ in csv.DictReader(src))==n,(f,n)
assert (root/'progress_preguntas/04_Modelos_Estocasticos_Markov_Veracruz_2026-10-18.docx').exists()
print('PASS: SQLite integrity, 216 original activity pairs, 36 association tests, 40 verification decisions, 212 municipalities, six new scenarios and Markov report')
