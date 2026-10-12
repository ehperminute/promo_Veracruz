"""Recompute static planner scenarios from the current repository inputs.

Run: python -m pytest -q tests/test_s7_reproducibility.py
"""
import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]


def load_solver():
    path = ROOT / 'scripts' / 'run_s7_framework.py'
    spec = importlib.util.spec_from_file_location('run_s7_framework', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('budget', [30000, 60000, 100000, 200000])
def test_s7_matches_published_planner(budget):
    profiles = pd.read_csv(ROOT / 'data' / 'interim' / 'destination_profiles_s4.csv')
    occupancy = pd.read_csv(ROOT / 'data' / 'reference' / 'datatur_veracruz_monthly_2025_2026.csv')
    planner = json.loads((ROOT / 'site' / 'data' / 's7_precomputed.json').read_text(encoding='utf-8'))
    solver = load_solver()
    actual, indicators = solver.solve(profiles, occupancy, budget=budget)
    expected = planner['budgets'][str(budget)]
    actual_pairs = {(r.destination, r.period) for r in actual.itertuples()}
    expected_pairs = {(r['destination'], r['period']) for r in expected}
    assert actual_pairs == expected_pairs, f'S7 selections changed for budget {budget}'
    assert indicators['spent_mxn'] <= budget
    assert len(actual) == len(expected)
    assert indicators['regions_represented'] == actual['region'].nunique()
