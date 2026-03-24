# Deckard Boundary Analysis — Shakespeare Sonnets Project

**PKD Codename: Rick Deckard** — Distinguishing deterministic tasks from probabilistic tasks.

This document maps every task in the project to either Python (deterministic, fast, exact) or Claude Code (probabilistic, judgment-requiring, batched for token efficiency).

---

## DETERMINISTIC TASKS (Python scripts)

These tasks require no LLM judgment. They are fast, exact, reproducible, and cheap.

| Task | Why Deterministic | Script | Confidence |
|------|-------------------|--------|------------|
| Parse 1609 Quarto text → 154 sonnets × 14 lines | Fixed structure, regex-reliable | `seed_sonnets.py` | HIGH |
| Assign section labels (Q1=1-4, Q2=5-8, Q3=9-12, COUPLET=13-14) | Pure function of line number | `seed_sonnets.py` | HIGH |
| Assign rhyme positions (ABAB CDCD EFEF GG) | Fixed pattern from line number | `seed_sonnets.py` | HIGH |
| Extract rhyme words (last word per line) | String split | `seed_sonnets.py` | HIGH |
| Compute global line numbers (1-2156) | Arithmetic: (sonnet-1)*14 + line | `seed_sonnets.py` | HIGH |
| Create sonnet_sections rows (154 × 4 = 616) | Deterministic from structure | `seed_sonnets.py` | HIGH |
| Syllable counting (baseline) | CMU Pronouncing Dictionary lookup | `seed_sonnets.py` | HIGH (modern), MEDIUM (archaic) |
| Schema creation and migrations | DDL is deterministic | `init_db.py`, `migrate_*.py` | HIGH |
| Seed JSON → SQLite ingestion | INSERT OR IGNORE, no judgment | All `seed_*.py` | HIGH |
| Cross-reference linking (glossary ↔ sonnets) | String matching after terms identified | `link_intertexts.py` (partial) | HIGH |
| Template assembly of analysis HTML | Read DB fields, fill template slots | `build_analysis.py` | HIGH |
| Static site generation (DB → HTML) | Jinja-style templating | `build_site.py` | HIGH |
| Validation (14 lines/sonnet, enum compliance) | SQL COUNT + assertions | `validate_sonnets.py` | HIGH |

---

## PROBABILISTIC TASKS (Claude Code — targeted reading)

These tasks require literary judgment, reading comprehension, or aesthetic decision-making. They are batched for token efficiency.

### Pass 1: Full Analysis (5-10 sonnets per batch)

**Read once, extract five things.** This is the most token-efficient pass.

| Extraction | Why LLM | Output Table |
|------------|---------|-------------|
| Classify primary addressee (FYM/DL/BOTH/SELF/UNKNOWN) | Requires understanding dramatic context, pronouns, tone | `sonnets.primary_addressee` |
| Identify line-level addressee shifts | Requires tracking pronoun reference across 14 lines | `line_addressee_shifts` |
| Identify rhetorical figures with line-span precision | Must distinguish metaphor from simile, recognize irony | `sonnet_figures` |
| Rank analytical salience (PRIMARY/SUPPORTING/MINOR per figure) | Aesthetic judgment: what makes THIS sonnet distinctive? | `sonnet_figures.analytical_salience` |
| Assign analysis_modes priority | Holistic judgment: "this sonnet is ABOUT wordplay" | `sonnet_analysis_modes` |
| Write section rhetorical_function (4 per sonnet) | Argumentative structure of each quatrain/couplet | `sonnet_sections.rhetorical_function` |
| Classify volta_type | How the turn works: reversal, amplification, resolution | `sonnets.volta_type` |

**Input per batch:** Sonnet text + device catalog + mode catalog + sequence group context.
**Output per sonnet:** Structured JSON with all 7 extractions.
**Estimated tokens:** ~500 per sonnet × 154 = ~77K total. Batched at 5-10, ~15-30 sessions.

### Pass 2: Scholarly Extraction (one PDF at a time)

| Task | Why LLM | Output Table |
|------|---------|-------------|
| Extract scholarly claims from corpus PDFs | Reading comprehension + structured extraction | `scholarly_refs` |

**Workflow:** Read ONE PDF → identify which sonnets it discusses → extract claims with interpretation_type, summary, page reference.
**Priority PDFs:** Vendler (all 154), Booth (all 154), Hotson (FYM identity), Chambers (FYM youth), Pequigney (sexuality), Healy (alchemy + sonnets).
**Estimated:** ~55 PDFs × variable extraction = major effort. Start with the 5 highest-value sources.

### Pass 3: Glossary & Annotation (10-15 sonnets per batch)

| Task | Why LLM | Output Table |
|------|---------|-------------|
| Identify archaic/specialized vocabulary | Early Modern English knowledge | `glossary_terms` |
| Place terms in sonnet context | Contextual word sense | `term_sonnet_refs` |
| Write line glosses and paraphrases | Literary interpretation | `annotations` |
| Write section-level commentary | Requires rhetorical understanding | `annotations` |

**Depends on:** Pass 1 (uses figures, modes, sections as context for better glosses).
**Estimated tokens:** ~300 per sonnet × 154 = ~46K total.

### Pass 4: Intertextual Links (by sequence group)

| Task | Why LLM | Output Table |
|------|---------|-------------|
| Identify sonnet-to-sonnet echoes | Requires recognizing thematic/verbal parallels | `intertextual_links` |
| Identify allusions to Ovid, Petrarch, Sidney, Daniel | Requires literary knowledge beyond corpus | `intertextual_links` |

**Batch by:** Sequence group (Procreation 1-17, FYM Beauty 18-77, etc.).
**Estimated:** Modest — ~200 links across 154 sonnets.

### Pass 5: Directing Notes (5 sonnets per batch)

| Task | Why LLM | Output Table |
|------|---------|-------------|
| Write line-by-line performance guidance | Requires understanding of meter, emotion, dramatic intent | New: `directing_notes` or embedded in annotations |
| Identify emotional arc per section | Requires reading the poem as spoken performance | `sonnet_sections` enrichment |
| Flag metrical variations that affect delivery | Aesthetic + technical judgment | `sonnet_lines` enrichment |

**Depends on:** Passes 1 and 3 (uses figures, addressee, glosses as input).
**Most expensive per-sonnet task.** Start with the 3 sample sonnets (v1 scope).

---

## TOKEN EFFICIENCY STRATEGY

**Principle: Read once, extract many.**

Instead of 5 separate passes over 154 sonnets (770 sonnet-reads), we do:
- Pass 1: 154 reads × 7 extractions = 154 reads (not 1,078)
- Pass 2: ~55 PDF reads (independent of sonnet count)
- Pass 3: 154 reads × 4 extractions = 154 reads (not 616)
- Pass 4: ~10 batch reads (by sequence group)
- Pass 5: 154 reads × 1 extraction = 154 reads

**Total: ~527 reads vs ~1,908 naive. ~72% reduction.**

For v1 (3 sample sonnets): ~15 reads total across all passes.

---

## VALIDATION LAYERS

Where LLM output crosses into deterministic systems:

| Boundary | Validation | Rejection Action |
|----------|------------|-----------------|
| Addressee classification → `sonnets` | CHECK constraint on enum values | Reject and re-prompt |
| Figures → `sonnet_figures` | line numbers 1-14; device_id exists; quoted_text matches actual line | Reject row, log error |
| Analysis modes → `sonnet_analysis_modes` | mode_id exists; priority is integer ≥ 1 | Reject row |
| Scholarly refs → `scholarly_refs` | sonnet_id exists; bib_id exists; interpretation_type valid | Reject row |
| Annotations → `annotations` | target_type matches provided fields; line numbers 1-14 | Reject row |
| ALL LLM outputs | Default provenance: source_method='LLM_ASSISTED', review_status='DRAFT', confidence='MEDIUM' | Automatic |

---

## BOUNDARY VIOLATIONS TO AVOID

### WASTE — Do NOT use LLM for:
- Splitting sonnets into lines (regex)
- Assigning Q1/Q2/Q3/COUPLET labels (arithmetic)
- Extracting rhyme words (string split)
- Computing line numbers (math)
- Counting syllables for modern words (CMU dictionary)
- Building HTML from DB fields (template assembly)
- Validating schema constraints (SQL)
- Generating the 616 sonnet_sections rows (deterministic from structure)

### RISK — Do NOT use deterministic code for:
- Classifying addressee (dramatic context required)
- Ranking analytical salience (aesthetic judgment)
- Identifying irony (the opposite of literal meaning — regex cannot do this)
- Writing section-level commentary (rhetorical understanding)
- Extracting scholarly claims from PDFs (reading comprehension)
- Writing directing notes (performance interpretation)
- Identifying puns (requires multiple meaning awareness)

### DANGER — Never allow:
- LLM output directly into DB without validation against enum constraints
- LLM-generated line text to overwrite 1609 Quarto text (the text is sacred)
- LLM analysis to auto-promote to VERIFIED status
- LLM to fabricate scholarly citations (must extract from actual PDFs)
- LLM to guess line numbers without querying sonnet_lines table first

---

## ARCHAIC WORD FALLBACK

Syllable counting uses CMU Pronouncing Dictionary (deterministic, HIGH confidence). For words not in CMU (archaic forms like "engross'd", "unthrift", "niggarding"):
1. First attempt: strip common suffixes (-'d, -st, -eth) and retry CMU
2. Fallback: LLM-assisted syllable count, tagged as LLM_ASSISTED / MEDIUM confidence
3. Human review queue: flag all LLM-counted words for batch verification

This is the ONE place where a deterministic task has a controlled LLM fallback.
