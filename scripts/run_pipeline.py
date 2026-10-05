from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    "build_candidates.py",
    "cluster_destinations.py",
    "mine_product_associations.py",
    "build_international_market_shortlist.py",
]

def main():
    for script in SCRIPTS:
        path = ROOT / "scripts" / script
        print(f"\n=== {script} ===")
        subprocess.run([sys.executable, str(path)], cwd=ROOT, check=True)
    print("\nPipeline completed.")

if __name__ == "__main__":
    main()
