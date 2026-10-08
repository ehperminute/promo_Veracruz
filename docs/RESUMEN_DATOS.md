# Resumen detallado de datos

Este documento explica los archivos de datos activos del proyecto Veracruz Tourism Intelligence, cómo evolucionan a través del pipeline y qué contiene cada tabla. Las estadísticas, categorías y ejemplos se calculan directamente desde los CSV presentes cuando se ejecuta el generador.

## Flujo general del pipeline

```text
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
```

## Evolución de las principales corrientes de datos

- **DataTur:** fuente bruta de centros hoteleros → `fact_datatur_centro_mes.csv` → `datatur_veracruz_monthly.csv` → `demand_series.csv` y campos de cobertura de demanda en `destination_master.csv`.
- **INAH:** catálogo y serie bruta de visitantes → `fact_inah_veracruz_mes.csv` → `demand_series.csv` y evidencia de demanda arqueológica en `destination_master.csv`.
- **DENUE + PIB turístico:** archivos económicos/de establecimientos → `mart_infraestructura_municipio_veracruz.csv` → variables estructurales en `destination_master.csv` → análisis S4 de similitud/candidatos.
- **Portal turístico oficial de Veracruz:** HTML congelado → productos/regiones/Pueblos Mágicos extraídos → `destination_master.csv` y `destination_profiles_s4.csv` → asociaciones y clústeres S4.
- **Mercados de origen:** evidencia validada por país para 2025 → `origin_market_opportunity.csv` → análisis posterior de marketing en S8.

## Fuentes brutas y activos no tabulares

| Archivo | Tamaño/forma conocida | Concepto | Límite de interpretación |
| --- | --- | --- | --- |
| `data/raw/Base70centros.csv` | 2,740,171 bytes | Fuente bruta mensual de centros hoteleros de SECTUR DataTur. | La cobertura de centros hoteleros no equivale a la demanda turística municipal. |
| `data/raw/INAH_visitantes_zonas_general.csv` | 737,783 bytes | Serie bruta de visitantes a zonas arqueológicas del INAH. | Los conteos son visitas a atractivos, no turismo total del municipio. |
| `data/raw/INAH_zonas_arqueologicas.csv` | 46,149 bytes | Catálogo y referencia de ubicación de zonas arqueológicas del INAH. | Evidencia de inventario/ubicación, no demanda. |
| `data/raw/PIB_Turistico_Estatal_y_Municipal_2018-2022_.zip` | 6,675,488 bytes | Archivo de libros de PIB turístico municipal de DataTur. | Contexto/estructura económica, no conteo de visitantes. |
| `data/raw/denue_00_48-49_csv.zip` | 4,910,330 bytes | Actividades de transporte de INEGI DENUE. | Se usa únicamente como proxy estructural. |
| `data/raw/denue_00_56_shp.zip` | 12,094,886 bytes | Servicios de viajes, tours y eventos de INEGI DENUE. | Se usa únicamente como proxy estructural. |
| `data/raw/denue_00_71_csv.zip` | 6,743,965 bytes | Actividades recreativas y culturales de INEGI DENUE. | Se usa únicamente como proxy estructural. |
| `data/raw/denue_00_72_1_csv.zip` | 49,342,606 bytes | Servicios de alojamiento y alimentos de INEGI DENUE, parte 1. | Se usa únicamente como proxy estructural. |
| `data/raw/denue_00_72_2_csv.zip` | 26,143,420 bytes | Servicios de alojamiento y alimentos de INEGI DENUE, parte 2. | Se usa únicamente como proxy estructural. |
| `data/raw/veracruz_productos_2026-10-06.html` | 1,127,651 bytes | Copia congelada de la página oficial de productos turísticos de Veracruz. | Evidencia de oferta; no representa el comportamiento de turistas. |
| `data/raw/veracruz_regiones_2026-10-06.html` | 75,025 bytes | Copia congelada de la página oficial de regiones turísticas de Veracruz. | Referencia para la regionalización turística oficial. |
| `data/raw/veracruz_pueblos_magicos_2026-10-06.html` | 15,064 bytes | Solicitud automatizada de Pueblos Mágicos conservada como evidencia de adquisición. | Devolvió CAPTCHA; no se usa como contenido sustantivo. |
| `data/raw/veracruz_pueblos_magicos_2026-10-06_manual.html` | 87,146 bytes | Página oficial de Pueblos Mágicos guardada manualmente desde el navegador. | Evidencia congelada preferida para la pertenencia a Pueblos Mágicos. |

## Tablas activas: estructura, valores y muestra

### `data/reference/source_registry.csv`

**Etapa:** REFERENCE  
**Tamaño actual:** 14 × 9  
**Concepto:** Registro de procedencia y checksum de las fuentes.  
**Límite de interpretación:** Define versiones congeladas/locales y referencias remotas fijas.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `filename` | str | 0 | 14 unique; examples: Base70centros.csv, INAH_visitantes_zonas_general.csv, INAH_zonas_arqueologicas.csv, PIB_Turistico_Estatal_y_Municipal_2018-2022_.zip |
| `institution` | str | 0 | categories: SECTUR DataTur, INAH, INEGI DENUE, Veracruz Turismo, SECTUR Veracruz, SECTUR DataTur / UPMRIP |
| `source_url` | str | 0 | categories: https://www.datatur.sectur.gob.mx/SitePages/hoteleria.aspx, https://datos.inah.gob.mx/datos-abiertos/visitantes-zonas-arqueologicas, https://datos.inah.gob.mx/datos-abiertos/zonas-arqueologicas, https://datatur.sectur.gob.mx/SitePages/pibturisticoestatalmunicipal.aspx, https://www.inegi.org.mx/app/descarga/?ti=6, https://www.veracruz.mx/productos.php, https://www.veracruz.gob.mx/turismo/regiones-turisticas/, https://www.veracruz.gob.mx/turismo/pueblos-magicos/, https://www.datatur.sectur.gob.mx/Documentoscompartidos/upm/RES_2025_12.pdf |
| `snapshot_date` | str | 0 | categories: 2026-10-06 |
| `release_or_coverage` | str | 0 | categories: coverage 2016-2024, coverage through 2026, 195-site catalog, 2018-2022, DENUE 05/2026, DENUE 05/2026 corrected release 2026-07-01, HTML snapshot, HTML snapshot returned Radware CAPTCHA, manual browser HTML snapshot, 2025 annual values; validated by source August 2026 |
| `project_role` | str | 0 | 14 unique; examples: Hotel-center monthly arrivals occupancy and room c, Archaeological-site monthly visitor series, Archaeological-site catalog and location evidence, Tourism GDP municipal structural context |
| `expected_sha256` | str | 1 | 13 unique; examples: a8ca3f9bf34edf46321a45c1abcd3f774363d02db0395f1d61, f7f960b8620af8de483990f9540473aa7ed112807f7989ee0f, ca080041e4b8dbd712cb545a005cd7663d1b3b08ac922c75a0, 680de133bcec8af264ff4999e8c7da9be46d1d6f8c4a752924 |
| `notes` | str | 11 | categories: Preserved failed automated acquisition (Radware CAPTCHA). The manually browser-saved official page is the preferred parser source., Saved manually in a browser after the automated Codespaces request returned a CAPTCHA; parser extracts the eight iframe title labels., Exact fixed official report remains remotely retrievable. Direct source facts are transcribed without scoring into data/reference/origin_market_2025_validated.csv so the normal pipeline stays offline and deterministic. |
| `storage_mode` | str | 0 | categories: local_raw, remote_fixed |

#### Muestra (primeras filas)

| filename | institution | source_url | snapshot_date | release_or_coverage | project_role | expected_sha256 | notes | storage_mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Base70centros.csv | SECTUR DataTur | https://www.datatur.sectur.gob.mx/SitePages/hoteleria.aspx | 2026-10-06 | coverage 2016-2024 | Hotel-center monthly arrivals occupancy and room context | a8ca3f9bf34edf46321a45c1abcd3f774363d02db0395f1d6132b8a7c4d7d671 |  | local_raw |
| INAH_visitantes_zonas_general.csv | INAH | https://datos.inah.gob.mx/datos-abiertos/visitantes-zonas-arqueolog… | 2026-10-06 | coverage through 2026 | Archaeological-site monthly visitor series | f7f960b8620af8de483990f9540473aa7ed112807f7989ee0f9e5722ac2a37d8 |  | local_raw |
| INAH_zonas_arqueologicas.csv | INAH | https://datos.inah.gob.mx/datos-abiertos/zonas-arqueologicas | 2026-10-06 | 195-site catalog | Archaeological-site catalog and location evidence | ca080041e4b8dbd712cb545a005cd7663d1b3b08ac922c75a0965c05d2304d67 |  | local_raw |

### `data/reference/destination_reference.csv`

**Etapa:** REFERENCE  
**Tamaño actual:** 55 × 28  
**Concepto:** Referencia curada de identidad, mapeo y temas turísticos para los 55 destinos de Veracruz.  
**Límite de interpretación:** Los temas son evidencia de perfil codificada por el proyecto, no demanda medida.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `destination` | str | 0 | 55 unique; examples: Actopan, Atzalan, Boca del Río, Carrillo Puerto |
| `municipio` | str | 0 | 55 unique; examples: Actopan, Atzalan, Boca del Río, Carrillo Puerto |
| `clave_municipio` | int64 | 0 | range 30,001–30,203; 55 unique |
| `region_turistica_preliminar` | str | 0 | categories: Primeros Pasos de Cortés, Totonacapan, Por verificar, Huasteca, Olmeca, Cultura y Aventura, Altas Montañas, Los Tuxtlas |
| `pueblo_magico` | int64 | 0 | values: 0, 1 |
| `oferta_turistica_oficial_web` | int64 | 0 | values: 1 |
| `productos_en_extracto_local_n` | int64 | 0 | range 0–24; 13 unique |
| `productos_ejemplo` | str | 14 | 31 unique; examples: Todo Veracruz es Bello \\| Quiahuiztlan Cempoala La , Todo Veracruz es Bello \\| Al sabor de Boka \\| Aventu, Todo Veracruz es Bello \\| Pueblos Mágicos del Toton, Todo Veracruz es Bello \\| Quiahuiztlan Cempoala La  |
| `tourism_tags` | str | 0 | 28 unique; examples: adventure; archaeology; culture_history; gastronom, archaeology; culture_history; gastronomy; nature, beach_coast; culture_history; gastronomy; urban_se, archaeology |
| `theme_beach_coast` | int64 | 0 | values: 0, 1 |
| `theme_nature` | int64 | 0 | values: 0, 1 |
| `theme_culture_history` | int64 | 0 | values: 0, 1 |
| `theme_archaeology` | int64 | 0 | values: 0, 1 |
| `theme_adventure` | int64 | 0 | values: 0, 1 |
| `theme_gastronomy_coffee` | int64 | 0 | values: 0, 1 |
| `theme_wellness_spiritual` | int64 | 0 | values: 0, 1 |
| `theme_urban_services` | int64 | 0 | values: 0, 1 |
| `inah_inventory_sites` | str | 45 | categories: Quiahuiztlán, Cuajilote \\| Vega de la Peña, Cuauhtochco, Castillo de Teayo, Las Limas, Cuyuxquihui \\| El Tajín, San Lorenzo Tenochtitlan, Cempoala, Las Higueras, Tres Zapotes |
| `inah_series_sites` | str | 46 | categories: Zona Arqueológica de Quiahuitztlán, Zona Arqueológica de Cuajilote \\| Zona Arqueológica de Vega de la Peña, Zona Arqueológica de Cuauhtochco, Zona Arqueológica de Castillo de Teayo con museo de sitio, Zona Arqueológica de Las Limas, Zona Arqueológica de Cuyuxquihui \\| Zona Arqueológica de El Tajín, Zona Arqueológica de San Lorenzo Tenochtitlan con museo de sitio, Zona Arqueológica de Cempoala con museo de sitio, Zona Arqueológica de Las Higueras con museo de sitio |
| `datatur_center` | str | 51 | categories: Veracruz-Boca del Río, Coatzacoalcos, Xalapa |
| `datatur_scope_note` | str | 51 | categories: Centro combinado; usar como contexto hotelero, no como dato municipal puro, Centro DataTur |
| `source_tourism_offer_snapshot` | str | 0 | categories: data/raw/veracruz_productos_2026-10-06.html |
| `source_region_snapshot` | str | 0 | categories: data/raw/veracruz_regiones_2026-10-06.html |
| `source_pueblo_magico_snapshot` | str | 47 | categories: data/raw/veracruz_productos_2026-10-06.html |
| `source_inah_visitors` | str | 0 | categories: data/raw/INAH_visitantes_zonas_general.csv |
| `source_inah_catalog` | str | 0 | categories: data/raw/INAH_zonas_arqueologicas.csv |
| `source_datatur` | str | 0 | categories: data/raw/Base70centros.csv |
| `curation_version` | str | 0 | categories: 2026-10-06-v1 |

#### Muestra (primeras filas)

La muestra se limita a las primeras 10 columnas para mantenerla legible; la tabla anterior enumera todas las columnas.

| destination | municipio | clave_municipio | region_turistica_preliminar | pueblo_magico | oferta_turistica_oficial_web | productos_en_extracto_local_n | productos_ejemplo | tourism_tags | theme_beach_coast |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Actopan | Actopan | 30004 | Primeros Pasos de Cortés | 0 | 1 | 7 | Todo Veracruz es Bello \| Quiahuiztlan Cempoala La Antigua Ruta de C… | adventure; archaeology; culture_history; gastronomy | 0 |
| Atzalan | Atzalan | 30023 | Totonacapan | 0 | 1 | 0 |  | archaeology; culture_history; gastronomy; nature | 0 |
| Boca del Río | Boca del Río | 30028 | Primeros Pasos de Cortés | 0 | 1 | 12 | Todo Veracruz es Bello \| Al sabor de Boka \| Aventura en Ríos | beach_coast; culture_history; gastronomy; urban_services | 1 |

### `data/reference/tourism_products.csv`

**Etapa:** REFERENCE  
**Tamaño actual:** 75 × 5  
**Concepto:** Selección histórica de 75 productos usada en actividades previas.  
**Límite de interpretación:** Se conserva para reproducibilidad; no es el catálogo oficial completo.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `producto` | str | 0 | 75 unique; examples: Todo Veracruz es Bello, Al sabor de Boka, Descubre Los Tuxtlas, Pueblos Mágicos del Totonacapan |
| `municipios` | str | 0 | 45 unique; examples: Catemaco\\|Boca del Río\\|Alvarado\\|Actopan\\|Coatepec\\|Có, Boca del Río\\|Alvarado\\|Veracruz, Catemaco\\|San Andrés Tuxtla\\|Santiago Tuxtla, Papantla\\|Zozocolco de Hidalgo |
| `n_municipios` | int64 | 0 | values: 1, 2, 3, 4, 5, 6, 17 |
| `source_snapshot` | str | 0 | categories: data/raw/veracruz_productos_2026-10-06.html |
| `curation_version` | str | 0 | categories: 2026-10-06-v1 |

#### Muestra (primeras filas)

| producto | municipios | n_municipios | source_snapshot | curation_version |
| --- | --- | --- | --- | --- |
| Todo Veracruz es Bello | Catemaco\|Boca del Río\|Alvarado\|Actopan\|Coatepec\|Córdoba\|Coscomatepe… | 17 | data/raw/veracruz_productos_2026-10-06.html | 2026-10-06-v1 |
| Al sabor de Boka | Boca del Río\|Alvarado\|Veracruz | 3 | data/raw/veracruz_productos_2026-10-06.html | 2026-10-06-v1 |
| Descubre Los Tuxtlas | Catemaco\|San Andrés Tuxtla\|Santiago Tuxtla | 3 | data/raw/veracruz_productos_2026-10-06.html | 2026-10-06-v1 |

### `data/reference/denue_activity_groups.csv`

**Etapa:** REFERENCE  
**Tamaño actual:** 21 × 4  
**Concepto:** Reglas SCIAN explícitas usadas para construir proxies turísticos con DENUE.  
**Límite de interpretación:** Las definiciones son auditables, pero no miden capacidad de carga.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `metric` | str | 0 | categories: alojamiento_n, alimentos_bebidas_n, sector_recreacion_total_n, recreacion_turistica_proxy_n, agencias_tours_eventos_n, transporte_turistico_n |
| `match_type` | str | 0 | categories: prefix, exact |
| `code` | int64 | 0 | range 71–713,999; 21 unique |
| `description` | str | 0 | 21 unique; examples: Servicios de alojamiento temporal, Servicios de preparación de alimentos y bebidas, Sector completo de servicios de esparcimiento cult, Promotores del sector público de espectáculos artí |

#### Muestra (primeras filas)

| metric | match_type | code | description |
| --- | --- | --- | --- |
| alojamiento_n | prefix | 721 | Servicios de alojamiento temporal |
| alimentos_bebidas_n | prefix | 722 | Servicios de preparación de alimentos y bebidas |
| sector_recreacion_total_n | prefix | 71 | Sector completo de servicios de esparcimiento culturales deportivos… |

### `data/reference/origin_market_2025_validated.csv`

**Etapa:** REFERENCE  
**Tamaño actual:** 25 × 9  
**Concepto:** Evidencia validada de entradas aéreas por país de residencia para 2025.  
**Límite de interpretación:** Contexto nacional; no son visitantes específicos de Veracruz.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `rank_2025` | int64 | 0 | range 1–25; 25 unique |
| `country_of_residence` | str | 0 | 25 unique; examples: Estados Unidos, Canadá, Reino Unido, Colombia |
| `air_entries_2024` | int64 | 0 | range 39,041–13,709,389; 25 unique |
| `air_entries_2025` | int64 | 0 | range 42,425–14,258,403; 25 unique |
| `share_2025_pct` | float64 | 0 | range 0.2–66.9; 14 unique |
| `growth_2025_vs_2024_pct` | float64 | 0 | range -45.4–30; 25 unique |
| `source_url` | str | 0 | categories: https://www.datatur.sectur.gob.mx/Documentoscompartidos/upm/RES_2025_12.pdf |
| `source_version` | str | 0 | categories: 2025 annual values validated by source in August 2026 |
| `scope_note` | str | 0 | categories: Foreign air-entry events to Mexico by country of residence; not Veracruz-specific demand. |

#### Muestra (primeras filas)

| rank_2025 | country_of_residence | air_entries_2024 | air_entries_2025 | share_2025_pct | growth_2025_vs_2024_pct | source_url | source_version | scope_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Estados Unidos | 13709389 | 14258403 | 66.9 | 4.0 | https://www.datatur.sectur.gob.mx/Documentoscompartidos/upm/RES_202… | 2025 annual values validated by source in August 2026 | Foreign air-entry events to Mexico by country of residence; not Ver… |
| 2 | Canadá | 2522479 | 2843977 | 13.3 | 12.7 | https://www.datatur.sectur.gob.mx/Documentoscompartidos/upm/RES_202… | 2025 annual values validated by source in August 2026 | Foreign air-entry events to Mexico by country of residence; not Ver… |
| 3 | Reino Unido | 426856 | 457712 | 2.1 | 7.2 | https://www.datatur.sectur.gob.mx/Documentoscompartidos/upm/RES_202… | 2025 annual values validated by source in August 2026 | Foreign air-entry events to Mexico by country of residence; not Ver… |

### `data/reference/destination_profile_enrichment.csv`

**Etapa:** REFERENCE  
**Tamaño actual:** 6 × 6  
**Concepto:** Pequeño conjunto de correcciones de perfil revisadas para S4.  
**Límite de interpretación:** Las correcciones tienen procedencia documentada y no agregan mediciones inventadas.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `destination` | str | 0 | categories: Carrillo Puerto, La Antigua, Poza Rica de Hidalgo |
| `field` | str | 0 | categories: region_turistica_preliminar, theme_culture_history, theme_gastronomy_coffee, theme_beach_coast, theme_nature |
| `new_value` | str | 0 | categories: Altas Montañas, 1, 0 |
| `evidence_source` | str | 0 | categories: https://www.veracruz.mx/region.php?id=5, https://www.veracruz.mx/destino.php?Municipio=31, https://www.veracruz.mx/destino.php?Municipio=16, https://www.veracruz.gob.mx/turismo/regiones-turisticas/ |
| `evidence_note` | str | 0 | categories: Official Altas Montañas page lists Carrillo Puerto among the municipalities of the region., Official destination page documents the pre-Hispanic province of Cuauhtochco, historical buildings, traditions and music., Official destination page has a dedicated gastronomy section with local dishes., Official destination page lists Playa de Chalchihuecan as a tourism center., Official destination page describes Río Huitzilapan, exuberant riverside vegetation and boat/swimming/fishing activities; SECTUR also describes mangrove boat trips., Reviewed tourism-specific sources characterize Poza Rica as an urban/petroleum-history and cultural destination/gateway; no nature-tourism attraction or activity is positively evidenced for the municipality. In S4, zero means not positively evidenced, not proven absence. |
| `review_date` | str | 0 | categories: 2026-10-07 |

#### Muestra (primeras filas)

| destination | field | new_value | evidence_source | evidence_note | review_date |
| --- | --- | --- | --- | --- | --- |
| Carrillo Puerto | region_turistica_preliminar | Altas Montañas | https://www.veracruz.mx/region.php?id=5 | Official Altas Montañas page lists Carrillo Puerto among the munici… | 2026-10-07 |
| Carrillo Puerto | theme_culture_history | 1 | https://www.veracruz.mx/destino.php?Municipio=31 | Official destination page documents the pre-Hispanic province of Cu… | 2026-10-07 |
| Carrillo Puerto | theme_gastronomy_coffee | 1 | https://www.veracruz.mx/destino.php?Municipio=31 | Official destination page has a dedicated gastronomy section with l… | 2026-10-07 |

### `data/reference/destination_profile_sources.csv`

**Etapa:** REFERENCE  
**Tamaño actual:** 13 × 5  
**Concepto:** Notas y fuentes de investigación para perfiles de destino con poca información.  
**Límite de interpretación:** Documentación de apoyo para revisar vacíos de información.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `destination` | str | 0 | categories: Carrillo Puerto, Las Choapas, Chinameca, Soteapan, Tlalnelhuayocan, Calcahualco, Xalapa, La Antigua, Poza Rica de Hidalgo |
| `evidence_scope` | str | 0 | categories: profile gap repair, region repair, sparse-offer cross-check, sparse-profile cross-check, targeted profile cross-check, targeted profile repair, targeted profile review |
| `source` | str | 0 | categories: https://www.veracruz.mx/destino.php?Municipio=31, https://www.veracruz.mx/region.php?id=5, https://www.veracruz.mx/destino.php?Municipio=61, https://www.veracruz.mx/destino.php?Municipio=59, data/raw/veracruz_productos_2026-10-06.html, https://www.veracruz.gob.mx/turismo/2025/08/29/recorre-xalapa-ciudad-de-parques-un-respiro-entre-la-urbanidad-y-la-naturaleza/, https://www.veracruz.mx/destino.php?Municipio=87, https://www.veracruz.mx/destino.php?Municipio=16, https://www.veracruz.gob.mx/turismo/2025/03/25/descubre-veracruz-a-traves-de-la-ruta-primeros-pasos-de-cortes-historia-aventura-y-naturaleza/, https://www.veracruz.gob.mx/turismo/regiones-turisticas/, https://www.veracruz.gob.mx/turismo/2026/03/23/descubre-los-atractivos-turisticos-del-norte-de-veracruz-durante-cumbre-tajin/ |
| `evidence_summary` | str | 0 | 13 unique; examples: Pre-Hispanic history, archaeological monument, tra, Official Altas Montañas page lists Carrillo Puerto, Official page documents tropical ecosystems, tradi, Official page documents local history and the muni |
| `review_date` | str | 0 | categories: 2026-10-07 |

#### Muestra (primeras filas)

| destination | evidence_scope | source | evidence_summary | review_date |
| --- | --- | --- | --- | --- |
| Carrillo Puerto | profile gap repair | https://www.veracruz.mx/destino.php?Municipio=31 | Pre-Hispanic history, archaeological monument, traditions/music and… | 2026-10-07 |
| Carrillo Puerto | region repair | https://www.veracruz.mx/region.php?id=5 | Official Altas Montañas page lists Carrillo Puerto in the region. | 2026-10-07 |
| Las Choapas | sparse-offer cross-check | https://www.veracruz.mx/destino.php?Municipio=61 | Official page documents tropical ecosystems, traditions/music, gast… | 2026-10-07 |

### `data/interim/source_registry_resolved.csv`

**Etapa:** S1/S2 INTERIM  
**Tamaño actual:** 14 × 12  
**Concepto:** Tabla resuelta de verificación de las fuentes del proyecto.  
**Límite de interpretación:** Verifica archivos locales exactos y referencias remotas fijas.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `filename` | str | 0 | 14 unique; examples: Base70centros.csv, INAH_visitantes_zonas_general.csv, INAH_zonas_arqueologicas.csv, PIB_Turistico_Estatal_y_Municipal_2018-2022_.zip |
| `institution` | str | 0 | categories: SECTUR DataTur, INAH, INEGI DENUE, Veracruz Turismo, SECTUR Veracruz, SECTUR DataTur / UPMRIP |
| `source_url` | str | 0 | categories: https://www.datatur.sectur.gob.mx/SitePages/hoteleria.aspx, https://datos.inah.gob.mx/datos-abiertos/visitantes-zonas-arqueologicas, https://datos.inah.gob.mx/datos-abiertos/zonas-arqueologicas, https://datatur.sectur.gob.mx/SitePages/pibturisticoestatalmunicipal.aspx, https://www.inegi.org.mx/app/descarga/?ti=6, https://www.veracruz.mx/productos.php, https://www.veracruz.gob.mx/turismo/regiones-turisticas/, https://www.veracruz.gob.mx/turismo/pueblos-magicos/, https://www.datatur.sectur.gob.mx/Documentoscompartidos/upm/RES_2025_12.pdf |
| `snapshot_date` | str | 0 | categories: 2026-10-06 |
| `release_or_coverage` | str | 0 | categories: coverage 2016-2024, coverage through 2026, 195-site catalog, 2018-2022, DENUE 05/2026, DENUE 05/2026 corrected release 2026-07-01, HTML snapshot, HTML snapshot returned Radware CAPTCHA, manual browser HTML snapshot, 2025 annual values; validated by source August 2026 |
| `project_role` | str | 0 | 14 unique; examples: Hotel-center monthly arrivals occupancy and room c, Archaeological-site monthly visitor series, Archaeological-site catalog and location evidence, Tourism GDP municipal structural context |
| `expected_sha256` | str | 1 | 13 unique; examples: a8ca3f9bf34edf46321a45c1abcd3f774363d02db0395f1d61, f7f960b8620af8de483990f9540473aa7ed112807f7989ee0f, ca080041e4b8dbd712cb545a005cd7663d1b3b08ac922c75a0, 680de133bcec8af264ff4999e8c7da9be46d1d6f8c4a752924 |
| `notes` | str | 11 | categories: Preserved failed automated acquisition (Radware CAPTCHA). The manually browser-saved official page is the preferred parser source., Saved manually in a browser after the automated Codespaces request returned a CAPTCHA; parser extracts the eight iframe title labels., Exact fixed official report remains remotely retrievable. Direct source facts are transcribed without scoring into data/reference/origin_market_2025_validated.csv so the normal pipeline stays offline and deterministic. |
| `storage_mode` | str | 0 | categories: local_raw, remote_fixed |
| `bytes` | float64 | 1 | range 15,064–49,342,606; 13 unique |
| `actual_sha256` | str | 1 | 13 unique; examples: a8ca3f9bf34edf46321a45c1abcd3f774363d02db0395f1d61, f7f960b8620af8de483990f9540473aa7ed112807f7989ee0f, ca080041e4b8dbd712cb545a005cd7663d1b3b08ac922c75a0, 680de133bcec8af264ff4999e8c7da9be46d1d6f8c4a752924 |
| `status` | str | 0 | categories: verified, remote_fixed |

#### Muestra (primeras filas)

La muestra se limita a las primeras 10 columnas para mantenerla legible; la tabla anterior enumera todas las columnas.

| filename | institution | source_url | snapshot_date | release_or_coverage | project_role | expected_sha256 | notes | storage_mode | bytes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Base70centros.csv | SECTUR DataTur | https://www.datatur.sectur.gob.mx/SitePages/hoteleria.aspx | 2026-10-06 | coverage 2016-2024 | Hotel-center monthly arrivals occupancy and room context | a8ca3f9bf34edf46321a45c1abcd3f774363d02db0395f1d6132b8a7c4d7d671 |  | local_raw | 2740171.0 |
| INAH_visitantes_zonas_general.csv | INAH | https://datos.inah.gob.mx/datos-abiertos/visitantes-zonas-arqueolog… | 2026-10-06 | coverage through 2026 | Archaeological-site monthly visitor series | f7f960b8620af8de483990f9540473aa7ed112807f7989ee0f9e5722ac2a37d8 |  | local_raw | 737783.0 |
| INAH_zonas_arqueologicas.csv | INAH | https://datos.inah.gob.mx/datos-abiertos/zonas-arqueologicas | 2026-10-06 | 195-site catalog | Archaeological-site catalog and location evidence | ca080041e4b8dbd712cb545a005cd7663d1b3b08ac922c75a0965c05d2304d67 |  | local_raw | 46149.0 |

### `data/interim/veracruz_products_parsed.csv`

**Etapa:** S1/S2 INTERIM  
**Tamaño actual:** 295 × 5  
**Concepto:** Todas las fichas oficiales de productos turísticos de Veracruz extraídas mecánicamente del HTML congelado.  
**Límite de interpretación:** Transacciones de oferta para conteos y asociaciones; no co-visita turística.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `source_card_index` | int64 | 0 | range 1–295; 295 unique |
| `producto` | str | 0 | 280 unique; examples: Todo Veracruz es Bello, Al sabor de Boka, Descubre Los Tuxtlas, Pueblos Mágicos del Totonacapan |
| `municipios` | str | 0 | 106 unique; examples: Catemaco\\|Boca del Río\\|Alvarado\\|Actopan\\|Coatepec\\|Có, Boca del Río\\|Alvarado\\|Veracruz, Catemaco\\|San Andrés Tuxtla\\|Santiago Tuxtla, Papantla\\|Zozocolco de Hidalgo |
| `n_municipios` | int64 | 0 | values: 1, 2, 3, 4, 5, 6, 7, 10, 17 |
| `source_snapshot` | str | 0 | categories: data/raw/veracruz_productos_2026-10-06.html |

#### Muestra (primeras filas)

| source_card_index | producto | municipios | n_municipios | source_snapshot |
| --- | --- | --- | --- | --- |
| 1 | Todo Veracruz es Bello | Catemaco\|Boca del Río\|Alvarado\|Actopan\|Coatepec\|Córdoba\|Coscomatepe… | 17 | data/raw/veracruz_productos_2026-10-06.html |
| 2 | Al sabor de Boka | Boca del Río\|Alvarado\|Veracruz | 3 | data/raw/veracruz_productos_2026-10-06.html |
| 3 | Descubre Los Tuxtlas | Catemaco\|San Andrés Tuxtla\|Santiago Tuxtla | 3 | data/raw/veracruz_productos_2026-10-06.html |

### `data/interim/veracruz_regions_parsed.csv`

**Etapa:** S1/S2 INTERIM  
**Tamaño actual:** 31 × 6  
**Concepto:** Mapeos extraídos de navegación regional y municipios.  
**Límite de interpretación:** Se usa como referencia/validación.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `region` | str | 0 | categories: Altas Montañas, Cultura y Aventura, Huasteca, Los Tuxtlas, Olmeca, Primeros Pasos de Cortés, Totonacapan |
| `source_municipality_name` | str | 0 | 31 unique; examples: Córdoba, Coscomatepec, Fortín de las Flores, Orizaba |
| `municipio` | str | 0 | 31 unique; examples: Córdoba, Coscomatepec, Fortín, Orizaba |
| `source_municipio_id` | int64 | 0 | range 11–203; 31 unique |
| `clave_municipio` | int64 | 0 | range 30,011–30,203; 31 unique |
| `source_snapshot` | str | 0 | categories: data/raw/veracruz_productos_2026-10-06.html |

#### Muestra (primeras filas)

| region | source_municipality_name | municipio | source_municipio_id | clave_municipio | source_snapshot |
| --- | --- | --- | --- | --- | --- |
| Altas Montañas | Córdoba | Córdoba | 44 | 30044 | data/raw/veracruz_productos_2026-10-06.html |
| Altas Montañas | Coscomatepec | Coscomatepec | 47 | 30047 | data/raw/veracruz_productos_2026-10-06.html |
| Altas Montañas | Fortín de las Flores | Fortín | 68 | 30068 | data/raw/veracruz_productos_2026-10-06.html |

### `data/interim/veracruz_pueblos_magicos_parsed.csv`

**Etapa:** S1/S2 INTERIM  
**Tamaño actual:** 8 × 5  
**Concepto:** Pertenencias oficiales a Pueblos Mágicos extraídas de la fuente.  
**Límite de interpretación:** Evidencia directa de pertenencia.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `source_name` | str | 0 | categories: COATEPEC, COSCOMATEPEC, CÓRDOBA, NAOLINCO, ORIZABA, PAPANTLA, XICO, ZOZOCOLCO |
| `pueblo_magico` | str | 0 | categories: Coatepec, Coscomatepec, Córdoba, Naolinco, Orizaba, Papantla, Xico, Zozocolco de Hidalgo |
| `source_snapshot` | str | 0 | categories: data/raw/veracruz_pueblos_magicos_2026-10-06_manual.html |
| `requested_snapshot` | str | 0 | categories: data/raw/veracruz_pueblos_magicos_2026-10-06.html |
| `extraction_note` | str | 0 | categories: manual_browser_snapshot_iframe_titles |

#### Muestra (primeras filas)

| source_name | pueblo_magico | source_snapshot | requested_snapshot | extraction_note |
| --- | --- | --- | --- | --- |
| COATEPEC | Coatepec | data/raw/veracruz_pueblos_magicos_2026-10-06_manual.html | data/raw/veracruz_pueblos_magicos_2026-10-06.html | manual_browser_snapshot_iframe_titles |
| COSCOMATEPEC | Coscomatepec | data/raw/veracruz_pueblos_magicos_2026-10-06_manual.html | data/raw/veracruz_pueblos_magicos_2026-10-06.html | manual_browser_snapshot_iframe_titles |
| CÓRDOBA | Córdoba | data/raw/veracruz_pueblos_magicos_2026-10-06_manual.html | data/raw/veracruz_pueblos_magicos_2026-10-06.html | manual_browser_snapshot_iframe_titles |

### `data/interim/fact_datatur_centro_mes.csv`

**Etapa:** S1/S2 INTERIM  
**Tamaño actual:** 6,900 × 11  
**Concepto:** Tabla de hechos limpia de DataTur por centro y mes.  
**Límite de interpretación:** Cada fila es una observación centro-hotelero/mes; no un total turístico municipal.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `anio` | int64 | 0 | values: 2,016, 2,017, 2,018, 2,019, 2,020, 2,021, 2,022, 2,023, 2,024 |
| `mes` | int64 | 0 | values: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 |
| `centro` | str | 0 | 64 unique; examples: Acapulco, Aguascalientes, Bahías de Huatulco, Campeche |
| `tipo_centro` | str | 0 | categories: Centros de Playa, Ciudades |
| `subtipo_centro` | str | 0 | categories: Tradicionales, Interior, Integralmente Planeados, Fronterizas, Grandes, Otros |
| `cuartos_disponibles` | int64 | 0 | range 3,300–1,905,162; 5,225 unique |
| `cuartos_ocupados` | int64 | 0 | range 0–1,375,423; 6,694 unique |
| `llegadas_total` | int64 | 0 | range 0–1,230,463; 6,713 unique |
| `turistas_noche_total` | int64 | 0 | range 0–2,990,249; 6,792 unique |
| `ocupacion_pct` | float64 | 0 | range 0–90.6609; 6,888 unique |
| `fecha` | str | 0 | 108 unique; examples: 2016-01-01, 2016-02-01, 2016-03-01, 2016-04-01 |

#### Muestra (primeras filas)

La muestra se limita a las primeras 10 columnas para mantenerla legible; la tabla anterior enumera todas las columnas.

| anio | mes | centro | tipo_centro | subtipo_centro | cuartos_disponibles | cuartos_ocupados | llegadas_total | turistas_noche_total | ocupacion_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2016 | 1 | Acapulco | Centros de Playa | Tradicionales | 576797 | 300902 | 578858 | 783691 | 52.16774705832381 |
| 2016 | 1 | Aguascalientes | Ciudades | Interior | 136441 | 58900 | 40385 | 84126 | 43.168842210186085 |
| 2016 | 1 | Bahías de Huatulco | Centros de Playa | Integralmente Planeados | 113150 | 86309 | 41866 | 186124 | 76.27839151568715 |

### `data/interim/datatur_veracruz_monthly.csv`

**Etapa:** S1/S2 INTERIM  
**Tamaño actual:** 324 × 11  
**Concepto:** Subconjunto mensual de DataTur correspondiente a Veracruz.  
**Límite de interpretación:** Cubre únicamente los centros DataTur disponibles en el proyecto.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `anio` | int64 | 0 | values: 2,016, 2,017, 2,018, 2,019, 2,020, 2,021, 2,022, 2,023, 2,024 |
| `mes` | int64 | 0 | values: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 |
| `centro` | str | 0 | categories: Coatzacoalcos, Veracruz-Boca del Río, Xalapa |
| `tipo_centro` | str | 0 | categories: Ciudades, Centros de Playa |
| `subtipo_centro` | str | 0 | categories: Interior, Tradicionales |
| `cuartos_disponibles` | int64 | 0 | range 49,558–327,112; 247 unique |
| `cuartos_ocupados` | int64 | 0 | range 3,974–210,279; 322 unique |
| `llegadas_total` | int64 | 0 | range 5,319–300,325; 324 unique |
| `turistas_noche_total` | int64 | 0 | range 5,920–497,899; 324 unique |
| `ocupacion_pct` | float64 | 0 | range 5.2466–74.8402; 324 unique |
| `fecha` | str | 0 | 108 unique; examples: 2016-01-01, 2016-02-01, 2016-03-01, 2016-04-01 |

#### Muestra (primeras filas)

La muestra se limita a las primeras 10 columnas para mantenerla legible; la tabla anterior enumera todas las columnas.

| anio | mes | centro | tipo_centro | subtipo_centro | cuartos_disponibles | cuartos_ocupados | llegadas_total | turistas_noche_total | ocupacion_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2016 | 1 | Coatzacoalcos | Ciudades | Interior | 49705 | 23511 | 27347 | 33495 | 47.30107635046776 |
| 2016 | 1 | Veracruz-Boca del Río | Centros de Playa | Tradicionales | 267673 | 108038 | 181995 | 214733 | 40.36193415099767 |
| 2016 | 1 | Xalapa | Ciudades | Interior | 72871 | 27106 | 36511 | 45553 | 37.197238956512194 |

### `data/interim/fact_inah_veracruz_mes.csv`

**Etapa:** S1/S2 INTERIM  
**Tamaño actual:** 4,048 × 8  
**Concepto:** Tabla de hechos limpia del INAH para Veracruz por zona arqueológica y mes.  
**Límite de interpretación:** Las visitas se mantienen como evidencia de demanda a nivel de atractivo.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `anio` | int64 | 0 | range 1,996–2,026; 31 unique |
| `mes` | int64 | 0 | values: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 |
| `clave_siinah` | int64 | 0 | range 3,110,016–3,220,015; 13 unique |
| `recinto` | str | 0 | 13 unique; examples: Zona Arqueológica El Zapotal, Zona Arqueológica de Castillo de Teayo con museo d, Zona Arqueológica de Cempoala con museo de sitio, Zona Arqueológica de Cuajilote |
| `visitantes_nacionales` | float64 | 0 | range 0–196,051; 1,602 unique |
| `visitantes_extranjeros` | float64 | 0 | range 0–34,764; 523 unique |
| `visitantes_total` | float64 | 0 | range 0–214,558; 1,613 unique |
| `fecha` | str | 0 | 368 unique; examples: 1996-01-01, 1996-02-01, 1996-03-01, 1996-04-01 |

#### Muestra (primeras filas)

| anio | mes | clave_siinah | recinto | visitantes_nacionales | visitantes_extranjeros | visitantes_total | fecha |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1996 | 1 | 3220013 | Zona Arqueológica El Zapotal | 0.0 | 0.0 | 0.0 | 1996-01-01 |
| 1996 | 1 | 3120011 | Zona Arqueológica de Castillo de Teayo con museo de sitio | 78.0 | 17.0 | 95.0 | 1996-01-01 |
| 1996 | 1 | 3120012 | Zona Arqueológica de Cempoala con museo de sitio | 1284.0 | 813.0 | 2097.0 | 1996-01-01 |

### `data/interim/mart_infraestructura_municipio_veracruz.csv`

**Etapa:** S1/S2 INTERIM  
**Tamaño actual:** 212 × 11  
**Concepto:** Mart municipal de infraestructura DENUE y PIB turístico.  
**Límite de interpretación:** Contexto estructural/económico, no demanda turística observada.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `clave_municipio` | int64 | 0 | range 30,001–30,212; 212 unique |
| `municipio` | str | 0 | 212 unique; examples: Acajete, Acatlán, Acayucan, Actopan |
| `alojamiento_n` | int64 | 0 | range 0–248; 37 unique |
| `alimentos_bebidas_n` | int64 | 0 | range 2–5,325; 152 unique |
| `sector_recreacion_total_n` | int64 | 0 | range 0–417; 51 unique |
| `recreacion_turistica_proxy_n` | int64 | 0 | range 0–42; 18 unique |
| `agencias_tours_eventos_n` | int64 | 0 | range 0–51; 15 unique |
| `transporte_turistico_n` | int64 | 0 | values: 0, 1, 2, 3, 4, 6, 8, 9, 10, 20, 28 |
| `pib_turistico_2022` | float64 | 75 | range 280,221.93–13,309,403,141; 118 unique |
| `participacion_turismo_pct` | float64 | 75 | range 0.0001–0.8856; 137 unique |
| `pib_municipal_2022` | float64 | 0 | range 1,722,252–182,564,249,103; 212 unique |

#### Muestra (primeras filas)

La muestra se limita a las primeras 10 columnas para mantenerla legible; la tabla anterior enumera todas las columnas.

| clave_municipio | municipio | alojamiento_n | alimentos_bebidas_n | sector_recreacion_total_n | recreacion_turistica_proxy_n | agencias_tours_eventos_n | transporte_turistico_n | pib_turistico_2022 | participacion_turismo_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 30001 | Acajete | 0 | 39 | 4 | 3 | 0 | 0 | 887227.282082128 | 0.006451695767772 |
| 30002 | Acatlán | 0 | 24 | 5 | 0 | 0 | 0 |  |  |
| 30003 | Acayucan | 32 | 583 | 41 | 9 | 40 | 2 | 869672875.7611876 | 0.1208075284895506 |

### `data/interim/tourism_products.csv`

**Etapa:** S1/S2 INTERIM  
**Tamaño actual:** 75 × 8  
**Concepto:** Tabla de 75 productos respaldada por fuentes para actividades previas.  
**Límite de interpretación:** Alcance histórico conservado para reproducibilidad.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `producto` | str | 0 | 75 unique; examples: Al sabor de Boka, Aventura Costas Tuxtlas, Aventura Dunas Playas Chachalacas, Aventura en Ríos |
| `municipios` | str | 0 | 45 unique; examples: Boca del Río\\|Alvarado\\|Veracruz, San Andrés Tuxtla, Ursulo Galván, Boca del Río\\|Jalcomulco\\|La Antigua\\|Veracruz |
| `n_municipios` | int64 | 0 | values: 1, 2, 3, 4, 5, 6, 17 |
| `source_snapshot` | str | 0 | categories: data/raw/veracruz_productos_2026-10-06.html |
| `curation_version` | str | 0 | categories: 2026-10-06-v1 |
| `source_card_index` | int64 | 0 | range 1–243; 75 unique |
| `source_producto` | str | 0 | 69 unique; examples: Al sabor de Boka, Aventura en las Costas de los Tuxtlas, Aventura en Dunas y Playas de Chachalacas, Aventura en Ríos |
| `source_match_score` | float64 | 0 | values: 0.6667, 0.7143, 0.7407, 0.7568, 0.7586, 0.7907, 0.7937, 0.8571, 0.9388, 1 |

#### Muestra (primeras filas)

| producto | municipios | n_municipios | source_snapshot | curation_version | source_card_index | source_producto | source_match_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Al sabor de Boka | Boca del Río\|Alvarado\|Veracruz | 3 | data/raw/veracruz_productos_2026-10-06.html | 2026-10-06-v1 | 2 | Al sabor de Boka | 1.0 |
| Aventura Costas Tuxtlas | San Andrés Tuxtla | 1 | data/raw/veracruz_productos_2026-10-06.html | 2026-10-06-v1 | 23 | Aventura en las Costas de los Tuxtlas | 1.0 |
| Aventura Dunas Playas Chachalacas | Ursulo Galván | 1 | data/raw/veracruz_productos_2026-10-06.html | 2026-10-06-v1 | 20 | Aventura en Dunas y Playas de Chachalacas | 1.0 |

### `data/interim/destination_profiles_s4.csv`

**Etapa:** S4 INTERIM  
**Tamaño actual:** 55 × 50  
**Concepto:** Tabla de perfiles de destino de S4 usada para agrupación y similitud local.  
**Límite de interpretación:** La agrupación usa características del perfil turístico; la demanda directa no forma los clústeres.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `destination` | str | 0 | 55 unique; examples: Acajete, Actopan, Alvarado, Atzalan |
| `municipio` | str | 0 | 55 unique; examples: Acajete, Actopan, Alvarado, Atzalan |
| `clave_municipio` | int64 | 0 | range 30,001–30,203; 55 unique |
| `region_turistica_preliminar` | str | 0 | categories: Cultura y Aventura, Primeros Pasos de Cortés, Totonacapan, Altas Montañas, Huasteca, Los Tuxtlas, Olmeca |
| `pueblo_magico` | int64 | 0 | values: 0, 1 |
| `oferta_turistica_oficial_web` | int64 | 0 | values: 1 |
| `productos_en_extracto_local_n` | int64 | 0 | range 0–24; 13 unique |
| `productos_ejemplo` | str | 14 | 31 unique; examples: Sones, Sabores y Tradiciones de Invierno, Todo Veracruz es Bello \\| Quiahuiztlan Cempoala La , Todo Veracruz es Bello \\| Al sabor de Boka \\| Salsas, Todo Veracruz es Bello \\| Al sabor de Boka \\| Aventu |
| `tourism_tags` | str | 0 | 28 unique; examples: culture_history; gastronomy; nature, adventure; archaeology; culture_history; gastronom, beach_coast; culture_history; gastronomy, archaeology; culture_history; gastronomy; nature |
| `theme_beach_coast` | int64 | 0 | values: 0, 1 |
| `theme_nature` | int64 | 0 | values: 0, 1 |
| `theme_culture_history` | int64 | 0 | values: 1 |
| `theme_archaeology` | int64 | 0 | values: 0, 1 |
| `theme_adventure` | int64 | 0 | values: 0, 1 |
| `theme_gastronomy_coffee` | int64 | 0 | values: 0, 1 |
| `theme_wellness_spiritual` | int64 | 0 | values: 0, 1 |
| `theme_urban_services` | int64 | 0 | values: 0, 1 |
| `inah_inventory_sites_n` | int64 | 0 | values: 0, 1, 2 |
| `inah_inventory_sites` | str | 45 | categories: Quiahuiztlán, Cuajilote \\| Vega de la Peña, Cuauhtochco, Castillo de Teayo, Las Limas, Cuyuxquihui \\| El Tajín, Tres Zapotes, San Lorenzo Tenochtitlan, Cempoala, Las Higueras |
| `inah_series_available` | int64 | 0 | values: 0, 1 |
| `inah_series_sites` | str | 46 | categories: Zona Arqueológica de Quiahuitztlán, Zona Arqueológica de Cuajilote \\| Zona Arqueológica de Vega de la Peña, Zona Arqueológica de Cuauhtochco, Zona Arqueológica de Castillo de Teayo con museo de sitio, Zona Arqueológica de Las Limas, Zona Arqueológica de Cuyuxquihui \\| Zona Arqueológica de El Tajín, Zona Arqueológica de San Lorenzo Tenochtitlan con museo de sitio, Zona Arqueológica de Cempoala con museo de sitio, Zona Arqueológica de Las Higueras con museo de sitio |
| `inah_visitors_2025` | float64 | 46 | values: 0, 834, 1,124, 2,428, 4,699, 5,880, 29,186, 31,120, 308,598 |
| `inah_foreign_share_2025` | float64 | 46 | values: 0, 0.0012, 0.0093, 0.0247, 0.0255 |
| `datatur_coverage` | int64 | 0 | values: 0, 1 |
| `datatur_center` | str | 51 | categories: Veracruz-Boca del Río, Coatzacoalcos, Xalapa |
| `datatur_scope_note` | str | 51 | categories: Centro combinado; usar como contexto hotelero, no como dato municipal puro, Centro DataTur |
| `datatur_arrivals_2024` | float64 | 51 | values: 473,350, 739,186, 2,481,563 |
| `datatur_occupancy_2024_pct` | float64 | 51 | values: 48.2382, 49.6068, 52.1509 |
| `denue_available` | int64 | 0 | values: 1 |
| `lodging_establishments` | int64 | 0 | range 0–248; 30 unique |
| `food_beverage_establishments` | int64 | 0 | range 10–5,325; 53 unique |
| `recreation_tourism_proxy` | int64 | 0 | range 0–42; 17 unique |
| `agencies_tours_events` | int64 | 0 | range 0–51; 14 unique |
| `tourist_transport_proxy` | int64 | 0 | values: 0, 1, 2, 3, 4, 6, 8, 9, 10, 20, 28 |
| `tourism_gdp_2022_mxn2018` | float64 | 5 | range 857,070.37–13,309,403,141; 50 unique |
| `tourism_share_proxy_2022` | float64 | 5 | range 0.0039–0.8856; 50 unique |
| `demand_evidence` | str | 0 | categories: No direct demand series in current project data, INAH attraction series, DataTur hotel-center series |
| `model_role_v1` | str | 0 | categories: Undermeasured analog target, Observed anchor / training evidence |
| `coverage_dimensions_n` | int64 | 0 | values: 2, 3, 4 |
| `source_tourism_offer` | str | 0 | categories: https://veracruz.mx/productos.php |
| `source_region` | str | 0 | categories: https://www.veracruz.gob.mx/turismo/regiones-turisticas/ |
| `source_pueblo_magico` | str | 47 | categories: https://www.veracruz.gob.mx/turismo/pueblos-magicos/ |
| `source_inah_visitors` | str | 46 | categories: https://datos.inah.gob.mx/datos-abiertos/visitantes-zonas-arqueologicas |
| `source_inah_location` | str | 45 | categories: https://datos.inah.gob.mx/datos-abiertos/zonas-arqueologicas |
| `source_denue` | str | 0 | categories: https://www.inegi.org.mx/app/descarga/?ti=6 |
| `source_tourism_gdp` | str | 5 | categories: https://datatur.sectur.gob.mx/SitePages/pibturisticoestatalmunicipal.aspx |
| `source_datatur` | str | 51 | categories: https://www.datatur.sectur.gob.mx/SitePages/hoteleria.aspx |
| `curation_version` | str | 0 | categories: 2026-10-06-v1 |
| `official_product_card_count_295` | int64 | 0 | range 0–58; 23 unique |
| `theme_evidence_count` | int64 | 0 | values: 2, 3, 4, 5 |

#### Muestra (primeras filas)

La muestra se limita a las primeras 10 columnas para mantenerla legible; la tabla anterior enumera todas las columnas.

| destination | municipio | clave_municipio | region_turistica_preliminar | pueblo_magico | oferta_turistica_oficial_web | productos_en_extracto_local_n | productos_ejemplo | tourism_tags | theme_beach_coast |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Acajete | Acajete | 30001 | Cultura y Aventura | 0 | 1 | 0 | Sones, Sabores y Tradiciones de Invierno | culture_history; gastronomy; nature | 0 |
| Actopan | Actopan | 30004 | Primeros Pasos de Cortés | 0 | 1 | 7 | Todo Veracruz es Bello \| Quiahuiztlan Cempoala La Antigua Ruta de C… | adventure; archaeology; culture_history; gastronomy | 0 |
| Alvarado | Alvarado | 30011 | Primeros Pasos de Cortés | 0 | 1 | 6 | Todo Veracruz es Bello \| Al sabor de Boka \| Salsas Sones y Danzones 3 | beach_coast; culture_history; gastronomy | 1 |

### `data/processed/destination_master.csv`

**Etapa:** S3 PROCESSED  
**Tamaño actual:** 55 × 48  
**Concepto:** Tabla integrada canónica de los 55 destinos de Veracruz.  
**Límite de interpretación:** Integra perfil, estructura y cobertura de demanda claramente etiquetada sin interpretar ausencia de cobertura como baja demanda.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `destination` | str | 0 | 55 unique; examples: Acajete, Actopan, Alvarado, Atzalan |
| `municipio` | str | 0 | 55 unique; examples: Acajete, Actopan, Alvarado, Atzalan |
| `clave_municipio` | int64 | 0 | range 30,001–30,203; 55 unique |
| `region_turistica_preliminar` | str | 0 | categories: Cultura y Aventura, Primeros Pasos de Cortés, Totonacapan, Altas Montañas, Por verificar, Huasteca, Los Tuxtlas, Olmeca |
| `pueblo_magico` | int64 | 0 | values: 0, 1 |
| `oferta_turistica_oficial_web` | int64 | 0 | values: 1 |
| `productos_en_extracto_local_n` | int64 | 0 | range 0–24; 13 unique |
| `productos_ejemplo` | str | 14 | 31 unique; examples: Sones, Sabores y Tradiciones de Invierno, Todo Veracruz es Bello \\| Quiahuiztlan Cempoala La , Todo Veracruz es Bello \\| Al sabor de Boka \\| Salsas, Todo Veracruz es Bello \\| Al sabor de Boka \\| Aventu |
| `tourism_tags` | str | 0 | 28 unique; examples: culture_history; gastronomy; nature, adventure; archaeology; culture_history; gastronom, beach_coast; culture_history; gastronomy, archaeology; culture_history; gastronomy; nature |
| `theme_beach_coast` | int64 | 0 | values: 0, 1 |
| `theme_nature` | int64 | 0 | values: 0, 1 |
| `theme_culture_history` | int64 | 0 | values: 0, 1 |
| `theme_archaeology` | int64 | 0 | values: 0, 1 |
| `theme_adventure` | int64 | 0 | values: 0, 1 |
| `theme_gastronomy_coffee` | int64 | 0 | values: 0, 1 |
| `theme_wellness_spiritual` | int64 | 0 | values: 0, 1 |
| `theme_urban_services` | int64 | 0 | values: 0, 1 |
| `inah_inventory_sites_n` | int64 | 0 | values: 0, 1, 2 |
| `inah_inventory_sites` | str | 45 | categories: Quiahuiztlán, Cuajilote \\| Vega de la Peña, Cuauhtochco, Castillo de Teayo, Las Limas, Cuyuxquihui \\| El Tajín, Tres Zapotes, San Lorenzo Tenochtitlan, Cempoala, Las Higueras |
| `inah_series_available` | int64 | 0 | values: 0, 1 |
| `inah_series_sites` | str | 46 | categories: Zona Arqueológica de Quiahuitztlán, Zona Arqueológica de Cuajilote \\| Zona Arqueológica de Vega de la Peña, Zona Arqueológica de Cuauhtochco, Zona Arqueológica de Castillo de Teayo con museo de sitio, Zona Arqueológica de Las Limas, Zona Arqueológica de Cuyuxquihui \\| Zona Arqueológica de El Tajín, Zona Arqueológica de San Lorenzo Tenochtitlan con museo de sitio, Zona Arqueológica de Cempoala con museo de sitio, Zona Arqueológica de Las Higueras con museo de sitio |
| `inah_visitors_2025` | float64 | 46 | values: 0, 834, 1,124, 2,428, 4,699, 5,880, 29,186, 31,120, 308,598 |
| `inah_foreign_share_2025` | float64 | 46 | values: 0, 0.0012, 0.0093, 0.0247, 0.0255 |
| `datatur_coverage` | int64 | 0 | values: 0, 1 |
| `datatur_center` | str | 51 | categories: Veracruz-Boca del Río, Coatzacoalcos, Xalapa |
| `datatur_scope_note` | str | 51 | categories: Centro combinado; usar como contexto hotelero, no como dato municipal puro, Centro DataTur |
| `datatur_arrivals_2024` | float64 | 51 | values: 473,350, 739,186, 2,481,563 |
| `datatur_occupancy_2024_pct` | float64 | 51 | values: 48.2382, 49.6068, 52.1509 |
| `denue_available` | int64 | 0 | values: 1 |
| `lodging_establishments` | int64 | 0 | range 0–248; 30 unique |
| `food_beverage_establishments` | int64 | 0 | range 10–5,325; 53 unique |
| `recreation_tourism_proxy` | int64 | 0 | range 0–42; 17 unique |
| `agencies_tours_events` | int64 | 0 | range 0–51; 14 unique |
| `tourist_transport_proxy` | int64 | 0 | values: 0, 1, 2, 3, 4, 6, 8, 9, 10, 20, 28 |
| `tourism_gdp_2022_mxn2018` | float64 | 5 | range 857,070.37–13,309,403,141; 50 unique |
| `tourism_share_proxy_2022` | float64 | 5 | range 0.0039–0.8856; 50 unique |
| `demand_evidence` | str | 0 | categories: No direct demand series in current project data, INAH attraction series, DataTur hotel-center series |
| `model_role_v1` | str | 0 | categories: Undermeasured analog target, Observed anchor / training evidence |
| `coverage_dimensions_n` | int64 | 0 | values: 2, 3, 4 |
| `source_tourism_offer` | str | 0 | categories: https://veracruz.mx/productos.php |
| `source_region` | str | 0 | categories: https://www.veracruz.gob.mx/turismo/regiones-turisticas/ |
| `source_pueblo_magico` | str | 47 | categories: https://www.veracruz.gob.mx/turismo/pueblos-magicos/ |
| `source_inah_visitors` | str | 46 | categories: https://datos.inah.gob.mx/datos-abiertos/visitantes-zonas-arqueologicas |
| `source_inah_location` | str | 45 | categories: https://datos.inah.gob.mx/datos-abiertos/zonas-arqueologicas |
| `source_denue` | str | 0 | categories: https://www.inegi.org.mx/app/descarga/?ti=6 |
| `source_tourism_gdp` | str | 5 | categories: https://datatur.sectur.gob.mx/SitePages/pibturisticoestatalmunicipal.aspx |
| `source_datatur` | str | 51 | categories: https://www.datatur.sectur.gob.mx/SitePages/hoteleria.aspx |
| `curation_version` | str | 0 | categories: 2026-10-06-v1 |

#### Muestra (primeras filas)

La muestra se limita a las primeras 10 columnas para mantenerla legible; la tabla anterior enumera todas las columnas.

| destination | municipio | clave_municipio | region_turistica_preliminar | pueblo_magico | oferta_turistica_oficial_web | productos_en_extracto_local_n | productos_ejemplo | tourism_tags | theme_beach_coast |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Acajete | Acajete | 30001 | Cultura y Aventura | 0 | 1 | 0 | Sones, Sabores y Tradiciones de Invierno | culture_history; gastronomy; nature | 0 |
| Actopan | Actopan | 30004 | Primeros Pasos de Cortés | 0 | 1 | 7 | Todo Veracruz es Bello \| Quiahuiztlan Cempoala La Antigua Ruta de C… | adventure; archaeology; culture_history; gastronomy | 0 |
| Alvarado | Alvarado | 30011 | Primeros Pasos de Cortés | 0 | 1 | 6 | Todo Veracruz es Bello \| Al sabor de Boka \| Salsas Sones y Danzones 3 | beach_coast; culture_history; gastronomy | 1 |

### `data/processed/demand_series.csv`

**Etapa:** S3 PROCESSED  
**Tamaño actual:** 4,372 × 13  
**Concepto:** Tabla mensual estandarizada de demanda observada que reúne registros de DataTur e INAH.  
**Límite de interpretación:** Los tipos de medición permanecen separados y nunca se suman entre sí.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `series_id` | str | 0 | 16 unique; examples: datatur:center:Coatzacoalcos, datatur:center:Veracruz-Boca del Río, datatur:center:Xalapa, inah:site:3110016 |
| `source_system` | str | 0 | categories: DataTur, INAH |
| `date` | str | 0 | 368 unique; examples: 2016-01-01, 2016-02-01, 2016-03-01, 2016-04-01 |
| `year` | int64 | 0 | range 1,996–2,026; 31 unique |
| `month` | int64 | 0 | values: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 |
| `geography_level` | str | 0 | categories: tourism_center, archaeological_site |
| `geography_name` | str | 0 | 16 unique; examples: Coatzacoalcos, Veracruz-Boca del Río, Xalapa, Zona Arqueológica de El Tajín |
| `metric` | str | 0 | categories: hotel_arrivals_total, archaeological_site_visitors_total |
| `value` | float64 | 0 | range 0–300,325; 1,937 unique |
| `unit` | str | 0 | categories: arrivals, visits |
| `measurement_scope` | str | 0 | categories: hotel_center_arrivals, archaeological_site_visits |
| `interpretation_note` | str | 0 | categories: Hotel-center arrivals observed by DataTur. Combined centers such as Veracruz-Boca del Río are not municipal demand totals., Visits to an INAH archaeological site; not total tourism demand for its municipality. |
| `source_table` | str | 0 | categories: data/interim/datatur_veracruz_monthly.csv, data/interim/fact_inah_veracruz_mes.csv |

#### Muestra (primeras filas)

La muestra se limita a las primeras 10 columnas para mantenerla legible; la tabla anterior enumera todas las columnas.

| series_id | source_system | date | year | month | geography_level | geography_name | metric | value | unit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| datatur:center:Coatzacoalcos | DataTur | 2016-01-01 | 2016 | 1 | tourism_center | Coatzacoalcos | hotel_arrivals_total | 27347.0 | arrivals |
| datatur:center:Coatzacoalcos | DataTur | 2016-02-01 | 2016 | 2 | tourism_center | Coatzacoalcos | hotel_arrivals_total | 29156.0 | arrivals |
| datatur:center:Coatzacoalcos | DataTur | 2016-03-01 | 2016 | 3 | tourism_center | Coatzacoalcos | hotel_arrivals_total | 37294.0 | arrivals |

### `data/processed/origin_market_opportunity.csv`

**Etapa:** S3 PROCESSED  
**Tamaño actual:** 25 × 9  
**Concepto:** Evidencia validada de mercados internacionales de origen preparada para el análisis de marketing.  
**Límite de interpretación:** Contexto nacional de entradas aéreas; no evidencia directa de visitantes a Veracruz.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `rank_2025` | int64 | 0 | range 1–25; 25 unique |
| `country_of_residence` | str | 0 | 25 unique; examples: Estados Unidos, Canadá, Reino Unido, Colombia |
| `air_entries_2024` | int64 | 0 | range 39,041–13,709,389; 25 unique |
| `air_entries_2025` | int64 | 0 | range 42,425–14,258,403; 25 unique |
| `share_2025_pct` | float64 | 0 | range 0.2–66.9; 14 unique |
| `growth_2025_vs_2024_pct` | float64 | 0 | range -45.4–30; 25 unique |
| `source_url` | str | 0 | categories: https://www.datatur.sectur.gob.mx/Documentoscompartidos/upm/RES_2025_12.pdf |
| `source_version` | str | 0 | categories: 2025 annual values validated by source in August 2026 |
| `scope_note` | str | 0 | categories: Foreign air-entry events to Mexico by country of residence; not Veracruz-specific demand. |

#### Muestra (primeras filas)

| rank_2025 | country_of_residence | air_entries_2024 | air_entries_2025 | share_2025_pct | growth_2025_vs_2024_pct | source_url | source_version | scope_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Estados Unidos | 13709389 | 14258403 | 66.9 | 4.0 | https://www.datatur.sectur.gob.mx/Documentoscompartidos/upm/RES_202… | 2025 annual values validated by source in August 2026 | Foreign air-entry events to Mexico by country of residence; not Ver… |
| 2 | Canadá | 2522479 | 2843977 | 13.3 | 12.7 | https://www.datatur.sectur.gob.mx/Documentoscompartidos/upm/RES_202… | 2025 annual values validated by source in August 2026 | Foreign air-entry events to Mexico by country of residence; not Ver… |
| 3 | Reino Unido | 426856 | 457712 | 2.1 | 7.2 | https://www.datatur.sectur.gob.mx/Documentoscompartidos/upm/RES_202… | 2025 annual values validated by source in August 2026 | Foreign air-entry events to Mexico by country of residence; not Ver… |

### `outputs/mining/audit/destination_profile_gaps.csv`

**Etapa:** S4 OUTPUT  
**Tamaño actual:** 55 × 16  
**Concepto:** Auditoría de integridad y vacíos documentales de los perfiles de destino.  
**Límite de interpretación:** Un vacío significa falta de evidencia/documentación, no bajo turismo.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `destination` | str | 0 | 55 unique; examples: Acajete, Actopan, Alvarado, Atzalan |
| `municipio` | str | 0 | 55 unique; examples: Acajete, Actopan, Alvarado, Atzalan |
| `region_turistica_preliminar` | str | 0 | categories: Cultura y Aventura, Primeros Pasos de Cortés, Totonacapan, Huasteca, Los Tuxtlas, Olmeca, Altas Montañas |
| `official_product_card_count_295` | int64 | 0 | range 0–58; 23 unique |
| `theme_evidence_count` | int64 | 0 | values: 2, 3, 4, 5 |
| `tourism_gdp_2022_mxn2018` | float64 | 5 | range 857,070.37–13,309,403,141; 50 unique |
| `inah_inventory_sites_n` | int64 | 0 | values: 0, 1, 2 |
| `model_role_v1` | str | 0 | categories: Undermeasured analog target, Observed anchor / training evidence |
| `no_product_cards` | bool | 0 | categories: False, True |
| `region_unresolved` | bool | 0 | categories: False |
| `theme_count_lt3` | bool | 0 | categories: False, True |
| `missing_tourism_gdp` | bool | 0 | categories: False, True |
| `no_inah_inventory` | bool | 0 | categories: False, True |
| `no_direct_demand_series` | bool | 0 | categories: False, True |
| `profile_review_priority` | str | 0 | categories: low, medium |
| `interpretation` | str | 0 | categories: profile-data audit only; missing product cards or demand coverage do not imply low tourism |

#### Muestra (primeras filas)

La muestra se limita a las primeras 10 columnas para mantenerla legible; la tabla anterior enumera todas las columnas.

| destination | municipio | region_turistica_preliminar | official_product_card_count_295 | theme_evidence_count | tourism_gdp_2022_mxn2018 | inah_inventory_sites_n | model_role_v1 | no_product_cards | region_unresolved |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Acajete | Acajete | Cultura y Aventura | 3 | 3 | 887227.282082128 | 0 | Undermeasured analog target | False | False |
| Actopan | Actopan | Primeros Pasos de Cortés | 24 | 4 | 156307315.2128738 | 1 | Observed anchor / training evidence | False | False |
| Alvarado | Alvarado | Primeros Pasos de Cortés | 13 | 3 | 163474640.52611774 | 0 | Undermeasured analog target | False | False |

### `outputs/mining/clustering/cluster_diagnostics.csv`

**Etapa:** S4 OUTPUT  
**Tamaño actual:** 19 × 9  
**Concepto:** Diagnósticos PAM/Gower para distintos valores candidatos de k.  
**Límite de interpretación:** Se usa para comparar ajuste y fragmentación, no para clasificar destinos por importancia.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `k` | int64 | 0 | range 2–20; 19 unique |
| `silhouette` | float64 | 0 | range 0.2841–0.7697; 19 unique |
| `pam_total_dissimilarity` | float64 | 0 | range 0.7–11.5786; 19 unique |
| `smallest_cluster` | int64 | 0 | values: 1, 2, 3, 4, 5, 11, 19 |
| `largest_cluster` | int64 | 0 | values: 9, 11, 12, 14, 17, 23, 28, 36 |
| `median_cluster_size` | float64 | 0 | values: 2, 3, 4, 4.5, 5, 5.5, 7, 9, 11, 13.5, 16, 27.5 |
| `singleton_clusters` | int64 | 0 | values: 0, 1, 2, 3, 4, 5, 6 |
| `recommended` | bool | 0 | categories: False, True |
| `selection_rule` | str | 0 | categories: maximize silhouette among singleton-free PAM solutions; interpretability reviewed separately |

#### Muestra (primeras filas)

| k | silhouette | pam_total_dissimilarity | smallest_cluster | largest_cluster | median_cluster_size | singleton_clusters | recommended | selection_rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 0.2841390749686314 | 11.57857142857143 | 19 | 36 | 27.5 | 0 | False | maximize silhouette among singleton-free PAM solutions; interpretab… |
| 3 | 0.3317776853455557 | 9.97857142857143 | 11 | 28 | 16.0 | 0 | False | maximize silhouette among singleton-free PAM solutions; interpretab… |
| 4 | 0.3447782155999284 | 8.411904761904763 | 5 | 23 | 13.5 | 0 | False | maximize silhouette among singleton-free PAM solutions; interpretab… |

### `outputs/mining/clustering/cluster_membership.csv`

**Etapa:** S4 OUTPUT  
**Tamaño actual:** 55 × 7  
**Concepto:** Pertenencia recomendada a clústeres locales por carácter turístico.  
**Límite de interpretación:** Los clústeres son grupos de similitud, no rutas ni clases de demanda.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `destination` | str | 0 | 55 unique; examples: Acajete, Emiliano Zapata, Jilotepec, Las Vigas de Ramírez |
| `region_turistica_preliminar` | str | 0 | categories: Cultura y Aventura, Huasteca, Primeros Pasos de Cortés, Altas Montañas, Totonacapan, Los Tuxtlas, Olmeca |
| `model_role_v1` | str | 0 | categories: Undermeasured analog target, Observed anchor / training evidence |
| `recommended_k` | int64 | 0 | values: 12 |
| `cluster` | int64 | 0 | values: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 |
| `cluster_medoid` | str | 0 | categories: Acajete, Actopan, Atzalan, Boca del Río, Calcahualco, Cazones de Herrera, Chinameca, Coatepec, Coatzacoalcos, Coscomatepec, Jesús Carranza, Puente Nacional |
| `distance_to_medoid` | float64 | 0 | values: 0, 0.1667, 0.2, 0.3333 |

#### Muestra (primeras filas)

| destination | region_turistica_preliminar | model_role_v1 | recommended_k | cluster | cluster_medoid | distance_to_medoid |
| --- | --- | --- | --- | --- | --- | --- |
| Acajete | Cultura y Aventura | Undermeasured analog target | 12 | 1 | Acajete | 0.0 |
| Emiliano Zapata | Cultura y Aventura | Undermeasured analog target | 12 | 1 | Acajete | 0.0 |
| Jilotepec | Cultura y Aventura | Undermeasured analog target | 12 | 1 | Acajete | 0.0 |

### `outputs/mining/clustering/cluster_profiles.csv`

**Etapa:** S4 OUTPUT  
**Tamaño actual:** 12 × 24  
**Concepto:** Resúmenes legibles de los clústeres locales seleccionados.  
**Límite de interpretación:** Los perfiles describen estructura de similitud, no popularidad observada.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `cluster` | int64 | 0 | values: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 |
| `medoid` | str | 0 | categories: Acajete, Actopan, Atzalan, Boca del Río, Calcahualco, Cazones de Herrera, Chinameca, Coatepec, Coatzacoalcos, Coscomatepec, Jesús Carranza, Puente Nacional |
| `n_destinations` | int64 | 0 | values: 2, 3, 4, 5, 8, 12 |
| `dominant_region` | str | 0 | categories: Cultura y Aventura, Primeros Pasos de Cortés, Totonacapan, Altas Montañas, Olmeca |
| `dominant_region_share` | float64 | 0 | values: 0.5, 0.6, 0.6667, 0.75, 0.8, 1 |
| `members` | str | 0 | categories: Acajete \\| Emiliano Zapata \\| Jilotepec \\| Las Vigas de Ramírez \\| Pánuco \\| Tempoal \\| Tlalnelhuayocan \\| Xalapa, Actopan \\| Carrillo Puerto \\| Ursulo Galván, Atzalan \\| Castillo de Teayo \\| Misantla \\| Papantla \\| Vega de Alatorre, Alvarado \\| Boca del Río \\| Poza Rica de Hidalgo \\| Tuxpan \\| Veracruz, Calcahualco \\| Catemaco \\| Cuitláhuac \\| Fortín \\| Huatusco \\| Jalcomulco \\| La Antigua \\| Perote \\| San Andrés Tuxtla \\| Tlapacoyan \\| Yanga \\| Zongolica, Cazones de Herrera \\| Nautla \\| Tamiahua \\| Tecolutla, Chinameca \\| Jáltipan \\| Las Choapas \\| Soteapan, Coatepec \\| Naolinco \\| Zozocolco de Hidalgo, Coatzacoalcos \\| Minatitlán, Coscomatepec \\| Córdoba \\| Orizaba \\| Xico, Jesús Carranza \\| Santiago Tuxtla \\| Texistepec, Puente Nacional \\| Tlacotalpan |
| `official_product_card_count_295_median` | float64 | 0 | values: 0, 0.5, 1, 1.5, 3, 3.5, 5, 5.5, 13, 14.5, 24 |
| `lodging_establishments_median` | float64 | 0 | values: 4, 5, 6, 8.5, 11, 13, 15, 42, 59, 80 |
| `food_beverage_establishments_median` | float64 | 0 | values: 73, 84, 109, 110.5, 124, 135, 169, 220.5, 310.5, 1,189.5, 1,332, 1,861.5 |
| `recreation_tourism_proxy_median` | float64 | 0 | values: 0, 0.5, 1, 2, 3, 3.5, 5, 8, 12, 17 |
| `agencies_tours_events_median` | float64 | 0 | values: 0, 0.5, 1, 2, 4, 6, 26 |
| `tourist_transport_proxy_median` | float64 | 0 | values: 0, 0.5, 2, 4 |
| `tourism_gdp_2022_mxn2018_median` | float64 | 0 | values: 6,506,333, 43,537,364, 55,780,289, 88,353,083, 102,627,882, 159,044,440, 219,616,854, 312,273,036, 351,807,127, 1,160,149,487, 3,095,490,653, 5,965,859,221 |
| `tourism_share_proxy_2022_median` | float64 | 0 | values: 0.0132, 0.0149, 0.0326, 0.0571, 0.0687, 0.0742, 0.0959, 0.125, 0.2707, 0.3777, 0.3968, 0.549 |
| `inah_inventory_sites_n_median` | float64 | 0 | values: 0, 1 |
| `pueblo_magico_share` | float64 | 0 | values: 0, 0.2, 1 |
| `theme_beach_coast_share` | float64 | 0 | values: 0, 0.1667, 0.3333, 0.8, 1 |
| `theme_nature_share` | float64 | 0 | values: 0, 0.2, 1 |
| `theme_culture_history_share` | float64 | 0 | values: 1 |
| `theme_archaeology_share` | float64 | 0 | values: 0, 1 |
| `theme_adventure_share` | float64 | 0 | values: 0, 0.3333, 0.6667, 1 |
| `theme_gastronomy_coffee_share` | float64 | 0 | values: 0, 0.8333, 1 |
| `theme_wellness_spiritual_share` | float64 | 0 | values: 0, 0.0833 |
| `theme_urban_services_share` | float64 | 0 | values: 0, 0.125, 0.5, 0.8, 1 |

#### Muestra (primeras filas)

La muestra se limita a las primeras 10 columnas para mantenerla legible; la tabla anterior enumera todas las columnas.

| cluster | medoid | n_destinations | dominant_region | dominant_region_share | members | official_product_card_count_295_median | lodging_establishments_median | food_beverage_establishments_median | recreation_tourism_proxy_median |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Acajete | 8 | Cultura y Aventura | 0.75 | Acajete \| Emiliano Zapata \| Jilotepec \| Las Vigas de Ramírez \| Pánu… | 3.0 | 4.0 | 110.5 | 2.0 |
| 2 | Actopan | 3 | Primeros Pasos de Cortés | 0.6666666666666666 | Actopan \| Carrillo Puerto \| Ursulo Galván | 24.0 | 6.0 | 124.0 | 3.0 |
| 3 | Atzalan | 5 | Totonacapan | 0.8 | Atzalan \| Castillo de Teayo \| Misantla \| Papantla \| Vega de Alatorre | 0.0 | 11.0 | 169.0 | 3.0 |

### `outputs/mining/clustering/cluster_medoid_similarity.csv`

**Etapa:** S4 OUTPUT  
**Tamaño actual:** 66 × 6  
**Concepto:** Similitud por pares entre los medoides de los clústeres seleccionados.  
**Límite de interpretación:** Se usa para revisar separación/solapamiento entre grupos.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `cluster_a` | int64 | 0 | values: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 |
| `medoid_a` | str | 0 | categories: Acajete, Atzalan, Calcahualco, Coatepec, Chinameca, Actopan, Boca del Río, Cazones de Herrera, Coatzacoalcos, Coscomatepec, Jesús Carranza |
| `cluster_b` | int64 | 0 | values: 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 |
| `medoid_b` | str | 0 | categories: Atzalan, Calcahualco, Cazones de Herrera, Jesús Carranza, Coscomatepec, Chinameca, Coatepec, Puente Nacional, Coatzacoalcos, Actopan, Boca del Río |
| `gower_distance` | float64 | 0 | values: 0.2, 0.25, 0.3333, 0.4, 0.5, 0.5714, 0.6, 0.6667, 0.7143 |
| `gower_similarity` | float64 | 0 | values: 0.2857, 0.3333, 0.4, 0.4286, 0.5, 0.6, 0.6667, 0.75, 0.8 |

#### Muestra (primeras filas)

| cluster_a | medoid_a | cluster_b | medoid_b | gower_distance | gower_similarity |
| --- | --- | --- | --- | --- | --- |
| 1 | Acajete | 3 | Atzalan | 0.2 | 0.8 |
| 1 | Acajete | 5 | Calcahualco | 0.2 | 0.8 |
| 1 | Acajete | 6 | Cazones de Herrera | 0.2 | 0.8 |

### `outputs/mining/clustering/destination_silhouettes.csv`

**Etapa:** S4 OUTPUT  
**Tamaño actual:** 55 × 5  
**Concepto:** Diagnóstico de silueta por destino para la agrupación seleccionada.  
**Límite de interpretación:** Valores negativos o limítrofes indican ambigüedad, no datos inválidos.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `destination` | str | 0 | 55 unique; examples: Acajete, Emiliano Zapata, Jilotepec, Las Vigas de Ramírez |
| `cluster` | int64 | 0 | values: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 |
| `cluster_medoid` | str | 0 | categories: Acajete, Actopan, Atzalan, Boca del Río, Calcahualco, Cazones de Herrera, Chinameca, Coatepec, Coatzacoalcos, Coscomatepec, Jesús Carranza, Puente Nacional |
| `silhouette` | float64 | 0 | range -0.3333–1; 19 unique |
| `borderline` | bool | 0 | categories: False, True |

#### Muestra (primeras filas)

| destination | cluster | cluster_medoid | silhouette | borderline |
| --- | --- | --- | --- | --- |
| Acajete | 1 | Acajete | 0.8571428571428571 | False |
| Emiliano Zapata | 1 | Acajete | 0.8571428571428571 | False |
| Jilotepec | 1 | Acajete | 0.8571428571428571 | False |

### `outputs/mining/clustering/feature_sensitivity.csv`

**Etapa:** S4 OUTPUT  
**Tamaño actual:** 9 × 4  
**Concepto:** Análisis de sensibilidad de clústeres retirando una variable a la vez.  
**Límite de interpretación:** Muestra qué variables de perfil afectan materialmente la partición.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `removed_feature` | str | 0 | categories: theme_adventure, theme_archaeology, theme_nature, theme_gastronomy_coffee, pueblo_magico, theme_beach_coast, theme_urban_services, theme_culture_history, theme_wellness_spiritual |
| `adjusted_rand_vs_full` | float64 | 0 | values: 0.605, 0.6113, 0.6984, 0.7149, 0.7581, 0.8347, 0.8746, 1 |
| `silhouette_without_feature` | float64 | 0 | values: 0.6404, 0.6471, 0.7202, 0.7479, 0.7647, 0.7756, 0.7762, 0.8002, 0.8066 |
| `singleton_clusters_without_feature` | int64 | 0 | values: 0, 1 |

#### Muestra (primeras filas)

| removed_feature | adjusted_rand_vs_full | silhouette_without_feature | singleton_clusters_without_feature |
| --- | --- | --- | --- |
| theme_adventure | 0.6049816813789373 | 0.7761686404902753 | 1 |
| theme_archaeology | 0.6112829263090541 | 0.7478907794522767 | 1 |
| theme_nature | 0.6984126984126984 | 0.7647384292944548 | 1 |

### `outputs/mining/similarity/undermeasured_anchor_similarity.csv`

**Etapa:** S4 OUTPUT  
**Tamaño actual:** 126 × 8  
**Concepto:** Coincidencias de análogos estructurales entre destinos submedidos y destinos ancla observados.  
**Límite de interpretación:** La similitud no prueba demanda no medida.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `target_destination` | str | 0 | 42 unique; examples: Acajete, Alvarado, Calcahualco, Catemaco |
| `target_region` | str | 0 | categories: Cultura y Aventura, Primeros Pasos de Cortés, Altas Montañas, Los Tuxtlas, Totonacapan, Olmeca, Huasteca |
| `anchor_destination` | str | 0 | 13 unique; examples: Castillo de Teayo, Atzalan, Vega de Alatorre, Boca del Río |
| `anchor_region` | str | 0 | categories: Huasteca, Totonacapan, Primeros Pasos de Cortés, Altas Montañas, Olmeca, Cultura y Aventura |
| `similarity_rank` | int64 | 0 | values: 1, 2, 3 |
| `gower_structural_distance` | float64 | 0 | range 0.1008–0.442; 126 unique |
| `gower_structural_similarity` | float64 | 0 | range 0.558–0.8992; 126 unique |
| `interpretation` | str | 0 | categories: mixed-profile structural analog only; not demand evidence or route feasibility |

#### Muestra (primeras filas)

| target_destination | target_region | anchor_destination | anchor_region | similarity_rank | gower_structural_distance | gower_structural_similarity | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Acajete | Cultura y Aventura | Castillo de Teayo | Huasteca | 1 | 0.1819878183023734 | 0.8180121816976266 | mixed-profile structural analog only; not demand evidence or route … |
| Acajete | Cultura y Aventura | Atzalan | Totonacapan | 2 | 0.2012609599362325 | 0.7987390400637675 | mixed-profile structural analog only; not demand evidence or route … |
| Acajete | Cultura y Aventura | Vega de Alatorre | Totonacapan | 3 | 0.2577809277504969 | 0.7422190722495031 | mixed-profile structural analog only; not demand evidence or route … |

### `outputs/mining/associations/municipality_pair_rules.csv`

**Etapa:** S4 OUTPUT  
**Tamaño actual:** 22 × 10  
**Concepto:** Reglas de asociación basadas en coaparición de municipios en productos turísticos oficiales.  
**Límite de interpretación:** La coaparición en la oferta no equivale a movimiento o co-visita de turistas.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `antecedent` | str | 0 | 14 unique; examples: Tlacotalpan, Coscomatepec, Santiago Tuxtla, Córdoba |
| `consequent` | str | 0 | categories: Alvarado, Orizaba, San Andrés Tuxtla, La Antigua, Ursulo Galván, Coatepec, Xalapa, Catemaco, Actopan, Xico, Veracruz |
| `n_baskets` | int64 | 0 | values: 295 |
| `antecedent_count` | int64 | 0 | range 6–40; 13 unique |
| `consequent_count` | int64 | 0 | values: 13, 21, 22, 24, 28, 29, 31, 35, 40, 48, 58 |
| `pair_count` | int64 | 0 | values: 5, 6, 7, 10, 11, 13, 14, 15, 17, 19, 22, 29 |
| `support` | float64 | 0 | values: 0.0169, 0.0203, 0.0237, 0.0339, 0.0373, 0.0441, 0.0475, 0.0508, 0.0576, 0.0644, 0.0746, 0.0983 |
| `confidence` | float64 | 0 | range 0.5–1; 21 unique |
| `lift` | float64 | 0 | range 2.7387–12.6068; 17 unique |
| `interpretation` | str | 0 | categories: tourism-offer co-occurrence; not tourist movement |

#### Muestra (primeras filas)

| antecedent | consequent | n_baskets | antecedent_count | consequent_count | pair_count | support | confidence | lift | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tlacotalpan | Alvarado | 295 | 9 | 13 | 5 | 0.0169491525423728 | 0.5555555555555556 | 12.606837606837608 | tourism-offer co-occurrence; not tourist movement |
| Coscomatepec | Orizaba | 295 | 8 | 21 | 6 | 0.0203389830508474 | 0.75 | 10.535714285714285 | tourism-offer co-occurrence; not tourist movement |
| Santiago Tuxtla | San Andrés Tuxtla | 295 | 6 | 28 | 5 | 0.0169491525423728 | 0.8333333333333334 | 8.779761904761905 | tourism-offer co-occurrence; not tourist movement |

### `outputs/mining/candidates/undermeasured_candidates.csv`

**Etapa:** S4 OUTPUT  
**Tamaño actual:** 42 × 17  
**Concepto:** Lista priorizada de destinos con evidencia estructural pero medición insuficiente.  
**Límite de interpretación:** No es un ranking de popularidad ni una lista final de rutas.

#### Columnas y valores observados

| Columna | Tipo | Faltantes | Rango / categorías / ejemplos |
| --- | --- | --- | --- |
| `evidence_priority_rank` | int64 | 0 | range 1–42; 42 unique |
| `destination` | str | 0 | 42 unique; examples: Córdoba, Orizaba, Poza Rica de Hidalgo, Minatitlán |
| `region_turistica_preliminar` | str | 0 | categories: Altas Montañas, Totonacapan, Olmeca, Los Tuxtlas, Huasteca, Cultura y Aventura, Primeros Pasos de Cortés |
| `pueblo_magico` | int64 | 0 | values: 0, 1 |
| `tourism_tags` | str | 0 | 21 unique; examples: adventure; culture_history; gastronomy_coffee; her, culture_history; gastronomy; nature; urban_service, culture_history; nature; urban_services, adventure; beach_coast; culture_history; nature |
| `official_product_card_count_295` | int64 | 0 | range 0–48; 19 unique |
| `lodging_establishments` | int64 | 0 | range 0–248; 26 unique |
| `food_beverage_establishments` | int64 | 0 | range 10–2,371; 41 unique |
| `recreation_tourism_proxy` | int64 | 0 | range 0–42; 13 unique |
| `agencies_tours_events` | int64 | 0 | values: 0, 1, 2, 3, 4, 6, 7, 8, 11, 17, 18 |
| `tourist_transport_proxy` | int64 | 0 | values: 0, 1, 2, 3, 4, 9, 10, 20, 28 |
| `tourism_gdp_2022_mxn2018` | float64 | 4 | range 857,070.37–5,965,859,221; 38 unique |
| `tourism_share_proxy_2022` | float64 | 4 | range 0.0039–0.8856; 38 unique |
| `coverage_dimensions_n` | int64 | 0 | values: 2, 3 |
| `model_role_v1` | str | 0 | categories: Undermeasured analog target |
| `tourism_service_establishments` | int64 | 0 | range 10–2,495; 41 unique |
| `ranking_scope` | str | 0 | categories: structural evidence priority; not observed demand or route feasibility |

#### Muestra (primeras filas)

La muestra se limita a las primeras 10 columnas para mantenerla legible; la tabla anterior enumera todas las columnas.

| evidence_priority_rank | destination | region_turistica_preliminar | pueblo_magico | tourism_tags | official_product_card_count_295 | lodging_establishments | food_beverage_establishments | recreation_tourism_proxy | agencies_tours_events |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Córdoba | Altas Montañas | 1 | adventure; culture_history; gastronomy_coffee; heritage; nature; ur… | 8 | 80 | 2371 | 23 | 11 |
| 2 | Orizaba | Altas Montañas | 1 | adventure; culture_history; gastronomy_coffee; heritage; nature; ur… | 21 | 69 | 2112 | 42 | 17 |
| 3 | Poza Rica de Hidalgo | Totonacapan | 0 | culture_history; gastronomy; nature; urban_services | 0 | 80 | 1332 | 8 | 4 |

## Reglas de interpretación que deben mantenerse

- La ausencia de cobertura de DataTur **no** significa baja demanda.
- Los conteos del INAH representan visitas a zonas arqueológicas, no turismo municipal total.
- DENUE y PIB turístico aportan contexto estructural/económico; no miden capacidad de carga ni visitantes.
- Las reglas de asociación representan coaparición en la oferta turística oficial, no movimiento de turistas.
- Los clústeres representan similitud de perfil turístico, no rutas.
- Los análogos estructurales son comparaciones, no prueba de demanda no observada.
- Las tablas derivadas deben regenerarse a partir de las fuentes y scripts activos; resultados históricos no deben convertirse en entradas activas.

Este archivo complementa `docs/DATA_CATALOG.md`: el catálogo es el inventario compacto; este resumen es la versión explicativa y demostrativa para revisión académica.
