from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "processed" / "destination_master_v1.csv"
OUTDIR = ROOT / "outputs" / "clustering"

NUMERIC = [
    "productos_en_extracto_local_n",
    "lodging_establishments",
    "food_beverage_establishments",
    "recreation_tourism_proxy",
    "agencies_tours_events",
    "tourist_transport_proxy",
    "tourism_gdp_2022_mxn2018",
    "tourism_share_proxy_2022",
    "inah_inventory_sites_n",
]
BINARY = [
    "pueblo_magico",
    "theme_beach_coast",
    "theme_nature",
    "theme_culture_history",
    "theme_archaeology",
    "theme_adventure",
    "theme_gastronomy_coffee",
    "theme_wellness_spiritual",
    "theme_urban_services",
]

def feature_matrix(df: pd.DataFrame) -> np.ndarray:
    num = df[NUMERIC].apply(pd.to_numeric, errors="coerce")
    num = num.fillna(num.median(numeric_only=True)).fillna(0)

    # Counts/GDP are strongly skewed. Log them before scaling.
    log_cols = [c for c in NUMERIC if c != "tourism_share_proxy_2022"]
    num.loc[:, log_cols] = np.log1p(num[log_cols].clip(lower=0))
    x_num = StandardScaler().fit_transform(num)

    x_bin = (
        df[BINARY]
        .apply(pd.to_numeric, errors="coerce")
        .fillna(0)
        .to_numpy(dtype=float)
    )

    x_region = pd.get_dummies(
        df["region_turistica_preliminar"].fillna("Unknown"),
        prefix="region",
        dtype=float,
    ).to_numpy()

    return np.hstack([x_num, x_bin, x_region])

def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(INPUT)
    X = feature_matrix(df)

    diagnostics = []
    models = {}
    max_k = min(18, len(df) - 1)

    for k in range(2, max_k + 1):
        model = KMeans(n_clusters=k, random_state=42, n_init=50)
        labels = model.fit_predict(X)
        counts = pd.Series(labels).value_counts()
        diagnostics.append({
            "k": k,
            "silhouette": silhouette_score(X, labels),
            "calinski_harabasz": calinski_harabasz_score(X, labels),
            "davies_bouldin": davies_bouldin_score(X, labels),
            "smallest_cluster": int(counts.min()),
            "singleton_clusters": int((counts == 1).sum()),
        })
        models[k] = labels

    pd.DataFrame(diagnostics).to_csv(OUTDIR / "cluster_diagnostics.csv", index=False)

    membership = df[["destination", "region_turistica_preliminar", "model_role_v1"]].copy()
    for k in (15, 17):
        if k <= max_k:
            membership[f"cluster_k{k}"] = models[k]
    membership.to_csv(OUTDIR / "cluster_membership.csv", index=False)

    print(f"Wrote diagnostics and membership -> {OUTDIR.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
