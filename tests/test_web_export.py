"""Smoke checks for public presentation of refined S4 destination profiles."""
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_export_uses_s4_profiles_and_named_clusters():
    subprocess.run([sys.executable, str(ROOT / "scripts/web/export_destinations.py")], cwd=ROOT, check=True)
    data = json.loads((ROOT / "site/data/destinations.json").read_text(encoding="utf-8"))
    profiles = pd.read_csv(ROOT / "data/interim/destination_profiles_s4.csv").set_index("destination")
    memberships = pd.read_csv(ROOT / "outputs/mining/clustering/cluster_membership.csv").set_index("destination")
    assert len(data) == len(profiles) == 55
    assert len({item["cluster"]["id"] for item in data}) == 12
    assert {item["name"] for item in data} == set(profiles.index)
    themes = {
        "theme_beach_coast": "beach_coast", "theme_nature": "nature",
        "theme_culture_history": "culture_history", "theme_archaeology": "archaeology",
        "theme_adventure": "adventure", "theme_gastronomy_coffee": "gastronomy_coffee",
        "theme_wellness_spiritual": "wellness_spiritual", "theme_urban_services": "urban_services",
    }
    for entry in data:
        p = profiles.loc[entry["name"]]
        expected = [label for column, label in themes.items() if p[column] == 1]
        assert entry["themes"] == expected
        assert entry["cluster"]["medoid"] == memberships.loc[entry["name"], "cluster_medoid"]
        for lang in ("en", "es", "ja"):
            assert entry["cluster"]["name"][lang].strip()
            assert entry["cluster"]["description"][lang].strip()
    lookup = {e["name"]: e for e in data}
    assert "culture_history" in lookup["Carrillo Puerto"]["themes"]
    assert "gastronomy_coffee" in lookup["Carrillo Puerto"]["themes"]
    assert "beach_coast" in lookup["La Antigua"]["themes"]
    assert "nature" not in lookup["Poza Rica de Hidalgo"]["themes"]
