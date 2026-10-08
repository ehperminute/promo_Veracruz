from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SIM = ROOT / "outputs" / "mining" / "similarity" / "undermeasured_anchor_similarity.csv"
MASTER = ROOT / "data" / "processed" / "destination_master.csv"


def test_each_undermeasured_target_has_three_gower_analogs():
    master = pd.read_csv(MASTER)
    observed = set(master.loc[master["model_role_v1"].eq("Observed anchor / training evidence"), "destination"])
    targets = set(master.loc[master["model_role_v1"].eq("Undermeasured analog target"), "destination"])
    sim = pd.read_csv(SIM)
    assert len(sim) == 42 * 3
    assert set(sim["target_destination"]) == targets
    assert set(sim["anchor_destination"]).issubset(observed)
    assert (sim.groupby("target_destination").size() == 3).all()
    assert sim["gower_structural_distance"].between(0, 1).all()
    assert sim["gower_structural_similarity"].between(0, 1).all()
    assert sim["interpretation"].str.contains("not demand evidence", regex=False).all()
