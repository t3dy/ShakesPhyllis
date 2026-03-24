# Roadmap — Shakespeare Sonnets

## Phase Overview

| Phase | Name | Status | Description |
|-------|------|--------|-------------|
| 0 | Init Documents | **BUILT** | Project docs, schema, pipeline, Deckard analysis |
| 1 | Scaffold & Seed | READY | Database creation, seed data, deterministic scripts |
| 2 | Site Scaffold | BLOCKED (on Phase 1) | SHWEP theme, page templates, static site generator |
| 3 | LLM Pass 1: Full Analysis | BLOCKED (on Phase 1) | Addressees, figures, modes, sections for 3 sample sonnets |
| 4 | Sample Content | BLOCKED (on Phases 2-3) | 3 sample sonnets × 3 content types + 2 thematic essays |
| 5 | V1 Deploy | BLOCKED (on Phase 4) | GitHub Pages deployment |
| 6 | LLM Pass 2: Scholarly Extraction | PLANNED | Extract claims from priority corpus PDFs |
| 7 | LLM Passes 3-5: Enrichment | PLANNED | Glossary, annotations, intertexts, directing notes |
| 8 | Full Coverage | PLANNED | Expand to all 154 sonnets across all pillars |
| 9 | Search & Navigation | PLANNED | Cross-references, thematic navigation, filters |

## Phase 0: Init Documents [BUILT]

| Deliverable | Status |
|-------------|--------|
| `CLAUDE.md` | DONE |
| `DOCUMENTAIRTRAFFICCONTROL.md` | DONE |
| `SONNETSTUDYDECKARDANALYSIS.md` | DONE |
| `docs/SYSTEM.md` | DONE |
| `docs/ONTOLOGY.md` | DONE |
| `docs/PIPELINE.md` | DONE |
| `docs/INTERFACE.md` | DONE |
| `docs/ROADMAP.md` | DONE |
| `PHASESTATUS.md` | DONE |
| `requirements.txt` | DONE |
| `.gitignore` | DONE |
| `git init` | DONE |

## Phase 1: Scaffold & Seed [READY]

**Prerequisites:** Phase 0 complete.

| Deliverable | Status |
|-------------|--------|
| `data/sonnet_texts.json` (154 sonnets, 1609 Quarto text) | TODO |
| `data/sonnets_seed.json` (characters, scholars, bib, devices, modes, groups) | TODO |
| `scripts/init_db.py` | TODO |
| `scripts/migrate_v2.py` | TODO |
| `scripts/migrate_v3.py` | TODO |
| `scripts/seed_sonnets.py` | TODO |
| `scripts/seed_characters.py` | TODO |
| `scripts/seed_scholars.py` | TODO |
| `scripts/seed_devices.py` | TODO |
| `scripts/seed_modes.py` | TODO |
| `scripts/seed_sequence_groups.py` | TODO |
| `scripts/validate_sonnets.py` | TODO |

**Acceptance gate:** `validate_sonnets.py` passes. 154 sonnets × 14 lines = 2,156 rows in sonnet_lines. All enum values valid.

## Phase 2: Site Scaffold [BLOCKED on Phase 1]

| Deliverable | Status |
|-------------|--------|
| `site/style.css` (SHWEP dark theme) | TODO |
| `site/script.js` (filters, navigation) | TODO |
| `scripts/build_site.py` | TODO |
| Page templates: homepage, sonnet index, analysis, directing, context, essay | TODO |

**Acceptance gate:** `build_site.py` generates valid HTML from seed data. Site renders in browser with correct theme.

## Phase 3: LLM Pass 1 — 3 Sample Sonnets [BLOCKED on Phase 1]

Target sonnets: **Sonnet 18** (FYM, extended metaphor), **Sonnet 130** (DL, irony), **Sonnet 1** (Procreation, opening).

| Deliverable | Status |
|-------------|--------|
| `scripts/extract_full_analysis.py` | TODO |
| Addressee classification for 3 sonnets | TODO |
| Rhetorical figures for 3 sonnets | TODO |
| Analysis modes for 3 sonnets | TODO |
| Section commentary for 3 sonnets | TODO |

**Acceptance gate:** All 3 sonnets have complete enrichment. Validation passes.

## Phase 4: Sample Content [BLOCKED on Phases 2-3]

| Deliverable | Status |
|-------------|--------|
| `scripts/build_analysis.py` | TODO |
| 3 complete Analysis pages | TODO |
| 3 complete Directing pages | TODO |
| 3 complete Context pages | TODO |
| 2 thematic Essays (FYM, Sonnet Structure) | TODO |
| FYM/DL candidate reference pages | TODO |

**Acceptance gate:** Site builds with all sample content. Pages are readable and scholarly.

## Phase 5: V1 Deploy [BLOCKED on Phase 4]

| Deliverable | Status |
|-------------|--------|
| GitHub repo created | TODO |
| GitHub Pages configured | TODO |
| Live site accessible | TODO |

**Acceptance gate:** Site is live and accessible at public URL.
