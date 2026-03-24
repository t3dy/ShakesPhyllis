# Document Air Traffic Control — Shakespeare Sonnets

**Read this file first.** It tells you which document to read for any task.

## Routing Table

| If you need to... | Read this |
|-------------------|-----------|
| Understand the project | `CLAUDE.md` |
| Find a document | **You're here** |
| Know what Python does vs what Claude Code does | `SONNETSTUDYDECKARDANALYSIS.md` |
| Understand the architecture | `docs/SYSTEM.md` |
| Work with the database schema | `docs/ONTOLOGY.md` |
| Know script execution order | `docs/PIPELINE.md` |
| Understand site structure or page templates | `docs/INTERFACE.md` |
| Check what's built vs what's next | `docs/ROADMAP.md` |
| Log session progress | `PHASESTATUS.md` |
| Find the plan that produced all this | `.claude/plans/lazy-inventing-llama.md` |

## Task-Specific Routing

| Task | Primary Doc | Also Read |
|------|------------|-----------|
| **Add or modify a database table** | `docs/ONTOLOGY.md` | `docs/PIPELINE.md` (which script creates it) |
| **Write a new pipeline script** | `docs/PIPELINE.md` | `docs/ONTOLOGY.md` (which tables it touches), `SONNETSTUDYDECKARDANALYSIS.md` (is it Python or LLM work?) |
| **Build a site page or template** | `docs/INTERFACE.md` | `docs/ONTOLOGY.md` (what data the page displays) |
| **Do LLM extraction (addressees, figures, modes)** | `SONNETSTUDYDECKARDANALYSIS.md` | `docs/ONTOLOGY.md` (target tables), `docs/PIPELINE.md` (which pass) |
| **Work with sonnet text** | `data/sonnet_texts.json` | `docs/ONTOLOGY.md` (sonnets + sonnet_lines tables) |
| **Work with characters (FYM, DL)** | `docs/ONTOLOGY.md` → characters table | `CLAUDE.md` (candidate list) |
| **Work with scholarly sources** | `docs/ONTOLOGY.md` → bibliography, scholarly_refs | Corpus PDFs in `corpus/` |
| **Add a new content tab or page type** | `docs/INTERFACE.md` | `docs/SYSTEM.md` (architecture constraints) |
| **Debug a build failure** | `docs/PIPELINE.md` | Script source in `scripts/` |
| **Check phase gates** | `docs/ROADMAP.md` | `PHASESTATUS.md` |
| **Start a new session** | `PHASESTATUS.md` | `docs/ROADMAP.md` |

## Document Status

| Document | Status | Last Updated |
|----------|--------|-------------|
| `CLAUDE.md` | CURRENT | 2026-03-24 |
| `DOCUMENTAIRTRAFFICCONTROL.md` | CURRENT | 2026-03-24 |
| `SONNETSTUDYDECKARDANALYSIS.md` | CURRENT | 2026-03-24 |
| `docs/SYSTEM.md` | CURRENT | 2026-03-24 |
| `docs/ONTOLOGY.md` | CURRENT | 2026-03-24 |
| `docs/PIPELINE.md` | CURRENT | 2026-03-24 |
| `docs/INTERFACE.md` | CURRENT | 2026-03-24 |
| `docs/ROADMAP.md` | CURRENT | 2026-03-24 |
| `PHASESTATUS.md` | CURRENT | 2026-03-24 |
| `data/sonnet_texts.json` | NOT YET CREATED | Phase 2 |
| `data/sonnets_seed.json` | NOT YET CREATED | Phase 2 |
