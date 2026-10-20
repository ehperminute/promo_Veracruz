# VERACRUZ PP6 — SINGLE CONSOLIDATED RELEASE (2026-10-20)

This ZIP **replaces both** older incremental ZIPs:
- VERACRUZ_PP6_AUTONOMOUS_STAGE_LOOP_2026-10-20.zip
- VERACRUZ_PP6_ORIGINAL_RUBRICS_RECOVERED_PATCH_2026-10-20.zip

It includes the second-pass analytical runner and original-rubric checks. The earlier
activity-discovery and audit ZIPs were experiments, NOT installation prerequisites.
DO NOT re-upload this ZIP to ChatGPT. It is meant for application to the GitHub Codespaces
repository when desired. The assistant already has the uploaded repo and research data.

## To apply, when ready

1. Download this consolidated ZIP to your computer, and add it to Codespaces through
   VS Code Explorer (do not git add / git commit it).
2. In Codespaces, at the repository root, execute:

   unzip -o VERACRUZ_PP6_SINGLE_CONSOLIDATED_RELEASE_2026-10-20.zip
   python scripts/pp6/run_loop.py

3. Inspect `outputs/pp6_loop/CHECKPOINT.md` and `SUBMISSION_GAP_AUDIT_ES.md`.
4. Remove the ZIP from repo directory after extraction; no need to push archive to GitHub.

**Caution:** The ZIP overwrites `README.md`, `.gitignore`, `requirements.txt`,
`tests/test_web_export.py` and listed PP6 files. Save any more recent local modifications
before extraction. It does not include or overwrite `data/`, `site/` or raw source PDFs.

## Status
S0–S8 research validations pass with the scientific limitations documented.
The complete raw-input rebuild is blocked by original archives excluded from the research ZIP;
it does not block analytical reporting from the recovered database.
The original university rubric is verified; the final 30–40-page report, complete
campaign, technical evidence package and <=15-minute colloquium are NOT certified as finished.
No marketing campaign response, visitor redistribution or verified venue capacity is fabricated.

The loop runs on command, does not keep working in the background, and records checkpoints.
