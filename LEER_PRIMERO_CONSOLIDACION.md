# Veracruz PP — paquete consolidado de resultados

**Corte:** 19 de octubre de 2026 · **Estado:** reporte académico y experimentos reproducibles. No es una actualización del mapa ni una modificación a la web.

## Por qué este archivo reemplaza varios ZIP de análisis

Consolida **sin sustituir resultados anteriores**:

1. **Minería de Datos:** `docs/mining/S4_DATA_MINING_FINDINGS.md`, `category_pair_audit.csv` y `audit_activity_pairs.py` (36 pruebas de asociación y corrección por comparaciones múltiples).
2. **Minería + Mercadotecnia:** `experiments/marketing/2026-10-19/` con la base SQLite congelada, las 40 decisiones revisadas de 14 municipios, cobertura 61→75, seis propuestas publicitarias, datos, código y reporte Word/PDF.
3. **Modelos Estocásticos:** el reporte en `progress_preguntas/` y el experimento original en `experiments/stochastic/markov_2026/` (incluido para evitar otra descarga independiente).
4. **Investigación de Operaciones — NUEVO:** `experiments/or/infrastructure_tradeoff_2026-10-19/` con comparación exacta entre variedad documentada e infraestructura hotelera, CSV y código reproducible.

La base SQLite está incluida **una sola vez**. Todos los archivos del proyecto original quedan intactos; el paquete no cambia `site/`, el optimizador del sitio, rutas ni scripts de producción.

## Qué resultado es válido para qué pregunta

| Pregunta | Usar | No afirmar |
|---|---|---|
| ¿Dónde tenemos evidencia turística? | Cobertura documental de 75 municipios | Que los 75 tengan reservas o servicios turísticos activos |
| ¿Qué temas suelen figurar juntos? | 36 pares del catálogo aceptado de 61 municipios | Que reflejen preferencias reales de viajeros; ningún par pasó la corrección |
| ¿Qué seis lugares maximizan variedad? | Cartera original: 47 tipos | Que esa cartera maximice visitas o retorno económico |
| ¿Qué sucede si priorizamos infraestructura receptiva? | Nueva comparación MILP, 47→43 tipos y 139→386 establecimientos | Que establecimientos = popularidad o demanda observada |
| ¿Cómo cambia la ocupación mensual? | Markov/S5–S6 donde hay DataTur | Que predice demanda municipal o rutas reales del turista |

**Importante:** los 14 nuevos municipios se incorporaron a la cobertura documental, **no** como 40 nuevos registros homogéneos en la matriz de actividades de la prueba de asociación o en la optimización exacta. Es un criterio de comparabilidad, no una omisión silenciosa.

## Uso sin ejecutar código

1. Descarga y **guarda el ZIP**. No necesitas Codespaces para leerlo.
2. Abre el informe `experiments/marketing/2026-10-19/Informe_Mineria_y_Mercadotecnia_Veracruz.pdf` y `experiments/or/infrastructure_tradeoff_2026-10-19/RESULTADOS.md`.
3. Si deseas añadirlos al repositorio, coloca el ZIP en la raíz de `promo_Veracruz` y ejecuta solamente:
   ```bash
   unzip -o VERACRUZ_ANALISIS_CONSOLIDADO_Y_EXPERIMENTO_2026-10-19.zip
   ```
   No requiere ejecución adicional para visualizar o conservar resultados.

## Advertencias metodológicas

- Los MX$5,000 por lugar son costo **supuesto**, sin cotización comercial.
- Los alojamientos de DENUE son un **indicador de oferta**, no un conteo de viajeros.
- Series DataTur miden centros hoteleros concretos; visitas INAH miden sitios determinados. No extrapolar automáticamente a los demás municipios.
- No hay una campaña ejecutada, CTR real, reservas ni aumento causal de visitantes.
- Los registros originales de 216 relaciones actividad–municipio no se han reescrito.
