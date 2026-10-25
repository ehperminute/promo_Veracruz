# Veracruz provider-offer pilot — GitHub Pages compatible

This **does not create a real-time supplier bidding or booking platform**. It provides a credible, testable first step: providers submit listings, the owner reviews them, and reviewed offers appear next to the route planner, filtered by municipality.

## Install

Place the ZIP in `promo_Veracruz`, unzip and run:

```bash
python veracruz_provider_marketplace_mvp/install.py .
python veracruz_provider_marketplace_mvp/tests/test_release.py .
python -m http.server 8100 -d site
```

- Open `http://localhost:8100/proveedores.html` for the supplier form.
- Open `http://localhost:8100/` and find **Servicios para tu itinerario**, below the map; route stops limit the listed offers.
- **Initially there are no approved offers**. This is intentional; the project has no contracted or verified bidders yet.

## Real submission cycle

1. A real business fills the form at `proveedores.html`.
2. By default, the form **downloads a private JSON submission**. It does not automatically send anything; the business sends it through a private channel to your team. You may configure a legitimate HTTPS submission endpoint with CORS in `site/data/provider_submission_config.json` (no API secrets) when you have one.
3. Check business identity, authorization, service and price/conditions with the provider. Don't trust a random self-submission.
4. Save the JSON in a **private** location outside `site/` and the tracked repository (e.g. `/tmp/provider_request.json`).
5. Review and explicitly approve:

```bash
python scripts/pp6/review_provider_offer.py /tmp/provider_request.json --repo . --approve --contact-verified
```

6. Examine `site/data/provider_offers.json` for accuracy, commit only the reviewed **public** offers JSON and deploy GitHub Pages. Private contact email is never copied to the public file.
7. The planner lists reviewed offers at matching route stops. A `Solicitar cotización` action provides a reusable message, and a business website link opens the provider's own page. No actual payment or booking is processed.

## What this proves / cannot prove

**Demonstrates:** supplier listing schema, intake interface, manual moderation, safe public projection, route-based offer discovery, price units and validity, and a required public website or social/contact URL; no fabricated providers.

**Not demonstrated:** supplier participation, live price updates, independent availability checks, bids responding to a traveler-specific request, user accounts, notifications, reservations, commissions or payment processing. Those need private server-side storage and real operators.

## Security and privacy

Do not use GitHub Issues or public PRs to collect administrative email addresses. The static form has no hidden secrets. The public JSON must contain no private email field. Posting a listing is a human-approved action, not an automatic form side effect. GitHub Pages serves JSON publicly; treat every field there as public. For production, add a private form service, consent/privacy notice, spam controls, identity verification and audit logs.

## Tests

`python veracruz_provider_marketplace_mvp/tests/test_release.py .` tests installer idempotence, submission validation, publication filtering, duplicate handling, and non-publication of administrative emails. It also checks `node --check` for JS syntax when Node is available.
