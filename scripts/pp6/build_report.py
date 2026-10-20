"""Generate a Spanish source-linked technical draft from validated PP6 artifacts.

Not a rubric-certified submission, not a statistical inference about unmeasured demand.
"""
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / 'experiments/pp6_second_pass/results'
OUT = ROOT / 'outputs/pp6_loop/TECHNICAL_REPORT_DRAFT_ES.md'

def read(name):
    return json.loads((RESULTS/name).read_text(encoding='utf-8'))

def pct(value):
    return f'{value*100:.1f}%'

def main():
    db=read('database_audit.json')
    s4=read('s4_evidence_discovery.json')
    s5=read('s5_paired_interpretation.json')
    s6=read('s6_interval_audit.json')
    s7=read('s7_evidence_sensitive_optimization.json')
    rows=[]
    with (ROOT/'outputs/marketing/foreign_campaign_test_matrix_v1.csv').open(encoding='utf-8-sig', newline='') as f:
        rows=list(csv.DictReader(f))
    if not (db['municipalities']==212 and len(rows)==24 and s5['paired_predictions']==52):
        raise ValueError('Missing verified inputs; no report will be generated')
    baseline=next(x for x in s5['comparison'] if x['baseline']=='three_month_mean')
    selected=s7['all_documented']
    markov=json.loads((ROOT/'experiments/stochastic/markov_2026/outputs/metadata.json').read_text(encoding='utf-8'))['overall']
    text=['# Inteligencia turística de Veracruz — informe técnico automatizado (borrador)',
      '',
      '**Estado:** borrador técnico producido a partir de resultados comprobados. No certifica la rúbrica docente ni representa una campaña ejecutada.',
      '',
      '## 1. Problema y alcance',
      'Estudiar cómo identificar experiencias turísticas documentadas y asignar recursos promocionales hipotéticos sin confundir oferta publicada, afluencia observada y comportamiento de compradores.',
      '',
      '## 2. Datos y trazabilidad',
      f'La base fuente-restaurada contiene {db["municipalities"]} municipios, {db["accepted_specific_activity_pairs"]} relaciones estrictas municipio–actividad ({db["municipalities_with_specific_activity_pairs"]} municipios y {db["specific_activity_types"]} actividades específicas). {db["pairs_with_recorded_original_text_support"]} relaciones registran respaldo de texto original, y se recuperaron {db["original_product_descriptions_restored"]} descripciones de fichas. Esta cobertura es documental, no un censo de actividad turística.',
      'La investigación vigente también conserva la revisión tipada de 14 municipios en una base auditada aparte. No se combina indiscriminadamente con las 216 relaciones homogéneas, pues incluye sitios, eventos y experiencias regionales de unidades distintas.',
      '',
      '## 3. Minería de datos y descubrimiento de experiencias',
      'El prototipo permite buscar coincidencias exactas entre actividades específicas, conservando identificadores de evidencia y enlaces a las fuentes. Las actividades no encontradas se consideran no documentadas, no inexistentes.',
      f'Para el portafolio de seis municipios, {s4["campaign_links_with_original_text_support"]} de {s4["campaign_distinct_feature_links"]} enlaces de actividades tienen respaldo registrado de texto original. La segmentación antigua de 55 destinos sigue siendo exploratoria y no define la base municipal actual.',
      '',
      '## 4. Aprendizaje automático',
      f'Se contrastaron modelos en las mismas {s5["paired_predictions"]} observaciones centro-mes. El bosque aleatorio obtuvo MAE {baseline["forest_mae_pp"]:.3f} puntos porcentuales y el promedio de los tres meses previos, MAE {baseline["baseline_mae_pp"]:.3f}. La diferencia ({baseline["improvement_pp"]:.3f} pp) no justifica declarar superioridad operativa; el intervalo exploratorio de remuestreo abarca valores negativos.',
      'Estos datos corresponden a ocupación hotelera medida en centros seleccionados, no a demanda por experiencia, sitio o municipio.',
      '',
      '## 5. Métodos estocásticos',
      'Se contrastó cobertura observada y amplitud de intervalos históricos. Ampliar un intervalo puede aumentar la cobertura pero no mejora necesariamente su utilidad para decisiones; las diferencias dependen del centro.',
      '',
      '| Centro | Cobertura fija | Amplitud fija (pp) | Cobertura móvil 12 | Amplitud móvil 12 (pp) |',
      '|---|---:|---:|---:|---:|']
    for x in s6['by_center']:
        text.append(f'| {x["center"]} | {pct(x["fixed_coverage"])} | {x["fixed_width_pp"]:.2f} | {pct(x["rolling12_coverage"])} | {x["rolling12_width_pp"]:.2f} |')
    text += ['',
      f'La cadena de Markov acertó {markov["markov_correct"]} de {markov["test_n"]} transiciones ({markov["markov_accuracy"]*100:.0f}%), igual que persistencia ({markov["persistence_correct"]}/{markov["test_n"]}). Un resultado sin mejora es también relevante.',
      '',
      '## 6. Investigación de Operaciones',
      f'La solución exacta de cobertura selecciona {selected["selected_n"]} municipios: {", ".join(selected["selected_municipalities"])}. Cubre {selected["objective_types_covered"]} tipos distintos con presupuesto supuesto de MXN {selected["budget_mxn"]:,} y seis inserciones de MXN 5,000 cada una. La restricción de respaldo textual conserva {s7["strict_original_text"]["objective_types_covered"]} tipos representados.',
      'El objetivo es cobertura documental, no retorno de inversión, afluencia esperada ni ruta óptima; faltan precios comerciales, accesos y capacidad real.',
      '',
      '## 7. Mercadotecnia digital',
      f'Existen {len(rows)} celdas de prueba propuesta, exportadas de un documento editorial preexistente. Los intereses de las audiencias son hipótesis; aún no hay clics, conversiones ni resultados atribuidos a publicidad real. La auditoría vincula {s4["campaign_links_with_original_text_support"]} de {s4["campaign_distinct_feature_links"]} relaciones del portafolio con respaldo documental.',
      '',
      '## 8. Límites, decisiones y trabajo pendiente',
      'La reproducción completa desde fuentes congeladas no fue posible en este paquete reducido porque se excluyeron archivos ZIP oficiales. La integridad de la base recuperada y las comprobaciones de investigación sí se ejecutaron.',
      'La publicación de las propuestas necesitaría comprobar actualidad de horarios, accesos, permisos, disponibilidad, costos reales y medición digital. Los reportes por materia requieren cotejo específico con cada rúbrica.',
      '',
      '## 9. Ubicación de la evidencia reproducible',
      '- Base restaurada: `data/recovered_source_descriptions/veracruz_pp3_master_with_originals.sqlite`',
      '- Auditoría y resultados S4–S8: `experiments/pp6_second_pass/results/`',
      '- Matriz propuesta original: `docs/marketing/foreign_campaign_test_matrix_v1.csv`',
      '- Comprobaciones y registro de bloqueos: `outputs/pp6_loop/state.json` y `docs/PP6_BLOCKERS.md`',
      '',
      '**Nota:** las cifras reflejan la versión de los datos analizada; cualquier reconstrucción posterior debe volver a calcular las tablas y el informe antes de entrega.',
      '']
    OUT.parent.mkdir(exist_ok=True, parents=True)
    OUT.write_text('\n'.join(text),encoding='utf-8')
    print('PASS: technical draft generated from verified outputs at',OUT.relative_to(ROOT))

if __name__=='__main__':
    main()
