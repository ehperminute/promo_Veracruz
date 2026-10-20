"""Validate the loop's control flow with isolated tests; no project data modified."""
import importlib.util
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "scripts/pp6/run_loop.py"
spec = importlib.util.spec_from_file_location("pp6_orchestration", PATH)
loop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loop)


def test_bounded_failure_and_independent_progress(monkeypatch, tmp_path):
    monkeypatch.setattr(loop, "OUTPUT", tmp_path)
    state = {"gates": {}}
    attempted = []

    def failing(name, attempt):
        attempted.append(attempt)
        raise ValueError("synthetic failure")

    loop.scope_gate("failed", failing, lambda: "never", 2, state)
    assert state["gates"]["failed"]["status"] == "FAILED"
    assert attempted == [1, 2]

    # An independent task must continue despite failure elsewhere.
    loop.scope_gate("independent", lambda n,a: None, lambda: "ok", 2, state)
    assert state["gates"]["independent"]["status"] == "PASS"
    assert len(state["gates"]["independent"]["attempts"]) == 1

    # A dependent task must not execute when upstream actually failed.
    calls = []
    loop.scope_gate("dependent", lambda n,a: calls.append(1), lambda: "ok", 2,
                    state, depends_on=("failed",))
    assert state["gates"]["dependent"]["status"] == "BLOCKED"
    assert not calls


def test_transient_failure_recovers_within_limit(monkeypatch, tmp_path):
    monkeypatch.setattr(loop, "OUTPUT", tmp_path)
    state = {"gates": {}}
    attempts = []

    def fail_once(name, attempt):
        attempts.append(attempt)
        if attempt == 1:
            raise RuntimeError("temporary failure")

    loop.scope_gate("recovered", fail_once, lambda: "verified", 2, state)
    assert attempts == [1, 2]
    assert state["gates"]["recovered"]["status"] == "PASS"
    assert [a["result"] for a in state["gates"]["recovered"]["attempts"]] == ["FAIL", "PASS"]
