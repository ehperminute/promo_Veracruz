from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "processed" / "international_market_opportunity_v1.csv"
OUTPUT = ROOT / "outputs" / "marketing" / "international_market_shortlist_v1.csv"

KEEP_TIERS = {"A_core_scale", "A_large_market", "A_growth_secondary", "B_established_secondary", "B_growth_test"}

def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with INPUT.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    selected = [r for r in rows if r["market_tier_v1"] in KEEP_TIERS]
    selected.sort(
        key=lambda r: (
            -float(r["share_2025_pct"]),
            -float(r["growth_2025_vs_2024_pct"])
        )
    )

    with OUTPUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(selected)

    print(f"Wrote {len(selected)} markets -> {OUTPUT.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
