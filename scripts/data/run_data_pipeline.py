from pathlib import Path
import argparse
import hashlib
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = [
    "build_source_registry.py",
    "prepare_veracruz_web_reference.py",
    "prepare_datatur.py",
    "prepare_inah.py",
    "prepare_infrastructure.py",
    "prepare_tourism_products.py",
    "build_destination_master.py",
    "build_demand_series.py",
    "prepare_origin_markets.py",
]
OUTPUTS = [
    ROOT / "data" / "interim" / "source_registry_resolved.csv",
    ROOT / "docs" / "DATA_SOURCES.md",
    ROOT / "data" / "interim" / "veracruz_products_parsed.csv",
    ROOT / "data" / "interim" / "veracruz_regions_parsed.csv",
    ROOT / "data" / "interim" / "veracruz_pueblos_magicos_parsed.csv",
    ROOT / "data" / "interim" / "fact_datatur_centro_mes.csv",
    ROOT / "data" / "interim" / "datatur_veracruz_monthly.csv",
    ROOT / "data" / "interim" / "fact_inah_veracruz_mes.csv",
    ROOT / "data" / "interim" / "mart_infraestructura_municipio_veracruz.csv",
    ROOT / "data" / "interim" / "tourism_products.csv",
    ROOT / "data" / "processed" / "destination_master.csv",
    ROOT / "data" / "processed" / "demand_series.csv",
    ROOT / "data" / "processed" / "origin_market_opportunity.csv",
]
TEST_FILES = [
    "tests/test_raw_sources.py",
    "tests/test_source_registry.py",
    "tests/test_veracruz_web_reference.py",
    "tests/test_denue_activity_groups.py",
    "tests/test_destination_reference.py",
    "tests/test_datatur_pipeline.py",
    "tests/test_inah_pipeline.py",
    "tests/test_infrastructure_pipeline.py",
    "tests/test_destination_master.py",
    "tests/test_demand_series.py",
    "tests/test_origin_market_opportunity.py",
    "tests/test_repository_docs.py",
]


def _run_pipeline() -> None:
    for script in SCRIPTS:
        path = ROOT / "scripts" / "data" / script
        print(f"\n=== {script} ===")
        subprocess.run([sys.executable, str(path)], cwd=ROOT, check=True)


def _digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Run Milestone-1 tests after rebuilding")
    parser.add_argument(
        "--idempotence",
        action="store_true",
        help="Run the data pipeline twice and assert byte-identical generated outputs",
    )
    args = parser.parse_args()

    _run_pipeline()

    if args.idempotence:
        before = {path: _digest(path) for path in OUTPUTS}
        _run_pipeline()
        after = {path: _digest(path) for path in OUTPUTS}
        changed = [str(path.relative_to(ROOT)) for path in OUTPUTS if before[path] != after[path]]
        if changed:
            raise SystemExit(f"Idempotence check failed; outputs changed on second run: {changed}")
        print("\nIdempotence check: PASS")

    if args.test:
        print("\n=== pytest: Milestone 1 ===")
        subprocess.run([sys.executable, "-m", "pytest", "-q", *TEST_FILES], cwd=ROOT, check=True)

    print("\nMilestone-1 data pipeline completed.")


if __name__ == "__main__":
    main()
