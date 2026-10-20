"""Check original 2026-2 rubric transcription; not grading individual submissions."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_original_rubric_is_complete():
    r=json.loads((ROOT/'docs/pp6/original_rubric_spec.json').read_text(encoding='utf-8'))
    assert len(r['weights'])==11
    assert len({x[0] for x in r['weights']})==11
    assert sum(x[1] for x in r['weights'])==100
    assert len(r['products'])==4
    assert [30,40]==next(x['suggested_pages_excluding_appendices'] for x in r['products'] if x['id']=='technical_report')
    assert next(x['max_minutes'] for x in r['products'] if x['id']=='colloquium')==15
