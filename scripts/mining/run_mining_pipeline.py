from pathlib import Path
import argparse
import hashlib
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = [
    "build_destination_profiles.py",
    "build_candidates.py",
    "cluster_destinations.py",
    "build_similarity.py",
    "mine_product_associations.py",
]
REPORT_SCRIPT = ROOT / "scripts" / "reporting" / "build_data_catalog.py"
OUTPUTS = [
    ROOT / "data" / "interim" / "destination_profiles_s4.csv",
    ROOT / "outputs" / "mining" / "audit" / "destination_profile_gaps.csv",
    ROOT / "outputs" / "mining" / "candidates" / "undermeasured_candidates.csv",
    ROOT / "outputs" / "mining" / "clustering" / "cluster_diagnostics.csv",
    ROOT / "outputs" / "mining" / "clustering" / "cluster_membership.csv",
    ROOT / "outputs" / "mining" / "clustering" / "cluster_profiles.csv",
    ROOT / "outputs" / "mining" / "clustering" / "cluster_medoid_similarity.csv",
    ROOT / "outputs" / "mining" / "clustering" / "destination_silhouettes.csv",
    ROOT / "outputs" / "mining" / "clustering" / "feature_sensitivity.csv",
    ROOT / "outputs" / "mining" / "similarity" / "undermeasured_anchor_similarity.csv",
    ROOT / "outputs" / "mining" / "associations" / "municipality_pair_rules.csv",
    ROOT / "docs" / "DATA_CATALOG.md",
]
TEST_FILES = [
    "tests/test_mining_profiles.py",
    "tests/test_mining_clustering.py",
    "tests/test_mining_similarity.py",
    "tests/test_mining_associations.py",
    "tests/test_mining_semantics.py",
]


def _run_pipeline() -> None:
    for script in SCRIPTS:
        path = ROOT / "scripts" / "mining" / script
        print(f"\n=== {script} ===")
        subprocess.run([sys.executable, str(path)], cwd=ROOT, check=True)
    print("\n=== build_data_catalog.py ===")
    subprocess.run([sys.executable, str(REPORT_SCRIPT)], cwd=ROOT, check=True)


def _digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--idempotence", action="store_true")
    args = parser.parse_args()

    _run_pipeline()
    if args.idempotence:
        before = {p: _digest(p) for p in OUTPUTS}
        _run_pipeline()
        after = {p: _digest(p) for p in OUTPUTS}
        changed = [str(p.relative_to(ROOT)) for p in OUTPUTS if before[p] != after[p]]
        if changed:
            raise SystemExit(f"Idempotence check failed: {changed}")
        print("\nS4 idempotence check: PASS")

    if args.test:
        print("\n=== pytest: S4 rework ===")
        subprocess.run([sys.executable, "-m", "pytest", "-q", *TEST_FILES], cwd=ROOT, check=True)

    print("\nS4 mixed-data mining pipeline completed.")


if __name__ == "__main__":
    main()
