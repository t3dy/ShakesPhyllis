# Document Air Traffic Control — Shakespeare Sonnets

**Read this file first.** It tells you which document to read for any task.

**DO NOT GUESS — ALWAYS ROUTE.**

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
| Review audit findings and corrections | `docs/SYSTEM_AUDIT.md` |
| Understand provenance promotion (DRAFT→VERIFIED) | `docs/REVIEW_PIPELINE.md` |
| Understand the swarm + deterministic architecture | `SWARMPLUSPYTHON.md` |
| Find valid vocabulary values (device_ids, mode_ids, etc.) | `CLAUDE.md` → Controlled Vocabularies |

## Task-Specific Routing

| Task | Primary Doc | Also Read |
|------|------------|-----------|
| **Add or modify a database table** | `docs/ONTOLOGY.md` | `docs/PIPELINE.md` (which script creates it) |
| **Write a new pipeline script** | `docs/PIPELINE.md` | `docs/ONTOLOGY.md`, `SONNETSTUDYDECKARDANALYSIS.md` |
| **Build a site page or template** | `docs/INTERFACE.md` | `docs/ONTOLOGY.md` (what data the page displays) |
| **Do LLM enrichment (analysis, devices, directing)** | `SONNETSTUDYDECKARDANALYSIS.md` | `CLAUDE.md` (controlled vocabularies), `docs/PIPELINE.md` (enrichment workflow) |
| **Prepare a swarm batch** | `docs/PIPELINE.md` → enrichment workflow | `CLAUDE.md` (controlled vocabularies) |
| **Validate enrichment output** | `docs/PIPELINE.md` | `scripts/validate_enrichment.py` |
| **Work with sonnet text** | `data/sonnet_texts.json` | `docs/ONTOLOGY.md` (sonnets, lines, stanzas) |
| **Work with characters (FYM, DL)** | `docs/ONTOLOGY.md` → characters table | `CLAUDE.md` (candidate list) |
| **Work with scholarly sources** | `docs/ONTOLOGY.md` → bibliography | Corpus PDFs in `corpus/` |
| **Add a new content tab or page type** | `docs/INTERFACE.md` | `docs/SYSTEM.md` |
| **Debug a build failure** | `docs/PIPELINE.md` | Script source in `scripts/` |
| **Check phase gates** | `docs/ROADMAP.md` | `PHASESTATUS.md` |
| **Start a new session** | `PHASESTATUS.md` | `docs/ROADMAP.md` |
| **Add a new controlled vocabulary value** | `CLAUDE.md` → Anti-Drift Rule | `docs/ONTOLOGY.md` |
| **Review or promote enrichment status** | `docs/REVIEW_PIPELINE.md` | `PHASESTATUS.md` |

## Document Status

| Document | Status | Last Updated |
|----------|--------|-------------|
| `CLAUDE.md` | CURRENT | 2026-03-24 (hardened) |
| `DOCUMENTAIRTRAFFICCONTROL.md` | CURRENT | 2026-03-24 (hardened) |
| `SONNETSTUDYDECKARDANALYSIS.md` | CURRENT | 2026-03-24 |
| `docs/SYSTEM.md` | CURRENT | 2026-03-24 |
| `docs/ONTOLOGY.md` | NEEDS UPDATE | 2026-03-24 (47 groups not documented) |
| `docs/PIPELINE.md` | CURRENT | 2026-03-24 (corrected) |
| `docs/INTERFACE.md` | CURRENT | 2026-03-24 |
| `docs/ROADMAP.md` | NEEDS UPDATE | 2026-03-24 (gates not updated) |
| `docs/SYSTEM_AUDIT.md` | NEW | 2026-03-24 |
| `docs/REVIEW_PIPELINE.md` | NEW | 2026-03-24 |
| `SWARMPLUSPYTHON.md` | NEW | 2026-03-24 |
| `PHASESTATUS.md` | NEEDS UPDATE | 2026-03-24 |
| `data/sonnet_texts.json` | BUILT | 2026-03-24 |
| `data/sonnets_seed.json` | BUILT | 2026-03-24 |
