# Phase Status Log — Shakespeare Sonnets

Update this file at the end of every session.

---

## Session: 2026-03-24 (Session 4) — System Hardening

**Phase:** Infrastructure Correction (cross-cutting)
**Status:** COMPLETE
**Trigger:** Swarm enrichment exposed structural weaknesses (invalid device_ids bypassing validation, ontology drift under LLM pressure, documentation lag)

### What was corrected:

**Infrastructure (new scripts):**
- `scripts/validate_enrichment.py` — pre-load validation gate with --fix mode. Maps invented device_ids/mode_ids to valid schema values. Rejects unmappable values. REQUIRED before enrich_sonnets.py.
- `scripts/prep_batch.py` — generates locked-vocabulary prompts for LLM agents. Prevents agents from inventing IDs.
- `scripts/fix_enrichment.py` — DEPRECATED (replaced by validate_enrichment.py --fix)

**Schema changes:**
- Added `sequence_arc_state` column to sonnets table (13 arc phases: PROCREATION through CUPID_CODA)
- Added 3 rhetorical devices: POLYPTOTON, RHETORICAL_QUESTION, ALLUSION (editorially justified additions from swarm output)

**Documentation hardened:**
- `CLAUDE.md` — rewritten as strict operational contract with controlled vocabularies, anti-drift rules, swarm rules, Deckard boundary
- `DOCUMENTAIRTRAFFICCONTROL.md` — added "DO NOT GUESS — ALWAYS ROUTE" rule, new doc entries
- `docs/PIPELINE.md` — corrected to show all 11 actual scripts with idempotency notes
- `docs/SYSTEM_AUDIT.md` — NEW: full audit findings and issue register
- `docs/REVIEW_PIPELINE.md` — NEW: DRAFT→REVIEWED→VERIFIED promotion criteria
- `SWARMPLUSPYTHON.md` — NEW: architectural rationale for two-layer approach

**Issues resolved:**
- C2: Pre-load validation gate now structural (validate_enrichment.py)
- C3: Vocabulary locked in prep_batch.py prompts
- H2: All 11 scripts documented in PIPELINE.md
- H3: PHASESTATUS.md updated to actual state
- M5: 3 added devices documented and justified

**Issues remaining:**
- C1: CHECK constraints not yet added to init_db.py (non-breaking; validate_enrichment.py catches at JSON level)
- H1: ONTOLOGY.md not yet updated with all 47 groups (large doc update)
- M1: 121 PDFs still in project root (not moved to corpus/)

### Enrichment state at end of session:
- 71 sonnets enriched (was: 17 documented, 54 undocumented)
- 14 enrichment batches present
- Swarm enrichment for remaining 83 sonnets: 7 agents still in progress

### Next steps:
- Process remaining swarm agent output through validate_enrichment.py --fix pipeline
- Update ONTOLOGY.md with 47 groups and sequence_arc_state
- Add CHECK constraints to init_db.py
- Move PDFs to corpus/
- Phase 3: build_site.py when enrichment reaches ~100 sonnets

### Blockers:
- None critical. ONTOLOGY.md update is deferred but non-blocking.

---

## Session: 2026-03-24 (Session 3) — Swarm Enrichment

**Phase:** 2 (Full Enrichment)
**Status:** IN PROGRESS

### What was built:
- 10 parallel enrichment agents launched (swarm pattern)
- Thematic batching: FYM devotion, absence, time, immortality, rival poet, estrangement, absence/beauty, fault, DL core, DL tail/cupid
- Batches 10, 13, 14, 15, 18, 19 completed and loaded
- Batches 11, 12, 16, 17 in progress
- `SWARMPLUSPYTHON.md` — documents the swarm + deterministic architecture

### Issues discovered:
- Swarm agents invented device_ids not in schema (POLYPTOTON, RHETORICAL_QUESTION, ALLUSION, TRANSFERRED_EPITHET, etc.)
- Swarm agents invented mode_ids not in schema (PHILOSOPHICAL, META-POETIC, CONFESSIONAL, etc.)
- Some agents output bare JSON arrays instead of {"batch":..., "sonnets":[...]}
- Reactive fix via fix_enrichment.py; later replaced by structural fix (validate_enrichment.py)

### Enrichment expanded from 54 → 71 sonnets in this session

---

## Session: 2026-03-24 (Session 2)

**Phases:** 1 (Scaffold & Seed) + 1b (Enrichment Sample)
**Status:** COMPLETE

### What was built:
- `data/sonnet_texts.json` — 154 sonnets parsed from Project Gutenberg 1609 Quarto, clean ASCII, correct line counts (including Sonnet 99's 15 lines and Sonnet 126's 12 lines)
- `data/sonnets_seed.json` — 4 characters with 10 historical candidates, 13 scholars, 15 bibliography entries, 20 rhetorical devices, 8 analytical modes, 8 sonnet groups with 101 memberships
- `scripts/parse_gutenberg.py` — one-time utility
- `scripts/init_db.py` — creates 22-table schema in single pass (no migrations)
- `scripts/seed_sonnets.py` — deterministic: 154 sonnets, 615 stanzas, 2,155 lines with stanza assignments
- `scripts/seed_reference.py` — all reference/lookup tables
- `scripts/enrich_sonnets.py` — loads LLM-generated enrichment from JSON batches
- `scripts/validate_db.py` — full integrity checks (all passing)
- 3 enrichment batches (17 sonnets total): procreation, triangle/betrayal, immortality/time
- Updated all system docs: ONTOLOGY.md, PIPELINE.md, ROADMAP.md

### Schema change from Phase 0 plan:
- Simplified from 25 tables across 3 migrations → 22 tables in single init_db.py
- Renamed: sonnet_lines → lines, sonnet_sections → stanzas, sonnet_figures → line_devices, sonnet_characters → character_appearances, analysis_modes → analytical_modes
- Added: directing_notes, line_annotations (with emphasis_words, delivery_note for audiobook project)
- Dropped: line_addressee_shifts, scholar_works, scholarly_refs, glossary_terms, term_sonnet_refs, intertextual_links, thematic_threads, timeline_events, editions, llm_analysis_queue (can add later if needed)

### Next steps:
- Phase 2: Continue enrichment (137 remaining sonnets, priority: FYM core, DL core, Rival Poet)
- Phase 3: build_site.py + SHWEP templates
- Template design for sonnet analysis pages, directing pages, context pages

### Blockers:
- None. Phase 2 and Phase 3 are both READY and can proceed in parallel.

---

## Session: 2026-03-24 (Session 1)

**Phase:** 0 (Init Documents)
**Status:** COMPLETE

### What was done:
- All 11 init documents created
- 25-table schema designed (later simplified in Session 2)
- Deckard boundary analysis completed
- 19-script pipeline defined (later simplified in Session 2)
- 4-tab site structure designed
- Git initialized

### Next steps:
- Phase 1 — create seed data and scaffold scripts
