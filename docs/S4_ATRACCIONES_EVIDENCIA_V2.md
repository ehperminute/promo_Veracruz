# Registro de fuentes y atractivos — S4 (versión de investigación 2)

Fecha de esta revisión: **2026-10-09**. No altera ningún dato S4, clúster ni sitio público.

## Qué incluye

- `data/evidence/s4_atractivos_fuentes_v2.csv`: **203 filas** (89 entradas heredadas + **114** nuevas entradas desglosadas de páginas consultadas directamente en esta sesión).
- `data/evidence/s4_log_fuentes_atractivos_v2.csv`: **62 URLs únicas**, algunas de fuentes heredadas y otras consultadas nuevamente. El campo `estado_url` distingue ambos casos.
- `data/evidence/s4_cobertura_destinos_v2.csv`: cobertura por cada uno de los 55 municipios/destinos.
- Estos ficheros son **evidencia de trabajo**, no una base final apta para publicación automática.

## Qué significan los estados

**TEXTO_RESPALDADO_EN_FUENTE_OFICIAL**: se revisó el texto de la ficha municipal indicada y la identificación está respaldada como dato publicado. **No** confirma que esté abierto, sea seguro o accesible hoy.

**PENDIENTE_COTEJO_INDIVIDUAL**: se conservó un registro de la extracción previa, con URL y descripción, pero no se contrastó cada dato en esta sesión. No elevar este estado automáticamente.

## Qué falta

1. Desambiguar municipio frente a localidad exacta y revisar duplicados/entradas compuestas.
2. Confirmar información operativa y si un atractivo tiene acceso público actual.
3. Archivar extractos propios o HTML/PDF de las páginas originales de manera legal cuando estén disponibles (guardar fecha y hash). **Los enlaces no son copias archivadas del contenido.**
4. Auditar los 8 indicadores de S4 contra evidencia explícita y acordar cómo tratar *desconocido*; no convertir ausencia de registro en ausencia de atributo.
5. Obtener fotografías con fuentes y licencias adecuadas antes de publicar.
6. Registrar validaciones independientes y discrepancias para los restantes municipios.

## Cómo usar estos datos

Los nombres de `destino` corresponden al conjunto de trabajo de 55 destinos, que mayormente coincide con municipios administrativos. El campo `atractivo_concreto` es una entidad o experiencia **asociada al municipio**, no implica que esté dentro del casco urbano. Algunas entradas nuevas desagregan entradas anteriores: se conservaron las dos para permitir revisión, **no deben contarse como atractivos únicos sin deduplicar**.

La documentación de procedencia de los insumos originales sigue en `data/reference/source_registry.csv` y `data/reference/destination_profile_sources.csv`. Esta versión añade un registro por afirmación, no los reemplaza.

## Ejemplo de trazabilidad

- Catemaco: la ficha [Municipio=32](https://www.veracruz.mx/destino.php?Municipio=32), secciones *CENTROS TURÍSTICOS* y *GASTRONOMÍA*, presenta Laguna de Catemaco, Nanciyaga, Sontecomapan y playas municipales, además de gastronomía local. Eso sostiene que debamos **reexaminar** `theme_beach_coast` y `theme_gastronomy_coffee` actualmente codificados 0; todavía hace falta una regla clara para incorporar cambios a S4.
- Coatepec: la ficha [Municipio=38](https://www.veracruz.mx/destino.php?Municipio=38) nombra patrimonio, museos y cascadas.
- Papantla: la ficha [Municipio=124](https://www.veracruz.mx/destino.php?Municipio=124) enumera El Tajín y Cuyuxquihui.

**No inventamos escalas de dominancia ni puntuaciones 0–3.** Tampoco reemplazamos el cálculo de PAM: primero se resuelven los problemas de evidencia y definición geográfica.
