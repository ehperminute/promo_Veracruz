from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "mining"))

import common  # noqa: E402


def test_s4_uses_current_canonical_inputs_not_legacy_v1():
    assert common.DESTINATION_MASTER.name == "destination_master.csv"
    assert common.PARSED_PRODUCTS.name == "veracruz_products_parsed.csv"
    scripts = "\n".join(
        p.read_text(encoding="utf-8")
        for p in (ROOT / "scripts" / "mining").glob("*.py")
    )
    assert "destination_master_v1.csv" not in scripts
    assert "tourism_products_sample_v1.csv" not in scripts


def test_clustering_features_exclude_direct_demand_and_region_is_interpretive_only():
    used = (
        set(common.PROFILE_NUMERIC_FEATURES)
        | set(common.PROFILE_SYMMETRIC_BINARY)
        | set(common.PROFILE_ASYMMETRIC_BINARY)
    )
    assert not (used & common.FORBIDDEN_DEMAND_FEATURES)
    assert "region_turistica_preliminar" not in used
    assert "datatur_arrivals_2024" not in used
    assert "inah_visitors_2025" not in used
