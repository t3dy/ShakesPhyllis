# Claude Code Instructions — Shakespeare Sonnets Digital Humanities Site

## Project Summary

Digital humanities website presenting Shakespeare's 154 Sonnets through four scholarly pillars: close-reading Analyses, line-by-line Directing notes, historical Contexts, and thematic Essays. Focused on the dramatic love triangle of the Fair Young Man, Dark Lady, and Speaker. Architecture: SQLite source of truth, Python static site generator, vanilla HTML/CSS/JS, GitHub Pages deployment. SHWEP-style dark academic theme.

## Document Routing

**Read `DOCUMENTAIRTRAFFICCONTROL.md` when you need to find the right file.** DO NOT GUESS — ALWAYS ROUTE.

## Quick Reference

| Document | Purpose |
|----------|---------|
| `DOCUMENTAIRTRAFFICCONTROL.md` | **Start here** — routes you to the right doc for any task |
| `SONNETSTUDYDECKARDANALYSIS.md` | Deckard boundary: what Python does vs what LLM does |
| `docs/SYSTEM.md` | Architecture, data flow, provenance model |
| `docs/ONTOLOGY.md` | Database schema (21 user tables), controlled vocabularies, entity relationships |
| `docs/PIPELINE.md` | Script execution order (9 scripts), stage dependencies, validation gates |
| `docs/INTERFACE.md` | 4-tab site structure, page templates, SHWEP theme |
| `docs/ROADMAP.md` | Phase status: BUILT / READY / BLOCKED / PLANNED |
| `docs/SYSTEM_AUDIT.md` | Audit findings, issue register, correction log |
| `docs/REVIEW_PIPELINE.md` | Provenance promotion: DRAFT → REVIEWED → VERIFIED |
| `PHASESTATUS.md` | Session discipline log — update at end of every session |
| `SWARMPLUSPYTHON.md` | Architectural rationale for two-layer (deterministic + LLM) approach |

---

## System Invariants

These rules are absolute. No task may violate them.

### Data Flow Direction

```
data/sonnet_texts.json    ← Canonical 1609 Quarto text (immutable)
data/sonnets_seed.json    ← Characters, scholars, bibliography, devices, modes
        ↓
seed scripts              →  SQLite (db/sonnets.db)
        ↓
LLM enrichment JSON       →  validate_enrichment.py  →  enrich_sonnets.py  →  SQLite
        ↓
build_site.py             →  static HTML (site/)
```

1. Changes flow ONE direction: seed JSON → DB → HTML.
2. Never edit generated HTML.
3. Never edit the DB directly.
4. Never let LLM output bypass validation.
5. 1609 Quarto text is sacred — never overwrite it.

### Deckard Boundary (Python vs LLM)

**DETERMINISTIC (Python)** — no LLM judgment needed:
- Parsing sonnets into lines, stanzas, rhyme positions
- Schema creation, migrations, seeding
- Loading validated enrichment JSON into DB
- Template assembly (DB → HTML)
- Validation (FK checks, enum compliance, line counts)

**JUDGMENT (LLM)** — requires literary interpretation:
- Addressee classification
- Rhetorical device identification and ranking
- Close-reading analysis, emotional arc, dramatic situation
- Performance/directing notes
- Scholarly extraction from PDFs

**WASTE** — do NOT use LLM for: line splitting, stanza labels, rhyme words, syllable counts, HTML generation, constraint validation.

**RISK** — do NOT use deterministic code for: irony detection, pun identification, aesthetic ranking, performance direction.

**DANGER** — never allow:
- LLM output directly into DB without validation
- LLM-generated text to overwrite 1609 Quarto text
- LLM analysis to auto-promote to VERIFIED status
- LLM to fabricate scholarly citations
- LLM to invent vocabulary not in controlled lists (device_ids, mode_ids, character_ids)

---

## Controlled Vocabularies

These are the ONLY valid values. LLM output using other values MUST be rejected or mapped.

### character_id
`FYM`, `DL`, `RP`, `SPEAKER`

### device_id (rhetorical_devices)
`METAPHOR`, `SIMILE`, `PUN`, `IRONY`, `CONCEIT`, `PERSONIFICATION`, `APOSTROPHE`, `ANTITHESIS`, `PARADOX`, `HYPERBOLE`, `SYNECDOCHE`, `METONYMY`, `ALLITERATION`, `ASSONANCE`, `ENJAMBMENT`, `CAESURA`, `VOLTA`, `BLAZON`, `CHIASMUS`, `ANAPHORA`, `EPIGRAM`, `POLYPTOTON`, `RHETORICAL_QUESTION`, `ALLUSION`

### mode_id (analytical_modes)
`RHETORICAL`, `DRAMATIC`, `PROSODIC`, `IMAGISTIC`, `STRUCTURAL`, `INTERTEXTUAL`, `HISTORICAL`, `THEMATIC`

### volta_type
`DRAMATIC`, `LOGICAL`, `TONAL`, `IRONIC`

### couplet_function
`RESOLUTION`, `REVERSAL`, `EXTENSION`, `EPIGRAM`, `IRONIC`

### addressee
`FYM`, `DL`, `RP`, `SELF`, `MIXED`, `NONE`

### source_method
`DETERMINISTIC`, `CORPUS_EXTRACTION`, `LLM_ASSISTED`, `SEED_DATA`, `HUMAN_VERIFIED`

### review_status
`DRAFT`, `REVIEWED`, `VERIFIED`

### confidence
`HIGH`, `MEDIUM`, `LOW`

### Anti-Drift Rule
To add a new value to any controlled vocabulary:
1. Justify why no existing value covers the case
2. Update ONTOLOGY.md with the new value and its definition
3. Update CLAUDE.md controlled vocabularies section
4. Update init_db.py CHECK constraints
5. Only THEN use the new value

LLM agents do NOT have authority to expand vocabularies. Expansion is an editorial decision.

---

## Operating Rules

### Before starting work:
- Check `PHASESTATUS.md` for current phase, prerequisites, blockers
- Check `docs/ROADMAP.md` for what's BUILT vs READY vs BLOCKED
- Read `docs/ONTOLOGY.md` if touching the database
- Read `SONNETSTUDYDECKARDANALYSIS.md` if unsure whether a task is Python or LLM work

### During work:
- Mark tasks in progress in PHASESTATUS.md
- Don't skip phases — each phase's outputs feed the next
- Update `docs/ONTOLOGY.md` IMMEDIATELY if schema changes
- Update `docs/PIPELINE.md` IMMEDIATELY if pipeline changes
- All LLM-generated content defaults to: source_method='LLM_ASSISTED', review_status='DRAFT', confidence='MEDIUM'
- All enrichment JSON MUST pass validate_enrichment.py before enrich_sonnets.py

### At end of session:
- Update PHASESTATUS.md with: phase status, what changed, next steps, blockers

### Swarm Rules (when using parallel agents for enrichment):
1. Agents select from controlled vocabularies ONLY — no invention
2. Every batch passes validate_enrichment.py before DB load
3. Raw agent output saved as `batch_NN_name_raw.json`; cleaned version as `batch_NN_name.json`
4. Swarm handles baseline enrichment; sequential pass for narrative-critical arcs
5. Unknown IDs get logged and rejected, not added to schema

---

## The Four Content Pillars

| Tab | Content | Granularity |
|-----|---------|-------------|
| **Sonnet Analyses** | Close readings: verbatim citations, scholarly synthesis, FYM/DL dynamics | Per sonnet (154) |
| **Sonnet Directing** | Line-by-line performance notes: meter, emphasis, emotional arc, volta, staging | Per line (2,155) |
| **Sonnet Contexts** | Historical context: biography, FYM/DL candidates, publication history | Per sonnet + candidate pages |
| **Essays** | Standalone thematic essays: FYM, DL, sexuality, irony, structure, etc. | Freestanding (~10-15) |

## Key Characters

| Character | ID | Primary Candidates | Sonnets |
|-----------|----|--------------------|---------|
| **Fair Young Man** | FYM | Henry Wriothesley (Southampton), William Herbert (Pembroke) | 1-126 |
| **Dark Lady** | DL | Emilia Lanier/Bassano, Mary Fitton, Lucy Negro, Aline Florio | 127-152 |
| **Rival Poet** | RP | Christopher Marlowe, George Chapman, others | 78-86 |
| **Speaker/Poet** | SPEAKER | Shakespeare (autobiographical reading) or persona | All 154 |

## Provenance Model

Every generated datum carries three fields:

| Field | Values |
|-------|--------|
| `source_method` | DETERMINISTIC, CORPUS_EXTRACTION, LLM_ASSISTED, SEED_DATA, HUMAN_VERIFIED |
| `review_status` | DRAFT → REVIEWED → VERIFIED (forward-only) |
| `confidence` | HIGH, MEDIUM, LOW |

Rules:
- Sonnet text from 1609 Quarto: DETERMINISTIC / VERIFIED / HIGH
- Seed reference data: SEED_DATA / REVIEWED / HIGH
- LLM-generated enrichment: LLM_ASSISTED / DRAFT / MEDIUM (always)
- Never overwrite VERIFIED data without logging discrepancy
- Never auto-promote LLM output to VERIFIED
- See `docs/REVIEW_PIPELINE.md` for promotion criteria
