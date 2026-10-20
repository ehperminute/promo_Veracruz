"""Execute one PP6 research gate without modifying source DB, site or map.

Stages use the *same* reviewed calculations as experiments/pp6_second_pass;
separating invocation means one failed/blocked experiment cannot starve others.
"""
from __future__ import annotations
import argparse
import importlib.util
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RUN_PASS = ROOT / "experiments/pp6_second_pass/run_pass.py"
spec = importlib.util.spec_from_file_location("pp6_scientific_pass", RUN_PASS)
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("database", "discovery", "forecast", "intervals", "milp", "campaign"))
    stage = parser.parse_args().stage
    p.OUT.mkdir(parents=True, exist_ok=True)
    if stage == "database":
        result = p.database_audit()
        assert result["integrity"] == "ok"
        assert result["municipalities"] == 212
        assert result["original_product_descriptions_restored"] == 295
        p.write_json(p.OUT/"database_audit.json", result)
    elif stage == "discovery":
        result = p.s4_audit(p.evidence_rows())
        assert result["campaign_links_with_original_text_support"] == 65
        p.write_json(p.OUT/"s4_evidence_discovery.json", result)
    elif stage == "forecast":
        result = p.s5_comparison()
        assert result["paired_predictions"] == 52
        p.write_json(p.OUT/"s5_paired_interpretation.json", result)
    elif stage == "intervals":
        result = p.s6_interval_audit()
        assert result["prediction_rows_checked"] == 212 and result["metric_rows_checked"] == 12
        p.write_json(p.OUT/"s6_interval_audit.json", result)
    elif stage == "milp":
        rows = p.evidence_rows()
        standard = p.solve_coverage(rows,False)
        strict = p.solve_coverage(rows,True)
        assert standard["objective_types_covered"] == strict["objective_types_covered"] == 47
        p.write_json(p.OUT/"s7_evidence_sensitive_optimization.json",{"all_documented":standard,"strict_original_text":strict})
    else:
        rows = p.evidence_rows()
        evidence = rows[rows.municipality.isin(p.CAMPAIGN)].sort_values(["municipality","feature_id"])
        assert len(evidence) == 66 and int((evidence.original_text_support_count>0).sum()) == 65
        evidence.to_csv(p.OUT/"s8_campaign_claims_evidence.csv",index=False)
    print("PASS",stage, "— verifiable artifact written only in experiments/pp6_second_pass/results/")

if __name__ == "__main__":
    main()
