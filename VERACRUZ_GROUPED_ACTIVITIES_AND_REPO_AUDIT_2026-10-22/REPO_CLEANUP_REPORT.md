# Veracruz repository cleanup audit — 2026-10-22

## What was inspected

A locally reconstructed repository from the user-uploaded research ZIP, plus the historical note on the Codespaces disk use reported earlier. This is **not** the live Codespaces Git history; do not treat its folder inventory as proof of current HEAD.

### Size breakdown in inspected snapshot (no `.git` / no OSM PBF checkpoints)

- `data/` about **26.8 MiB** — keep (canonical and processed datasets plus research evidence).
- `site/` about **9.0 MiB** — keep (GitHub Pages deployment).
- `VERACRUZ_GEOGRAPHY_COURSE_RESULTS_2026-10-18/` about **8.4 MiB** — preserve until scripts are checked for dependencies, contains research SQLite.
- `veracruz_all_descriptions_patch/` about **8.1 MiB** — preserve until data provenance is verified, includes reconstructed source-first SQLite.
- remaining code, outputs, reports and test files are comparatively small.

The earlier Codespaces listing showed `.git/` around **1.2 GiB** and `.veracruz_osm_checkpoints/` around **618 MiB**, much larger than the active source code. **These are not part of the inspected 59-MiB snapshot.**

### Genuine clutter identified

- 10 timestamped backup directory candidates, collectively **about 0.3 MiB** in the inspected snapshot.
- Numerous dated `VERACRUZ_ROUTE_*`, `VERACRUZ_MAP_*` patch directories. They are historical implementations, not necessarily safe to delete until test/dependency review.
- At least two groups of byte-identical duplicated source exports: one original HTML snapshot and one three-way copied PDF-text CSV. **Do not delete any copy solely from a matching checksum**; paths may support provenance manifests.
- Old SVG activity placeholders remain after grouping, but the new public group gallery no longer needs to load them. They can be archived after a live acceptance check.

## Recommendation: clean THIS repo, not create a new one

1. **Keep** `site/`, current `data/`, tests, `scripts/`, `outputs/`, research evidence, references and DOI/source links.
2. **Inventory** patch and backup directories with the included `repo_hygiene.py` script. Move only *untracked timestamped backups* out of the repository using its optional flag. Never blanket-delete folders named `data`, `research`, `patch`, or `outputs`.
3. **Freeze** obsolete `VERACRUZ_ROUTE_*` patches as a historical archive outside the deployable site **after** validating their files are not imported by any active component.
4. **Inspect Git** separately. Large objects can persist in `.git` even if the 1.36-GB ZIP is no longer present in the working tree. Do not delete `.git` or run history-rewriting commands without a full backup and a proven clean remote branch.
5. **OSM**: retain one canonical road source or derived graph if needed, but put large PBF, checkpoints and temporary extracts outside the repository or in a cache ignored by Git. Verify the live route service no longer requires them before moving.
6. A **new repository** is a last resort if the history cannot be slimmed down safely. It would lose ordinary commit provenance unless the old repo remains archived and linked.

## Commands for Codespaces

From `/workspaces/promo_Veracruz` after unpacking this release:

```bash
# 1. Non-destructive report, saved next to repo instead of inside it
python grouped_activity_cleanup/repo_hygiene.py .

# 2. Show current Git state; don't assume remote push is clean
git status -sb
git count-objects -vH
git ls-files '*.zip' '*.pbf' '*.osm'

# 3. Check remaining heavyweight directories
du -h --max-depth=1 . | sort -h | tail -20

# 4. Optional ONLY if the audit labels timestamped backups untracked:
python grouped_activity_cleanup/repo_hygiene.py . --quarantine-untracked-backups
```

**What the optional flag does:** it moves directories whose names are unambiguous timestamped backups and which Git says are fully untracked into a sibling folder next to the repo. It does **not** delete tracked files, backup branches, `.git`, source databases, or routing checkpoints.

## Image-library note

The current update provides **eight representative documentary photographs, one per grouped section**, with Commons file-page links and credits. It does **not** source all 78 distinct activity photos or 212 municipality photos. That would need an editorial image-by-image relevance and rights review. No claims about real destination photographs should be made for the earlier generated SVG BLOB placeholders.
