from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_readme_documents_reproducible_milestone_command():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "scripts/data/run_data_pipeline.py --idempotence --test" in text
    assert "Missing DataTur coverage is missing measurement" in text
    assert "56 Milestone-1 tests PASS" in text
    assert "demand_series.csv" in text
    assert "origin_market_opportunity.csv" in text


def test_project_tree_reflects_current_milestone_files():
    text = (ROOT / "PROJECT_TREE.txt").read_text(encoding="utf-8")
    for required in [
        "source_registry.csv",
        "denue_activity_groups.csv",
        "origin_market_2025_validated.csv",
        "prepare_veracruz_web_reference.py",
        "build_demand_series.py",
        "prepare_origin_markets.py",
        "demand_series.csv",
        "origin_market_opportunity.csv",
        "veracruz_pueblos_magicos_2026-10-06_manual.html",
        "test_veracruz_web_reference.py",
        "test_demand_series.py",
        "test_origin_market_opportunity.py",
    ]:
        assert required in text
    assert "promo_veracruz_milestone1_patch.zip" not in text
