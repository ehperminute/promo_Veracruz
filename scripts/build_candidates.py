from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "scripts" / "mining" / "build_candidates.py"

if __name__ == "__main__":
    subprocess.run([sys.executable, str(TARGET)], cwd=ROOT, check=True)
