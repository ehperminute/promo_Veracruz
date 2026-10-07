from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
INTERIM = ROOT / "data" / "interim"
OUTDIR = ROOT / "data" / "processed"
DATATUR = INTERIM / "datatur_veracruz_monthly.csv"
INAH = INTERIM / "fact_inah_veracruz_mes.csv"
OUTPUT = OUTDIR / "demand_series.csv"

COLUMNS = [
    "series_id",
    "source_system",
    "date",
    "year",
    "month",
    "geography_level",
    "geography_name",
    "metric",
    "value",
    "unit",
    "measurement_scope",
    "interpretation_note",
    "source_table",
]


def build_datatur(df: pd.DataFrame) -> pd.DataFrame:
    required = {"anio", "mes", "centro", "llegadas_total", "fecha"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"DataTur interim is missing columns: {sorted(missing)}")

    out = pd.DataFrame(
        {
            "series_id": "datatur:center:" + df["centro"].astype(str),
            "source_system": "DataTur",
            "date": df["fecha"].astype(str),
            "year": pd.to_numeric(df["anio"], errors="raise").astype(int),
            "month": pd.to_numeric(df["mes"], errors="raise").astype(int),
            "geography_level": "tourism_center",
            "geography_name": df["centro"].astype(str),
            "metric": "hotel_arrivals_total",
            "value": pd.to_numeric(df["llegadas_total"], errors="raise"),
            "unit": "arrivals",
            "measurement_scope": "hotel_center_arrivals",
            "interpretation_note": (
                "Hotel-center arrivals observed by DataTur. Combined centers such as "
                "Veracruz-Boca del Río are not municipal demand totals."
            ),
            "source_table": "data/interim/datatur_veracruz_monthly.csv",
        }
    )
    return out[COLUMNS]


def build_inah(df: pd.DataFrame) -> pd.DataFrame:
    required = {"anio", "mes", "clave_siinah", "recinto", "visitantes_total", "fecha"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"INAH interim is missing columns: {sorted(missing)}")

    clave = df["clave_siinah"].astype(str).str.strip()
    if clave.eq("").any():
        raise AssertionError("INAH demand series requires non-empty clave_siinah")

    out = pd.DataFrame(
        {
            "series_id": "inah:site:" + clave,
            "source_system": "INAH",
            "date": df["fecha"].astype(str),
            "year": pd.to_numeric(df["anio"], errors="raise").astype(int),
            "month": pd.to_numeric(df["mes"], errors="raise").astype(int),
            "geography_level": "archaeological_site",
            "geography_name": df["recinto"].astype(str),
            "metric": "archaeological_site_visitors_total",
            "value": pd.to_numeric(df["visitantes_total"], errors="raise"),
            "unit": "visits",
            "measurement_scope": "archaeological_site_visits",
            "interpretation_note": (
                "Visits to an INAH archaeological site; not total tourism demand for its municipality."
            ),
            "source_table": "data/interim/fact_inah_veracruz_mes.csv",
        }
    )
    return out[COLUMNS]


def transform(datatur: pd.DataFrame, inah: pd.DataFrame) -> pd.DataFrame:
    out = pd.concat([build_datatur(datatur), build_inah(inah)], ignore_index=True)
    out["value"] = pd.to_numeric(out["value"], errors="raise")

    if out["value"].isna().any():
        raise AssertionError("Demand series contains missing observed values")
    if (out["value"] < 0).any():
        raise AssertionError("Demand series contains negative observed values")
    if not out["month"].between(1, 12).all():
        raise AssertionError("Demand series contains an invalid month")
    if out.duplicated(["series_id", "date", "metric"]).any():
        raise AssertionError("Demand series contains duplicate series-date observations")

    return out.sort_values(["source_system", "series_id", "date"], kind="stable").reset_index(drop=True)


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    datatur = pd.read_csv(DATATUR)
    inah = pd.read_csv(INAH)
    out = transform(datatur, inah)
    out.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(out):,} rows -> {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
