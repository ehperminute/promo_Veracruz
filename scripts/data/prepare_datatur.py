from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "Base70centros.csv"
OUTDIR = ROOT / "data" / "interim"
OUT_ALL = OUTDIR / "fact_datatur_centro_mes.csv"
OUT_VERACRUZ = OUTDIR / "datatur_veracruz_monthly.csv"

VERACRUZ_CENTERS = {"Coatzacoalcos", "Veracruz-Boca del Río", "Xalapa"}

REQUIRED_COLUMNS = {
    "anio",
    "mes",
    "tipo_centro",
    "subtipo_centro",
    "centro",
    "categoria",
    "cuartos_disponibles",
    "cuartos_ocupados_no_residentes",
    "cuartos_ocupados_residentes",
    "llegada_turistas_no_residentes",
    "llegada_turistas_residentes",
    "turistas_noche_no_residentes",
    "turistas_noche_residentes",
}

RAW_NUMERIC = [
    "cuartos_disponibles",
    "cuartos_ocupados_no_residentes",
    "cuartos_ocupados_residentes",
    "llegada_turistas_no_residentes",
    "llegada_turistas_residentes",
    "turistas_noche_no_residentes",
    "turistas_noche_residentes",
]


def load_raw(path: Path = RAW) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t", encoding="utf-8")
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"DataTur raw file is missing columns: {sorted(missing)}")
    return df


def transform(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    work = df.copy()

    work["anio"] = pd.to_numeric(work["anio"], errors="raise").astype(int)
    work["mes"] = pd.to_numeric(work["mes"], errors="raise").astype(int)
    if not work["mes"].between(1, 12).all():
        raise ValueError("DataTur contains month values outside 1..12")

    for col in RAW_NUMERIC:
        numeric = pd.to_numeric(work[col], errors="coerce")
        invalid = numeric.isna() & work[col].notna()
        if invalid.any():
            raise ValueError(f"DataTur contains non-numeric values in {col}")
        work[col] = numeric.fillna(0)

    work["cuartos_ocupados"] = (
        work["cuartos_ocupados_no_residentes"] + work["cuartos_ocupados_residentes"]
    )
    work["llegadas_total"] = (
        work["llegada_turistas_no_residentes"] + work["llegada_turistas_residentes"]
    )
    work["turistas_noche_total"] = (
        work["turistas_noche_no_residentes"] + work["turistas_noche_residentes"]
    )

    group_cols = ["anio", "mes", "centro", "tipo_centro", "subtipo_centro"]
    sum_cols = [
        "cuartos_disponibles",
        "cuartos_ocupados",
        "llegadas_total",
        "turistas_noche_total",
    ]

    fact = work.groupby(group_cols, as_index=False, dropna=False)[sum_cols].sum()
    for col in sum_cols:
        fact[col] = fact[col].round().astype("int64")

    fact["ocupacion_pct"] = np.where(
        fact["cuartos_disponibles"] > 0,
        100.0 * fact["cuartos_ocupados"] / fact["cuartos_disponibles"],
        np.nan,
    )
    fact["fecha"] = pd.to_datetime(
        {"year": fact["anio"], "month": fact["mes"], "day": 1}
    ).dt.strftime("%Y-%m-%d")

    fact = fact[
        [
            "anio",
            "mes",
            "centro",
            "tipo_centro",
            "subtipo_centro",
            "cuartos_disponibles",
            "cuartos_ocupados",
            "llegadas_total",
            "turistas_noche_total",
            "ocupacion_pct",
            "fecha",
        ]
    ].sort_values(["anio", "mes", "centro"], kind="stable")

    if fact.duplicated(["anio", "mes", "centro"]).any():
        raise AssertionError("DataTur aggregation did not produce unique center-month rows")

    veracruz = fact[fact["centro"].isin(VERACRUZ_CENTERS)].copy()
    missing_centers = VERACRUZ_CENTERS - set(veracruz["centro"].unique())
    if missing_centers:
        raise AssertionError(f"Expected Veracruz DataTur centers are missing: {missing_centers}")

    return fact.reset_index(drop=True), veracruz.reset_index(drop=True)


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    fact, veracruz = transform(load_raw())
    fact.to_csv(OUT_ALL, index=False)
    veracruz.to_csv(OUT_VERACRUZ, index=False)
    print(f"Wrote {len(fact):,} rows -> {OUT_ALL.relative_to(ROOT)}")
    print(f"Wrote {len(veracruz):,} rows -> {OUT_VERACRUZ.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
