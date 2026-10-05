from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]

def test_market_table_has_25_ranked_markets():
    path = ROOT / "data" / "processed" / "international_market_opportunity_v1.csv"
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 25
    assert [int(r["rank_2025"]) for r in rows] == list(range(1, 26))

def test_campaign_matrix_has_24_controlled_cells():
    path = ROOT / "outputs" / "marketing" / "foreign_campaign_test_matrix_v1.csv"
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 24
    assert len({r["test_id"] for r in rows}) == 24
