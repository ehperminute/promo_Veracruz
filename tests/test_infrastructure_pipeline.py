from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
MART = ROOT / "data" / "interim" / "mart_infraestructura_municipio_veracruz.csv"

COUNT_COLS = [
    "alojamiento_n",
    "alimentos_bebidas_n",
    "sector_recreacion_total_n",
    "recreacion_turistica_proxy_n",
    "agencias_tours_eventos_n",
    "transporte_turistico_n",
]


def test_infrastructure_mart_has_all_212_veracruz_municipalities():
    df = pd.read_csv(MART)
    assert len(df) == 212
    assert df["municipio"].is_unique
    assert df["clave_municipio"].astype(str).str.zfill(5).is_unique
    assert "Naolinco" in set(df["municipio"])
    assert "Naolinco (Naolinco de Victoria)" not in set(df["municipio"])
    assert (df[COUNT_COLS] >= 0).all().all()
    assert (df["recreacion_turistica_proxy_n"] <= df["sector_recreacion_total_n"]).all()


@pytest.mark.parametrize(
    "municipio,expected",
    [
        ("Acajete", [0, 39, 4, 3, 0, 0]),
        ("Acayucan", [32, 583, 41, 9, 40, 2]),
        ("Actopan", [6, 124, 11, 3, 0, 1]),
        ("Boca del Río", [80, 1630, 160, 12, 18, 4]),
        ("Veracruz", [200, 5325, 409, 31, 26, 9]),
    ],
)
def test_denue_counts_match_known_2026_snapshot(municipio, expected):
    df = pd.read_csv(MART).set_index("municipio")
    assert df.loc[municipio, COUNT_COLS].astype(int).tolist() == expected


def test_pib_2022_values_are_read_from_current_workbook_not_hardcoded():
    df = pd.read_csv(MART).set_index("municipio")
    assert df.loc["Boca del Río", "pib_turistico_2022"] == pytest.approx(13309403140.827042)
    assert df.loc["Boca del Río", "participacion_turismo_pct"] == pytest.approx(0.1956722532286187)
    assert df.loc["Papantla", "pib_turistico_2022"] == pytest.approx(485340729.72662777)
    assert pd.isna(df.loc["Calcahualco", "pib_turistico_2022"])
