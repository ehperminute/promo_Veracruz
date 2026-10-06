from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "data" / "reference" / "tourism_products.csv"
OUTDIR = ROOT / "data" / "interim"
OUTPUT = OUTDIR / "tourism_products.csv"

REQUIRED = {"producto", "municipios", "n_municipios", "source_snapshot", "curation_version"}


def transform(df: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Tourism-product reference is missing columns: {sorted(missing)}")

    out = df.copy()
    out["producto"] = out["producto"].astype(str).str.strip()
    out["municipios"] = out["municipios"].fillna("").astype(str)
    out["n_municipios"] = pd.to_numeric(out["n_municipios"], errors="raise").astype(int)

    actual_counts = out["municipios"].map(
        lambda value: len({x.strip() for x in value.split("|") if x.strip()})
    )
    if not actual_counts.equals(out["n_municipios"]):
        bad = out.loc[actual_counts.ne(out["n_municipios"]), ["producto", "municipios", "n_municipios"]]
        raise AssertionError(f"Tourism-product municipality counts disagree:\n{bad.to_string(index=False)}")
    if out["producto"].duplicated().any():
        raise AssertionError("Tourism-product names must be unique in the current reference")

    return out.sort_values("producto", kind="stable").reset_index(drop=True)


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    out = transform(pd.read_csv(REFERENCE))
    out.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(out):,} rows -> {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
