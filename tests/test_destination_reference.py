from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "data" / "reference" / "destination_reference.csv"
PRODUCTS = ROOT / "data" / "reference" / "tourism_products.csv"

BANNED_MEASURED_COLUMNS = {
    "inah_visitors_2025",
    "inah_foreign_share_2025",
    "datatur_arrivals_2024",
    "datatur_occupancy_2024_pct",
    "lodging_establishments",
    "food_beverage_establishments",
    "recreation_tourism_proxy",
    "agencies_tours_events",
    "tourist_transport_proxy",
    "tourism_gdp_2022_mxn2018",
    "tourism_share_proxy_2022",
    "cluster_k15",
    "cluster_k17",
}

THEMES = [
    "theme_beach_coast",
    "theme_nature",
    "theme_culture_history",
    "theme_archaeology",
    "theme_adventure",
    "theme_gastronomy_coffee",
    "theme_wellness_spiritual",
    "theme_urban_services",
]


def test_reference_has_55_unique_destinations_and_no_measured_outputs():
    df = pd.read_csv(REFERENCE)
    assert len(df) == 55
    assert df["destination"].is_unique
    assert df["clave_municipio"].astype(str).str.zfill(5).str.match(r"^30\d{3}$").all()
    assert df["clave_municipio"].astype(str).is_unique
    assert not (BANNED_MEASURED_COLUMNS & set(df.columns))


def test_reference_binary_fields_and_sources_are_well_formed():
    df = pd.read_csv(REFERENCE)
    for col in ["pueblo_magico", "oferta_turistica_oficial_web", *THEMES]:
        assert set(df[col].dropna().astype(int).unique()).issubset({0, 1})
    assert df["source_tourism_offer_snapshot"].eq(
        "data/raw/veracruz_productos_2026-10-06.html"
    ).all()
    assert df["source_region_snapshot"].eq(
        "data/raw/veracruz_regiones_2026-10-06.html"
    ).all()
    pueblos = df[df["pueblo_magico"].eq(1)]
    assert pueblos["source_pueblo_magico_snapshot"].eq(
        "data/raw/veracruz_pueblos_magicos_2026-10-06.html"
    ).all()


def test_datatur_mapping_is_deliberately_small_and_exact():
    df = pd.read_csv(REFERENCE)
    mapped = df[df["datatur_center"].notna()][["destination", "datatur_center"]]
    assert set(mapped["destination"]) == {"Boca del Río", "Coatzacoalcos", "Veracruz", "Xalapa"}
    assert set(mapped["datatur_center"]) == {
        "Coatzacoalcos",
        "Veracruz-Boca del Río",
        "Xalapa",
    }


def test_inah_series_mappings_are_exact_recinto_strings_not_fuzzy_labels():
    df = pd.read_csv(REFERENCE)
    mapped = df[df["inah_series_sites"].notna()]
    assert len(mapped) == 9
    assert mapped["inah_series_sites"].str.contains("Zona Arqueológica").all()


def test_tourism_product_reference_has_expected_grain_and_counts():
    df = pd.read_csv(PRODUCTS)
    assert len(df) == 75
    assert df["producto"].is_unique
    actual = df["municipios"].map(
        lambda x: len({p.strip() for p in str(x).split("|") if p.strip()})
    )
    assert actual.equals(df["n_municipios"].astype(int))
    assert df["source_snapshot"].eq("data/raw/veracruz_productos_2026-10-06.html").all()
