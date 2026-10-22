# Veracruz budget-range fallback

Adds an editable **planning spending envelope** above the existing price ledger. This makes routes with no matched supplier prices usable for preliminary budgeting without labeling invented numbers as observations.

## Install

From repository root:

```
unzip -o VERACRUZ_BUDGET_RANGE_FALLBACK_2026-10-22.zip
python veracruz_budget_range_release/install.py .
node veracruz_budget_range_release/tests/test_core.js
node --check site/js/budget-range.js
python -m http.server 8100 -d site
```

## Design boundaries

- The three scenario levels are **editable budgeting assumptions**, NOT statistics or municipality-specific market prices.
- The national reference gasoline price MXN 23.68/L comes from a 2026-09-04 PROFECO report for August 27, 2026; it is editable, and actual station prices differ. The 12 km/L fuel economy is illustrative, not measured.
- Counts only road distance **returned by the router** or entered manually; it does not silently substitute straight-line distance. The trip is not assumed to include returning home.
- Tolls have no default and are flagged unless the visitor enters them. Check federal roads with [SICT Routes point-to-point](https://app.sct.gob.mx/sibuac_internet/ControllerUI?action=cmdEscogeRutaMovil).
- Quoted supplier items already selected in the existing pricing panel are included using its calculations. Assumed activity count is reduced for paid selected offers. If accommodation is already priced, no assumed room charge is added. Package inclusions may still overlap; caller must confirm.
- **Not** a quote, price forecast, statistical confidence interval, verified service offering or availability check. Stays on static GitHub Pages.

## Acceptance tests

1. Selecting stops (including one with no provider price) shows a low–high spending envelope instead of a dead end.
2. Three assumption scenarios and six editable bounds are available; values are transparent.
3. Changing people, nights, days, paid activities or route distance recomputes the range.
4. Published item pricing and conditional group/tax logic are preserved by the original ledger.
5. No road route? Fuel amount is excluded and clearly marked unresolved.
6. ES/EN/JA captions and mobile layout load.
7. Reinstall does not duplicate scripts.
