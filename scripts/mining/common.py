from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DESTINATION_MASTER = ROOT / "data" / "processed" / "destination_master.csv"
PARSED_PRODUCTS = ROOT / "data" / "interim" / "veracruz_products_parsed.csv"
PROFILE_ENRICHMENT = ROOT / "data" / "reference" / "destination_profile_enrichment.csv"
PROFILE_SOURCES = ROOT / "data" / "reference" / "destination_profile_sources.csv"
PROFILE_TABLE = ROOT / "data" / "interim" / "destination_profiles_s4.csv"
OUTDIR = ROOT / "outputs" / "mining"

THEME_FEATURES = [
    "theme_beach_coast",
    "theme_nature",
    "theme_culture_history",
    "theme_archaeology",
    "theme_adventure",
    "theme_gastronomy_coffee",
    "theme_wellness_spiritual",
    "theme_urban_services",
]

# Main destination-character clustering deliberately excludes direct demand and
# broad infrastructure scale. It asks "what kind of tourism profile is this?"
PROFILE_NUMERIC_FEATURES = []
PROFILE_SYMMETRIC_BINARY = ["pueblo_magico"]
PROFILE_ASYMMETRIC_BINARY = THEME_FEATURES

# Broader structural similarity is a separate question. Missing numerical
# values are handled pairwise by Gower distance rather than median imputation.
STRUCTURAL_NUMERIC_FEATURES = [
    "official_product_card_count_295",
    "lodging_establishments",
    "food_beverage_establishments",
    "recreation_tourism_proxy",
    "agencies_tours_events",
    "tourist_transport_proxy",
    "tourism_gdp_2022_mxn2018",
    "tourism_share_proxy_2022",
    "inah_inventory_sites_n",
]
STRUCTURAL_SYMMETRIC_BINARY = ["pueblo_magico"]
STRUCTURAL_ASYMMETRIC_BINARY = THEME_FEATURES

FORBIDDEN_DEMAND_FEATURES = {
    "inah_visitors_2025",
    "inah_foreign_share_2025",
    "datatur_arrivals_2024",
    "datatur_occupancy_2024_pct",
}


def load_destination_master() -> pd.DataFrame:
    df = pd.read_csv(DESTINATION_MASTER)
    if len(df) != 55 or not df["destination"].is_unique:
        raise AssertionError("destination_master must contain 55 unique destinations")
    return df


def load_profile_table() -> pd.DataFrame:
    df = pd.read_csv(PROFILE_TABLE)
    if len(df) != 55 or not df["destination"].is_unique:
        raise AssertionError("destination_profiles_s4 must contain 55 unique destinations")
    return df


def _log_transform_numeric(df: pd.DataFrame, numeric_features: list[str]) -> pd.DataFrame:
    out = df[numeric_features].apply(pd.to_numeric, errors="coerce").astype(float)
    for col in numeric_features:
        if col != "tourism_share_proxy_2022":
            out[col] = np.log1p(out[col].clip(lower=0))
    return out


def gower_distance_matrix(
    df: pd.DataFrame,
    numeric_features: list[str],
    symmetric_binary: list[str],
    asymmetric_binary: list[str],
) -> np.ndarray:
    """Gower-style mixed distance with pairwise missing-value handling.

    Numeric variables are log-transformed where appropriate and range scaled.
    Symmetric binaries count both matches and mismatches. Tourism-theme flags are
    asymmetric: a shared zero is ignored, because "not evidenced" should not make
    two destinations artificially similar.
    """
    used = set(numeric_features) | set(symmetric_binary) | set(asymmetric_binary)
    overlap = FORBIDDEN_DEMAND_FEATURES & used
    if overlap:
        raise AssertionError(f"Direct demand leaked into S4 features: {sorted(overlap)}")

    n = len(df)
    numeric = _log_transform_numeric(df, numeric_features)
    num_values = numeric.to_numpy(dtype=float)
    ranges: list[float | None] = []
    for col in numeric_features:
        values = numeric[col].dropna()
        span = float(values.max() - values.min()) if len(values) else np.nan
        ranges.append(span if np.isfinite(span) and span > 0 else None)

    symmetric = (
        df[symmetric_binary].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
        if symmetric_binary
        else np.empty((n, 0), dtype=float)
    )
    asymmetric = (
        df[asymmetric_binary].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
        if asymmetric_binary
        else np.empty((n, 0), dtype=float)
    )

    distances = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(i + 1, n):
            distance_sum = 0.0
            weight_sum = 0.0

            for idx, span in enumerate(ranges):
                a, b = num_values[i, idx], num_values[j, idx]
                if span is None or np.isnan(a) or np.isnan(b):
                    continue
                distance_sum += abs(a - b) / span
                weight_sum += 1.0

            for idx in range(symmetric.shape[1]):
                a, b = symmetric[i, idx], symmetric[j, idx]
                if np.isnan(a) or np.isnan(b):
                    continue
                distance_sum += 0.0 if a == b else 1.0
                weight_sum += 1.0

            for idx in range(asymmetric.shape[1]):
                a, b = asymmetric[i, idx], asymmetric[j, idx]
                if np.isnan(a) or np.isnan(b):
                    continue
                if a == 0 and b == 0:
                    continue
                distance_sum += 0.0 if a == b else 1.0
                weight_sum += 1.0

            if weight_sum == 0:
                raise AssertionError(
                    f"No comparable S4 profile features for rows {i} and {j}"
                )
            distances[i, j] = distances[j, i] = distance_sum / weight_sum

    if not np.isfinite(distances).all():
        raise AssertionError("Non-finite values in Gower distance matrix")
    return distances


def pam(distance_matrix: np.ndarray, k: int, max_iter: int = 100) -> tuple[np.ndarray, np.ndarray, float]:
    """Deterministic Partitioning Around Medoids (BUILD + SWAP)."""
    n = distance_matrix.shape[0]
    if k < 2 or k >= n:
        raise ValueError("k must be between 2 and n-1")

    medoids = [int(np.argmin(distance_matrix.sum(axis=1)))]
    nearest = distance_matrix[:, medoids[0]].copy()
    while len(medoids) < k:
        best_candidate = None
        best_cost = np.inf
        for candidate in range(n):
            if candidate in medoids:
                continue
            cost = np.minimum(nearest, distance_matrix[:, candidate]).sum()
            if cost < best_cost - 1e-12 or (
                abs(cost - best_cost) <= 1e-12
                and (best_candidate is None or candidate < best_candidate)
            ):
                best_cost = cost
                best_candidate = candidate
        if best_candidate is None:
            raise AssertionError("PAM BUILD failed to choose a medoid")
        medoids.append(best_candidate)
        nearest = np.minimum(nearest, distance_matrix[:, best_candidate])

    def assign(meds: list[int]) -> tuple[np.ndarray, float]:
        meds = sorted(meds)
        local = np.argmin(distance_matrix[:, meds], axis=1)
        labels = local.astype(int)
        for cluster_id, medoid in enumerate(meds):
            labels[medoid] = cluster_id
        cost = sum(distance_matrix[row, meds[labels[row]]] for row in range(n))
        return labels, float(cost)

    medoids = sorted(medoids)
    labels, cost = assign(medoids)
    for _ in range(max_iter):
        best_cost = cost
        best_medoids = None
        best_labels = None
        non_medoids = [idx for idx in range(n) if idx not in medoids]
        for old in medoids:
            for new in non_medoids:
                proposal = sorted([new if value == old else value for value in medoids])
                proposal_labels, proposal_cost = assign(proposal)
                if proposal_cost < best_cost - 1e-10:
                    best_cost = proposal_cost
                    best_medoids = proposal
                    best_labels = proposal_labels
        if best_medoids is None:
            break
        medoids, labels, cost = best_medoids, best_labels, best_cost

    return np.array(medoids, dtype=int), labels, float(cost)
