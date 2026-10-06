from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = ROOT / "data" / "interim" / "veracruz_products_parsed.csv"
REGIONS = ROOT / "data" / "interim" / "veracruz_regions_parsed.csv"
PUEBLOS = ROOT / "data" / "interim" / "veracruz_pueblos_magicos_parsed.csv"
SELECTED = ROOT / "data" / "interim" / "tourism_products.csv"
DEST_REF = ROOT / "data" / "reference" / "destination_reference.csv"
RAW_PUEBLOS = ROOT / "data" / "raw" / "veracruz_pueblos_magicos_2026-10-06.html"
RAW_PUEBLOS_MANUAL = ROOT / "data" / "raw" / "veracruz_pueblos_magicos_2026-10-06_manual.html"


def test_products_html_parser_extracts_real_product_cards():
    df = pd.read_csv(PRODUCTS)
    assert len(df) == 295
    assert df["source_card_index"].is_unique
    row = df[df["producto"].eq("Descubre Los Tuxtlas")].iloc[0]
    assert set(row["municipios"].split("|")) == {
        "Catemaco",
        "San Andrés Tuxtla",
        "Santiago Tuxtla",
    }
    assert int(row["n_municipios"]) == 3


def test_region_navigation_extracts_all_seven_regions_with_municipality_codes():
    df = pd.read_csv(REGIONS, dtype={"clave_municipio": str})
    assert set(df["region"]) == {
        "Huasteca",
        "Totonacapan",
        "Cultura y Aventura",
        "Primeros Pasos de Cortés",
        "Altas Montañas",
        "Los Tuxtlas",
        "Olmeca",
    }
    assert len(df) == 31
    papantla = df[df["municipio"].eq("Papantla")].iloc[0]
    assert papantla["region"] == "Totonacapan"
    assert str(papantla["clave_municipio"]).zfill(5) == "30124"


def test_pueblos_uses_manual_browser_snapshot_and_preserves_failed_automated_capture():
    automated = RAW_PUEBLOS.read_text(encoding="utf-8", errors="replace")
    manual = RAW_PUEBLOS_MANUAL.read_text(encoding="utf-8", errors="replace")
    assert "Radware Captcha Page" in automated
    assert "Pueblos Mágicos" in manual
    assert 'title="PAPANTLA"' in manual

    df = pd.read_csv(PUEBLOS)
    assert len(df) == 8
    assert set(df["extraction_note"]) == {"manual_browser_snapshot_iframe_titles"}
    assert df["source_snapshot"].eq("data/raw/veracruz_pueblos_magicos_2026-10-06_manual.html").all()
    assert set(df["pueblo_magico"]) == {
        "Coatepec",
        "Córdoba",
        "Coscomatepec",
        "Naolinco",
        "Orizaba",
        "Papantla",
        "Xico",
        "Zozocolco de Hidalgo",
    }


def test_destination_reference_pueblo_flags_match_parsed_source():
    pueblos = set(pd.read_csv(PUEBLOS)["pueblo_magico"])
    ref = pd.read_csv(DEST_REF)
    flagged = set(ref.loc[ref["pueblo_magico"].eq(1), "destination"])
    assert flagged == pueblos


def test_region_reference_agrees_where_official_navigation_exposes_destination():
    parsed = pd.read_csv(REGIONS, dtype={"clave_municipio": str})
    ref = pd.read_csv(DEST_REF, dtype={"clave_municipio": str})
    merged = ref.merge(
        parsed[["clave_municipio", "region"]],
        on="clave_municipio",
        how="inner",
        validate="one_to_one",
    )
    assert len(merged) >= 25
    assert merged["region_turistica_preliminar"].eq(merged["region"]).all()


def test_75_product_project_selection_is_grounded_in_frozen_html():
    df = pd.read_csv(SELECTED)
    assert len(df) == 75
    assert df["source_card_index"].notna().all()
    assert df["source_producto"].notna().all()
    assert df["source_match_score"].ge(0.65).all()
