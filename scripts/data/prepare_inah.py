from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "INAH_visitantes_zonas_general.csv"
OUTDIR = ROOT / "data" / "interim"
OUTPUT = OUTDIR / "fact_inah_veracruz_mes.csv"

MONTHS = [
    (1, "enero"),
    (2, "febrero"),
    (3, "marzo"),
    (4, "abril"),
    (5, "mayo"),
    (6, "junio"),
    (7, "julio"),
    (8, "agosto"),
    (9, "septiembre"),
    (10, "octubre"),
    (11, "noviembre"),
    (12, "diciembre"),
]

BASE_COLUMNS = {"anio", "estado", "clave_siinah", "recinto"}


def load_raw(path: Path = RAW) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    required = set(BASE_COLUMNS)
    for _, month in MONTHS:
        required.update({f"{month}_nac", f"{month}_ext"})
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"INAH raw file is missing columns: {sorted(missing)}")
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    work = df[df["estado"].astype(str).str.strip().eq("Veracruz")].copy()
    if work.empty:
        raise AssertionError("No Veracruz records found in INAH visitor file")

    rows: list[pd.DataFrame] = []
    for month_num, month_name in MONTHS:
        nac_col = f"{month_name}_nac"
        ext_col = f"{month_name}_ext"
        part = work[["anio", "clave_siinah", "recinto", nac_col, ext_col]].copy()
        part["visitantes_nacionales"] = pd.to_numeric(part[nac_col], errors="coerce")
        part["visitantes_extranjeros"] = pd.to_numeric(part[ext_col], errors="coerce")

        # Future/unreported months are blank in the source; do not turn them into zero observations.
        part = part[
            part["visitantes_nacionales"].notna()
            | part["visitantes_extranjeros"].notna()
        ].copy()
        part["visitantes_nacionales"] = part["visitantes_nacionales"].fillna(0.0)
        part["visitantes_extranjeros"] = part["visitantes_extranjeros"].fillna(0.0)
        part["mes"] = month_num
        part["visitantes_total"] = (
            part["visitantes_nacionales"] + part["visitantes_extranjeros"]
        )
        rows.append(
            part[
                [
                    "anio",
                    "mes",
                    "clave_siinah",
                    "recinto",
                    "visitantes_nacionales",
                    "visitantes_extranjeros",
                    "visitantes_total",
                ]
            ]
        )

    out = pd.concat(rows, ignore_index=True)
    out["anio"] = pd.to_numeric(out["anio"], errors="raise").astype(int)
    out["mes"] = out["mes"].astype(int)
    out["fecha"] = pd.to_datetime(
        {"year": out["anio"], "month": out["mes"], "day": 1}
    ).dt.strftime("%Y-%m-%d")

    if (out[["visitantes_nacionales", "visitantes_extranjeros", "visitantes_total"]] < 0).any().any():
        raise AssertionError("INAH visitor counts must be non-negative")
    if out.duplicated(["anio", "mes", "clave_siinah", "recinto"]).any():
        raise AssertionError("INAH transformation produced duplicate site-month rows")

    return out.sort_values(["anio", "mes", "recinto"], kind="stable").reset_index(drop=True)


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    out = transform(load_raw())
    out.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(out):,} rows -> {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
