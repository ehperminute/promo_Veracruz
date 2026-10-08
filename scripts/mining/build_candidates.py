from pathlib import Path

import pandas as pd

from common import OUTDIR, load_profile_table

OUTPUT = OUTDIR / "candidates" / "undermeasured_candidates.csv"

KEEP = [
    "destination",
    "region_turistica_preliminar",
    "pueblo_magico",
    "tourism_tags",
    "official_product_card_count_295",
    "lodging_establishments",
    "food_beverage_establishments",
    "recreation_tourism_proxy",
    "agencies_tours_events",
    "tourist_transport_proxy",
    "tourism_gdp_2022_mxn2018",
    "tourism_share_proxy_2022",
    "coverage_dimensions_n",
    "model_role_v1",
]

SERVICE_COLS = [
    "lodging_establishments",
    "food_beverage_establishments",
    "recreation_tourism_proxy",
    "agencies_tours_events",
    "tourist_transport_proxy",
]


def build_candidates(df: pd.DataFrame) -> pd.DataFrame:
    out = df.loc[df["model_role_v1"].eq("Undermeasured analog target"), KEEP].copy()
    for col in SERVICE_COLS:
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0)

    out["tourism_service_establishments"] = out[SERVICE_COLS].sum(axis=1)
    out = out.sort_values(
        ["coverage_dimensions_n", "tourism_service_establishments", "destination"],
        ascending=[False, False, True],
        kind="mergesort",
    ).reset_index(drop=True)
    out.insert(0, "evidence_priority_rank", range(1, len(out) + 1))
    out["ranking_scope"] = "structural evidence priority; not observed demand or route feasibility"
    return out


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    out = build_candidates(load_profile_table())
    out.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(out)} candidates -> {OUTPUT.relative_to(Path(__file__).resolve().parents[2])}")


if __name__ == "__main__":
    main()
