from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "data" / "reference" / "source_registry.csv"
RESOLVED = ROOT / "data" / "interim" / "source_registry_resolved.csv"
DOC = ROOT / "docs" / "DATA_SOURCES.md"


def test_source_registry_covers_all_13_frozen_raw_inputs():
    ref = pd.read_csv(REFERENCE, dtype=str).fillna("")
    assert len(ref) == 13
    assert ref["filename"].is_unique
    assert ref["expected_sha256"].str.fullmatch(r"[0-9a-f]{64}").all()
    assert ref["source_url"].str.startswith("https://").all()


def test_resolved_registry_verifies_exact_bytes():
    df = pd.read_csv(RESOLVED, dtype=str).fillna("")
    assert len(df) == 13
    assert set(df["status"]) == {"verified"}
    assert df["expected_sha256"].equals(df["actual_sha256"])
    assert pd.to_numeric(df["bytes"]).gt(0).all()


def test_generated_data_sources_document_lists_every_registered_file():
    ref = pd.read_csv(REFERENCE, dtype=str).fillna("")
    text = DOC.read_text(encoding="utf-8")
    for filename in ref["filename"]:
        assert f"`{filename}`" in text
    assert "CAPTCHA" in text
    assert "SHA-256" in text
