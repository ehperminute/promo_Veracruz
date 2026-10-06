from pathlib import Path
from difflib import SequenceMatcher
import re
import unicodedata

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "data" / "reference" / "tourism_products.csv"
PARSED = ROOT / "data" / "interim" / "veracruz_products_parsed.csv"
OUTDIR = ROOT / "data" / "interim"
OUTPUT = OUTDIR / "tourism_products.csv"

REQUIRED = {"producto", "municipios", "n_municipios", "source_snapshot", "curation_version"}


def _municipality_set(value: object) -> frozenset[str]:
    return frozenset(x.strip() for x in str(value).split("|") if x.strip())


def _normalize_title(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode().lower()
    text = re.sub(r"\d+$", "", text).strip()
    text = re.sub(r"\b(de|del|la|las|los|el|en|con|y|a|por)\b", " ", text)
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def _ground_selection(selection: pd.DataFrame, parsed: pd.DataFrame) -> pd.DataFrame:
    parsed = parsed.copy()
    parsed["municipality_set"] = parsed["municipios"].map(_municipality_set)
    parsed["title_norm"] = parsed["producto"].map(_normalize_title)

    rows = []
    for r in selection.itertuples(index=False):
        municipalities = _municipality_set(r.municipios)
        candidates = parsed[parsed["municipality_set"].eq(municipalities)]
        if candidates.empty:
            raise AssertionError(
                f"Curated tourism product has no source card with the same municipalities: {r.producto}"
            )
        target = _normalize_title(r.producto)
        scored = []
        for candidate in candidates.itertuples(index=False):
            score = SequenceMatcher(None, target, candidate.title_norm).ratio()
            scored.append((score, candidate))
        score, best = max(scored, key=lambda x: x[0])
        if score < 0.65:
            raise AssertionError(
                f"Curated product could not be grounded confidently in frozen HTML: {r.producto}; "
                f"best={best.producto!r}, score={score:.3f}"
            )
        row = r._asdict()
        row.update(
            {
                "source_card_index": int(best.source_card_index),
                "source_producto": best.producto,
                "source_match_score": round(float(score), 6),
            }
        )
        rows.append(row)
    return pd.DataFrame(rows)


def transform(df: pd.DataFrame, parsed: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Tourism-product reference is missing columns: {sorted(missing)}")

    out = df.copy()
    out["producto"] = out["producto"].astype(str).str.strip()
    out["municipios"] = out["municipios"].fillna("").astype(str)
    out["n_municipios"] = pd.to_numeric(out["n_municipios"], errors="raise").astype(int)

    actual_counts = out["municipios"].map(lambda value: len(_municipality_set(value)))
    if not actual_counts.equals(out["n_municipios"]):
        bad = out.loc[actual_counts.ne(out["n_municipios"]), ["producto", "municipios", "n_municipios"]]
        raise AssertionError(f"Tourism-product municipality counts disagree:\n{bad.to_string(index=False)}")
    if out["producto"].duplicated().any():
        raise AssertionError("Tourism-product names must be unique in the current reference")

    out = _ground_selection(out, parsed)
    return out.sort_values("producto", kind="stable").reset_index(drop=True)


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    out = transform(pd.read_csv(REFERENCE), pd.read_csv(PARSED))
    out.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(out):,} rows -> {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
