from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
FACT = ROOT / "data" / "interim" / "fact_datatur_centro_mes.csv"
VERACRUZ = ROOT / "data" / "interim" / "datatur_veracruz_monthly.csv"


def test_datatur_fact_has_expected_grain_and_time_span():
    df = pd.read_csv(FACT)
    assert len(df) == 6900
    assert df["anio"].min() == 2016
    assert df["anio"].max() == 2024
    assert not df.duplicated(["anio", "mes", "centro"]).any()
    assert df["mes"].between(1, 12).all()
    assert (df[["cuartos_disponibles", "cuartos_ocupados", "llegadas_total"]] >= 0).all().all()


def test_veracruz_datatur_slice_has_three_centers_and_324_months():
    df = pd.read_csv(VERACRUZ)
    assert len(df) == 324
    assert set(df["centro"]) == {"Coatzacoalcos", "Veracruz-Boca del Río", "Xalapa"}
    assert df.groupby("centro").size().to_dict() == {
        "Coatzacoalcos": 108,
        "Veracruz-Boca del Río": 108,
        "Xalapa": 108,
    }


@pytest.mark.parametrize(
    "center,expected_arrivals,expected_occupancy",
    [
        ("Coatzacoalcos", 473350, 48.23816317494676),
        ("Veracruz-Boca del Río", 2481563, 52.15094278783945),
        ("Xalapa", 739186, 49.60682352270578),
    ],
)
def test_2024_datatur_aggregates_match_known_raw_totals(center, expected_arrivals, expected_occupancy):
    df = pd.read_csv(VERACRUZ)
    rows = df[(df["centro"].eq(center)) & (df["anio"].eq(2024))]
    assert rows["llegadas_total"].sum() == expected_arrivals
    weighted_occupancy = 100 * rows["cuartos_ocupados"].sum() / rows["cuartos_disponibles"].sum()
    assert weighted_occupancy == pytest.approx(expected_occupancy, abs=1e-10)
