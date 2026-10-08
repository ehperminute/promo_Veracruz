from pathlib import Path
from collections import Counter
from itertools import combinations

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = ROOT / "data" / "interim" / "veracruz_products_parsed.csv"
RULES = ROOT / "outputs" / "mining" / "associations" / "municipality_pair_rules.csv"


def test_rules_use_all_295_parsed_official_product_cards():
    products = pd.read_csv(PRODUCTS)
    rules = pd.read_csv(RULES)
    assert len(products) == 295
    assert not rules.empty
    assert set(rules["n_baskets"]) == {295}
    assert rules["support"].ge(0.015).all()
    assert rules["confidence"].ge(0.50).all()
    assert rules["lift"].ge(1.0).all()
    assert rules["interpretation"].eq("tourism-offer co-occurrence; not tourist movement").all()


def test_rule_metrics_recompute_from_source_baskets():
    products = pd.read_csv(PRODUCTS)
    baskets = [sorted({x.strip() for x in str(v).split("|") if x.strip()}) for v in products["municipios"].fillna("")]
    singles = Counter()
    pairs = Counter()
    for basket in baskets:
        singles.update(basket)
        pairs.update(combinations(basket, 2))

    rules = pd.read_csv(RULES)
    row = rules.iloc[0]
    pair = tuple(sorted([row["antecedent"], row["consequent"]]))
    pair_count = pairs[pair]
    n = len(baskets)
    expected_support = pair_count / n
    expected_confidence = pair_count / singles[row["antecedent"]]
    expected_lift = expected_confidence / (singles[row["consequent"]] / n)

    assert row["pair_count"] == pair_count
    assert abs(row["support"] - expected_support) < 1e-12
    assert abs(row["confidence"] - expected_confidence) < 1e-12
    assert abs(row["lift"] - expected_lift) < 1e-12
