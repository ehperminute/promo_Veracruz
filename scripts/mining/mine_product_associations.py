from collections import Counter
from itertools import combinations
from pathlib import Path

import pandas as pd

from common import OUTDIR, PARSED_PRODUCTS

OUTPUT = OUTDIR / "associations" / "municipality_pair_rules.csv"
MIN_SUPPORT = 0.015
MIN_CONFIDENCE = 0.50
MIN_LIFT = 1.00

COLUMNS = [
    "antecedent",
    "consequent",
    "n_baskets",
    "antecedent_count",
    "consequent_count",
    "pair_count",
    "support",
    "confidence",
    "lift",
    "interpretation",
]


def baskets_from_products(df: pd.DataFrame) -> list[list[str]]:
    return [
        sorted({part.strip() for part in str(value).split("|") if part.strip()})
        for value in df["municipios"].fillna("")
    ]


def mine_rules(df: pd.DataFrame) -> pd.DataFrame:
    baskets = baskets_from_products(df)
    n = len(baskets)
    if n == 0:
        raise AssertionError("No tourism-product baskets available")

    singles: Counter[str] = Counter()
    pairs: Counter[tuple[str, str]] = Counter()
    for basket in baskets:
        singles.update(basket)
        pairs.update(combinations(basket, 2))

    rows = []
    for (a, b), pair_count in pairs.items():
        support_ab = pair_count / n
        if support_ab < MIN_SUPPORT:
            continue
        for antecedent, consequent in ((a, b), (b, a)):
            antecedent_count = singles[antecedent]
            consequent_count = singles[consequent]
            confidence = pair_count / antecedent_count
            lift = confidence / (consequent_count / n)
            if confidence >= MIN_CONFIDENCE and lift >= MIN_LIFT:
                rows.append(
                    {
                        "antecedent": antecedent,
                        "consequent": consequent,
                        "n_baskets": n,
                        "antecedent_count": antecedent_count,
                        "consequent_count": consequent_count,
                        "pair_count": pair_count,
                        "support": support_ab,
                        "confidence": confidence,
                        "lift": lift,
                        "interpretation": "tourism-offer co-occurrence; not tourist movement",
                    }
                )

    out = pd.DataFrame(rows, columns=COLUMNS)
    if not out.empty:
        out = out.sort_values(
            ["lift", "confidence", "support", "antecedent", "consequent"],
            ascending=[False, False, False, True, True],
            kind="mergesort",
        ).reset_index(drop=True)
    return out


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(PARSED_PRODUCTS)
    out = mine_rules(df)
    out.to_csv(OUTPUT, index=False)
    print(f"Mined {len(out)} rules from {len(df)} official product cards -> {OUTPUT.relative_to(Path(__file__).resolve().parents[2])}")


if __name__ == "__main__":
    main()
