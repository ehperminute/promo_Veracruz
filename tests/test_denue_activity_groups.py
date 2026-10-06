from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "data" / "reference" / "denue_activity_groups.csv"
SCRIPT = ROOT / "scripts" / "data" / "prepare_infrastructure.py"

EXPECTED_METRICS = {
    "alojamiento_n",
    "alimentos_bebidas_n",
    "sector_recreacion_total_n",
    "recreacion_turistica_proxy_n",
    "agencias_tours_eventos_n",
    "transporte_turistico_n",
}


def test_denue_proxy_rules_are_externalized_and_well_formed():
    df = pd.read_csv(RULES, dtype=str)
    assert set(df["metric"]) == EXPECTED_METRICS
    assert set(df["match_type"]).issubset({"exact", "prefix"})
    assert not df[["metric", "match_type", "code"]].duplicated().any()
    assert df["description"].notna().all()


def test_known_tourism_codes_are_explicit_reference_rows():
    df = pd.read_csv(RULES, dtype=str)
    tourist_transport = set(df.loc[df["metric"].eq("transporte_turistico_n"), "code"])
    assert tourist_transport == {"485510", "487110", "487210"}
    agencies = set(df.loc[df["metric"].eq("agencias_tours_eventos_n"), "code"])
    assert agencies == {"561510", "561520", "561590", "561920"}


def test_infrastructure_script_consumes_reference_instead_of_hidden_code_sets():
    text = SCRIPT.read_text(encoding="utf-8")
    assert "denue_activity_groups.csv" in text
    assert "RECREATION_TOURISM_PROXY_CODES" not in text
    assert "AGENCIES_TOURS_EVENTS_CODES" not in text
    assert "TOURIST_TRANSPORT_CODES" not in text
