from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "processed" / "destination_master_v1.csv"
OUTPUT = ROOT / "data" / "processed" / "undermeasured_candidates.csv"

KEEP = [
    "destination",
    "region_turistica_preliminar",
    "pueblo_magico",
    "tourism_tags",
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

def main():
    df = pd.read_csv(INPUT)
    mask = df["model_role_v1"].eq("Undermeasured analog target")
    out = df.loc[mask, KEEP].copy()

    service_cols = [
        "lodging_establishments",
        "food_beverage_establishments",
        "recreation_tourism_proxy",
        "agencies_tours_events",
        "tourist_transport_proxy",
    ]
    for c in service_cols:
        out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0)

    out["tourism_service_establishments"] = out[service_cols].sum(axis=1)
    out = out.sort_values(
        ["coverage_dimensions_n", "tourism_service_establishments", "destination"],
        ascending=[False, False, True],
    )
    out.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(out)} rows -> {OUTPUT.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
