# S7 — Investigación de Operaciones: explicación y alineación académica

## Qué se resuelve
Una autoridad turística debe seleccionar **destinos y temporadas de promoción** con presupuesto limitado. El prototipo considera 55 destinos de Veracruz y cuatro temporadas. La salida es una propuesta de asignación, **no** una previsión de turistas o de retorno de inversión.

## Conexión documental
La *Planeación Didáctica de Investigación de Operaciones* (2026-2), bloque B, pide formular variables de decisión, objetivo y restricciones; contempla programación lineal, simplex, programación entera, objetivos múltiples y análisis de sensibilidad, e incluye expresamente el caso de asignar presupuesto publicitario entre destinos, temporadas y canales. El *Problema Prototípico* pide optimización de recursos para una campaña basada en datos turísticos. No basta con mostrar el sitio: debe entregarse una explicación del modelo, cálculos, sensibilidad y limitaciones.

## Modelo comprensible
- Para cada destino `i` y temporada `t`, `x[i,t] = 1` significa incluir esa promoción y `0` significa no incluirla.
- Restricción presupuestaria: suma de costos multiplicados por selecciones <= presupuesto establecido.
- Restricción de calendario: no programar más promociones que el límite especificado; reglas adicionales deben justificarse.
- Objetivo actual del prototipo: favorecer cobertura de regiones, cobertura de categorías de experiencia y evidencia de oferta/servicios; penalizar demanda elevada solo cuando hay indicadores comparables.
- Ejemplo: dos opciones cuestan $5,000 cada una. Si el presupuesto es $5,000, solo cabe una. El método compara cuál agrega más cobertura según sus reglas.
- No sabemos el retorno ni la conversión de anuncios. El costo uniforme de $5,000 es un supuesto didáctico.

## Método y simpleza
Como cada selección es sí/no, corresponde **programación entera/binaria**. El simplex convencional permite cantidades fraccionarias; no resuelve por sí solo las restricciones binarias. La presentación puede añadir una pequeña relajación lineal para demostrar cómo se relaciona con simplex, pero **no debe afirmar que el programa utiliza simplex sin verificar el código**.

## Validación pendiente para la evidencia formal
1. Auditar función objetivo y restricciones en el código original del S7 (no se incluyen en este pequeño parche de sitio).
2. Comparar contra un método sencillo con los mismos datos y presupuestos.
3. Variar presupuestos, costos supuestos y prioridades para medir sensibilidad; presentar el cambio en cobertura y destinos elegidos.
4. Registrar fuentes/fechas del indicador de ocupación; un dato faltante no indica poca demanda.
5. Distinguir escenarios de campaña de resultados reales: el sitio visualiza escenarios precalculados y **no** ejecuta un solver en vivo ni comprueba ROI.

## Qué hace este parche
Añade enlace `Campaign Planner` al menú existente (traducciones EN/ES/JA) y página `site/planner.html` con escenarios precalculados. **Es una visualización académica, no la evidencia completa de Investigación de Operaciones.**
