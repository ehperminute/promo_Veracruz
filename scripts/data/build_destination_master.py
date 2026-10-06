from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "data" / "reference" / "destination_reference.csv"
INAH = ROOT / "data" / "interim" / "fact_inah_veracruz_mes.csv"
DATATUR = ROOT / "data" / "interim" / "datatur_veracruz_monthly.csv"
INFRA = ROOT / "data" / "interim" / "mart_infraestructura_municipio_veracruz.csv"
OUTDIR = ROOT / "data" / "processed"
OUTPUT = OUTDIR / "destination_master.csv"

THEME_COLUMNS = [
    "theme_beach_coast",
    "theme_nature",
    "theme_culture_history",
    "theme_archaeology",
    "theme_adventure",
    "theme_gastronomy_coffee",
    "theme_wellness_spiritual",
    "theme_urban_services",
]

SOURCE_TOURISM_OFFER = "https://veracruz.mx/productos.php"
SOURCE_REGION = "https://www.veracruz.gob.mx/turismo/regiones-turisticas/"
SOURCE_PUEBLO = "https://www.veracruz.gob.mx/turismo/pueblos-magicos/"
SOURCE_INAH_VISITORS = "https://datos.inah.gob.mx/datos-abiertos/visitantes-zonas-arqueologicas"
SOURCE_INAH_CATALOG = "https://datos.inah.gob.mx/datos-abiertos/zonas-arqueologicas"
SOURCE_DENUE = "https://www.inegi.org.mx/app/descarga/?ti=6"
SOURCE_PIB = "https://datatur.sectur.gob.mx/SitePages/pibturisticoestatalmunicipal.aspx"
SOURCE_DATATUR = "https://www.datatur.sectur.gob.mx/SitePages/hoteleria.aspx"


def _split_pipe(value: object) -> list[str]:
    if pd.isna(value):
        return []
    return [part.strip() for part in str(value).split("|") if part.strip()]


def _inah_summary(reference: pd.DataFrame, fact: pd.DataFrame) -> pd.DataFrame:
    fact_2025 = fact[fact["anio"].eq(2025)].copy()
    known_sites = set(fact["recinto"].astype(str))
    rows = []

    for row in reference.itertuples(index=False):
        sites = _split_pipe(getattr(row, "inah_series_sites"))
        missing_sites = set(sites) - known_sites
        if missing_sites:
            raise AssertionError(
                f"{row.destination}: INAH series mapping not found in raw fact: {sorted(missing_sites)}"
            )

        selected = fact_2025[fact_2025["recinto"].isin(sites)] if sites else fact_2025.iloc[0:0]
        total = float(selected["visitantes_total"].sum()) if sites else np.nan
        foreign = float(selected["visitantes_extranjeros"].sum()) if sites else np.nan
        share = (foreign / total) if sites and total > 0 else (0.0 if sites else np.nan)

        rows.append(
            {
                "destination": row.destination,
                "inah_inventory_sites_n": len(_split_pipe(getattr(row, "inah_inventory_sites"))),
                "inah_series_available": int(bool(sites)),
                "inah_visitors_2025": total,
                "inah_foreign_share_2025": share,
            }
        )
    return pd.DataFrame(rows)


def _datatur_summary(reference: pd.DataFrame, monthly: pd.DataFrame) -> pd.DataFrame:
    current = monthly[monthly["anio"].eq(2024)].copy()
    known_centers = set(monthly["centro"].astype(str))
    rows = []

    for row in reference.itertuples(index=False):
        center = getattr(row, "datatur_center")
        if pd.isna(center) or not str(center).strip():
            rows.append(
                {
                    "destination": row.destination,
                    "datatur_coverage": 0,
                    "datatur_arrivals_2024": np.nan,
                    "datatur_occupancy_2024_pct": np.nan,
                }
            )
            continue

        center = str(center).strip()
        if center not in known_centers:
            raise AssertionError(f"{row.destination}: DataTur center not found: {center}")
        selected = current[current["centro"].eq(center)]
        arrivals = int(selected["llegadas_total"].sum())
        available = int(selected["cuartos_disponibles"].sum())
        occupied = int(selected["cuartos_ocupados"].sum())
        occupancy = 100.0 * occupied / available if available else np.nan
        rows.append(
            {
                "destination": row.destination,
                "datatur_coverage": 1,
                "datatur_arrivals_2024": arrivals,
                "datatur_occupancy_2024_pct": occupancy,
            }
        )
    return pd.DataFrame(rows)


def build_master(
    reference: pd.DataFrame,
    inah: pd.DataFrame,
    datatur: pd.DataFrame,
    infra: pd.DataFrame,
) -> pd.DataFrame:
    if not reference["destination"].is_unique:
        raise AssertionError("Destination reference must contain unique destinations")

    for col in ["pueblo_magico", "oferta_turistica_oficial_web", *THEME_COLUMNS]:
        vals = set(pd.to_numeric(reference[col], errors="raise").astype(int).unique())
        if not vals.issubset({0, 1}):
            raise AssertionError(f"Reference column {col} is not binary: {vals}")

    out = reference.copy()
    out = out.merge(_inah_summary(reference, inah), on="destination", validate="one_to_one")
    out = out.merge(_datatur_summary(reference, datatur), on="destination", validate="one_to_one")

    infra_cols = [
        "clave_municipio",
        "municipio",
        "alojamiento_n",
        "alimentos_bebidas_n",
        "recreacion_turistica_proxy_n",
        "agencias_tours_eventos_n",
        "transporte_turistico_n",
        "pib_turistico_2022",
        "participacion_turismo_pct",
    ]
    out = out.merge(
        infra[infra_cols],
        on="clave_municipio",
        how="left",
        validate="many_to_one",
        suffixes=("", "_infra"),
        indicator="_infra_merge",
    )
    out["denue_available"] = out["_infra_merge"].eq("both").astype(int)
    out = out.drop(columns=["_infra_merge", "municipio_infra"])

    out = out.rename(
        columns={
            "alojamiento_n": "lodging_establishments",
            "alimentos_bebidas_n": "food_beverage_establishments",
            "recreacion_turistica_proxy_n": "recreation_tourism_proxy",
            "agencias_tours_eventos_n": "agencies_tours_events",
            "transporte_turistico_n": "tourist_transport_proxy",
            "pib_turistico_2022": "tourism_gdp_2022_mxn2018",
            "participacion_turismo_pct": "tourism_share_proxy_2022",
        }
    )

    count_cols = [
        "lodging_establishments",
        "food_beverage_establishments",
        "recreation_tourism_proxy",
        "agencies_tours_events",
        "tourist_transport_proxy",
    ]
    out[count_cols] = out[count_cols].fillna(0).astype(int)

    has_inah = out["inah_series_available"].eq(1)
    has_datatur = out["datatur_coverage"].eq(1)
    out["demand_evidence"] = np.select(
        [has_inah, has_datatur],
        ["INAH attraction series", "DataTur hotel-center series"],
        default="No direct demand series in current project data",
    )
    out["model_role_v1"] = np.where(
        has_inah | has_datatur,
        "Observed anchor / training evidence",
        "Undermeasured analog target",
    )

    pib_available = out["tourism_gdp_2022_mxn2018"].notna().astype(int)
    out["coverage_dimensions_n"] = (
        out["oferta_turistica_oficial_web"].astype(int)
        + out["inah_series_available"].astype(int)
        + out["datatur_coverage"].astype(int)
        + out["denue_available"].astype(int)
        + pib_available
    )

    out["source_tourism_offer"] = SOURCE_TOURISM_OFFER
    out["source_region"] = SOURCE_REGION
    out["source_pueblo_magico"] = np.where(out["pueblo_magico"].eq(1), SOURCE_PUEBLO, "")
    out["source_inah_visitors"] = np.where(has_inah, SOURCE_INAH_VISITORS, "")
    out["source_inah_location"] = np.where(
        out["inah_inventory_sites_n"].gt(0), SOURCE_INAH_CATALOG, ""
    )
    out["source_denue"] = np.where(out["denue_available"].eq(1), SOURCE_DENUE, "")
    out["source_tourism_gdp"] = np.where(pib_available.eq(1), SOURCE_PIB, "")
    out["source_datatur"] = np.where(has_datatur, SOURCE_DATATUR, "")

    columns = [
        "destination",
        "municipio",
        "clave_municipio",
        "region_turistica_preliminar",
        "pueblo_magico",
        "oferta_turistica_oficial_web",
        "productos_en_extracto_local_n",
        "productos_ejemplo",
        "tourism_tags",
        *THEME_COLUMNS,
        "inah_inventory_sites_n",
        "inah_inventory_sites",
        "inah_series_available",
        "inah_series_sites",
        "inah_visitors_2025",
        "inah_foreign_share_2025",
        "datatur_coverage",
        "datatur_center",
        "datatur_scope_note",
        "datatur_arrivals_2024",
        "datatur_occupancy_2024_pct",
        "denue_available",
        *count_cols,
        "tourism_gdp_2022_mxn2018",
        "tourism_share_proxy_2022",
        "demand_evidence",
        "model_role_v1",
        "coverage_dimensions_n",
        "source_tourism_offer",
        "source_region",
        "source_pueblo_magico",
        "source_inah_visitors",
        "source_inah_location",
        "source_denue",
        "source_tourism_gdp",
        "source_datatur",
        "curation_version",
    ]
    out = out[columns].sort_values("destination", kind="stable").reset_index(drop=True)

    if len(out) != len(reference) or not out["destination"].is_unique:
        raise AssertionError("Destination master changed destination grain")
    return out


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    master = build_master(
        pd.read_csv(REFERENCE),
        pd.read_csv(INAH),
        pd.read_csv(DATATUR),
        pd.read_csv(INFRA),
    )
    master.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(master):,} rows -> {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
