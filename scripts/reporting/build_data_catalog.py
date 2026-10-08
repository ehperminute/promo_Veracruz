from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs" / "DATA_CATALOG.md"

ENTRIES = [
    ("S0 RAW", "data/raw/Base70centros.csv", "SECTUR DataTur frozen monthly hotel-centre source", "Source for DataTur facts; centre coverage is not municipal tourism demand."),
    ("S0 RAW", "data/raw/INAH_visitantes_zonas_general.csv", "INAH archaeological-site visitor time series", "Attraction visits only, not total destination tourism."),
    ("S0 RAW", "data/raw/INAH_zonas_arqueologicas.csv", "INAH archaeological-site catalogue", "Inventory/location evidence, not demand."),
    ("S0 RAW", "data/raw/PIB_Turistico_Estatal_y_Municipal_2018-2022_.zip", "Municipal tourism-GDP workbook archive", "Economic structure/context, not visitor counts."),
    ("S0 RAW", "data/raw/denue_00_48-49_csv.zip", "DENUE transport activities", "Tourist-transport structural proxy."),
    ("S0 RAW", "data/raw/denue_00_56_shp.zip", "DENUE travel/tour/event services", "Service-infrastructure proxy."),
    ("S0 RAW", "data/raw/denue_00_71_csv.zip", "DENUE recreation/culture activities", "Recreation/cultural structural proxy."),
    ("S0 RAW", "data/raw/denue_00_72_1_csv.zip", "DENUE accommodation/food part 1", "Service-infrastructure proxy."),
    ("S0 RAW", "data/raw/denue_00_72_2_csv.zip", "DENUE accommodation/food part 2", "Service-infrastructure proxy."),
    ("S0 RAW", "data/raw/veracruz_productos_2026-10-06.html", "Frozen official Veracruz tourism-product webpage", "Contains 295 mechanically parsed product cards; offer evidence, not tourist behaviour."),
    ("S0 RAW", "data/raw/veracruz_regiones_2026-10-06.html", "Frozen official Veracruz tourism-region page", "Region narrative/reference."),
    ("S0 RAW", "data/raw/veracruz_pueblos_magicos_2026-10-06.html", "Automated Pueblos Mágicos request that returned CAPTCHA", "Preserved acquisition evidence; not used as substantive page content."),
    ("S0 RAW", "data/raw/veracruz_pueblos_magicos_2026-10-06_manual.html", "Browser-saved official Pueblos Mágicos page", "Preferred frozen source for the eight memberships."),
    ("REFERENCE", "data/reference/source_registry.csv", "Source provenance/checksum registry", "Defines frozen/local and fixed-remote source versions."),
    ("REFERENCE", "data/reference/destination_reference.csv", "55-destination curated identity/mapping/theme reference", "Themes are reviewed project-coded profile evidence, not demand."),
    ("REFERENCE", "data/reference/tourism_products.csv", "75-product coursework selection", "Historical coursework scope; not the full official catalogue."),
    ("REFERENCE", "data/reference/denue_activity_groups.csv", "Explicit SCIAN rules for DENUE tourism proxies", "Makes proxy definitions auditable."),
    ("REFERENCE", "data/reference/origin_market_2025_validated.csv", "Validated country-of-residence air-entry extract", "Mexico-wide origin-market context, not Veracruz visitors."),
    ("REFERENCE", "data/reference/destination_profile_enrichment.csv", "Reviewed profile corrections used by S4", "Small provenance-backed corrections only; no measured values inserted."),
    ("REFERENCE", "data/reference/destination_profile_sources.csv", "Research notes for sparse destination profiles", "Documentation/support for gap review and final report."),
    ("S1/S2 INTERIM", "data/interim/source_registry_resolved.csv", "Resolved source verification table", "Confirms exact local raw bytes and fixed remote references."),
    ("S1/S2 INTERIM", "data/interim/veracruz_products_parsed.csv", "All official tourism product cards parsed from frozen HTML", "295 offer transactions used by S4 associations/product counts."),
    ("S1/S2 INTERIM", "data/interim/veracruz_regions_parsed.csv", "Region-navigation municipality mappings", "Mechanically parsed validation/reference."),
    ("S1/S2 INTERIM", "data/interim/veracruz_pueblos_magicos_parsed.csv", "Eight Pueblos Mágicos memberships", "Direct official membership evidence."),
    ("S1/S2 INTERIM", "data/interim/fact_datatur_centro_mes.csv", "Clean DataTur centre-month fact", "Hotel-centre observations."),
    ("S1/S2 INTERIM", "data/interim/datatur_veracruz_monthly.csv", "Veracruz DataTur monthly subset", "324 rows for the three covered centres."),
    ("S1/S2 INTERIM", "data/interim/fact_inah_veracruz_mes.csv", "Clean Veracruz INAH site-month fact", "Archaeological-site visits only."),
    ("S1/S2 INTERIM", "data/interim/mart_infraestructura_municipio_veracruz.csv", "212-municipality DENUE/PIB infrastructure mart", "Structural/economic context."),
    ("S1/S2 INTERIM", "data/interim/tourism_products.csv", "Source-grounded 75-product coursework selection", "Kept for legacy coursework reproducibility."),
    ("S4 INTERIM", "data/interim/destination_profiles_s4.csv", "55-destination S4 profile table", "Adds full 295-card product counts and reviewed profile corrections; no direct demand features used for clustering."),
    ("S3 PROCESSED", "data/processed/destination_master.csv", "Canonical 55-destination integrated table", "Structural/profile evidence plus clearly labelled demand coverage."),
    ("S3 PROCESSED", "data/processed/demand_series.csv", "Standardized DataTur + INAH monthly observations", "Measurement types remain separate; they are not summed."),
    ("S3 PROCESSED", "data/processed/origin_market_opportunity.csv", "25 validated foreign origin-market rows", "Mexico-wide air-entry context for later marketing."),
    ("S4 OUTPUT", "outputs/mining/audit/destination_profile_gaps.csv", "Profile completeness/gap audit", "Flags documentation gaps; no gap is interpreted as low tourism."),
    ("S4 OUTPUT", "outputs/mining/clustering/cluster_diagnostics.csv", "PAM/Gower k=2..20 diagnostics", "Used to compare silhouette and fragmentation."),
    ("S4 OUTPUT", "outputs/mining/clustering/cluster_membership.csv", "Recommended tourism-profile segmentation", "Similarity groups only; not routes or demand classes."),
    ("S4 OUTPUT", "outputs/mining/clustering/cluster_profiles.csv", "Human-readable summaries of the selected clusters", "Structural values describe clusters but do not define observed demand."),
    ("S4 OUTPUT", "outputs/mining/clustering/cluster_medoid_similarity.csv", "Pairwise similarity between cluster medoids", "Shows where selected clusters remain close/overlapping."),
    ("S4 OUTPUT", "outputs/mining/clustering/destination_silhouettes.csv", "Per-destination cluster fit", "Highlights borderline assignments rather than hiding them."),
    ("S4 OUTPUT", "outputs/mining/clustering/feature_sensitivity.csv", "Leave-one-feature-out stability diagnostics", "Shows which profile factors materially affect the partition."),
    ("S4 OUTPUT", "outputs/mining/similarity/undermeasured_anchor_similarity.csv", "Gower structural analog matches", "Analogs only; not proof of unmeasured demand."),
    ("S4 OUTPUT", "outputs/mining/associations/municipality_pair_rules.csv", "Offer co-occurrence association rules from all 295 products", "Not tourist movement/co-visitation."),
    ("S4 OUTPUT", "outputs/mining/candidates/undermeasured_candidates.csv", "Undermeasured structural-evidence priority list", "Not a popularity ranking or route shortlist."),
]


def _shape(path: Path) -> str:
    if not path.exists():
        return "not generated"
    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
        return f"{len(df):,} × {len(df.columns):,}"
    return f"{path.stat().st_size:,} bytes"


def main() -> None:
    lines = [
        "# Data catalog",
        "",
        "This page is a compact map of the datasets used and generated by the Veracruz Tourism Intelligence project. It is intended for both reproducibility and the final report: readers can see where each table comes from, what it means, and what it **does not** mean.",
        "",
        "| Stage / class | Dataset | Current size | Purpose | Interpretation boundary |",
        "|---|---|---:|---|---|",
    ]
    for stage, rel, purpose, boundary in ENTRIES:
        path = ROOT / rel
        lines.append(
            f"| {stage} | `{rel}` | {_shape(path)} | {purpose} | {boundary} |"
        )
    lines += [
        "",
        "## Why the 75-product and 295-product tables both exist",
        "",
        "The official frozen Veracruz product page contains **295 product cards**. The older `data/reference/tourism_products.csv` is only a **75-product coursework selection** retained for reproducibility of earlier exercises. S4 now uses the full parsed 295-card table for product-count and association analyses; it does not pretend the 75-row selection is the complete catalogue.",
        "",
        "## Reporting use",
        "",
        "For the final report, this catalog can be condensed into a one-page data-flow/table: source → cleaned/interim table → canonical processed table → analysis output. Keeping this full version in the repository makes the project easier to audit without forcing the report itself to list every implementation detail.",
        "",
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote -> {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
