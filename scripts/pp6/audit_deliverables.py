"""Audit PP6 academic deliverable *completeness* without pretending to grade quality.

Reads the recovered 2026-2 rubric spec and the current repository outputs.
Creates a persistent manifest of evidence present, incomplete and externally unverified.
Does not alter source databases, website files or academic source PDFs.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / 'docs/pp6/original_rubric_spec.json'
OUT = ROOT / 'outputs/pp6_loop'


def check_artifacts(root: Path = ROOT) -> dict:
    rubric = json.loads((root/'docs/pp6/original_rubric_spec.json').read_text(encoding='utf-8'))
    # Conditions are explicit and conservative: existence doesn't mean academic merit.
    slots = [
        ('research_database', 'technical_artifacts', ['data/recovered_source_descriptions/veracruz_pp3_master_with_originals.sqlite'], 'PRESENT', 'Existing restored research database, not a substitute for missing source archives'),
        ('processing_and_analytics_code', 'technical_artifacts', ['scripts/pp6/run_loop.py', 'experiments/pp6_second_pass/run_pass.py'], 'PRESENT', 'Reproducibility must still be tested on clean environments'),
        ('source_provenance', 'technical_artifacts', ['experiments/pp6_second_pass/results/database_audit.json'], 'PARTIAL', 'Raw archival rebuild remains unavailable in compact transfer'),
        ('mining_outputs', 'technical_artifacts', ['experiments/pp6_second_pass/results/s4_evidence_discovery.json'], 'PRESENT', 'Source-supported activity matching, not visitor segmentation'),
        ('ml_evaluation', 'technical_artifacts', ['experiments/pp6_second_pass/results/s5_paired_metrics.csv'], 'PRESENT', 'Paired retrospective benchmark; not validated deployment predictor'),
        ('stochastic_evaluation', 'technical_artifacts', ['experiments/pp6_second_pass/results/s6_interval_audit.json', 'experiments/stochastic/markov_2026/outputs/resumen_validacion_markov.csv'], 'PRESENT', 'Interval and negative Markov results; no invented response probabilities'),
        ('or_optimization', 'technical_artifacts', ['experiments/pp6_second_pass/results/s7_evidence_sensitive_optimization.json'], 'PRESENT', 'Six-placement optimization with illustrative costs'),
        ('campaign_source_ledger', 'campaign', ['experiments/pp6_second_pass/results/s8_campaign_claims_evidence.csv'], 'PRESENT', 'Archived citation checks only; operators/access must be confirmed'),
        ('campaign_test_matrix', 'campaign', ['outputs/marketing/foreign_campaign_test_matrix_v1.csv'], 'PRESENT', 'Planned test cells, not observed campaign data'),
        ('brand_and_buyer_persona', 'campaign', ['docs/MARKETING_SEGMENTATION.md'], 'PARTIAL', 'Existing audience hypotheses; final integrated branding/persona/positioning not certified'),
        ('channel_allocation', 'campaign', ['docs/marketing/foreign_campaign_test_matrix_v1.csv'], 'PARTIAL', 'Hypothetical six-placement budget is not verified allocation across real media prices'),
        ('live_implementation', 'campaign', [], 'EXTERNAL', 'No evidence of completed ads on selected channels; do not invent spend or conversions'),
        ('conversion_impact_tracking', 'campaign', [], 'EXTERNAL', 'Tracking, visit redistribution and environmental impact have not been observed'),
        ('report_draft', 'technical_report', ['outputs/pp6_loop/TECHNICAL_REPORT_DRAFT_ES.md'], 'PARTIAL', 'Draft is not the required 30–40-page technical report and does not contain all 23 sections'),
        ('integrated_colloquium', 'colloquium', [], 'MISSING', 'A final <=15-minute integrated defense deck and speaking plan have not been verified'),
    ]
    items=[]
    for key, prod, paths, if_found, caveat in slots:
        exists = [str(p) for p in paths if (root/p).is_file() and (root/p).stat().st_size>0]
        missing = [str(p) for p in paths if not (root/p).is_file() or (root/p).stat().st_size==0]
        state = if_found if not missing else 'MISSING'
        items.append({'id':key,'product':prod,'state':state,'present_files':exists,'missing_files':missing,'caveat':caveat})
    doc = root / 'outputs/pp6_loop/TECHNICAL_REPORT_DRAFT_ES.md'
    draft = doc.read_text(encoding='utf-8') if doc.is_file() else ''
    result={
        'spec_version':rubric['version'],
        'rubric_criteria':len(rubric['weights']),
        'rubric_weight_total':sum(x[1] for x in rubric['weights']),
        'deliverables_expected':[p['id'] for p in rubric['products']],
        'technical_report_suggested_pages':rubric['products'][1]['suggested_pages_excluding_appendices'],
        'report_current_draft_lines':len(draft.splitlines()),
        'report_sections_required':len(rubric['products'][1]['required_sections']),
        'report_final_certified':False,
        'items':items,
        'state_counts':{s:sum(i['state']==s for i in items) for s in ('PRESENT','PARTIAL','MISSING','EXTERNAL')},
        'conclusion':'This is an inventory and gap audit, NOT a grade or certification of the final academic submission.',
    }
    return result


def main():
    audit=check_artifacts()
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'submission_audit.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    lines=['# PP6 — entrega: auditoría contra la rúbrica original', '',
           '**Resultado:** comprobación de existencia y cobertura, no calificación universitaria.', '',
           'Rúbrica: 11 criterios, 100%; 4 productos. Reporte técnico sugerido: 30–40 páginas.',
           f'Borrador automatizado actual: {audit["report_current_draft_lines"]} líneas (NO es informe final).','',
           '| Elemento | Estado | Acción / limitación |','|---|---|---|']
    for x in audit['items']:
        lines.append(f'| {x["id"]} | {x["state"]} | {x["caveat"]} |')
    lines.extend(['', '## Orden de trabajo',
                  '1. Elaborar campaña integral con buyer persona hipotético rotulado, branding, medios, presupuesto por canal y KPI medibles.',
                  '2. Expandir el borrador técnico hasta cubrir las 23 secciones exigidas; comprobar profundidad y paginación real en DOCX/PDF.',
                  '3. Ensamblar anexo técnico con enlaces a bases, consultas, código, validaciones y métricas conservadas.',
                  '4. Crear la presentación de coloquio <=15 minutos con defensa y participación distribuida.',
                  '5. Reauditar; mantener como EXTERNAL las métricas de implementación no observadas.',
                  '', '**No volver a pedir los PDFs de las rúbricas ni el catálogo ya investigado.**'])
    (OUT/'SUBMISSION_GAP_AUDIT_ES.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Submission audit:',json.dumps(audit['state_counts']))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
