from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "data" / "reference" / "origin_market_2025_validated.csv"
OUTDIR = ROOT / "data" / "processed"
OUTPUT = OUTDIR / "origin_market_opportunity.csv"

SOURCE_URL = "https://www.datatur.sectur.gob.mx/Documentoscompartidos/upm/RES_2025_12.pdf"
TOP25_2025_TOTAL = 20_667_837
OTHER_UNSPECIFIED_2025 = 654_520
OFFICIAL_2025_TOTAL = 21_322_357

REQUIRED = {
    "rank_2025",
    "country_of_residence",
    "air_entries_2024",
    "air_entries_2025",
    "share_2025_pct",
    "growth_2025_vs_2024_pct",
    "source_url",
    "source_version",
    "scope_note",
}


def transform(df: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Origin-market reference is missing columns: {sorted(missing)}")

    out = df.copy()
    out["rank_2025"] = pd.to_numeric(out["rank_2025"], errors="raise").astype(int)
    for col in ["air_entries_2024", "air_entries_2025"]:
        out[col] = pd.to_numeric(out[col], errors="raise").astype("int64")
    for col in ["share_2025_pct", "growth_2025_vs_2024_pct"]:
        out[col] = pd.to_numeric(out[col], errors="raise").astype(float)

    out = out.sort_values("rank_2025", kind="stable").reset_index(drop=True)

    if out["rank_2025"].tolist() != list(range(1, 26)):
        raise AssertionError("Origin-market reference must contain ranks 1..25 exactly once")
    if out["country_of_residence"].duplicated().any():
        raise AssertionError("Origin-market countries must be unique")
    if (out[["air_entries_2024", "air_entries_2025"]] < 0).any().any():
        raise AssertionError("Origin-market entry counts must be non-negative")
    if not out["share_2025_pct"].between(0, 100).all():
        raise AssertionError("Origin-market shares must be percentages")
    if set(out["source_url"]) != {SOURCE_URL}:
        raise AssertionError("Origin-market reference must point to the fixed official DataTur report")

    calculated_growth = 100.0 * (out["air_entries_2025"] / out["air_entries_2024"] - 1.0)
    if not np.allclose(calculated_growth, out["growth_2025_vs_2024_pct"], atol=0.11):
        raise AssertionError("Origin-market growth does not agree with the source counts within rounding tolerance")

    if int(out["air_entries_2025"].sum()) != TOP25_2025_TOTAL:
        raise AssertionError("Top-25 2025 entry total does not match the validated source extract")
    if TOP25_2025_TOTAL + OTHER_UNSPECIFIED_2025 != OFFICIAL_2025_TOTAL:
        raise AssertionError("Origin-market source control total is internally inconsistent")

    # S3 stays factual. Marketing tiers, personas and targeting decisions belong downstream in S8.
    keep = [
        "rank_2025",
        "country_of_residence",
        "air_entries_2024",
        "air_entries_2025",
        "share_2025_pct",
        "growth_2025_vs_2024_pct",
        "source_url",
        "source_version",
        "scope_note",
    ]
    return out[keep]


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    source = pd.read_csv(REFERENCE)
    out = transform(source)
    out.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(out):,} rows -> {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
