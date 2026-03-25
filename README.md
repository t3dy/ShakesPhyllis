# ShakesPhyllis

**A digital humanities database and visualization site for Shakespeare's 154 Sonnets.**

Built with Claude Code. Enriched by a 10-agent LLM swarm. Validated by a deterministic Python pipeline.

**[View the live site](https://t3dy.github.io/ShakesPhyllis/)**

---

## What This Is

ShakesPhyllis is a structured scholarly database of Shakespeare's Sonnets, designed to support close reading, performance direction, and data visualization. Every sonnet has been analyzed for rhetorical devices, dramatic situation, emotional arc, character dynamics, and themes — then stored in a 21-table SQLite database with full provenance tracking.

The project explores the dramatic love triangle at the heart of the sequence:

- **The Fair Young Man (FYM)** — the beautiful young nobleman of Sonnets 1-126
- **The Dark Lady (DL)** — the sexually compelling, morally ambiguous woman of Sonnets 127-152
- **The Rival Poet (RP)** — the competing poet of Sonnets 78-86
- **The Speaker** — Shakespeare's persona, caught between devotion, jealousy, and self-knowledge

## What's In the Database

| Layer | Contents | Rows |
|-------|----------|------|
| **Core Text** | 154 sonnets, 2,155 lines, 615 stanzas (1609 Quarto via Project Gutenberg) | 2,924 |
| **Characters** | 4 characters, 10 historical candidates, 13 scholars, 15 bibliography entries | 42 |
| **Rhetoric** | 24 rhetorical devices, 8 analytical modes, 1,041 device instances | 1,073 |
| **Enrichment** | 154 close-reading analyses, 1,177 line annotations, 752 theme tags, 332 character appearances, 154 directing notes, 541 mode assignments | 3,110 |
| **Essays** | 2 thematic essays with sonnet cross-references | 31 |
| **Groups** | 47 scholarly sonnet groupings across the sequence | 47+ |

Every enrichment datum carries provenance: `source_method` (DETERMINISTIC, LLM_ASSISTED, SEED_DATA), `review_status` (DRAFT, REVIEWED, VERIFIED), and `confidence` (HIGH, MEDIUM, LOW).

## How It Was Built

### The Two-Layer Architecture

The project enforces a strict separation between **deterministic work** (Python) and **judgment work** (LLM):

```
Seed JSON → Python scripts → SQLite database → Python build → Static HTML
                ↑                    ↑
           (deterministic)    (LLM enrichment,
                               validated before
                               insertion)
```

**Python handles:** parsing sonnets from the 1609 Quarto, building the schema, seeding reference data, validating enrichment against controlled vocabularies, loading enrichment into the database, generating the site.

**LLM handles:** close-reading analysis, rhetorical device identification, dramatic situation analysis, performance direction notes, theme classification, character appearance mapping.

Neither layer does the other's job. Python cannot identify irony. The LLM cannot maintain foreign key constraints.

### The Swarm

The 154 sonnets were enriched using a **10-agent parallel swarm** — each agent handling a thematic batch (Procreation, Devotion, First Betrayal, Absence, Time/Mortality, Rival Poet, Estrangement, etc.). Each agent received:

- The sonnet texts for its batch
- Locked controlled vocabularies (valid device_ids, mode_ids, character_ids)
- A style exemplar (Sonnet 1's full enrichment)
- Thematic context for its batch's dramatic arc

Agent output passed through `validate_enrichment.py` before entering the database — mapping invented vocabulary to valid schema values and rejecting unmappable entries. The deterministic layer policed the judgment layer's output.

### The Data Ontology

21 tables across 5 layers, designed so the LLM can reference poetic structure accurately:

- **Lines as first-class entities** — the LLM quotes by line number, never hallucinates text
- **Stanzas map to Q1/Q2/Q3/COUPLET** — structural analysis is always grounded in form
- **Volta as data** — every sonnet's turn is recorded with line number and type (DRAMATIC, LOGICAL, TONAL, IRONIC)
- **Controlled vocabularies** — 24 rhetorical devices, 8 analytical modes, 4 characters, all with CHECK-level enforcement
- **Sequence arc state** — 13 dramatic phases from PROCREATION through CUPID_CODA

### The Pipeline

```bash
# Full rebuild (deterministic)
python scripts/init_db.py --force          # 21 empty tables
python scripts/seed_sonnets.py             # 154 sonnets, 2,155 lines, 615 stanzas
python scripts/seed_reference.py           # characters, scholars, devices, modes
python scripts/seed_groups_v2.py           # 47 scholarly groupings
python scripts/seed_essay_unresolved.py    # seed essay

# Enrichment (LLM-assisted, validated)
python scripts/validate_enrichment.py --fix  # pre-load validation gate
python scripts/enrich_sonnets.py             # load all enrichment batches
python scripts/validate_db.py                # post-load integrity check

# Build
python scripts/build_visualizations.py     # data visualization dashboard
```

11 scripts, all idempotent (safe to re-run). Enrichment JSON files in `data/enrichment/` are the source of truth; the database is the compiled state.

## The Visualizations

The site includes an 11-chart data dashboard built with Chart.js in the SHWEP dark academic theme:

1. **The Dramatic Arc** — 13-phase color-coded timeline across 154 sonnets
2. **Addressee Distribution** — FYM dominance (123/154 sonnets)
3. **Theme Constellation** — Top 25 of 328 themes (beauty and time dominate)
4. **Theme x Addressee Heatmap** — what the Speaker talks about changes by character
5. **Rhetorical Device Frequency** — metaphor (235), paradox (114), pun (108) lead
6. **Device Density Histogram** — bell curve peaking at 7-8 devices per sonnet
7. **Volta & Couplet Types** — how sonnets turn and how they end
8. **Love Triangle Stream** — character presence across the sequence
9. **Analytical Mode Radar** — rhetorical and dramatic modes dominate
10. **Scholarly Groupings** — 47 thematic clusters
11. **Annotation Density by Line** — where readers focus (line 1 and couplet)

## The Essay

**"Shakespeare's Sonnet Against Petrarch: Form, Volta, and the English Innovation"** — a comparative essay examining how the three-quatrain-plus-couplet structure enabled a fundamentally different kind of poem from the Petrarchan model, drawing on the database's volta and couplet function data.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Database | SQLite 3 (single file, zero config) |
| Scripts | Python 3.10+ (standard library only) |
| Enrichment | Claude Code (Opus 4.6) via 10-agent swarm |
| Validation | `validate_enrichment.py` (pre-load gate with controlled vocabulary mapping) |
| Charts | Chart.js 4 (CDN, no npm) |
| Site | Vanilla HTML/CSS/JS (no frameworks) |
| Theme | SHWEP-style dark academic (navy + cream + gold) |
| Deploy | GitHub Pages |

## Project Documentation

| Document | Purpose |
|----------|---------|
| `CLAUDE.md` | Operational contract: data flow, controlled vocabularies, Deckard boundary |
| `docs/ONTOLOGY.md` | 21-table schema with all columns, types, and constraints |
| `docs/PIPELINE.md` | 11 scripts in execution order with validation gates |
| `docs/SYSTEM.md` | Architecture and provenance model |
| `docs/SYSTEM_AUDIT.md` | Audit findings and correction log |
| `docs/REVIEW_PIPELINE.md` | DRAFT → REVIEWED → VERIFIED promotion criteria |
| `SWARMPLUSPYTHON.md` | Architectural rationale for two-layer (deterministic + LLM) approach |
| `SONNETSTUDYDECKARDANALYSIS.md` | What Python does vs what the LLM does |

## License

Sonnet texts are public domain (1609 Quarto via Project Gutenberg). Analysis, annotations, and code are original work.

---

*Built with [Claude Code](https://claude.ai/claude-code)*
