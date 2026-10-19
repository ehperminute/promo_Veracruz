# Data Mining — audit of documented experience co-occurrence
**Veracruz PP · 19 October 2026 · Exploratory analytical check**

## Question
Do municipalities that have evidence for one broad tourist-experience family also show more than expected evidence for another family? This is **not** a study of tourists' actual preferences or travel behavior.

## Inputs
Recovered master `veracruz_pp3_master_RECOVERED.sqlite`, table `s4_statewide_evidence_pairs_v1`, using distinct municipality–family links. The table includes **216 accepted municipality–specific-activity pairs**, across **61 municipalities**, grouped into **9 activity families**. The newer external verification of 14 municipalities is **not yet included** in this accepted-pairs table. Municipalities with no accepted evidence are not coded as zero-tourism in this test.

## Method
Binary matrix (61 municipalities × 9 families). Examine each of 36 family pairs with co-occurrence counts, support, confidence and lift. Fisher's exact test (one-sided: positive association), with Benjamini–Hochberg adjustment over all 36 tests. Family assignment is based on source-linked evidence, not visitor surveys. The test is exploratory and assumes observed municipality records are a meaningful sampling frame, which they may not be.

## Results
- **0 of 36 pairs** meet adjusted `q < 0.05`.
- Example: `food_agriculture` + `wellness_spiritual` occurs in **5 municipalities**. Lift = **2.35**, unadjusted p ≈ **0.0285**, but adjusted q ≈ **0.256**.
- The smallest unadjusted p is for `other_specific_unclassified` + `wellness_spiritual`, but this includes a residual 'unclassified' category, making it a poor basis for visitor-facing promotional targeting.

## Interpretation for PP
The current accepted catalog is strong enough to enumerate and classify documented offers but **does not support claiming statistically established combinations of tourist interests** from municipal co-occurrence. Use individual documented activities for visitor filters and marketing *hypotheses*. Don't call the co-occurrence pairs measured audience segments or expected demand. No new clustering or pseudo-popularity score is justified by this test.

## Next connected stage
Digital Marketing: for the **existing six-municipality MXN 30,000 hypothetical promotion portfolio**, assign source-backed experiences, explicit audience-interest hypotheses, one creative/message per selected placement, source dates and measurable KPIs. Mark proposed costs and audience fit as assumptions; do not claim observed campaign return.

## Reproduction
Run `python audit_activity_pairs.py <path-to-SQLite-file>`; output has all 36 comparisons. Neither script nor analysis modifies the project database.
