from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "processed" / "demand_series.csv"


def test_demand_series_has_expected_observed_grain():
    df = pd.read_csv(PATH)
    assert len(df) == 4_372
    assert set(df["source_system"]) == {"DataTur", "INAH"}
    assert (df["source_system"] == "DataTur").sum() == 324
    assert (df["source_system"] == "INAH").sum() == 4_048
    assert not df.duplicated(["series_id", "date", "metric"]).any()


def test_demand_series_keeps_measurement_scopes_separate():
    df = pd.read_csv(PATH)
    pairs = set(zip(df["source_system"], df["metric"], df["measurement_scope"]))
    assert pairs == {
        ("DataTur", "hotel_arrivals_total", "hotel_center_arrivals"),
        ("INAH", "archaeological_site_visitors_total", "archaeological_site_visits"),
    }
    text = " ".join(df["interpretation_note"].dropna().astype(str).unique())
    assert "not municipal demand totals" in text
    assert "not total tourism demand" in text


def test_demand_series_contains_only_observed_nonnegative_values():
    df = pd.read_csv(PATH)
    values = pd.to_numeric(df["value"], errors="raise")
    assert values.notna().all()
    assert (values >= 0).all()


@pytest.mark.parametrize(
    "center, expected",
    [
        ("Coatzacoalcos", 473_350),
        ("Veracruz-Boca del Río", 2_481_563),
        ("Xalapa", 739_186),
    ],
)
def test_2024_datatur_arrivals_are_preserved(center, expected):
    df = pd.read_csv(PATH)
    rows = df[
        (df["source_system"] == "DataTur")
        & (df["geography_name"] == center)
        & (pd.to_numeric(df["year"]) == 2024)
    ]
    assert int(pd.to_numeric(rows["value"]).sum()) == expected


def test_inah_2026_stops_at_latest_observed_month_not_future_zeroes():
    df = pd.read_csv(PATH)
    rows = df[(df["source_system"] == "INAH") & (pd.to_numeric(df["year"]) == 2026)]
    assert pd.to_numeric(rows["month"]).max() == 8
