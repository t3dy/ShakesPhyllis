# System Architecture — Shakespeare Sonnets Digital Humanities Site

## Architecture Pattern

Replicates AtalantaClaudiens: single-direction data flow, no runtime dependencies.

```
data/sonnet_texts.json  ─┐
data/sonnets_seed.json  ─┤
                         ↓
              Python seed scripts (deterministic)
                         ↓
              SQLite database (db/sonnets.db)  ← SOURCE OF TRUTH
                         ↓
              Python extract scripts (LLM-assisted, validated)
                         ↓
              SQLite database (enriched)
                         ↓
              build_analysis.py (deterministic template assembly)
                         ↓
              build_site.py (static site generation)
                         ↓
              site/ (static HTML + CSS + JS)
                         ↓
              GitHub Pages
```

## Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Database | SQLite 3 | Zero-config, single file, portable, perfect for static site generation |
| Scripts | Python 3.10+ | Matches AtalantaClaudiens; standard library + minimal deps |
| Site | Vanilla HTML/CSS/JS | No frameworks, no npm, no build tools — works forever |
| Theme | SHWEP-style dark academic | Dark background, serif typography, scholarly voice |
| Deploy | GitHub Pages | Free, static, versioned |
| LLM | Claude Code (interactive sessions) | Not API — Claude Code reads sonnets and writes structured JSON to staging |

## Constraints

- **No runtime dependencies.** The generated site is pure static HTML.
- **No frameworks.** No React, no Hugo, no 11ty. Python generates HTML directly.
- **Idempotent scripts.** Every script is safe to re-run (CREATE TABLE IF NOT EXISTS, INSERT OR IGNORE).
- **One-direction data flow.** Seed JSON → DB → HTML. Never edit generated HTML or the DB directly.
- **No API calls at build time.** LLM work happens in interactive sessions, outputs go to seed JSON or staging, then deterministic scripts ingest.

## Provenance Model

Every datum in the database carries three provenance fields:

| Field | Type | Values |
|-------|------|--------|
| `source_method` | TEXT | `DETERMINISTIC` · `CORPUS_EXTRACTION` · `LLM_ASSISTED` · `SEED_DATA` · `HUMAN_VERIFIED` |
| `review_status` | TEXT | `DRAFT` → `REVIEWED` → `VERIFIED` (forward-only promotion) |
| `confidence` | TEXT | `HIGH` · `MEDIUM` · `LOW` |

### Provenance Rules

| Data Type | source_method | confidence | review_status |
|-----------|--------------|------------|---------------|
| 1609 Quarto text, line numbers, sections | DETERMINISTIC | HIGH | VERIFIED |
| Scholarly metadata from seed JSON | SEED_DATA | HIGH | REVIEWED |
| LLM-classified addressees | LLM_ASSISTED | MEDIUM | DRAFT |
| LLM-identified rhetorical figures | LLM_ASSISTED | MEDIUM | DRAFT |
| LLM-written commentary | LLM_ASSISTED | MEDIUM | DRAFT |
| PDF-extracted scholarly claims | CORPUS_EXTRACTION | MEDIUM | DRAFT |
| Human-reviewed data | HUMAN_VERIFIED | HIGH | VERIFIED |

- Never overwrite `VERIFIED` data without logging discrepancy
- Never auto-promote `DRAFT` → `VERIFIED` (requires human review step)
- `REVIEWED` means a human glanced at it; `VERIFIED` means a human confirmed it against sources

## File Locations

| Purpose | Path |
|---------|------|
| Project instructions | `CLAUDE.md` |
| Document routing | `DOCUMENTAIRTRAFFICCONTROL.md` |
| Deckard boundary map | `SONNETSTUDYDECKARDANALYSIS.md` |
| Database | `db/sonnets.db` (generated) |
| Pipeline scripts | `scripts/*.py` |
| Canonical seed data | `data/*.json` |
| Architecture docs | `docs/SYSTEM.md` (this file) |
| Schema docs | `docs/ONTOLOGY.md` |
| Pipeline docs | `docs/PIPELINE.md` |
| Site structure docs | `docs/INTERFACE.md` |
| Phase tracking | `docs/ROADMAP.md`, `PHASESTATUS.md` |
| Generated site | `site/` |
| Source PDFs | `corpus/` (read-only) |

## Deploy Target

GitHub Pages at `t3dy/ShakespeareSonnets` (or similar). Deploy from `site/` directory via GitHub Actions or manual push.
