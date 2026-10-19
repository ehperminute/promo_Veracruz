# Veracruz: evidencia geográfica y resultados para el informe integrador

**Proyecto:** Inteligencia turística y planeación de campañas en Veracruz  
**Fecha del corte:** 18 de octubre de 2026  
**Áreas vinculadas:** Minería de Datos; Investigación de Operaciones; Métodos Estocásticos; Mercadotecnia Digital.

## Resumen ejecutivo

Se construyó una base turística relacional que conserva los documentos originales y vincula municipios, actividades, productos, fuentes y evidencias. El análisis más reciente no sustituye esa base. Utiliza 212 municipios como universo geográfico, 216 relaciones aceptadas municipio–actividad en 61 municipios y una revisión complementaria de 40 referencias turísticas en 14 municipios anteriormente insuficientemente documentados. De las 40 referencias, 26 corresponden a sitios físicos o áreas geográficas, siete a eventos, cinco a actividades o prácticas distribuidas, una a patrimonio arqueológico sin acceso público confirmado y una se descartó como atractivo individual.

Para el mapa se contrastaron las 26 referencias físicas con fuentes geográficas publicadas: diez cuentan con una entidad cartografiada identificable, tres ya aparecían en el mapa actual y siete se incorporan mediante el instalador adjunto. Las 16 restantes permanecen en investigación, sin coordenadas inventadas. Ningún punto nuevo se declara entrada vehicular validada.

En la parte analítica se reproduce una comparación real entre optimización de cobertura y selección aleatoria: al elegir seis municipios, la cobertura máxima del modelo es de 47 tipos de actividad, frente a una media de 17.70 en 5,000 selecciones aleatorias independientes. Las cifras no estiman visitantes ni retorno de inversión.

## 1. Fuentes y unidad de análisis

- **Unidad geográfica:** 212 municipios del registro estatal; NO equivale a 212 sitios turísticos.
- **Unidad temática aceptada:** 216 pares municipio–actividad de `s4_statewide_evidence_pairs_v1`, distribuidos en 61 municipios.
- **Investigación complementaria:** 40 referencias documentadas de 14 municipios en `external_14_tourism_evidence_reviewed`. Se mantienen separadas de las 216 relaciones ya aceptadas para permitir una comparación antes/después, sin alterar retrospectivamente los resultados.
- **Puntos geográficos nuevos:** siete sitios o áreas con referencias en servicios cartográficos basados en OpenStreetMap/GeoNames. Su localización no implica operación turística actual.
- **Registros de soporte:** 295 productos del catálogo, 49 registros de lugares nombrados, 151 leads culturales/geográficos, con posibles repeticiones entre inventarios; no son 495 atracciones únicas.

## 2. Minería de Datos: cobertura, clasificación y sesgo documental

El problema analítico no consiste solo en agrupar lugares; primero hay que decidir qué representa cada registro. El catálogo contiene lugares puntuales, áreas naturales, actividades, festivales y productos turísticos compuestos. Tratar todas estas entidades como puntos individuales o como un mismo tipo de atractivo produce información engañosa.

La revisión clasificó 40 nuevas referencias: 26 sitios/áreas, siete eventos, cinco experiencias distribuidas, un sitio arqueológico con acceso no acreditado y un registro demasiado general. La distribución demuestra que la extracción de entidades debe distinguir entre **tipo de evidencia** y **tipo de experiencia**. Además, los 14 municipios tenían infraestructura de alojamiento registrada, pese a no tener actividades aceptadas en esta tabla. Por tanto, un valor cero en la base de evidencias no representa ausencia comprobada de turismo.

**Aplicaciones del área:** auditoría de cobertura, clasificación de registros, normalización de topónimos, resolución de duplicados, control de procedencia, y futura evaluación de agrupamientos con perfiles enriquecidos. Los agrupamientos anteriores hechos sobre subconjuntos reducidos no deben extrapolarse automáticamente al catálogo recuperado.

## 3. Investigación de Operaciones: cobertura máxima bajo presupuesto

La formulación básica utiliza variables binarias `x_m` (promocionar o no el municipio m) y `y_a` (cubrir o no la actividad a). Con costo **hipotético** de $5,000 MXN por municipio, el presupuesto impone `5000 Σ x_m ≤ B`; una actividad se considera cubierta si por lo menos un municipio seleccionado la tiene documentada. Se maximiza `Σ y_a`. El criterio es diversidad **documentada**, no popularidad, demanda ni rentabilidad.

| Presupuesto MXN | Municipios seleccionados | Cobertura exacta de tipos | Cobertura por selección codiciosa |
|---:|---:|---:|---:|
| 30,000 | 6 | 47 | 47 |
| 60,000 | 12 | 62 | 62 |
| 100,000 | 20 | 72 | 72 |
| 200,000 | 40 | 78 | 78 |

Resultados tomados de `or_statewide_scenario_results` (universo estatal y 61 municipios elegibles). La coincidencia de la heurística codiciosa con el exacto en estos cuatro escenarios no demuestra que siempre sea óptima.

Se desarrolló además una sensibilidad de calidad de evidencia: al priorizar fragmentos originales de las fuentes, en el escenario de 30,000 MXN se cubren 39 tipos en vez de 47, mientras que el número de tipos respaldados por pasajes originales sube de 14 a 19. Esto representa un intercambio entre amplitud de oferta y respaldo documental. No es una comparación causal de eficacia publicitaria.

## 4. Métodos Estocásticos: simulación Monte Carlo reproducible

Para conocer cuánto mejora la optimización respecto de una política sin información, se simularon **5,000 selecciones aleatorias uniformes sin reemplazo por presupuesto** entre los 61 municipios con evidencia aceptada. Se mantuvo el mismo número de municipios de cada escenario. Semilla fija: `20261018`.

| Presupuesto MXN | Cobertura exacta | Media aleatoria | Desv. est. | Rango percentil 2.5–97.5 |
|---:|---:|---:|---:|---:|
| 30,000 | 47 | 17.70 | 6.16 | 7–31 |
| 60,000 | 62 | 29.90 | 6.26 | 18–42 |
| 100,000 | 72 | 41.78 | 6.05 | 30–53 |
| 200,000 | 78 | 62.19 | 4.67 | 52–70 |

Ninguna de las 5,000 selecciones aleatorias de cada presupuesto alcanzó el óptimo exacto; ello describe únicamente este procedimiento experimental, no una probabilidad poblacional sobre la demanda turística. La aleatoriedad proviene de la estrategia de selección, **no de un modelo estocástico del comportamiento de viajeros**.

**Pendiente para la materia:** modelar incertidumbre de demanda a partir de errores históricos de pronóstico y periodos de la serie DataTur, y utilizar escenarios de tiempo de viaje. Los archivos históricos de pronóstico S5 existen en la trayectoria del proyecto, pero no se reprocesaron para este reporte y no se deben mezclar con la simulación anterior.

## 5. Mercadotecnia Digital: de cobertura a segmentación útil

La evidencia permite construir propuestas por tema (naturaleza, agua, patrimonio, gastronomía y aventura) y por región sin inventar puntajes de satisfacción. La estrategia de cobertura maximiza el **portafolio comunicable** dentro de un presupuesto, mientras que una estrategia comercial madura también necesitaría canales, alcance, costos observados, conversiones y preferencias de audiencias.

Una campaña orientada a la oferta cultural puede seleccionar lugares con patrimonio corroborado y elaborar mensajes basados en sus fuentes; una campaña de aventura necesita además verificar condiciones operativas y seguridad. El mapa y sus guías son un producto de comunicación, **no una prueba de aumento en las visitas**.

## 6. Cartografía y soporte de rutas

Se cotejaron las 26 atracciones/áreas identificadas en la investigación complementaria. Diez tienen geometría cartografiada diferenciable: tres ya estaban en el sitio y siete quedan listas para incorporarse. Otras 16 siguen sin un punto fiable. Algunas búsquedas devolvieron homónimos o localidades vecinas en lugar del atractivo; esos casos se excluyen del mapa.

El `geographic_audit_26.csv` conserva el nombre, estatus, coordenadas cuando existen y fuente geográfica. Ninguno de estos diez puntos es **entrada vehicular verificada**. No deben convertirse automáticamente en nodos de un problema de rutas para turistas; esa etapa requiere encontrar accesos, red vial conectada y distancias calculadas.

## 7. Alcances, límites y entregables comprobables

**Listo para sustentar en el informe:** (i) normalización y auditoría de coberturas de datos; (ii) formulación de cobertura con presupuesto y comparación exacto–codicioso; (iii) experimento Monte Carlo con distribución y percentiles; (iv) segmentación de ofertas y límites de la inferencia de demanda; (v) procedencia geográfica y control de calidad.

**No probado todavía:** popularidad municipal derivada de visitantes, retorno de inversión de publicidad, acceso vigente de cada atractivo, rutas estatales verificadas por entrada, optimización estocástica de tráfico, causalidad entre campaña y afluencia, o validez general de los clústeres antiguos.

## Fuentes y reproducibilidad

- Base de referencia: `veracruz_master_with_verified_evidence.sqlite`, tablas `municipalities`, `s4_statewide_evidence_pairs_v1`, `external_14_tourism_evidence_reviewed`, `or_statewide_scenario_results`.
- Comparación de calidad documental: `VERACRUZ_OR_EVIDENCE_STABILITY_2026-10-18/results/REPORT.md`.
- Monte Carlo reproducible: `reproduce_monte_carlo.py`, `monte_carlo_draws.csv` y `monte_carlo_summary.csv`.
- Verificación espacial por registro: `geographic_audit_26.csv`, con enlaces individuales a los registros OSM/Mapcarta.
- Fuente institucional complementaria de la Casa de Cultura en Lerdo de Tejada: https://sic.cultura.gob.mx/ficha.php?table=centro_cultural&table_id=3162 (domicilio publicado, sin punto cartográfico independiente).
- No se crearon coordenadas para sitios ambiguos. Cualquier nuevo mapa debe conservar la bandera `mapped_site` o `mapped_area` y la advertencia de acceso no comprobado.

**Conclusión:** El proyecto ya cuenta con un soporte cuantitativo demostrable en cuatro áreas, aunque no todas las preguntas de turismo están resueltas. La diferencia entre cobertura aceptada, existencia física, entrada turística y demanda real es una parte esencial de la calidad del modelo, no una deficiencia que deba ocultarse mediante marcadores inventados.
