from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
FACT = ROOT / "data" / "interim" / "fact_inah_veracruz_mes.csv"


def test_inah_fact_has_expected_grain_and_observed_only_months():
    df = pd.read_csv(FACT)
    assert len(df) == 4048
    assert df["recinto"].nunique() == 13
    assert not df.duplicated(["anio", "mes", "clave_siinah", "recinto"]).any()
    assert df["mes"].between(1, 12).all()
    assert (df[["visitantes_nacionales", "visitantes_extranjeros", "visitantes_total"]] >= 0).all().all()
    # Blank future months from the 2026 source must not become zero observations.
    assert df.loc[df["anio"].eq(2026), "mes"].max() == 8


def test_inah_total_is_sum_of_national_and_foreign():
    df = pd.read_csv(FACT)
    assert (df["visitantes_total"] == df["visitantes_nacionales"] + df["visitantes_extranjeros"]).all()


def test_selected_2025_destination_site_totals_match_source():
    df = pd.read_csv(FACT)
    y = df[df["anio"].eq(2025)]

    cempoala = y[y["recinto"].eq("Zona Arqueológica de Cempoala con museo de sitio")]
    assert cempoala["visitantes_total"].sum() == 31120

    papantla_sites = {
        "Zona Arqueológica de Cuyuxquihui",
        "Zona Arqueológica de El Tajín",
    }
    papantla = y[y["recinto"].isin(papantla_sites)]
    total = papantla["visitantes_total"].sum()
    foreign = papantla["visitantes_extranjeros"].sum()
    assert total == 308598
    assert foreign / total == pytest.approx(0.009335770160532473, abs=1e-14)
