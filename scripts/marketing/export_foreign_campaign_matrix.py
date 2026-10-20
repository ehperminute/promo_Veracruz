"""Reproduce the original 24-cell *proposed* campaign matrix from its authored specification.

This creates no observed campaign metrics. Kept separate from live/site outputs.
"""
from pathlib import Path
import csv
import hashlib
import shutil

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/marketing/foreign_campaign_test_matrix_v1.csv"
OUTPUT = ROOT / "outputs/marketing/foreign_campaign_test_matrix_v1.csv"


def main():
    with SOURCE.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 24, "Authored matrix must have 24 controlled cells"
    assert len({r["test_id"] for r in rows}) == 24, "Duplicate test identifiers"
    assert all(r["source_market"] and r["primary_metric"] for r in rows), "Incomplete matrix"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if not OUTPUT.exists() or hashlib.sha256(OUTPUT.read_bytes()).digest() != hashlib.sha256(SOURCE.read_bytes()).digest():
        shutil.copyfile(SOURCE, OUTPUT)
    assert OUTPUT.read_bytes() == SOURCE.read_bytes()
    print(f"PASS: {len(rows)} planned marketing cells exported (not observed results)")

if __name__ == "__main__":
    main()
