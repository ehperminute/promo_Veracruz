from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score, silhouette_samples, silhouette_score

from common import (
    OUTDIR,
    PROFILE_ASYMMETRIC_BINARY,
    PROFILE_NUMERIC_FEATURES,
    PROFILE_SYMMETRIC_BINARY,
    STRUCTURAL_NUMERIC_FEATURES,
    THEME_FEATURES,
    gower_distance_matrix,
    load_profile_table,
    pam,
)

CLUSTER_DIR = OUTDIR / "clustering"
DIAGNOSTICS = CLUSTER_DIR / "cluster_diagnostics.csv"
MEMBERSHIP = CLUSTER_DIR / "cluster_membership.csv"
PROFILES = CLUSTER_DIR / "cluster_profiles.csv"
MEDOID_SIMILARITY = CLUSTER_DIR / "cluster_medoid_similarity.csv"
DESTINATION_SILHOUETTES = CLUSTER_DIR / "destination_silhouettes.csv"
FEATURE_SENSITIVITY = CLUSTER_DIR / "feature_sensitivity.csv"
MIN_K = 2
MAX_K = 20


def _profile_distance(df: pd.DataFrame) -> np.ndarray:
    return gower_distance_matrix(
        df,
        PROFILE_NUMERIC_FEATURES,
        PROFILE_SYMMETRIC_BINARY,
        PROFILE_ASYMMETRIC_BINARY,
    )


def _select_k(diag: pd.DataFrame) -> int:
    # Singleton-free solutions only. Among those, maximize silhouette.
    eligible = diag[diag["singleton_clusters"].eq(0)]
    if eligible.empty:
        raise AssertionError("No singleton-free cluster solution available")
    return int(
        eligible.sort_values(["silhouette", "k"], ascending=[False, True]).iloc[0]["k"]
    )


def main() -> None:
    CLUSTER_DIR.mkdir(parents=True, exist_ok=True)
    df = load_profile_table().reset_index(drop=True)
    distance = _profile_distance(df)

    diagnostics = []
    solutions: dict[int, tuple[np.ndarray, np.ndarray, float]] = {}
    for k in range(MIN_K, min(MAX_K, len(df) - 1) + 1):
        medoids, labels, cost = pam(distance, k)
        counts = pd.Series(labels).value_counts()
        diagnostics.append(
            {
                "k": k,
                "silhouette": silhouette_score(distance, labels, metric="precomputed"),
                "pam_total_dissimilarity": cost,
                "smallest_cluster": int(counts.min()),
                "largest_cluster": int(counts.max()),
                "median_cluster_size": float(counts.median()),
                "singleton_clusters": int((counts == 1).sum()),
            }
        )
        solutions[k] = (medoids, labels, cost)

    diag = pd.DataFrame(diagnostics)
    recommended_k = _select_k(diag)
    diag["recommended"] = diag["k"].eq(recommended_k)
    diag["selection_rule"] = (
        "maximize silhouette among singleton-free PAM solutions; interpretability reviewed separately"
    )
    diag.to_csv(DIAGNOSTICS, index=False)

    medoids, labels, _ = solutions[recommended_k]
    medoid_for_cluster = {cluster: int(medoid) for cluster, medoid in enumerate(medoids)}
    membership = df[["destination", "region_turistica_preliminar", "model_role_v1"]].copy()
    membership["recommended_k"] = recommended_k
    membership["cluster"] = labels + 1
    membership["cluster_medoid"] = [
        df.at[medoid_for_cluster[int(label)], "destination"] for label in labels
    ]
    membership["distance_to_medoid"] = [
        distance[idx, medoid_for_cluster[int(label)]] for idx, label in enumerate(labels)
    ]
    membership = membership.sort_values(["cluster", "destination"], kind="mergesort")
    membership.to_csv(MEMBERSHIP, index=False)

    sample_sil = silhouette_samples(distance, labels, metric="precomputed")
    silhouette_df = membership[["destination", "cluster", "cluster_medoid"]].copy()
    # membership was sorted; realign by destination rather than position.
    sil_map = dict(zip(df["destination"], sample_sil))
    silhouette_df["silhouette"] = silhouette_df["destination"].map(sil_map)
    silhouette_df["borderline"] = silhouette_df["silhouette"].lt(0.10)
    silhouette_df.to_csv(DESTINATION_SILHOUETTES, index=False)

    profile_rows = []
    descriptive_numeric = [
        col for col in STRUCTURAL_NUMERIC_FEATURES if col in df.columns
    ]
    for cluster_id in range(recommended_k):
        group = df.loc[labels == cluster_id].copy()
        medoid_name = df.at[medoid_for_cluster[cluster_id], "destination"]
        regions = group["region_turistica_preliminar"].value_counts()
        row = {
            "cluster": cluster_id + 1,
            "medoid": medoid_name,
            "n_destinations": int(len(group)),
            "dominant_region": regions.index[0],
            "dominant_region_share": float(regions.iloc[0] / len(group)),
            "members": " | ".join(sorted(group["destination"])),
        }
        for col in descriptive_numeric:
            row[f"{col}_median"] = pd.to_numeric(group[col], errors="coerce").median()
        for col in ["pueblo_magico", *THEME_FEATURES]:
            row[f"{col}_share"] = pd.to_numeric(group[col], errors="coerce").mean()
        profile_rows.append(row)
    pd.DataFrame(profile_rows).to_csv(PROFILES, index=False)

    medoid_rows = []
    for left in range(recommended_k):
        for right in range(left + 1, recommended_k):
            left_idx = medoid_for_cluster[left]
            right_idx = medoid_for_cluster[right]
            d = float(distance[left_idx, right_idx])
            medoid_rows.append(
                {
                    "cluster_a": left + 1,
                    "medoid_a": df.at[left_idx, "destination"],
                    "cluster_b": right + 1,
                    "medoid_b": df.at[right_idx, "destination"],
                    "gower_distance": d,
                    "gower_similarity": 1.0 - d,
                }
            )
    pd.DataFrame(medoid_rows).sort_values(
        ["gower_similarity", "cluster_a", "cluster_b"],
        ascending=[False, True, True],
        kind="mergesort",
    ).to_csv(MEDOID_SIMILARITY, index=False)

    # Sensitivity: remove one clustering feature at a time and compare the
    # recommended-k partition with Adjusted Rand Index (ARI).
    sensitivity_rows = []
    feature_names = [
        *PROFILE_NUMERIC_FEATURES,
        *PROFILE_SYMMETRIC_BINARY,
        *PROFILE_ASYMMETRIC_BINARY,
    ]
    for removed in feature_names:
        numeric = [c for c in PROFILE_NUMERIC_FEATURES if c != removed]
        symmetric = [c for c in PROFILE_SYMMETRIC_BINARY if c != removed]
        asymmetric = [c for c in PROFILE_ASYMMETRIC_BINARY if c != removed]
        reduced_distance = gower_distance_matrix(df, numeric, symmetric, asymmetric)
        _, reduced_labels, _ = pam(reduced_distance, recommended_k)
        counts = pd.Series(reduced_labels).value_counts()
        sensitivity_rows.append(
            {
                "removed_feature": removed,
                "adjusted_rand_vs_full": adjusted_rand_score(labels, reduced_labels),
                "silhouette_without_feature": silhouette_score(
                    reduced_distance, reduced_labels, metric="precomputed"
                ),
                "singleton_clusters_without_feature": int((counts == 1).sum()),
            }
        )
    pd.DataFrame(sensitivity_rows).sort_values(
        ["adjusted_rand_vs_full", "removed_feature"], kind="mergesort"
    ).to_csv(FEATURE_SENSITIVITY, index=False)

    print(
        f"PAM/Gower profile clustering tested k={MIN_K}..{MAX_K}; "
        f"recommended k={recommended_k} (best silhouette among singleton-free solutions)"
    )
    print(f"Wrote clustering outputs -> {CLUSTER_DIR.relative_to(Path(__file__).resolve().parents[2])}")


if __name__ == "__main__":
    main()
