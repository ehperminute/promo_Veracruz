from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "outputs" / "mining" / "candidates" / "undermeasured_candidates.csv"
SIMILARITY = ROOT / "outputs" / "mining" / "similarity" / "undermeasured_anchor_similarity.csv"
MASTER = ROOT / "data" / "processed" / "destination_master.csv"


def test_candidate_set_is_current_undermeasured_set():
    master = pd.read_csv(MASTER)
    expected = set(master.loc[master["model_role_v1"].eq("Undermeasured analog target"), "destination"])
    out = pd.read_csv(CANDIDATES)
    assert len(out) == 42
    assert set(out["destination"]) == expected
    assert out["evidence_priority_rank"].tolist() == list(range(1, 43))
    assert "official_product_card_count_295" in out.columns
    assert out["ranking_scope"].str.contains("not observed demand", regex=False).all()


def test_each_undermeasured_target_has_three_observed_gower_analogs():
    master = pd.read_csv(MASTER)
    observed = set(master.loc[master["model_role_v1"].eq("Observed anchor / training evidence"), "destination"])
    sim = pd.read_csv(SIMILARITY)
    assert len(sim) == 42 * 3
    assert set(sim["similarity_rank"]) == {1, 2, 3}
    assert (sim.groupby("target_destination").size() == 3).all()
    assert set(sim["anchor_destination"]).issubset(observed)
    assert sim["gower_structural_distance"].between(0, 1).all()
    assert sim["gower_structural_similarity"].between(0, 1).all()
    assert sim["interpretation"].str.contains("not demand evidence", regex=False).all()
