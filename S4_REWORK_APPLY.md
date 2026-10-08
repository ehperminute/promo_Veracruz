# S4 mixed-data rework

This patch replaces the earlier exploratory K-Means clustering with the current mixed-data workflow.

From repository root:

```bash
unzip -o promo_veracruz_S4_GOWER_PAM_v2.zip
python scripts/mining/run_mining_pipeline.py --idempotence --test
```

Expected current result:

- 55 S4 destination profiles;
- 295 official product cards used for offer counts/associations;
- k=2..20 evaluated with Gower + PAM;
- recommended singleton-free tourism-profile solution: k=12 after the targeted Xalapa/La Antigua/Poza Rica profile review;
- 42 undermeasured candidates;
- 126 target-anchor structural analog comparisons;
- 22 association rules;
- S4 idempotence PASS.

The old k=15/k=17 K-Means results are historical exploratory outputs only and are not active inputs.
