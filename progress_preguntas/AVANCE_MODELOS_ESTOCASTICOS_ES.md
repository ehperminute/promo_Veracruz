# Avance de Modelos Estocásticos — Proyecto turístico de Veracruz

**Fecha de corte:** 14 de octubre de 2026. **Estado:** avance metodológico con resultados cuantitativos; aún no es un modelo estocástico completo de movilidad turística.

## 1. Problema que se estudia

El proyecto pretende orientar una campaña para promover experiencias turísticas en Veracruz. Antes de decidir cuándo promocionar un destino, conviene conocer la variabilidad de su demanda. En esta etapa se analiza **la incertidumbre de pronósticos de ocupación hotelera** en los tres centros con series comparables de DataTur: Coatzacoalcos, Xalapa y Veracruz–Boca del Río. No existen observaciones mensuales equivalentes para todos los municipios contemplados en el inventario de experiencias.

## 2. Trabajo realizado

En la etapa S5 se compararon pronósticos mensuales de ocupación con métodos simples y modelos de regresión, incluidos bosques aleatorios. El error de pronóstico se calcula comparando la ocupación prevista con la realmente observada. En S6 se usaron errores obtenidos fuera de la muestra de entrenamiento para construir **intervalos de predicción**: un margen inferior y otro superior alrededor de cada estimación.

La cobertura objetivo es de 90 %. Para comprobar la utilidad del procedimiento se comparó el porcentaje de observaciones reales dentro de los intervalos (**cobertura empírica**) y la amplitud promedio de éstos. Se estudió una calibración fija y alternativas que actualizan los errores con ventanas móviles de 12 y 24 meses, además de una ventana expansiva.

## 3. Resultados observados de enero de 2025 a julio de 2026

| Centro DataTur | Observaciones evaluadas | Intervalo fijo: cobertura | Ventana móvil de 12 meses: cobertura | Amplitud fija media | Amplitud móvil media |
|---|---:|---:|---:|---:|---:|
| Coatzacoalcos | 19 | 13/19 = 68.4 % | 17/19 = 89.5 % | 10.19 pp | 15.72 pp |
| Veracruz–Boca del Río | 15 | 14/15 = 93.3 % | 14/15 = 93.3 % | 24.44 pp | 26.70 pp |
| Xalapa | 19 | 17/19 = 89.5 % | 16/19 = 84.2 % | 21.14 pp | 45.20 pp |

En Coatzacoalcos la ventana móvil se acercó a la cobertura buscada, a costa de intervalos más amplios. En Veracruz–Boca del Río la cobertura permaneció igual, pero la amplitud creció. En Xalapa la cobertura disminuyó mientras el intervalo se hizo mucho más ancho. **No hay evidencia de que una sola estrategia de actualización sea superior en los tres centros.**

## 4. Interpretación y relación con los modelos estocásticos

Los resultados ilustran cómo estudiar la incertidumbre mediante datos históricos y errores observados. Sin embargo, un intervalo basado en cuantiles de errores no equivale automáticamente a una cadena de Markov ni a un proceso de Poisson. Tampoco mide, por sí solo, las decisiones individuales de los turistas o la capacidad máxima de cada destino. La conexión práctica con Investigación de Operaciones sería comunicar escenarios de mayor o menor incertidumbre para los *tres centros medidos*, evitando extrapolaciones a otros municipios.

## 5. Limitaciones y próximos temas

La muestra de evaluación es pequeña (15–19 meses por centro), faltan meses en Veracruz–Boca del Río y los errores pueden cambiar con el tiempo. Los intervalos de ocupación también deben interpretarse dentro del rango físico de 0 a 100 %. En el siguiente avance se puede analizar mediante **bootstrap o simulación Monte Carlo** la estabilidad de la cobertura, pero sólo si se documenta qué se remuestrea o simula y se comprueban los supuestos. Las cadenas de Markov para movimiento turístico necesitarían registros de transiciones que todavía no tenemos.

## 6. Preguntas para el profesor

1. ¿Es aceptable presentar calibración empírica de intervalos como el avance aplicado de Modelos Estocásticos, mientras desarrollamos un componente de simulación?
2. ¿Cómo comparar formalmente métodos de calibración con muestras pequeñas y cambios de régimen?
3. ¿Qué modelo sencillo de simulación sería académicamente apropiado para los datos realmente observados, sin inventar desplazamientos entre municipios?

**Archivos de respaldo:** `stochastic_evidence/s6_rolling_comparison_metrics.csv`, `stochastic_evidence/s6_coverage_metrics.csv`, `stochastic_evidence/s5_new_period_metrics.csv` y scripts S5/S6 del repositorio. Fuente primaria: DataTur, Secretaría de Turismo (https://www.datatur.sectur.gob.mx/). **Estos resultados no demuestran todavía un efecto real de redistribución turística.**
