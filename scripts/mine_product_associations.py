from collections import Counter
from itertools import combinations
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "processed" / "tourism_products_sample_v1.csv"
OUTDIR = ROOT / "outputs" / "associations"

MIN_SUPPORT = 0.04
MIN_CONFIDENCE = 0.50
MIN_LIFT = 1.00

def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(INPUT)

    baskets = []
    for value in df["municipios"].fillna(""):
        basket = sorted({x.strip() for x in str(value).split("|") if x.strip()})
        baskets.append(basket)

    n = len(baskets)
    singles = Counter()
    pairs = Counter()

    for basket in baskets:
        singles.update(basket)
        pairs.update(combinations(basket, 2))

    rows = []
    for (a, b), pair_count in pairs.items():
        support_ab = pair_count / n
        if support_ab < MIN_SUPPORT:
            continue

        for antecedent, consequent in ((a, b), (b, a)):
            support_a = singles[antecedent] / n
            support_b = singles[consequent] / n
            confidence = support_ab / support_a
            lift = confidence / support_b

            if confidence >= MIN_CONFIDENCE and lift >= MIN_LIFT:
                rows.append({
                    "antecedent": antecedent,
                    "consequent": consequent,
                    "support": support_ab,
                    "confidence": confidence,
                    "lift": lift,
                    "pair_count": pair_count,
                })

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["lift", "confidence", "support"], ascending=False)

    out.to_csv(OUTDIR / "municipality_pair_rules.csv", index=False)
    print(f"Wrote {len(out)} rules -> {(OUTDIR / 'municipality_pair_rules.csv').relative_to(ROOT)}")

if __name__ == "__main__":
    main()
