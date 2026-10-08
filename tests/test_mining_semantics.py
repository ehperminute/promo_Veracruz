from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "MINING_METHODS.md"
CATALOG = ROOT / "docs" / "DATA_CATALOG.md"


def test_mining_document_preserves_interpretation_boundaries_and_method():
    text = DOC.read_text(encoding="utf-8")
    assert "Gower" in text
    assert "PAM" in text
    assert "k=2 through k=20" in text
    assert "not geographic routes" in text
    assert "not tourist itineraries" in text
    assert "Direct demand" in text
    assert "295" in text


def test_data_catalog_explains_75_vs_295_products_and_intermediate_tables():
    text = CATALOG.read_text(encoding="utf-8")
    assert "295 product cards" in text
    assert "75-product coursework selection" in text
    assert "data/interim/destination_profiles_s4.csv" in text
    assert "data/processed/demand_series.csv" in text
