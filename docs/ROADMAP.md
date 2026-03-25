# Roadmap — Shakespeare Sonnets

## Phase Overview

| Phase | Name | Status | Description |
|-------|------|--------|-------------|
| 0 | Init Documents | **BUILT** | Project docs, schema, pipeline, Deckard analysis |
| 1 | Scaffold & Seed | **BUILT** | Database (22 tables), 154 sonnets, 2,155 lines, reference data |
| 1b | Enrichment (17 sonnets) | **BUILT** | 3 enrichment batches: procreation, triangle, immortality |
| 2 | Enrichment (all 154) | READY | Remaining 137 sonnets |
| 3 | Site Scaffold | READY | SHWEP theme, page templates, build_site.py |
| 4 | Sample Content Build | BLOCKED (on 3) | Build 17 enriched sonnets into HTML pages |
| 5 | V1 Deploy | BLOCKED (on 4) | GitHub Pages launch with 17-sonnet sample |
| 6 | Full 154 Enrichment | BLOCKED (on 5) | Complete enrichment for all sonnets |
| 7 | Essays & Context | BLOCKED (on 6) | Thematic essays, historical context pages |
| 8 | Scholarly Extraction | PLANNED | Corpus PDF extraction (Vendler, Booth, etc.) |
| 9 | Polish & Launch | PLANNED | Navigation, search, cross-references, full deploy |

---

## Phase 0: Init Documents — BUILT

All project documents created:
- CLAUDE.md, DOCUMENTAIRTRAFFICCONTROL.md, SONNETSTUDYDECKARDANALYSIS.md
- docs/SYSTEM.md, ONTOLOGY.md, PIPELINE.md, INTERFACE.md, ROADMAP.md
- PHASESTATUS.md

## Phase 1: Scaffold & Seed — BUILT

**Scripts:** `init_db.py`, `seed_sonnets.py`, `seed_reference.py`, `validate_db.py`

**Data files:**
- `data/sonnet_texts.json` — 154 sonnets, 2,155 lines, clean ASCII from 1609 Quarto
- `data/sonnets_seed.json` — 4 characters (10 candidates), 13 scholars, 15 bibliography entries, 20 rhetorical devices, 8 analytical modes, 8 sonnet groups

**Database:** 22 tables, all Layer 1 (core text) and Layer 2 (reference) tables populated.

## Phase 1b: Enrichment Sample — BUILT

17 sonnets fully enriched across 3 batches:

| Batch | Sonnets | Focus |
|-------|---------|-------|
| batch_01_procreation | 1, 3, 12, 17, 18 | Procreation → immortality pivot |
| batch_02_triangle | 40, 42, 93, 94, 129, 130, 138, 144 | Love triangle, betrayal, lust, deception |
| batch_03_immortality | 55, 73, 116, 126 | Poetry vs. Time, aging, envoi |

**Per-sonnet enrichment includes:**
- Full close-reading analysis (volta, argument, emotional arc, dramatic situation, subtext)
- Line-by-line annotations (emphasis words, delivery notes, glosses, commentary)
- Directing notes (scene setting, character notes, FYM/DL notes, key moments)
- Theme tagging (with PRIMARY/SECONDARY prominence)
- Character appearances (with role: ADDRESSED, MENTIONED, IMPLIED)
- Rhetorical device instances per line (with quotation and explanation)
- Analytical mode priorities per sonnet (with rationale)

**Totals:** 17 analyses, 88 line annotations, 86 themes, 38 character appearances, 17 directing note sets, 89 device instances, 54 mode assignments.

## Phase 2: Full Enrichment — READY

Enrich remaining 137 sonnets in batches of 5-10. Priority order:
1. FYM core (19, 20, 29, 30, 33, 34, 35, 57, 71, 87) — essential FYM dynamics
2. DL core (127, 128, 131, 132, 141, 147, 151, 152) — DL desire/disgust
3. Rival Poet (78-86) — the competition sequence
4. Remaining FYM (all others 1-126 not yet done)
5. Cupid coda (153, 154)

## Phase 3: Site Scaffold — READY

Build `build_site.py` and the HTML/CSS/JS templates. SHWEP dark academic theme.

## Phases 4-9: See descriptions in table above.

---

## Acceptance Gates

| Phase → Phase | Gate |
|---------------|------|
| 0 → 1 | All docs written, schema designed |
| 1 → 1b | DB populated, validate_db.py passes |
| 1b → 2 | 17 sonnets enriched with all 7 enrichment types |
| 2 → 3 | At least 50 sonnets enriched |
| 3 → 4 | build_site.py generates valid HTML for enriched sonnets |
| 4 → 5 | 17 sample pages render correctly with all tabs |
| 5 → 6 | V1 deployed to GitHub Pages |
