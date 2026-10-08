from pathlib import Path

import numpy as np
import pandas as pd

from common import (
    OUTDIR,
    STRUCTURAL_ASYMMETRIC_BINARY,
    STRUCTURAL_NUMERIC_FEATURES,
    STRUCTURAL_SYMMETRIC_BINARY,
    gower_distance_matrix,
    load_profile_table,
)

OUTPUT = OUTDIR / "similarity" / "undermeasured_anchor_similarity.csv"
TOP_N = 3
TARGET_ROLE = "Undermeasured analog target"
ANCHOR_ROLE = "Observed anchor / training evidence"


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df = load_profile_table().reset_index(drop=True)
    distance = gower_distance_matrix(
        df,
        STRUCTURAL_NUMERIC_FEATURES,
        STRUCTURAL_SYMMETRIC_BINARY,
        STRUCTURAL_ASYMMETRIC_BINARY,
    )

    target_idx = np.flatnonzero(df["model_role_v1"].eq(TARGET_ROLE).to_numpy())
    anchor_idx = np.flatnonzero(df["model_role_v1"].eq(ANCHOR_ROLE).to_numpy())
    if len(target_idx) == 0 or len(anchor_idx) == 0:
        raise AssertionError("Both undermeasured targets and observed anchors are required")

    rows = []
    for target_pos in target_idx:
        candidate_distances = [(int(anchor_pos), float(distance[target_pos, anchor_pos])) for anchor_pos in anchor_idx]
        candidate_distances.sort(key=lambda item: (item[1], df.at[item[0], "destination"]))
        for rank, (anchor_pos, d) in enumerate(candidate_distances[:TOP_N], start=1):
            rows.append(
                {
                    "target_destination": df.at[target_pos, "destination"],
                    "target_region": df.at[target_pos, "region_turistica_preliminar"],
                    "anchor_destination": df.at[anchor_pos, "destination"],
                    "anchor_region": df.at[anchor_pos, "region_turistica_preliminar"],
                    "similarity_rank": rank,
                    "gower_structural_distance": d,
                    "gower_structural_similarity": 1.0 - d,
                    "interpretation": "mixed-profile structural analog only; not demand evidence or route feasibility",
                }
            )

    out = pd.DataFrame(rows).sort_values(
        ["target_destination", "similarity_rank", "anchor_destination"],
        kind="mergesort",
    )
    out.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(out)} target-anchor comparisons -> {OUTPUT.relative_to(Path(__file__).resolve().parents[2])}")


if __name__ == "__main__":
    main()
