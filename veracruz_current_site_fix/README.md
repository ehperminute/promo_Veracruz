# Veracruz — current-site cleanup and itinerary v3

**Purpose:** fix missing municipality stop choices (e.g. Tecolutla), retire obsolete S4 55-destination / 12-cluster sections from the public homepage, and label the older S8 campaign planner historical. This does **not** rewrite the tourism database or certify the project research.

## Install in Codespaces — one installer, no prerequisites

Download `VERACRUZ_CURRENT_SITE_TECOLUTLA_FIX_2026-10-21.zip` into the repository root and run:

```bash
cd /workspaces/promo_Veracruz
unzip -o VERACRUZ_CURRENT_SITE_TECOLUTLA_FIX_2026-10-21.zip
python veracruz_current_site_fix/install.py .
python -m http.server 8001 -d site
```

Visit the forwarded port 8001; hard-refresh (Ctrl+Shift+R). Test **Tecolutla**, **Xalapa**, and **Museo Marino Tecolutla** in the route search. A Tecolutla *municipality* stop is an approximate municipality reference, **not** a verified parking lot or tourist attraction entrance. The separate attraction is precisely mapped but entry access still requires checking.

If the map loads but OSRM fails: the external road-directions links remain available. The live service is NOT verified by local tests and is not production reliable.

## Scope and rollback

- Homepage removes the historical **12 experience collections**, **55 destination card explorer**, and Gower/PAM teaching widget. The modern source-backed map, guide and attractions remain.
- `site/planner.html` is kept but marked **ARCHIVED** and removed from main navigation. Its old precomputed 55-destination results are *not* current.
- Existing source files (`site/data/destinations.json`, historical scripts and studies) remain on disk for academic reproducibility. Canonical database is not touched.
- Original versions of each touched site file are backed up in `.local-site-backup-before-v3/` and ignored by Git. Rollback individual files from the corresponding relative path in that folder.
- This installer is repeatable; rerunning it doesn't duplicate the UI elements or archives.
- If you want to commit the changes, commit the modified site and documentation files, **not the downloaded ZIP**.

## Testing done here

- Static: 212 municipalities, 506 mapped attractions; Tecolutla exists in municipality file; homepage excludes 55/12 feature; legacy planner clearly archived; rerunning installer works.
- Browser mock: search Tecolutla, select its municipality, select distinct marine museum, municipality-marker selection, three-stop mocked route drawing; JS syntax.
- **Not** verified here: live road directions services, latest GitHub state beyond uploaded 2026-10-20 repository snapshot, real provider prices, production traffic, or actual tourist redistribution.

See `RESEARCH_OPEN_ITEMS.md` for academic research still to finish.
