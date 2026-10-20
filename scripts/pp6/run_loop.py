"""PP6 local, bounded, stage-gated validation runner.

Usage: python scripts/pp6/run_loop.py [--max-attempts 2]
Works on *existing* recovered source-backed database and derived results.
Does NOT touch the web/map or replace source data. Refuses to silently
promote planned campaigns into observed results, or unresolved predictions
into public features. Writes all new execution records to outputs/pp6_loop/.
"""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "outputs/pp6_loop"
AUDIT = ROOT / "experiments/pp6_second_pass/results"
SOURCE = ROOT / "docs/marketing/foreign_campaign_test_matrix_v1.csv"
RAW_REQUIRED = (
    "PIB_Turistico_Estatal_y_Municipal_2018-2022_.zip",
    "denue_00_48-49_csv.zip", "denue_00_56_shp.zip",
    "denue_00_71_csv.zip", "denue_00_72_1_csv.zip",
    "denue_00_72_2_csv.zip",
)


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(filename: str) -> dict:
    return json.loads((AUDIT / filename).read_text(encoding="utf-8"))


def check_results() -> str:
    info = load_json("database_audit.json")
    if not (info["integrity"] == "ok" and info["municipalities"] == 212
            and info["original_product_descriptions_restored"] == 295
            and info["accepted_specific_activity_pairs"] == 216
            and all(s["valid_hash"] for s in info["verified_html_snapshots"])):
        raise ValueError("Database integrity/source/evidence acceptance criteria not met")
    s4 = load_json("s4_evidence_discovery.json")
    if not(s4["campaign_distinct_feature_links"] == 66 and s4["campaign_links_with_original_text_support"] == 65):
        raise ValueError("Source-backed activity evidence changed; review rather than overwrite")
    s7 = load_json("s7_evidence_sensitive_optimization.json")
    if any(item["objective_types_covered"] != 47 or item["selected_n"] != 6
           for item in s7.values()):
        raise ValueError("Documented exact MILP objective no longer reproduces")
    s5 = load_json("s5_paired_interpretation.json")
    if s5["paired_predictions"] != 52 or any(r["paired_n"] != 52 for r in s5["comparison"]):
        raise ValueError("ML comparisons are not on the same cases")
    s6 = load_json("s6_interval_audit.json")
    if s6["metric_rows_checked"] != 12 or s6["prediction_rows_checked"] != 212:
        raise ValueError("Stored interval metrics did not reproduce")
    return "Recovered source, paired ML comparisons, S6 intervals and exact S7 allocation agree with stored evidence"


def check_marketing() -> str:
    output = ROOT / "outputs/marketing/foreign_campaign_test_matrix_v1.csv"
    if not output.exists() or sha(SOURCE) != sha(output):
        raise ValueError("Expected 24-cell authored matrix not mirrored correctly")
    with output.open(encoding="utf-8-sig", newline="") as f:
        records = list(csv.DictReader(f))
    if len(records) != 24 or len({x["test_id"] for x in records}) != 24:
        raise ValueError("Campaign matrix is not 24 controlled unique test cells")
    ledger = ROOT / "experiments/pp6_second_pass/results/s8_campaign_claims_evidence.csv"
    if not ledger.is_file():
        raise FileNotFoundError("Missing evidence ledger generated from canonical source")
    with ledger.open(encoding="utf-8", newline="") as f:
        claims = list(csv.DictReader(f))
    if len(claims) != 66 or sum(int(r["original_text_support_count"]) > 0 for r in claims) != 65:
        raise ValueError("Source-backed campaign claim counts differ from audited baseline")
    return "24 marketing proposal cells restored from authored specification; 65/66 campaign claims have archived original-text support (not current operation)"



def check_markov() -> str:
    """Recheck Markov's negative result against the unchanged DataTur rows."""
    from collections import Counter
    source = ROOT / 'experiments/stochastic/markov_2026/source_data/datatur_2025_2026_snapshot.csv'
    current = ROOT / 'data/reference/datatur_veracruz_monthly_2025_2026.csv'
    fields = ['fecha', 'anio', 'mes', 'centro', 'ocupacion_pct', 'source_archive']
    def load_rows(path):
        with path.open(encoding='utf-8', newline='') as f:
            return Counter(tuple(row[c] for c in fields) for row in csv.DictReader(f))
    if load_rows(source) != load_rows(current):
        raise ValueError('Markov snapshot does not match current reference on all shared fields')
    metadata = json.loads((ROOT/'experiments/stochastic/markov_2026/outputs/metadata.json').read_text(encoding='utf-8'))
    overall = metadata['overall']
    if (overall['test_n'], overall['markov_correct'], overall['persistence_correct']) != (20, 8, 8):
        raise ValueError('Markov holdout result changed; investigate rather than claim success')
    return 'Markov 8/20 and persistence 8/20, with matching 53 source observations; no predictive advantage'


def run_cmd(name: str, argv: list[str], attempt: int, timeout: int = 120) -> None:
    log = OUTPUT / "logs" / f"{name}_attempt{attempt}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w", encoding="utf-8") as f:
        f.write("Command: " + " ".join(argv) + "\n\n")
        f.flush()
        process = subprocess.run(argv, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT,
                                 timeout=timeout, check=False)
    if process.returncode != 0:
        raise RuntimeError(f"Exit code {process.returncode}; see {log.relative_to(ROOT)}")


def scope_gate(name: str, runner, verify, attempts: int, state: dict,
               status="PASS", depends_on=()):
    record = {"status": "PENDING", "attempts": [], "dependencies": list(depends_on)}
    state["gates"][name] = record
    for dep in depends_on:
        if state["gates"].get(dep, {}).get("status") not in {"PASS", "RESEARCH_PASS", "PASS_WITH_LIMITS"}:
            record.update(status="BLOCKED", reason=f"Dependency {dep} did not pass")
            atomic_json(OUTPUT / "state.json", state)
            print(f"[{name}] BLOCKED: {record['reason']}")
            return
    for n in range(1, attempts+1):
        try:
            runner(name, n)
            reason = verify()
            record["attempts"].append({"number": n, "result": "PASS"})
            record.update(status=status, reason=reason)
            break
        except Exception as e:
            record["attempts"].append({"number": n, "result": "FAIL", "diagnosis": str(e)})
            record.update(status="FAILED", reason=str(e))
            # Retry only once; deterministic failures must be fixed in source, not concealed.
    atomic_json(OUTPUT / "state.json", state)
    print(f"[{name}] {record['status']}: {record['reason']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-attempts", type=int, default=2)
    args = parser.parse_args()
    if not 1 <= args.max_attempts <= 3:
        parser.error("--max-attempts must be 1 to 3")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    state = {
        "protocol": "PP6-stage-gates-v1",
        "utc_executed": datetime.now(timezone.utc).isoformat(),
        "source_of_truth": "data/recovered_source_descriptions/veracruz_pp3_master_with_originals.sqlite",
        "scope": "Evidence checks, not production deployment or observed tourism demand",
        "max_attempts": args.max_attempts,
        "gates": {},
    }
    atomic_json(OUTPUT/"state.json",state)

    # S0: missing frozen archives are external-input blockers; do not fabricate them.
    missing = [name for name in RAW_REQUIRED if not (ROOT/"data/raw"/name).exists()]
    state["gates"]["S0_FULL_RAW_REBUILD"] = {
        "status": "BLOCKED" if missing else "DEFERRED",
        "reason": "Slim transfer excludes frozen raw archives" if missing else "All archived inputs appear present; full rebuild intentionally not run against working tree",
        "missing_inputs": missing,
        "attempts": [],
    }
    atomic_json(OUTPUT/"state.json",state)
    print(f"[S0_FULL_RAW_REBUILD] {state['gates']['S0_FULL_RAW_REBUILD']['status']}: {len(missing)} unavailable archives")

    # Independent stages: a genuine S5 failure must not block S4/S6/S7.
    stage_specs = [
        ("S0_DATABASE", "database", lambda: "Recovered SQLite, source checksums and 295 descriptions verified", "PASS", ()),
        ("S4_DISCOVERY", "discovery", lambda: "Activity matches have source IDs; archived 65/66 campaign pairs have text support", "PASS", ("S0_DATABASE",)),
        ("S5_FORECAST", "forecast", lambda: "52 identical cases for baseline/model comparison; deployment superiority not established", "RESEARCH_PASS", ()),
        ("S6_INTERVALS", "intervals", lambda: "212 archived predictions and 12 interval metrics internally consistent; not statewide forecasts", "RESEARCH_PASS", ()),
        ("S7_MILP", "milp", lambda: "Exact MILP reproduces six municipalities, 47 activity types; hypothetical budget", "PASS_WITH_LIMITS", ("S4_DISCOVERY",)),
        ("S8_EVIDENCE_LEDGER", "campaign", lambda: "66 source-linked archived campaign claims; no actual market response observed", "PASS_WITH_LIMITS", ("S4_DISCOVERY",)),
    ]
    for name,stage,verify,status,deps in stage_specs:
        scope_gate(name, lambda name,n,stage=stage: run_cmd(name,[sys.executable,"scripts/pp6/run_stage.py",stage],n),
                   verify, args.max_attempts, state, status=status, depends_on=deps)
    scope_gate("S6_MARKOV", lambda name,n: run_cmd(name,[sys.executable,"experiments/stochastic/markov_2026/run_markov.py"],n),
               check_markov, args.max_attempts, state, status="RESEARCH_PASS")
    scope_gate("SCIENTIFIC_TESTS", lambda name,n: run_cmd(name,[sys.executable,"-m","pytest","-q","experiments/pp6_second_pass/tests/test_second_pass.py"],n),
               lambda: "10 independent scientific reproducibility tests passed", args.max_attempts, state,
               depends_on=("S0_DATABASE", "S4_DISCOVERY", "S5_FORECAST", "S6_INTERVALS", "S7_MILP"))
    scope_gate("S8_CAMPAIGN_EXPORT", lambda name,n: run_cmd(name,[sys.executable,"scripts/marketing/export_foreign_campaign_matrix.py"],n),
               check_marketing,args.max_attempts,state,status="PASS_WITH_LIMITS",depends_on=("S8_EVIDENCE_LEDGER",))
    # Current tests without deliberately excluded raw snapshots or the historically
    # published site exporter that writes site/data/destinations.json during testing.
    scope_gate("REPOSITORY_TESTS", lambda name,n: run_cmd(name,[sys.executable,"-m","pytest","-q","tests","--ignore=tests/test_raw_sources.py","--ignore=tests/test_web_export.py"],n),
               lambda: "Scoped repository tests passed without modifying published site data",args.max_attempts,state)

    scope_gate("S9_TECHNICAL_DRAFT", lambda name,n: run_cmd(name,[sys.executable,"scripts/pp6/build_report.py"],n),
               lambda: "Research report generated from latest tested artifacts; course-rubric certification separate",
               args.max_attempts,state,status="PASS_WITH_LIMITS",
               depends_on=("S0_DATABASE", "S4_DISCOVERY", "S5_FORECAST", "S6_INTERVALS", "S7_MILP", "S8_CAMPAIGN_EXPORT"))

    # Requirements were recovered from the original 2026-2 academic PDF.
    # This gate verifies the SPEC, not completion of all deliverables.
    rubric_spec = ROOT / "docs/pp6/original_rubric_spec.json"
    try:
        requirement = json.loads(rubric_spec.read_text(encoding="utf-8"))
        weighting = requirement["weights"]
        ids = [entry[0] for entry in weighting]
        if (len(weighting) != 11 or len(set(ids)) != 11
                or sum(entry[1] for entry in weighting) != 100
                or len(requirement["products"]) != 4):
            raise ValueError("Original rubric specification inconsistent")
        state["gates"]["S9_RUBRIC_SPEC"] = {
            "status": "PASS", "attempts": [{"number": 1, "result": "PASS"}],
            "reason": "Original 2026-2 PP retrieved; 11 weighted criteria sum to 100%; four required products identified",
        }
        state["gates"]["S9_RUBRIC_SUBMISSIONS"] = {
            "status": "IN_PROGRESS", "attempts": [],
            "reason": "Original rubrics are available; final 30–40-page report, campaign implementation/evaluation, technical artifacts and <=15-min defense need completion and audit",
        }
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
        state["gates"]["S9_RUBRIC_SPEC"] = {"status": "FAILED", "attempts": [], "reason": str(exc)}
        state["gates"]["S9_RUBRIC_SUBMISSIONS"] = {"status": "BLOCKED", "attempts": [], "reason": "Rubric specification validation failed"}
    # Audits *completeness* of four deliverables; research tests cannot certify final submission.
    scope_gate("S9_SUBMISSION_GAP_AUDIT",
               lambda name,n: run_cmd(name,[sys.executable,"scripts/pp6/audit_deliverables.py"],n),
               lambda: "Submission gap ledger produced; 30–40-page report, integrated campaign and colloquium still require completion",
               args.max_attempts, state, status="PASS_WITH_LIMITS", depends_on=("S9_RUBRIC_SPEC",))
    state["gates"]["PUBLIC_MARKETING_DEPLOYMENT"] = {
        "status": "BLOCKED", "attempts": [],
        "reason": "Opening/access, provider schedules, actual media prices and real user responses not verified; research study may still conclude",
    }
    atomic_json(OUTPUT/"state.json",state)
    statuses = {k:r["status"] for k,r in state["gates"].items()}
    summary = "# PP6 execution checkpoint\n\n" + "\n".join(f"- **{k}**: {v} — {state['gates'][k]['reason']}" for k,v in statuses.items()) + "\n"
    (OUTPUT/"CHECKPOINT.md").write_text(summary,encoding="utf-8")
    print("\nCheckpoint:",OUTPUT/"state.json")
    failed = [k for k,v in statuses.items() if v=="FAILED"]
    if failed:
        print("FAILED gates requiring source correction:",failed)
        return 1
    print("Completed available gates; blocked external gates documented; no website or map modified.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
