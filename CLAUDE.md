# Claude Code Instructions — Shakespeare Sonnets Digital Humanities Site

## Project Summary

Digital humanities website presenting Shakespeare's 154 Sonnets through four scholarly pillars: close-reading Analyses, line-by-line Directing notes, historical Contexts, and thematic Essays. Focused on the dramatic love triangle of the Fair Young Man, Dark Lady, and Speaker. Architecture replicates AtalantaClaudiens: SQLite source of truth, Python static site generator, vanilla HTML/CSS/JS, GitHub Pages deployment. SHWEP-style dark academic theme.

## Document Routing

**Read `DOCUMENTAIRTRAFFICCONTROL.md` when you need to find the right file.** It routes you to the correct document for any task (schema work, sonnet analysis, extraction, site building, planning).

## Quick Reference

| Document | Purpose |
|----------|---------|
| `DOCUMENTAIRTRAFFICCONTROL.md` | **Start here** — routes you to the right doc for any task |
| `SONNETSTUDYDECKARDANALYSIS.md` | Deckard boundary map: what Python does vs what Claude Code does |
| `docs/SYSTEM.md` | Architecture, data flow, provenance model |
| `docs/ONTOLOGY.md` | Database schema (25 tables), entity relationships |
| `docs/PIPELINE.md` | Script execution order (19 scripts), stage dependencies |
| `docs/INTERFACE.md` | 4-tab site structure, page templates, SHWEP theme |
| `docs/ROADMAP.md` | Phase status: BUILT / READY / BLOCKED / PLANNED |
| `PHASESTATUS.md` | Session discipline log — update at end of every session |

## Data Flow Direction

```
data/sonnet_texts.json    ← Canonical 1609 Quarto text (154 sonnets, line-by-line)
data/sonnets_seed.json    ← Characters, scholars, bibliography, devices, modes
        ↓
seed scripts              →  SQLite (db/sonnets.db)
        ↓
extract/enrich scripts    →  LLM-assisted enrichment → SQLite
        ↓
build_analysis.py         →  Deterministic template assembly → SQLite
        ↓
build_site.py             →  static HTML (site/)
```

Changes flow ONE direction: seed JSON → DB → HTML. Never edit generated HTML. Never edit the DB directly.

## The Four Content Pillars

| Tab | Content | Granularity |
|-----|---------|-------------|
| **Sonnet Analyses** | Close readings: verbatim citations, scholarly synthesis, FYM/DL dynamics | Per sonnet (154) |
| **Sonnet Directing** | Line-by-line performance notes: meter, emphasis, emotional arc, volta, staging | Per line (2,156) |
| **Sonnet Contexts** | Historical context: biography, FYM/DL candidates, publication history | Per sonnet + candidate pages |
| **Essays** | Standalone thematic essays: FYM, DL, sexuality, irony, structure, etc. | Freestanding (~10-15) |

## Key Characters

| Character | Primary Candidates | Sonnets |
|-----------|-------------------|---------|
| **Fair Young Man (FYM)** | Henry Wriothesley (Southampton), William Herbert (Pembroke) | 1-126 |
| **Dark Lady (DL)** | Emilia Lanier/Bassano, Mary Fitton, Lucy Negro, Aline Florio | 127-152 |
| **Rival Poet** | Christopher Marlowe, George Chapman, others | 78-86 |
| **Speaker/Poet** | Shakespeare (autobiographical reading) or persona | All 154 |

## Operating Rules

### Before starting work:
- Check `PHASESTATUS.md` for current phase, prerequisites, blockers
- Check `docs/ROADMAP.md` for what's BUILT vs READY vs BLOCKED
- Read `docs/ONTOLOGY.md` if touching the database
- Read `SONNETSTUDYDECKARDANALYSIS.md` if unsure whether a task is Python or LLM work

### During work:
- Mark tasks in progress in PHASESTATUS.md
- Don't skip phases — each phase's outputs feed the next
- Update `docs/ONTOLOGY.md` immediately if schema changes
- Update `docs/PIPELINE.md` immediately if pipeline changes
- All LLM-generated content defaults to: source_method='LLM_ASSISTED', review_status='DRAFT', confidence='MEDIUM'

### At end of session:
- Update PHASESTATUS.md with: phase status, what changed, next steps, blockers

## Provenance Model

Every generated datum carries three fields:

| Field | Values |
|-------|--------|
| `source_method` | DETERMINISTIC, CORPUS_EXTRACTION, LLM_ASSISTED, SEED_DATA, HUMAN_VERIFIED |
| `review_status` | DRAFT → REVIEWED → VERIFIED (forward-only) |
| `confidence` | HIGH, MEDIUM, LOW |

Rules:
- Sonnet text from 1609 Quarto: DETERMINISTIC / HIGH
- LLM-classified data: LLM_ASSISTED / MEDIUM / DRAFT
- Never overwrite VERIFIED data without logging discrepancy
- Never auto-promote LLM output to VERIFIED
