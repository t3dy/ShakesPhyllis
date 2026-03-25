# Swarm + Python: A Two-Layer Architecture for LLM-Assisted Digital Humanities

## The Core Insight

Building a knowledge-rich database from a literary corpus requires two fundamentally different kinds of work:

1. **Deterministic work** — parsing, counting, structuring, validating, templating — where the answer is computable and reproducible.
2. **Judgment work** — literary analysis, close reading, rhetorical classification, performance direction — where the answer requires taste, context, and interpretation.

These two layers have different tools, different failure modes, and different quality guarantees. Mixing them produces unreliable systems. Separating them cleanly produces something greater than either alone.

## The Architecture

```
                    DETERMINISTIC LAYER (Python)
                    ============================
Seed JSON ──→ init_db.py ──→ SQLite schema (22 tables)
              seed_sonnets.py ──→ 154 sonnets, 2,155 lines, 615 stanzas
              seed_reference.py ──→ characters, scholars, devices, modes
              enrich_sonnets.py ──→ loads validated JSON into enrichment tables
              validate_db.py ──→ integrity checks, FK constraints, enum compliance
              build_site.py ──→ static HTML from DB (template assembly)

                    JUDGMENT LAYER (LLM Swarm)
                    ==========================
Sonnet text + schema + exemplar + thematic context
    ↓
10 parallel agents, each handling a thematic batch:
    → Close-reading analysis (volta, argument, emotional arc)
    → Line-by-line annotations (emphasis, delivery, gloss)
    → Directing notes (performance guidance, character notes)
    → Rhetorical device identification (per-line, with quotation)
    → Analytical mode ranking (per-sonnet, with rationale)
    → Theme tagging (with prominence)
    → Character appearance mapping (with evidence)
    ↓
Structured JSON (validated against schema)
    ↓
enrich_sonnets.py ──→ SQLite (INSERT OR REPLACE, idempotent)
    ↓
validate_db.py ──→ pass/fail
```

## Why Two Layers?

### The Deterministic Layer guarantees:
- **Reproducibility**: Run the same script twice, get the same database.
- **Referential integrity**: Foreign keys, UNIQUE constraints, CHECK constraints.
- **Auditability**: Every datum has provenance (source_method, review_status, confidence).
- **Idempotency**: Every script is safe to re-run. CREATE TABLE IF NOT EXISTS. INSERT OR REPLACE.

### The Judgment Layer provides:
- **Literary interpretation**: What does "contracted to thine own bright eyes" mean? (Narcissism + legal pun on marriage contract.)
- **Aesthetic judgment**: Which rhetorical device is PRIMARY here? Is this ironic or sincere?
- **Dramatic reading**: Who is the Speaker in this moment? What does he want? What is he hiding?
- **Cross-reference awareness**: How does this sonnet echo or reverse an earlier one?

### Neither can do the other's job:
- Python cannot identify irony. (Irony is the opposite of literal meaning — no regex for that.)
- LLMs cannot reliably count to 14 or maintain FK constraints across 22 tables.
- Python cannot decide whether "sweet" is sincere or sarcastic in context.
- LLMs cannot guarantee that line_number 5 in Sonnet 99 maps to the correct line_id.

## The Swarm Pattern

### What makes enrichment swarm-friendly:

1. **Independence**: Each sonnet's enrichment is self-contained. Sonnet 34's analysis doesn't depend on Sonnet 60's analysis having been done first.
2. **Well-defined contract**: The JSON schema is rigid — every agent produces the same structure.
3. **Bounded context**: Each agent needs only: the sonnet text, the device/mode catalog, one style exemplar, and thematic context for its batch.

### What the swarm CANNOT do:

1. **Cross-sonnet consistency**: Agent A analyzing Sonnet 34 doesn't know what Agent B said about Sonnet 35, even though they're consecutive. This is mitigated by grouping thematically related sonnets in the same batch.
2. **Cumulative voice**: A single analyst doing all 154 sonnets would develop an interpretive "feel" — consistent terminology, deepening understanding. The swarm trades this for speed.
3. **Sequence-aware analysis**: The sonnets tell a story. Agent working on Sonnet 120 ("Then give me welcome, next my heaven the best") doesn't see that Sonnet 119 built up to this moment. Again, thematic batching mitigates but doesn't eliminate this.

### Mitigation strategies:

- **Thematic batching**: Group sonnets by dramatic arc, not by number. The "First Betrayal" triptych (33-36) goes to one agent. The "Will" pun sonnets (135-136) go together.
- **Rich context in prompt**: Each agent gets not just the sonnet text but scholarly context about the group's dramatic situation, key critical debates, and character dynamics.
- **Style exemplar**: Every agent sees the same Sonnet 1 enrichment as a quality/depth template.
- **Post-hoc validation**: The deterministic layer catches structural errors (bad line numbers, invalid device_ids, missing fields). A review pass can catch tonal inconsistencies.

## The Provenance Model

Every datum in the database carries three metadata fields:

| Field | Values | Purpose |
|-------|--------|---------|
| `source_method` | DETERMINISTIC, SEED_DATA, CORPUS_EXTRACTION, LLM_ASSISTED, HUMAN_VERIFIED | Where did this come from? |
| `review_status` | DRAFT → REVIEWED → VERIFIED | Forward-only promotion. |
| `confidence` | HIGH, MEDIUM, LOW | How sure are we? |

### Rules:
- 1609 Quarto text: `DETERMINISTIC / VERIFIED / HIGH` (the text is sacred)
- Seed reference data: `SEED_DATA / REVIEWED / HIGH`
- LLM-generated enrichment: `LLM_ASSISTED / DRAFT / MEDIUM` (always)
- Human-reviewed analysis: `HUMAN_VERIFIED / VERIFIED / HIGH` (only after expert review)
- Never auto-promote `DRAFT → VERIFIED`
- Never overwrite `VERIFIED` data without logging the discrepancy

This means the swarm's output enters the database as DRAFT/MEDIUM — explicitly marked as provisional. The deterministic layer treats it as first-class data for site generation, but the provenance trail means a scholar can always ask: "Was this analysis human-verified or machine-generated?"

## The Deckard Boundary

Named after the PKD character who distinguishes humans from replicants, the **Deckard Boundary** is the explicit map of which tasks are deterministic and which require judgment.

### WASTE — Do NOT use LLM for:
- Splitting sonnets into lines (regex)
- Assigning Q1/Q2/Q3/COUPLET labels (arithmetic from line number)
- Extracting rhyme words (string split)
- Counting syllables (CMU Pronouncing Dictionary)
- Building HTML from DB fields (Jinja templating)
- Validating enum constraints (SQL CHECK)

### RISK — Do NOT use deterministic code for:
- Classifying addressee (dramatic context required)
- Ranking analytical salience (aesthetic judgment)
- Identifying irony or puns (requires multiple-meaning awareness)
- Writing close readings (rhetorical understanding)
- Performance direction (interpretive empathy)

### The boundary is SHARP, not fuzzy:
Every task sits clearly on one side. If you're unsure, you're probably trying to use the wrong tool. The heuristic: "Could a competent programmer who doesn't read English write this script?" If yes → deterministic. If no → judgment.

## Token Efficiency

The "read once, extract many" principle: instead of separate passes for devices, modes, themes, characters, analysis, and directing, each agent does ALL extractions in a single reading of each sonnet.

**Naive approach**: 6 passes × 154 sonnets = 924 sonnet-reads
**Batched approach**: 1 pass × 154 sonnets = 154 reads (83% reduction)
**Swarm approach**: 10 agents × ~10 sonnets each = same 154 reads, but in parallel

The swarm doesn't save tokens — it saves wall-clock time. Ten agents working simultaneously finish in the time it takes one agent to do its batch of ~10-16 sonnets.

## Practical Numbers

| Metric | Value |
|--------|-------|
| Total sonnets | 154 |
| Previously enriched | 54 |
| Swarm batch | 100 sonnets across 10 agents |
| Enrichment fields per sonnet | 7 (analysis, directing, annotations, themes, characters, devices, modes) |
| Lines annotated per sonnet | 8-14 |
| Devices identified per sonnet | 8-15 |
| JSON output per sonnet | ~10-15 KB |
| Total enrichment JSON | ~1-1.5 MB |
| DB rows generated | ~3,000-4,000 across 7 tables |

## When NOT to Swarm

Swarming works for independent, schema-constrained extraction. It does NOT work for:

1. **Essays**: Long-form thematic essays that need to reference multiple sonnets coherently. These require a single sustained analytical voice.
2. **Scholarly extraction**: Reading a PDF by Vendler or Booth and extracting claims. The claims build on each other within the PDF — they're not independent.
3. **Intertextual linking**: Identifying echoes between Sonnet 34 and Sonnet 120 requires having read both. A single agent doing the full sequence would catch these; a swarm won't.
4. **Editorial decisions**: Choosing between variant readings, resolving textual cruces, or making judgment calls that need to be consistent across the whole sequence.

## The Pipeline in Practice

```bash
# 1. DETERMINISTIC: Build the empty database
python scripts/init_db.py --force
python scripts/seed_sonnets.py
python scripts/seed_reference.py

# 2. JUDGMENT: Swarm generates enrichment JSON
# (10 parallel Claude agents, each writing to data/enrichment/batch_NN_*.json)

# 3. DETERMINISTIC: Load enrichment into database
python scripts/enrich_sonnets.py

# 4. DETERMINISTIC: Validate everything
python scripts/validate_db.py

# 5. DETERMINISTIC: Build the site
python scripts/build_site.py
```

Steps 1, 3, 4, 5 are fully automated, reproducible, and fast.
Step 2 is the expensive, non-deterministic part — but its output is validated by step 4 before being consumed by step 5.

## Summary

The two-layer architecture gives you:
- **Speed** (swarm parallelism) without sacrificing **integrity** (deterministic validation)
- **Rich interpretation** (LLM judgment) without sacrificing **reproducibility** (schema contracts)
- **Provenance** (every datum tagged) without sacrificing **usability** (site just works)
- **Scalability** (add more agents) without sacrificing **coherence** (thematic batching)

The key discipline is the Deckard Boundary: know which layer each task belongs to, and never cross the line.
