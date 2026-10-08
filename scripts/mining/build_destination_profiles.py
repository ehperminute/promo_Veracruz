from pathlib import Path
from collections import Counter

import pandas as pd

from common import (
    OUTDIR,
    PARSED_PRODUCTS,
    PROFILE_ENRICHMENT,
    PROFILE_TABLE,
    THEME_FEATURES,
    load_destination_master,
)

GAP_OUTPUT = OUTDIR / "audit" / "destination_profile_gaps.csv"


def _product_counts() -> Counter[str]:
    products = pd.read_csv(PARSED_PRODUCTS)
    if len(products) != 295:
        raise AssertionError("Expected 295 parsed official tourism-product cards")
    counts: Counter[str] = Counter()
    for value in products["municipios"].fillna(""):
        for municipality in str(value).split("|"):
            municipality = municipality.strip()
            if municipality:
                counts[municipality] += 1
    return counts


def build_profiles() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = load_destination_master().copy()
    counts = _product_counts()
    df["official_product_card_count_295"] = (
        df["municipio"].map(counts).fillna(0).astype(int)
    )

    enrichment = pd.read_csv(PROFILE_ENRICHMENT, dtype=str).fillna("")
    for row in enrichment.itertuples(index=False):
        mask = df["destination"].eq(row.destination)
        if mask.sum() != 1:
            raise AssertionError(f"Unknown/non-unique enrichment destination: {row.destination}")
        if row.field not in df.columns:
            raise AssertionError(f"Unknown enrichment field: {row.field}")
        if row.field in THEME_FEATURES:
            df.loc[mask, row.field] = int(row.new_value)
        else:
            df.loc[mask, row.field] = row.new_value

    for col in THEME_FEATURES:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    df["pueblo_magico"] = pd.to_numeric(df["pueblo_magico"], errors="coerce").fillna(0).astype(int)
    df["theme_evidence_count"] = df[THEME_FEATURES].sum(axis=1).astype(int)

    # Gap audit is descriptive, not a score used by clustering.
    gaps = df[
        [
            "destination",
            "municipio",
            "region_turistica_preliminar",
            "official_product_card_count_295",
            "theme_evidence_count",
            "tourism_gdp_2022_mxn2018",
            "inah_inventory_sites_n",
            "model_role_v1",
        ]
    ].copy()
    gaps["no_product_cards"] = gaps["official_product_card_count_295"].eq(0)
    gaps["region_unresolved"] = gaps["region_turistica_preliminar"].eq("Por verificar")
    gaps["theme_count_lt3"] = gaps["theme_evidence_count"].lt(3)
    gaps["missing_tourism_gdp"] = pd.to_numeric(
        gaps["tourism_gdp_2022_mxn2018"], errors="coerce"
    ).isna()
    gaps["no_inah_inventory"] = pd.to_numeric(
        gaps["inah_inventory_sites_n"], errors="coerce"
    ).fillna(0).eq(0)
    gaps["no_direct_demand_series"] = gaps["model_role_v1"].ne(
        "Observed anchor / training evidence"
    )

    high = gaps["region_unresolved"] | gaps["theme_evidence_count"].lt(2)
    medium = (
        (gaps["no_product_cards"] & gaps["theme_count_lt3"])
        | gaps["missing_tourism_gdp"]
    )
    gaps["profile_review_priority"] = "low"
    gaps.loc[medium, "profile_review_priority"] = "medium"
    gaps.loc[high, "profile_review_priority"] = "high"
    gaps["interpretation"] = (
        "profile-data audit only; missing product cards or demand coverage do not imply low tourism"
    )

    return df, gaps


def main() -> None:
    PROFILE_TABLE.parent.mkdir(parents=True, exist_ok=True)
    GAP_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    profiles, gaps = build_profiles()
    profiles.sort_values("destination", kind="mergesort").to_csv(PROFILE_TABLE, index=False)
    gaps.sort_values(
        ["profile_review_priority", "destination"],
        ascending=[True, True],
        kind="mergesort",
    ).to_csv(GAP_OUTPUT, index=False)
    print(f"Wrote {len(profiles)} S4 destination profiles -> {PROFILE_TABLE.relative_to(Path(__file__).resolve().parents[2])}")
    print(f"Wrote profile-gap audit -> {GAP_OUTPUT.relative_to(Path(__file__).resolve().parents[2])}")


if __name__ == "__main__":
    main()
