# S8 — Veracruz cultural evidence: expanded audit (12 October 2026)

## Question and rule
The original S4 table marked all 55 destinations as culture/history. We tested whether that was supported by **specific named heritage, festivals, museums, dances, buildings or locally documented traditions**, not simply historical background or generic references to culture. Findings are **evidence of cultural features**, not proof of visitor-ready activities.

## Results
- **55/55** have at least one named cultural feature or event in the expanded review (40 substantiated with newly located named examples; 15 retained from the earlier conservative audit). This reverses the earlier finding of only 20 substantiated destinations, which was based on an incomplete source pass.
- **26/55** have an identifiable experience type with potential marketing relevance for follow-up, versus **29/55** for which the named feature is insufficient on its own to promise a visitor experience. This is an editorial triage, *not* a statistical model or confirmation of operating tours.
- **0/55** have been independently confirmed in this review as currently operating/bookable commercial cultural products. That is a missing-verification count, not an absence count.
- S4's universal culture flag may be reasonable if it means **at least one cultural feature exists**, but is nearly useless for discriminating tourist interests. We therefore recommend distinct subtypes and evidence/readiness fields for S8 instead of silently changing S4 clusters.

## Evidence gaps identified and searches performed
1. Earlier unresolved “no evidence” cities: individual state tourism municipal pages for Coatzacoalcos (historic buildings/Archive), Minatitlán (Carnaval), Poza Rica (Casa de la Cultura/Carnaval del Petróleo), Pánuco (Casa de la Cultura with Huasteca collection), Tecolutla (Museo Marino/Festival del Coco), Nautla (San Miguel Arcángel festivities). All moved from “unconfirmed” to **named evidence**.
2. Earlier generic leads: destination-specific searches for Acajete, Calcahualco, Catemaco, Cazones, Chinameca, Córdoba, Emiliano Zapata, Fortín, Huatusco, Jalcomulco, Jilotepec, Jáltipan, Las Vigas, Misantla, Naolinco, Orizaba, Perote, Puente Nacional, San Andrés Tuxtla, Soteapan, Tamiahua, Tlapacoyan, Tuxpan, Xalapa, Xico and Zozocolco. State tourism pages provided named buildings, events or practices.
3. Confusable names/geography: Carrillo Puerto **Veracruz**, not Felipe Carrillo Puerto in Quintana Roo; verified with Secretaría de Cultura festivities register. Texistepec linked to San Lorenzo, Yanga to the 2026 Afro-Caribbean festival, and Las Choapas to a current municipal festival calendar. Cuitláhuac required direct inspection of the actual municipal tourism page after searches were polluted by the former Veracruz governor’s name; that page identifies Trapiche Meza and the San Juan Bautista festival.

## Examples of documentation
- **Archaeology/history:** Castillo de Teayo pyramid and museum (INAH); Actopan/Quiahuiztlán (INAH); Texistepec/San Lorenzo (Veracruz tourism); Córdoba historic centre and Museo de la Ciudad.
- **Music/traditions:** Naolinco's La Cantada, Soteapan's traditional dances, Jáltipan's Malinche dance, Pánuco's huapango.
- **Festivals:** Catemaco Candelaria/first Friday in March; Tecolutla Festival del Coco; Yanga 2026 International Afro-Caribbean Festival; Las Choapas Festival de la Chopa.
- **Buildings/museums:** Xalapa Museo de Antropología; Orizaba Museo de Arte; Tuxpan México-Cuba museum; Poza Rica Casa de la Cultura.

## Recommended S8 data model
Store separate, nullable fields: `municipality`, `specific_cultural_feature`, `experience_subtype` (archaeology, museum, architecture, festival, craft, dance, etc.), `source_url`, `evidence_date`, `festival_month_if_known`, `visitor_access_verified`, `operating_status_verified`, `source_confidence`, `s8_use_level`. Do not equate a city's monument with a marketable tour. In the exported CSV, `culture_evidence_flag` represents a named feature; `s8_use_level` separates stronger activity hypotheses from features needing further verification.

## Important caveats
Government destination biographies often lack dates and mix historical traditions with current visitor opportunities. A listed dance may not be open to visitors, a museum's hours may have changed, and a festival documented in 2026 is not guaranteed in 2027. Source records may also describe cross-municipal attraction routes; check the exact locality before using campaign copy. This review proves neither that the activities are currently purchasable nor that international audiences desire them.

## Primary links and relevant indexes
- Municipal destination reference template: https://veracruz.mx/destino.php?Municipio=53 (Cuitláhuac); https://veracruz.mx/destino.php?Municipio=158 (Tecolutla); https://veracruz.mx/destino.php?Municipio=39 (Coatzacoalcos); https://veracruz.mx/destino.php?Municipio=123 (Pánuco). The CSV gives per-destination direct source URLs.
- INAH Castillo de Teayo: https://www.inah.gob.mx/zonas/143-zona-arqueologica-castillo-de-teayo-con-museo
- INAH Quiahuiztlán: https://lugares.inah.gob.mx/es/node/4450
- Carrillo Puerto Veracruz, Secretaría de Cultura: https://sic.cultura.gob.mx/ficha.php?disciplina=&table=festividad&table_id=369
- Yanga 2026 festival: https://www.veracruz.gob.mx/2026/10/02/yanga-simbolo-de-libertad-mexico-no-se-doblega-ni-se-subordina-rocio-nahle/
- Las Choapas municipal programme: https://laschoapas.gob.mx/convocatorias.aspx

## Recommendation
**Do not automatically set the S4 culture flag to zero.** The broader search found specific features in all 55 cases. Instead, change S8 to match audiences to **specific named activities** and filter out destinations for which only a historical artifact or general festival mention is documented. A subsequent visitor-readiness check should verify opening and current event calendars for any place actively promoted.
