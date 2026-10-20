# Inteligencia turística de Veracruz — informe técnico automatizado (borrador)

**Estado:** borrador técnico producido a partir de resultados comprobados. No certifica la rúbrica docente ni representa una campaña ejecutada.

## 1. Problema y alcance
Estudiar cómo identificar experiencias turísticas documentadas y asignar recursos promocionales hipotéticos sin confundir oferta publicada, afluencia observada y comportamiento de compradores.

## 2. Datos y trazabilidad
La base fuente-restaurada contiene 212 municipios, 216 relaciones estrictas municipio–actividad (61 municipios y 78 actividades específicas). 173 relaciones registran respaldo de texto original, y se recuperaron 295 descripciones de fichas. Esta cobertura es documental, no un censo de actividad turística.
La investigación vigente también conserva la revisión tipada de 14 municipios en una base auditada aparte. No se combina indiscriminadamente con las 216 relaciones homogéneas, pues incluye sitios, eventos y experiencias regionales de unidades distintas.

## 3. Minería de datos y descubrimiento de experiencias
El prototipo permite buscar coincidencias exactas entre actividades específicas, conservando identificadores de evidencia y enlaces a las fuentes. Las actividades no encontradas se consideran no documentadas, no inexistentes.
Para el portafolio de seis municipios, 65 de 66 enlaces de actividades tienen respaldo registrado de texto original. La segmentación antigua de 55 destinos sigue siendo exploratoria y no define la base municipal actual.

## 4. Aprendizaje automático
Se contrastaron modelos en las mismas 52 observaciones centro-mes. El bosque aleatorio obtuvo MAE 5.593 puntos porcentuales y el promedio de los tres meses previos, MAE 5.665. La diferencia (0.071 pp) no justifica declarar superioridad operativa; el intervalo exploratorio de remuestreo abarca valores negativos.
Estos datos corresponden a ocupación hotelera medida en centros seleccionados, no a demanda por experiencia, sitio o municipio.

## 5. Métodos estocásticos
Se contrastó cobertura observada y amplitud de intervalos históricos. Ampliar un intervalo puede aumentar la cobertura pero no mejora necesariamente su utilidad para decisiones; las diferencias dependen del centro.

| Centro | Cobertura fija | Amplitud fija (pp) | Cobertura móvil 12 | Amplitud móvil 12 (pp) |
|---|---:|---:|---:|---:|
| Coatzacoalcos | 68.4% | 10.19 | 89.5% | 15.72 |
| Veracruz-Boca del Río | 93.3% | 24.44 | 93.3% | 26.70 |
| Xalapa | 89.5% | 21.14 | 84.2% | 45.20 |

La cadena de Markov acertó 8 de 20 transiciones (40%), igual que persistencia (8/20). Un resultado sin mejora es también relevante.

## 6. Investigación de Operaciones
La solución exacta de cobertura selecciona 6 municipios: Atlahuilco, Catemaco, Coatepec, Fortín, Papantla, San Andrés Tuxtla. Cubre 47 tipos distintos con presupuesto supuesto de MXN 30,000 y seis inserciones de MXN 5,000 cada una. La restricción de respaldo textual conserva 47 tipos representados.
El objetivo es cobertura documental, no retorno de inversión, afluencia esperada ni ruta óptima; faltan precios comerciales, accesos y capacidad real.

## 7. Mercadotecnia digital
Existen 24 celdas de prueba propuesta, exportadas de un documento editorial preexistente. Los intereses de las audiencias son hipótesis; aún no hay clics, conversiones ni resultados atribuidos a publicidad real. La auditoría vincula 65 de 66 relaciones del portafolio con respaldo documental.

## 8. Límites, decisiones y trabajo pendiente
La reproducción completa desde fuentes congeladas no fue posible en este paquete reducido porque se excluyeron archivos ZIP oficiales. La integridad de la base recuperada y las comprobaciones de investigación sí se ejecutaron.
La publicación de las propuestas necesitaría comprobar actualidad de horarios, accesos, permisos, disponibilidad, costos reales y medición digital. Los reportes por materia requieren cotejo específico con cada rúbrica.

## 9. Ubicación de la evidencia reproducible
- Base restaurada: `data/recovered_source_descriptions/veracruz_pp3_master_with_originals.sqlite`
- Auditoría y resultados S4–S8: `experiments/pp6_second_pass/results/`
- Matriz propuesta original: `docs/marketing/foreign_campaign_test_matrix_v1.csv`
- Comprobaciones y registro de bloqueos: `outputs/pp6_loop/state.json` y `docs/PP6_BLOCKERS.md`

**Nota:** las cifras reflejan la versión de los datos analizada; cualquier reconstrucción posterior debe volver a calcular las tablas y el informe antes de entrega.
