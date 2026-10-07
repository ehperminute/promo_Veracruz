from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "data" / "reference" / "source_registry.csv"
RESOLVED = ROOT / "data" / "interim" / "source_registry_resolved.csv"
DOC = ROOT / "docs" / "DATA_SOURCES.md"


def test_source_registry_covers_local_raw_and_fixed_remote_sources():
    ref = pd.read_csv(REFERENCE, dtype=str).fillna("")
    assert len(ref) == 14
    assert ref["filename"].is_unique
    assert set(ref["storage_mode"]) == {"local_raw", "remote_fixed"}

    local = ref[ref["storage_mode"] == "local_raw"]
    remote = ref[ref["storage_mode"] == "remote_fixed"]
    assert len(local) == 13
    assert len(remote) == 1
    assert local["expected_sha256"].str.fullmatch(r"[0-9a-f]{64}").all()
    assert remote["expected_sha256"].eq("").all()
    assert ref["source_url"].str.startswith("https://").all()


def test_resolved_registry_verifies_local_bytes_without_network_dependency():
    df = pd.read_csv(RESOLVED, dtype=str).fillna("")
    assert len(df) == 14
    local = df[df["storage_mode"] == "local_raw"]
    remote = df[df["storage_mode"] == "remote_fixed"]
    assert set(local["status"]) == {"verified"}
    assert local["expected_sha256"].equals(local["actual_sha256"])
    assert pd.to_numeric(local["bytes"]).gt(0).all()
    assert len(remote) == 1
    assert remote["status"].iloc[0] == "remote_fixed"
    assert remote["actual_sha256"].iloc[0] == ""


def test_generated_data_sources_document_lists_every_registered_source():
    ref = pd.read_csv(REFERENCE, dtype=str).fillna("")
    text = DOC.read_text(encoding="utf-8")
    for filename in ref["filename"]:
        assert filename in text
    assert "CAPTCHA" in text
    assert "SHA-256" in text
    assert "origin-market" in text
