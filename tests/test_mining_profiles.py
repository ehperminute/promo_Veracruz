from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "data" / "interim" / "destination_profiles_s4.csv"
GAPS = ROOT / "outputs" / "mining" / "audit" / "destination_profile_gaps.csv"
PRODUCTS = ROOT / "data" / "interim" / "veracruz_products_parsed.csv"


def test_profiles_use_full_295_card_catalogue_and_keep_55_destinations():
    profiles = pd.read_csv(PROFILES)
    products = pd.read_csv(PRODUCTS)
    assert len(products) == 295
    assert len(profiles) == 55
    assert profiles["destination"].is_unique
    assert "official_product_card_count_295" in profiles.columns
    assert int(profiles.loc[profiles["destination"].eq("Soteapan"), "official_product_card_count_295"].iloc[0]) == 7
    assert int(profiles.loc[profiles["destination"].eq("Tlalnelhuayocan"), "official_product_card_count_295"].iloc[0]) == 4


def test_carrillo_profile_gap_is_repaired_with_reviewed_provenance():
    profiles = pd.read_csv(PROFILES)
    row = profiles.loc[profiles["destination"].eq("Carrillo Puerto")].iloc[0]
    assert row["region_turistica_preliminar"] == "Altas Montañas"
    assert int(row["theme_archaeology"]) == 1
    assert int(row["theme_culture_history"]) == 1
    assert int(row["theme_gastronomy_coffee"]) == 1
    assert int(row["theme_evidence_count"]) >= 3

    antigua = profiles.loc[profiles["destination"].eq("La Antigua")].iloc[0]
    assert int(antigua["theme_beach_coast"]) == 1
    assert int(antigua["theme_nature"]) == 1
    poza = profiles.loc[profiles["destination"].eq("Poza Rica de Hidalgo")].iloc[0]
    assert int(poza["theme_nature"]) == 0
    xalapa = profiles.loc[profiles["destination"].eq("Xalapa")].iloc[0]
    assert int(xalapa["theme_nature"]) == 1


def test_gap_audit_does_not_equate_missing_product_cards_with_low_tourism():
    gaps = pd.read_csv(GAPS)
    assert len(gaps) == 55
    assert not gaps["region_unresolved"].any()
    assert gaps["interpretation"].str.contains("do not imply low tourism", regex=False).all()
    assert set(gaps["profile_review_priority"]).issubset({"low", "medium", "high"})
