from pathlib import Path
import argparse
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run implemented project stages through S4")
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--idempotence", action="store_true")
    args = parser.parse_args()

    data_cmd = [sys.executable, str(ROOT / "scripts" / "data" / "run_data_pipeline.py")]
    mining_cmd = [sys.executable, str(ROOT / "scripts" / "mining" / "run_mining_pipeline.py")]
    if args.test:
        data_cmd.append("--test")
        mining_cmd.append("--test")
    if args.idempotence:
        data_cmd.append("--idempotence")
        mining_cmd.append("--idempotence")

    subprocess.run(data_cmd, cwd=ROOT, check=True)
    subprocess.run(mining_cmd, cwd=ROOT, check=True)
    print("\nImplemented pipeline through S4 completed.")


if __name__ == "__main__":
    main()
