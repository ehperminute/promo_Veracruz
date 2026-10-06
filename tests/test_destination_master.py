from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "processed" / "destination_master.csv"


def _master():
    return pd.read_csv(MASTER).set_index("destination")


def test_destination_master_has_expected_grain_and_no_future_campaign_fields():
    df = pd.read_csv(MASTER)
    assert len(df) == 55
    assert df["destination"].is_unique
    assert "comments_future_campaign_only" not in df.columns
    assert "comments_future_use" not in df.columns
    assert "cluster_k15" not in df.columns


def test_destination_master_rebuilds_known_denue_pib_values():
    df = _master()
    assert int(df.loc["Córdoba", "lodging_establishments"]) == 80
    assert int(df.loc["Córdoba", "food_beverage_establishments"]) == 2371
    assert int(df.loc["Córdoba", "recreation_tourism_proxy"]) == 23
    assert int(df.loc["Córdoba", "agencies_tours_events"]) == 11
    assert int(df.loc["Córdoba", "tourist_transport_proxy"]) == 10
    assert df.loc["Córdoba", "tourism_gdp_2022_mxn2018"] == pytest.approx(2291385198.3258405)


def test_destination_master_rebuilds_observed_inah_anchor():
    df = _master()
    assert int(df.loc["Papantla", "inah_series_available"]) == 1
    assert df.loc["Papantla", "inah_visitors_2025"] == 308598
    assert df.loc["Papantla", "inah_foreign_share_2025"] == pytest.approx(0.009335770160532473)
    assert df.loc["Papantla", "demand_evidence"] == "INAH attraction series"
    assert df.loc["Papantla", "model_role_v1"] == "Observed anchor / training evidence"


def test_destination_master_rebuilds_datatur_context_without_calling_it_municipal_demand():
    df = _master()
    for destination in ["Veracruz", "Boca del Río"]:
        assert int(df.loc[destination, "datatur_coverage"]) == 1
        assert df.loc[destination, "datatur_center"] == "Veracruz-Boca del Río"
        assert "combinado" in df.loc[destination, "datatur_scope_note"].lower()
        assert df.loc[destination, "datatur_arrivals_2024"] == 2481563
        assert df.loc[destination, "datatur_occupancy_2024_pct"] == pytest.approx(52.15094278783945)


def test_undermeasured_means_unmeasured_not_zero_demand():
    df = _master()
    assert df.loc["Catemaco", "model_role_v1"] == "Undermeasured analog target"
    assert df.loc["Catemaco", "demand_evidence"] == "No direct demand series in current project data"
    assert pd.isna(df.loc["Catemaco", "inah_visitors_2025"])
    assert pd.isna(df.loc["Catemaco", "datatur_arrivals_2024"])
    # Structural evidence can still be substantial.
    assert int(df.loc["Catemaco", "lodging_establishments"]) == 40
    assert int(df.loc["Catemaco", "food_beverage_establishments"]) == 287


def test_coverage_dimension_is_derived_from_current_sources():
    df = _master()
    assert int(df.loc["Actopan", "coverage_dimensions_n"]) == 4
    assert int(df.loc["Boca del Río", "coverage_dimensions_n"]) == 4
    assert int(df.loc["Calcahualco", "coverage_dimensions_n"]) == 2


def test_master_has_no_negative_structural_counts():
    df = pd.read_csv(MASTER)
    cols = [
        "lodging_establishments",
        "food_beverage_establishments",
        "recreation_tourism_proxy",
        "agencies_tours_events",
        "tourist_transport_proxy",
    ]
    assert (df[cols] >= 0).all().all()
