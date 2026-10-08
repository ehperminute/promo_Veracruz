from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DIAG = ROOT / "outputs" / "mining" / "clustering" / "cluster_diagnostics.csv"
MEMBERSHIP = ROOT / "outputs" / "mining" / "clustering" / "cluster_membership.csv"
MEDOIDS = ROOT / "outputs" / "mining" / "clustering" / "cluster_medoid_similarity.csv"
SIL = ROOT / "outputs" / "mining" / "clustering" / "destination_silhouettes.csv"
SENS = ROOT / "outputs" / "mining" / "clustering" / "feature_sensitivity.csv"


def test_pam_gower_diagnostics_cover_requested_k2_through_k20():
    df = pd.read_csv(DIAG)
    assert df["k"].tolist() == list(range(2, 21))
    assert df["silhouette"].between(-1, 1).all()
    assert (df["smallest_cluster"] >= 1).all()
    assert df["recommended"].sum() == 1
    recommended = df.loc[df["recommended"]].iloc[0]
    assert int(recommended["singleton_clusters"]) == 0
    eligible = df[df["singleton_clusters"].eq(0)]
    assert recommended["silhouette"] == eligible["silhouette"].max()


def test_current_recommended_solution_has_no_singletons_and_all_55_destinations():
    diag = pd.read_csv(DIAG)
    membership = pd.read_csv(MEMBERSHIP)
    k = int(diag.loc[diag["recommended"], "k"].iloc[0])
    assert len(membership) == 55
    assert membership["destination"].is_unique
    assert membership["cluster"].nunique() == k
    assert membership.groupby("cluster").size().min() >= 2


def test_cluster_similarity_and_borderline_assignments_are_exposed():
    medoids = pd.read_csv(MEDOIDS)
    membership = pd.read_csv(MEMBERSHIP)
    sil = pd.read_csv(SIL)
    k = membership["recommended_k"].iloc[0]
    assert len(medoids) == k * (k - 1) // 2
    assert medoids["gower_similarity"].between(0, 1).all()
    assert len(sil) == 55
    assert sil["silhouette"].between(-1, 1).all()
    assert "borderline" in sil.columns


def test_feature_sensitivity_covers_every_profile_clustering_factor():
    sens = pd.read_csv(SENS)
    expected = {
        "pueblo_magico",
        "theme_beach_coast",
        "theme_nature",
        "theme_culture_history",
        "theme_archaeology",
        "theme_adventure",
        "theme_gastronomy_coffee",
        "theme_wellness_spiritual",
        "theme_urban_services",
    }
    assert set(sens["removed_feature"]) == expected
    assert sens["adjusted_rand_vs_full"].between(-1, 1).all()
