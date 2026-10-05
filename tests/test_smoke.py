from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def test_destination_master_has_expected_grain():
    df = pd.read_csv(ROOT / "data" / "processed" / "destination_master_v1.csv")
    assert len(df) == 55
    assert df["destination"].is_unique

def test_products_sample_has_75_products():
    df = pd.read_csv(ROOT / "data" / "processed" / "tourism_products_sample_v1.csv")
    assert len(df) == 75
    assert df["producto"].notna().all()

def test_outputs_are_results_not_project_notes():
    outputs = ROOT / "outputs"
    bad = {"METHODOLOGY.md", "PROJECT_STATUS.md", "DECISIONS_AND_LIMITATIONS.md"}
    present = {p.name for p in outputs.rglob("*") if p.is_file()}
    assert not (bad & present)
