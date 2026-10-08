from __future__ import annotations

from pathlib import Path
import math
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[2] if Path(__file__).resolve().parent.name == 'reporting' else Path.cwd()

OUT_EN = ROOT / 'docs' / 'DATA_SUMMARY.md'
OUT_ES = ROOT / 'docs' / 'RESUMEN_DATOS.md'

RAW_ASSETS = [
    ('data/raw/Base70centros.csv', 'SECTUR DataTur raw monthly hotel-centre source.', 'Fuente bruta mensual de centros hoteleros de SECTUR DataTur.', 'Hotel-centre coverage is not equivalent to municipal tourism demand.', 'La cobertura de centros hoteleros no equivale a la demanda turística municipal.'),
    ('data/raw/INAH_visitantes_zonas_general.csv', 'INAH raw archaeological-site visitor time series.', 'Serie bruta de visitantes a zonas arqueológicas del INAH.', 'Counts are attraction visits, not total tourism in the municipality.', 'Los conteos son visitas a atractivos, no turismo total del municipio.'),
    ('data/raw/INAH_zonas_arqueologicas.csv', 'INAH archaeological-site catalogue and location reference.', 'Catálogo y referencia de ubicación de zonas arqueológicas del INAH.', 'Inventory/location evidence, not demand.', 'Evidencia de inventario/ubicación, no demanda.'),
    ('data/raw/PIB_Turistico_Estatal_y_Municipal_2018-2022_.zip', 'Municipal tourism-GDP workbook archive from DataTur.', 'Archivo de libros de PIB turístico municipal de DataTur.', 'Economic structure/context, not visitor counts.', 'Contexto/estructura económica, no conteo de visitantes.'),
    ('data/raw/denue_00_48-49_csv.zip', 'INEGI DENUE transport activities.', 'Actividades de transporte de INEGI DENUE.', 'Used as a structural proxy only.', 'Se usa únicamente como proxy estructural.'),
    ('data/raw/denue_00_56_shp.zip', 'INEGI DENUE travel, tour and event services.', 'Servicios de viajes, tours y eventos de INEGI DENUE.', 'Used as a structural proxy only.', 'Se usa únicamente como proxy estructural.'),
    ('data/raw/denue_00_71_csv.zip', 'INEGI DENUE recreation and cultural activities.', 'Actividades recreativas y culturales de INEGI DENUE.', 'Used as a structural proxy only.', 'Se usa únicamente como proxy estructural.'),
    ('data/raw/denue_00_72_1_csv.zip', 'INEGI DENUE accommodation and food services, part 1.', 'Servicios de alojamiento y alimentos de INEGI DENUE, parte 1.', 'Used as a structural proxy only.', 'Se usa únicamente como proxy estructural.'),
    ('data/raw/denue_00_72_2_csv.zip', 'INEGI DENUE accommodation and food services, part 2.', 'Servicios de alojamiento y alimentos de INEGI DENUE, parte 2.', 'Used as a structural proxy only.', 'Se usa únicamente como proxy estructural.'),
    ('data/raw/veracruz_productos_2026-10-06.html', 'Frozen official Veracruz tourism-products webpage.', 'Copia congelada de la página oficial de productos turísticos de Veracruz.', 'Offer evidence; it does not represent tourist behaviour.', 'Evidencia de oferta; no representa el comportamiento de turistas.'),
    ('data/raw/veracruz_regiones_2026-10-06.html', 'Frozen official Veracruz tourism-regions webpage.', 'Copia congelada de la página oficial de regiones turísticas de Veracruz.', 'Reference for official regional framing.', 'Referencia para la regionalización turística oficial.'),
    ('data/raw/veracruz_pueblos_magicos_2026-10-06.html', 'Automated Pueblos Mágicos request preserved as acquisition evidence.', 'Solicitud automatizada de Pueblos Mágicos conservada como evidencia de adquisición.', 'Returned CAPTCHA; not used as substantive content.', 'Devolvió CAPTCHA; no se usa como contenido sustantivo.'),
    ('data/raw/veracruz_pueblos_magicos_2026-10-06_manual.html', 'Browser-saved official Pueblos Mágicos webpage.', 'Página oficial de Pueblos Mágicos guardada manualmente desde el navegador.', 'Preferred frozen evidence for membership.', 'Evidencia congelada preferida para la pertenencia a Pueblos Mágicos.'),
]

TABLES = [
    ('REFERENCE', 'data/reference/source_registry.csv', 'Source provenance and checksum registry.', 'Registro de procedencia y checksum de las fuentes.', 'Defines frozen/local and fixed-remote source versions.', 'Define versiones congeladas/locales y referencias remotas fijas.'),
    ('REFERENCE', 'data/reference/destination_reference.csv', 'Curated identity, mapping and tourism-theme reference for the 55 Veracruz destinations.', 'Referencia curada de identidad, mapeo y temas turísticos para los 55 destinos de Veracruz.', 'Themes are project-coded profile evidence, not measured demand.', 'Los temas son evidencia de perfil codificada por el proyecto, no demanda medida.'),
    ('REFERENCE', 'data/reference/tourism_products.csv', 'Historical 75-product coursework selection.', 'Selección histórica de 75 productos usada en actividades previas.', 'Retained for reproducibility; it is not the complete official catalogue.', 'Se conserva para reproducibilidad; no es el catálogo oficial completo.'),
    ('REFERENCE', 'data/reference/denue_activity_groups.csv', 'Explicit SCIAN rules used to build DENUE tourism-service proxies.', 'Reglas SCIAN explícitas usadas para construir proxies turísticos con DENUE.', 'Proxy definitions are auditable but are not carrying-capacity measures.', 'Las definiciones son auditables, pero no miden capacidad de carga.'),
    ('REFERENCE', 'data/reference/origin_market_2025_validated.csv', 'Validated country-of-residence air-entry evidence for 2025.', 'Evidencia validada de entradas aéreas por país de residencia para 2025.', 'Mexico-wide context; not Veracruz-specific visitor counts.', 'Contexto nacional; no son visitantes específicos de Veracruz.'),
    ('REFERENCE', 'data/reference/destination_profile_enrichment.csv', 'Small set of reviewed profile corrections used by S4.', 'Pequeño conjunto de correcciones de perfil revisadas para S4.', 'Corrections are provenance-backed and do not add invented measurements.', 'Las correcciones tienen procedencia documentada y no agregan mediciones inventadas.'),
    ('REFERENCE', 'data/reference/destination_profile_sources.csv', 'Research notes and sources for sparse destination profiles.', 'Notas y fuentes de investigación para perfiles de destino con poca información.', 'Documentation/support for gap review.', 'Documentación de apoyo para revisar vacíos de información.'),

    ('S1/S2 INTERIM', 'data/interim/source_registry_resolved.csv', 'Resolved verification table for the project sources.', 'Tabla resuelta de verificación de las fuentes del proyecto.', 'Checks exact local bytes and fixed remote references.', 'Verifica archivos locales exactos y referencias remotas fijas.'),
    ('S1/S2 INTERIM', 'data/interim/veracruz_products_parsed.csv', 'All official Veracruz tourism-product cards mechanically parsed from frozen HTML.', 'Todas las fichas oficiales de productos turísticos de Veracruz extraídas mecánicamente del HTML congelado.', 'Offer transactions for product counts and association mining; not tourist co-visitation.', 'Transacciones de oferta para conteos y asociaciones; no co-visita turística.'),
    ('S1/S2 INTERIM', 'data/interim/veracruz_regions_parsed.csv', 'Parsed region-navigation and municipality mappings.', 'Mapeos extraídos de navegación regional y municipios.', 'Used as reference/validation.', 'Se usa como referencia/validación.'),
    ('S1/S2 INTERIM', 'data/interim/veracruz_pueblos_magicos_parsed.csv', 'Parsed official Pueblos Mágicos memberships.', 'Pertenencias oficiales a Pueblos Mágicos extraídas de la fuente.', 'Direct membership evidence.', 'Evidencia directa de pertenencia.'),
    ('S1/S2 INTERIM', 'data/interim/fact_datatur_centro_mes.csv', 'Clean DataTur centre-month fact table.', 'Tabla de hechos limpia de DataTur por centro y mes.', 'One row is a hotel-centre/month observation; not a municipality-wide tourism total.', 'Cada fila es una observación centro-hotelero/mes; no un total turístico municipal.'),
    ('S1/S2 INTERIM', 'data/interim/datatur_veracruz_monthly.csv', 'Veracruz-only monthly DataTur subset.', 'Subconjunto mensual de DataTur correspondiente a Veracruz.', 'Covers only the DataTur centres available in the project.', 'Cubre únicamente los centros DataTur disponibles en el proyecto.'),
    ('S1/S2 INTERIM', 'data/interim/fact_inah_veracruz_mes.csv', 'Clean Veracruz INAH archaeological-site/month fact table.', 'Tabla de hechos limpia del INAH para Veracruz por zona arqueológica y mes.', 'Site visits remain attraction-level demand evidence.', 'Las visitas se mantienen como evidencia de demanda a nivel de atractivo.'),
    ('S1/S2 INTERIM', 'data/interim/mart_infraestructura_municipio_veracruz.csv', 'Municipality-level DENUE and tourism-GDP infrastructure mart.', 'Mart municipal de infraestructura DENUE y PIB turístico.', 'Structural/economic context, not observed tourist demand.', 'Contexto estructural/económico, no demanda turística observada.'),
    ('S1/S2 INTERIM', 'data/interim/tourism_products.csv', 'Source-grounded 75-product coursework table.', 'Tabla de 75 productos respaldada por fuentes para actividades previas.', 'Legacy scope kept for reproducibility.', 'Alcance histórico conservado para reproducibilidad.'),
    ('S4 INTERIM', 'data/interim/destination_profiles_s4.csv', 'S4 destination-profile table used for local clustering and similarity.', 'Tabla de perfiles de destino de S4 usada para agrupación y similitud local.', 'Clustering uses tourism-character features; direct demand is not used to form the clusters.', 'La agrupación usa características del perfil turístico; la demanda directa no forma los clústeres.'),

    ('S3 PROCESSED', 'data/processed/destination_master.csv', 'Canonical integrated table for the 55 Veracruz destinations.', 'Tabla integrada canónica de los 55 destinos de Veracruz.', 'Combines profile, structure and clearly labelled demand coverage without treating missing coverage as low demand.', 'Integra perfil, estructura y cobertura de demanda claramente etiquetada sin interpretar ausencia de cobertura como baja demanda.'),
    ('S3 PROCESSED', 'data/processed/demand_series.csv', 'Standardized monthly observed-demand table combining DataTur and INAH records.', 'Tabla mensual estandarizada de demanda observada que reúne registros de DataTur e INAH.', 'Measurement types remain separate and are never added together.', 'Los tipos de medición permanecen separados y nunca se suman entre sí.'),
    ('S3 PROCESSED', 'data/processed/origin_market_opportunity.csv', 'Validated foreign origin-market evidence prepared for later marketing analysis.', 'Evidencia validada de mercados internacionales de origen preparada para el análisis de marketing.', 'Mexico-wide air-entry context; not direct Veracruz visitor evidence.', 'Contexto nacional de entradas aéreas; no evidencia directa de visitantes a Veracruz.'),

    ('S4 OUTPUT', 'outputs/mining/audit/destination_profile_gaps.csv', 'Completeness and documentation-gap audit for destination profiles.', 'Auditoría de integridad y vacíos documentales de los perfiles de destino.', 'A gap means missing evidence/documentation, not low tourism.', 'Un vacío significa falta de evidencia/documentación, no bajo turismo.'),
    ('S4 OUTPUT', 'outputs/mining/clustering/cluster_diagnostics.csv', 'PAM/Gower diagnostics across candidate values of k.', 'Diagnósticos PAM/Gower para distintos valores candidatos de k.', 'Used to compare fit and fragmentation, not to rank destinations.', 'Se usa para comparar ajuste y fragmentación, no para clasificar destinos por importancia.'),
    ('S4 OUTPUT', 'outputs/mining/clustering/cluster_membership.csv', 'Recommended local tourism-character cluster membership.', 'Pertenencia recomendada a clústeres locales por carácter turístico.', 'Clusters are similarity groups, not routes or demand classes.', 'Los clústeres son grupos de similitud, no rutas ni clases de demanda.'),
    ('S4 OUTPUT', 'outputs/mining/clustering/cluster_profiles.csv', 'Human-readable summaries of the selected local clusters.', 'Resúmenes legibles de los clústeres locales seleccionados.', 'Profile summaries describe similarity structure, not observed popularity.', 'Los perfiles describen estructura de similitud, no popularidad observada.'),
    ('S4 OUTPUT', 'outputs/mining/clustering/cluster_medoid_similarity.csv', 'Pairwise similarity between the selected cluster medoids.', 'Similitud por pares entre los medoides de los clústeres seleccionados.', 'Used to inspect separation/overlap between groups.', 'Se usa para revisar separación/solapamiento entre grupos.'),
    ('S4 OUTPUT', 'outputs/mining/clustering/destination_silhouettes.csv', 'Per-destination silhouette diagnostics for the selected clustering.', 'Diagnóstico de silueta por destino para la agrupación seleccionada.', 'Negative/borderline values indicate ambiguity, not invalid data.', 'Valores negativos o limítrofes indican ambigüedad, no datos inválidos.'),
    ('S4 OUTPUT', 'outputs/mining/clustering/feature_sensitivity.csv', 'Leave-one-feature-out clustering sensitivity analysis.', 'Análisis de sensibilidad de clústeres retirando una variable a la vez.', 'Shows which profile variables materially affect the partition.', 'Muestra qué variables de perfil afectan materialmente la partición.'),
    ('S4 OUTPUT', 'outputs/mining/similarity/undermeasured_anchor_similarity.csv', 'Structural analogue matches between undermeasured destinations and observed anchors.', 'Coincidencias de análogos estructurales entre destinos submedidos y destinos ancla observados.', 'Similarity is not proof of unmeasured demand.', 'La similitud no prueba demanda no medida.'),
    ('S4 OUTPUT', 'outputs/mining/associations/municipality_pair_rules.csv', 'Association rules based on municipality co-occurrence in official tourism products.', 'Reglas de asociación basadas en coaparición de municipios en productos turísticos oficiales.', 'Offer co-occurrence is not tourist movement or co-visitation.', 'La coaparición en la oferta no equivale a movimiento o co-visita de turistas.'),
    ('S4 OUTPUT', 'outputs/mining/candidates/undermeasured_candidates.csv', 'Priority list of structurally evidenced but undermeasured destinations.', 'Lista priorizada de destinos con evidencia estructural pero medición insuficiente.', 'Not a popularity ranking or final route shortlist.', 'No es un ranking de popularidad ni una lista final de rutas.'),
]

KNOWN_SHAPES = {
    'data/raw/Base70centros.csv': '31,147 × 1',
    'data/raw/INAH_visitantes_zonas_general.csv': '5,097 × 28',
    'data/raw/INAH_zonas_arqueologicas.csv': '195 × 9',
    'data/reference/source_registry.csv': '14 × 9',
    'data/reference/destination_reference.csv': '55 × 28',
    'data/reference/tourism_products.csv': '75 × 5',
    'data/reference/denue_activity_groups.csv': '21 × 4',
    'data/reference/origin_market_2025_validated.csv': '25 × 9',
    'data/reference/destination_profile_enrichment.csv': '6 × 6',
    'data/reference/destination_profile_sources.csv': '13 × 5',
    'data/interim/source_registry_resolved.csv': '14 × 12',
    'data/interim/veracruz_products_parsed.csv': '295 × 5',
    'data/interim/veracruz_regions_parsed.csv': '31 × 6',
    'data/interim/veracruz_pueblos_magicos_parsed.csv': '8 × 5',
    'data/interim/fact_datatur_centro_mes.csv': '6,900 × 11',
    'data/interim/datatur_veracruz_monthly.csv': '324 × 11',
    'data/interim/fact_inah_veracruz_mes.csv': '4,048 × 8',
    'data/interim/mart_infraestructura_municipio_veracruz.csv': '212 × 11',
    'data/interim/tourism_products.csv': '75 × 8',
    'data/interim/destination_profiles_s4.csv': '55 × 50',
    'data/processed/destination_master.csv': '55 × 48',
    'data/processed/demand_series.csv': '4,372 × 13',
    'data/processed/origin_market_opportunity.csv': '25 × 9',
    'outputs/mining/audit/destination_profile_gaps.csv': '55 × 16',
    'outputs/mining/clustering/cluster_diagnostics.csv': '19 × 9',
    'outputs/mining/clustering/cluster_membership.csv': '55 × 7',
    'outputs/mining/clustering/cluster_profiles.csv': '12 × 24',
    'outputs/mining/clustering/cluster_medoid_similarity.csv': '66 × 6',
    'outputs/mining/clustering/destination_silhouettes.csv': '55 × 5',
    'outputs/mining/clustering/feature_sensitivity.csv': '9 × 4',
    'outputs/mining/similarity/undermeasured_anchor_similarity.csv': '126 × 8',
    'outputs/mining/associations/municipality_pair_rules.csv': '22 × 10',
    'outputs/mining/candidates/undermeasured_candidates.csv': '42 × 17',
}

PIPELINE_EN = '''```text
S0 raw/reference sources
        ↓
S1 ingestion and cleaning
        ↓
S2 curated interim tables
        ↓
S3 integrated analysis tables
        ↓
S4 mining: clusters, similarity, associations, candidates
        ↓
S5–S8: forecasting, uncertainty, planning and marketing (added as completed)
        ↓
S9 final site / submissions / portfolio
```'''

PIPELINE_ES = '''```text
S0 fuentes brutas/de referencia
        ↓
S1 ingestión y limpieza
        ↓
S2 tablas intermedias curadas
        ↓
S3 tablas integradas para análisis
        ↓
S4 minería: clústeres, similitud, asociaciones y candidatos
        ↓
S5–S8: pronóstico, incertidumbre, planeación y marketing (se agregan al completarse)
        ↓
S9 sitio final / entregas / portafolio
```'''

STREAMS_EN = '''- **DataTur:** raw hotel-centre source → `fact_datatur_centro_mes.csv` → `datatur_veracruz_monthly.csv` → `demand_series.csv` and demand-coverage fields in `destination_master.csv`.
- **INAH:** raw site catalogue + visitor series → `fact_inah_veracruz_mes.csv` → `demand_series.csv` and archaeological-demand evidence in `destination_master.csv`.
- **DENUE + tourism GDP:** raw economic/establishment files → `mart_infraestructura_municipio_veracruz.csv` → structural fields in `destination_master.csv` → S4 similarity/candidate analysis.
- **Official Veracruz tourism portal:** frozen HTML → parsed products/regions/Pueblos Mágicos → `destination_master.csv` and `destination_profiles_s4.csv` → S4 associations and clustering.
- **Origin markets:** validated 2025 country evidence → `origin_market_opportunity.csv` → later S8 marketing analysis.'''

STREAMS_ES = '''- **DataTur:** fuente bruta de centros hoteleros → `fact_datatur_centro_mes.csv` → `datatur_veracruz_monthly.csv` → `demand_series.csv` y campos de cobertura de demanda en `destination_master.csv`.
- **INAH:** catálogo y serie bruta de visitantes → `fact_inah_veracruz_mes.csv` → `demand_series.csv` y evidencia de demanda arqueológica en `destination_master.csv`.
- **DENUE + PIB turístico:** archivos económicos/de establecimientos → `mart_infraestructura_municipio_veracruz.csv` → variables estructurales en `destination_master.csv` → análisis S4 de similitud/candidatos.
- **Portal turístico oficial de Veracruz:** HTML congelado → productos/regiones/Pueblos Mágicos extraídos → `destination_master.csv` y `destination_profiles_s4.csv` → asociaciones y clústeres S4.
- **Mercados de origen:** evidencia validada por país para 2025 → `origin_market_opportunity.csv` → análisis posterior de marketing en S8.'''


def esc(value: object) -> str:
    s = '' if value is None else str(value)
    return s.replace('|', '\\|').replace('\n', ' ')


def fmt_num(x: float) -> str:
    if pd.isna(x):
        return 'NA'
    x = float(x)
    if abs(x) >= 1_000_000:
        return f'{x:,.0f}'
    if abs(x) >= 1_000:
        return f'{x:,.2f}'.rstrip('0').rstrip('.')
    if float(x).is_integer():
        return f'{int(x)}'
    return f'{x:.4f}'.rstrip('0').rstrip('.')


def observed_summary(s: pd.Series) -> str:
    non = s.dropna()
    if non.empty:
        return 'all missing'
    nunique = non.nunique(dropna=True)
    if pd.api.types.is_bool_dtype(non):
        vals = sorted(map(str, non.unique().tolist()))
        return 'categories: ' + ', '.join(vals)
    if pd.api.types.is_numeric_dtype(non):
        vals = sorted(non.unique().tolist())
        if nunique <= 12:
            return 'values: ' + ', '.join(fmt_num(v) for v in vals)
        return f'range {fmt_num(non.min())}–{fmt_num(non.max())}; {nunique:,} unique'
    vals = [str(v) for v in non.astype(str).unique().tolist()]
    if nunique <= 12:
        return 'categories: ' + ', '.join(esc(v) for v in vals)
    examples = ', '.join(esc(v[:50]) for v in vals[:4])
    return f'{nunique:,} unique; examples: {examples}'


def read_csv_safe(path: Path):
    try:
        return pd.read_csv(path, low_memory=False)
    except Exception:
        try:
            return pd.read_csv(path, sep=None, engine='python', low_memory=False)
        except Exception:
            return None


def md_table(headers, rows):
    out = ['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join('---' for _ in headers) + ' |']
    out += ['| ' + ' | '.join(esc(v) for v in row) + ' |' for row in rows]
    return '\n'.join(out)


def shape_for(path: Path, rel: str, df=None):
    if df is not None:
        return f'{len(df):,} × {len(df.columns):,}'
    if path.exists():
        return f'{path.stat().st_size:,} bytes'
    return KNOWN_SHAPES.get(rel, 'not available in this checkout')


def sample_table(df: pd.DataFrame, n_rows=3, max_cols=10):
    sample = df.head(n_rows).copy()
    cols = list(sample.columns[:max_cols])
    sample = sample[cols]
    rows = []
    for _, row in sample.iterrows():
        vals = []
        for c in cols:
            v = row[c]
            if pd.isna(v):
                vals.append('')
            else:
                txt = str(v).replace('\n', ' ')
                vals.append(txt if len(txt) <= 70 else txt[:67] + '…')
        rows.append(vals)
    return md_table([str(c) for c in cols], rows), len(df.columns) > max_cols


def build(lang: str) -> str:
    es = lang == 'es'
    title = '# Resumen detallado de datos' if es else '# Detailed data summary'
    intro = (
        'Este documento explica los archivos de datos activos del proyecto Veracruz Tourism Intelligence, cómo evolucionan a través del pipeline y qué contiene cada tabla. Las estadísticas, categorías y ejemplos se calculan directamente desde los CSV presentes cuando se ejecuta el generador.'
        if es else
        'This document explains the active data files in the Veracruz Tourism Intelligence project, how they evolve through the pipeline, and what each table contains. Statistics, categories and examples are computed directly from the CSV files present when the generator is run.'
    )
    lines = [title, '', intro, '', '## Flujo general del pipeline' if es else '## Overall pipeline flow', '', PIPELINE_ES if es else PIPELINE_EN, '', '## Evolución de las principales corrientes de datos' if es else '## Evolution of the main data streams', '', STREAMS_ES if es else STREAMS_EN, '']

    lines += ['## Fuentes brutas y activos no tabulares' if es else '## Raw sources and non-tabular assets', '']
    raw_rows = []
    for rel, en_c, es_c, en_b, es_b in RAW_ASSETS:
        p = ROOT / rel
        raw_rows.append([f'`{rel}`', shape_for(p, rel), es_c if es else en_c, es_b if es else en_b])
    lines += [md_table(
        ['Archivo', 'Tamaño/forma conocida', 'Concepto', 'Límite de interpretación'] if es else ['File', 'Size/known shape', 'Concept', 'Interpretation boundary'],
        raw_rows
    ), '']

    lines += ['## Tablas activas: estructura, valores y muestra' if es else '## Active tables: structure, values and sample', '']

    for stage, rel, en_c, es_c, en_b, es_b in TABLES:
        p = ROOT / rel
        df = read_csv_safe(p) if p.exists() and p.suffix.lower() == '.csv' else None
        lines += [f'### `{rel}`', '', f'**{"Etapa" if es else "Stage"}:** {stage}  ', f'**{"Tamaño actual" if es else "Current size"}:** {shape_for(p, rel, df)}  ', f'**{"Concepto" if es else "Concept"}:** {es_c if es else en_c}  ', f'**{"Límite de interpretación" if es else "Interpretation boundary"}:** {es_b if es else en_b}', '']

        if df is None:
            lines += [
                ('> El archivo no está disponible en este checkout. La forma conocida se conserva arriba; al ejecutar este generador dentro del repositorio completo se añadirán automáticamente columnas, rangos/categorías y la muestra.' if es else '> This file is not available in this checkout. The known shape is retained above; running this generator inside the complete repository will automatically add columns, ranges/categories and the sample.'),
                ''
            ]
            continue

        col_rows = []
        for c in df.columns:
            s = df[c]
            col_rows.append([
                f'`{c}`',
                str(s.dtype),
                f'{int(s.isna().sum()):,}',
                observed_summary(s),
            ])
        lines += [f'#### {"Columnas y valores observados" if es else "Columns and observed values"}', '', md_table(
            ['Columna', 'Tipo', 'Faltantes', 'Rango / categorías / ejemplos'] if es else ['Column', 'Type', 'Missing', 'Range / categories / examples'],
            col_rows
        ), '']

        sample, truncated = sample_table(df)
        lines += [f'#### {"Muestra (primeras filas)" if es else "Sample (first rows)"}', '']
        if truncated:
            lines += [('La muestra se limita a las primeras 10 columnas para mantenerla legible; la tabla anterior enumera todas las columnas.' if es else 'The sample is limited to the first 10 columns for readability; the table above lists every column.'), '']
        lines += [sample, '']

    lines += [
        '## Reglas de interpretación que deben mantenerse' if es else '## Interpretation rules that must be preserved',
        '',
    ]
    rules_es = [
        'La ausencia de cobertura de DataTur **no** significa baja demanda.',
        'Los conteos del INAH representan visitas a zonas arqueológicas, no turismo municipal total.',
        'DENUE y PIB turístico aportan contexto estructural/económico; no miden capacidad de carga ni visitantes.',
        'Las reglas de asociación representan coaparición en la oferta turística oficial, no movimiento de turistas.',
        'Los clústeres representan similitud de perfil turístico, no rutas.',
        'Los análogos estructurales son comparaciones, no prueba de demanda no observada.',
        'Las tablas derivadas deben regenerarse a partir de las fuentes y scripts activos; resultados históricos no deben convertirse en entradas activas.'
    ]
    rules_en = [
        'Missing DataTur coverage does **not** mean low demand.',
        'INAH counts represent archaeological-site visits, not total municipal tourism.',
        'DENUE and tourism GDP provide structural/economic context; they do not measure carrying capacity or visitor totals.',
        'Association rules represent co-occurrence in the official tourism offer, not tourist movement.',
        'Clusters represent tourism-profile similarity, not routes.',
        'Structural analogues are comparisons, not proof of unobserved demand.',
        'Derived tables should be regenerated from active sources and scripts; historical outputs should not become active inputs.'
    ]
    for r in (rules_es if es else rules_en):
        lines.append(f'- {r}')
    lines += ['', ('Este archivo complementa `docs/DATA_CATALOG.md`: el catálogo es el inventario compacto; este resumen es la versión explicativa y demostrativa para revisión académica.' if es else 'This file complements `docs/DATA_CATALOG.md`: the catalog is the compact inventory; this summary is the explanatory, demonstrative version for academic review.'), '']
    return '\n'.join(lines)


def main():
    OUT_EN.parent.mkdir(parents=True, exist_ok=True)
    OUT_EN.write_text(build('en'), encoding='utf-8')
    OUT_ES.write_text(build('es'), encoding='utf-8')
    print(f'Wrote -> {OUT_EN.relative_to(ROOT)}')
    print(f'Wrote -> {OUT_ES.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
