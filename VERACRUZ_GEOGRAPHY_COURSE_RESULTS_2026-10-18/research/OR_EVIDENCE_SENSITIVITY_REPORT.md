# Veracruz PP3 — evidence-aware campaign decision stability

**New experiment:** The previous source-quality comparison optimized each evidence universe separately. This cross-evaluation instead assesses the *same chosen municipalities* under both evidence standards. No probabilities are invented.

| Hypothetical budget | Strategy | Activity types (accepted evidence) | Activity types (original passages) | Municipalities shared across strategies |
|---:|---|---:|---:|---:|
| MXN 30,000 | broad then original | 47 | 14 | 4/6 |
| MXN 30,000 | original then broad | 39 | 19 | 4/6 |
| MXN 60,000 | broad then original | 62 | 22 | 9/12 |
| MXN 60,000 | original then broad | 53 | 27 | 9/12 |
| MXN 100,000 | broad then original | 72 | 31 | 16/20 |
| MXN 100,000 | original then broad | 60 | 35 | 16/20 |
| MXN 200,000 | broad then original | 78 | 37 | 34/40 |
| MXN 200,000 | original then broad | 78 | 37 | 34/40 |

## Interpreting the scenarios

The *broad-first* method prioritizes the largest diversity of activity types from all 216 accepted municipality-activity relations, then breaks ties by activity diversity supported by preserved original passages. The *original-first* method reverses these priorities. Both select the same number of municipalities at each budget.

A higher original-passage coverage does NOT guarantee better tourist experiences or demand. The absence of source text is an evidence gap, not evidence that a tourist activity does not exist.

## Reproducibility and scope

Database SHA-256: `ceb935532c783c5eb8df5fd8abce5c975582fc3262e7d021f121d3a2496dda35`

The script opens the database read-only and writes only the analysis CSVs and audit. Unlike the earlier route experiments, it does not require coordinates. The 5,000 MXN per placement is a hypothetical teaching assumption, not an observed advertising cost.

**Next analytical step:** introduce a genuine uncertainty model *only after* defining empirical or explicitly hypothetical scenario probabilities, or use interval-based robust optimization without probability estimates.
