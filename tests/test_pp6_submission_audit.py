"""Check that the academic gap inventory doesn't confuse outputs with completed research."""
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('pp6_submission_audit',ROOT/'scripts/pp6/audit_deliverables.py')
MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

def test_rubric_totals():
    result=MODULE.check_artifacts()
    assert result['rubric_criteria']==11 and result['rubric_weight_total']==100
    assert len(result['deliverables_expected'])==4

def test_report_is_not_automatically_certified():
    result=MODULE.check_artifacts()
    assert result['report_final_certified'] is False
    assert result['report_sections_required']==23

def test_distinguish_computation_from_campaign():
    records={x['id']:x for x in MODULE.check_artifacts()['items']}
    assert records['research_database']['state']=='PRESENT'
    assert records['live_implementation']['state']=='EXTERNAL'
    assert records['integrated_colloquium']['state']=='MISSING'
