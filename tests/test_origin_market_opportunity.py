from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "processed" / "origin_market_opportunity.csv"
SOURCE = ROOT / "data" / "reference" / "origin_market_2025_validated.csv"


def test_origin_market_table_is_25_ranked_source_backed_markets():
    df = pd.read_csv(PATH)
    assert len(df) == 25
    assert df["rank_2025"].tolist() == list(range(1, 26))
    assert df["country_of_residence"].is_unique
    assert df["source_url"].nunique() == 1
    assert df["source_url"].iloc[0].endswith("/RES_2025_12.pdf")


def test_origin_market_uses_validated_2025_source_values():
    df = pd.read_csv(PATH).set_index("country_of_residence")
    assert int(df.loc["Estados Unidos", "air_entries_2025"]) == 14_258_403
    assert int(df.loc["Canadá", "air_entries_2025"]) == 2_843_977
    assert int(df.loc["Reino Unido", "air_entries_2025"]) == 457_712
    assert float(df.loc["Colombia", "growth_2025_vs_2024_pct"]) == -16.7


def test_origin_market_control_total_matches_official_report():
    df = pd.read_csv(PATH)
    top25 = int(pd.to_numeric(df["air_entries_2025"]).sum())
    assert top25 == 20_667_837
    assert top25 + 654_520 == 21_322_357


def test_origin_market_growth_is_derived_from_counts_with_rounding_tolerance():
    df = pd.read_csv(PATH)
    calc = 100.0 * (df["air_entries_2025"] / df["air_entries_2024"] - 1.0)
    assert np.allclose(calc, df["growth_2025_vs_2024_pct"], atol=0.11)


def test_s3_origin_table_does_not_contain_marketing_decisions():
    df = pd.read_csv(PATH)
    forbidden = {"market_tier_v1", "trend_flag", "targeting_phase", "persona", "campaign"}
    assert forbidden.isdisjoint(df.columns)
    source = pd.read_csv(SOURCE)
    assert "not Veracruz-specific demand" in " ".join(source["scope_note"].astype(str).unique())
