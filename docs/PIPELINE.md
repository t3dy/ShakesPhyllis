# Pipeline — Shakespeare Sonnets

11 scripts across 5 stages. See `SONNETSTUDYDECKARDANALYSIS.md` for Python vs LLM boundaries.

**Last verified:** 2026-03-24 (System Audit)

---

## Data Flow

```
data/gutenberg_sonnets.txt     ← Downloaded from Project Gutenberg
        ↓
scripts/parse_gutenberg.py     → data/sonnet_texts.json (one-time utility)
data/sonnets_seed.json         ← Hand-authored seed data
        ↓
scripts/init_db.py             → db/sonnets.db (21 tables, empty)
        ↓
scripts/seed_sonnets.py        → sonnets (154), stanzas (615), lines (2,155)
scripts/seed_reference.py      → characters, candidates, scholars, bibliography,
                                  devices, modes, groups (8 base), group_members
scripts/seed_groups_v2.py      → sonnet_groups expanded to 47 scholarly groupings
scripts/seed_essay_unresolved.py → essays (1), essay_sonnet_links (20)
        ↓
scripts/prep_batch.py          → data/batch_prompts/ (locked vocabulary prompts for LLM)
        ↓
[LLM agents generate enrichment JSON]
        ↓
scripts/validate_enrichment.py → pre-load validation gate (REQUIRED before enrich)
scripts/validate_enrichment.py --fix → auto-fix mappable issues
        ↓
scripts/enrich_sonnets.py      ← data/enrichment/batch_*.json
                               → sonnet_analyses, line_annotations, directing_notes,
                                 sonnet_themes, character_appearances, line_devices,
                                 sonnet_modes
        ↓
scripts/validate_db.py         → integrity checks (post-load)
        ↓
[FUTURE] scripts/build_site.py → site/ (static HTML)
```

---

## Stage 1: Scaffold & Seed — BUILT

| Script | Input | Output | Idempotent | Status |
|--------|-------|--------|-----------|--------|
| `init_db.py` | — | `db/sonnets.db` (21 empty tables) | Yes (CREATE IF NOT EXISTS) | BUILT |
| `init_db.py --force` | — | Drops and recreates DB | Destructive | BUILT |
| `seed_sonnets.py` | `data/sonnet_texts.json` | sonnets (154), stanzas (615), lines (2,155) | Yes (INSERT OR IGNORE) | BUILT |
| `seed_reference.py` | `data/sonnets_seed.json` | characters (4), candidates (10), scholars (13), bibliography (15), devices (21→24), modes (8), groups (8), group_members | Yes (INSERT OR IGNORE) | BUILT |
| `seed_groups_v2.py` | hardcoded | sonnet_groups (47), group_members expanded | **No** (DELETE→INSERT) | BUILT |
| `seed_essay_unresolved.py` | hardcoded | essays (1), essay_sonnet_links (20) | Yes (INSERT OR IGNORE) | BUILT |

## Stage 2: Prepare & Enrich — IN PROGRESS

| Script | Input | Output | Idempotent | Status |
|--------|-------|--------|-----------|--------|
| `prep_batch.py` | sonnet IDs, DB | `data/batch_prompts/*.prompt.md` + `*.template.json` | Yes | BUILT |
| `validate_enrichment.py [--fix] [file]` | `data/enrichment/*.json` | Validation report; with --fix, repairs mappable issues | Yes | BUILT |
| `enrich_sonnets.py [file]` | `data/enrichment/*.json` | All Layer 4 enrichment tables | Yes (INSERT OR REPLACE) | BUILT |

**Enrichment workflow (corrected):**
1. `python scripts/prep_batch.py --range 41 54 --name fym_absence` → locked prompt + template
2. LLM agent generates enrichment JSON using locked vocabulary
3. `python scripts/validate_enrichment.py --fix batch_NN.json` → validate and fix
4. `python scripts/enrich_sonnets.py batch_NN.json` → load into DB
5. `python scripts/validate_db.py` → post-load integrity check

Enrichment status: 71 of 154 sonnets enriched (14 batches). 83 remaining.

## Stage 3: Validate — BUILT

| Script | Input | Output | Status |
|--------|-------|--------|--------|
| `validate_db.py` | `db/sonnets.db` | Pass/fail integrity report | BUILT |

## Stage 4: Build Site — PLANNED

| Script | Input | Output | Status |
|--------|-------|--------|--------|
| `build_site.py` | `db/sonnets.db` | `site/` (static HTML) | PLANNED |

---

## Utilities

| Script | Purpose | Status |
|--------|---------|--------|
| `parse_gutenberg.py` | One-time: parse Gutenberg text → `sonnet_texts.json` | BUILT |
| `fix_enrichment.py` | **DEPRECATED** — replaced by `validate_enrichment.py --fix` | DEPRECATED |

---

## Full Rebuild Command

```bash
python scripts/init_db.py --force
python scripts/seed_sonnets.py
python scripts/seed_reference.py
python scripts/seed_groups_v2.py
python scripts/seed_essay_unresolved.py
python scripts/validate_enrichment.py --fix     # fix all enrichment batches
python scripts/enrich_sonnets.py                 # load all enrichment batches
python scripts/validate_db.py
```

---

## Idempotency Notes

- Most scripts use INSERT OR IGNORE or INSERT OR REPLACE (safe to re-run)
- `seed_groups_v2.py` uses DELETE→INSERT: running it wipes custom group edits
- `init_db.py --force` is destructive: drops and recreates all tables
- Enrichment files are the source of truth; DB is the compiled state
