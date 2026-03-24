# Pipeline — Shakespeare Sonnets

19 scripts across 5 stages. All scripts are idempotent (safe to re-run).

See `SONNETSTUDYDECKARDANALYSIS.md` for which tasks are Python vs Claude Code.

---

## Stage 1: Scaffold [PLANNED]

| Script | Creates | Notes |
|--------|---------|-------|
| `init_db.py` | Tables 1-11 (core) | CREATE TABLE IF NOT EXISTS |
| `migrate_v2.py` | Tables 12-15 (rhetoric & analysis) | Adds rhetoric tables |
| `migrate_v3.py` | Tables 16-25 (enrichment + infrastructure) | Adds enrichment tables |

## Stage 1b: Seed (deterministic) [PLANNED]

| Script | Populates | Input | Method |
|--------|-----------|-------|--------|
| `seed_sonnets.py` | sonnets, sonnet_lines, sonnet_sections | `data/sonnet_texts.json` | DETERMINISTIC |
| `seed_characters.py` | characters | `data/sonnets_seed.json` | SEED_DATA |
| `seed_scholars.py` | scholars, bibliography, scholar_works | `data/sonnets_seed.json` | SEED_DATA |
| `seed_devices.py` | rhetorical_devices | `data/sonnets_seed.json` | SEED_DATA |
| `seed_modes.py` | analysis_modes | `data/sonnets_seed.json` | SEED_DATA |
| `seed_sequence_groups.py` | sequence_groups, thematic_threads, sonnet_themes | `data/sonnets_seed.json` | SEED_DATA |

### seed_sonnets.py Detail

This is the most important deterministic script. For each of 154 sonnets:

1. Parse sonnet text into 14 lines
2. Create `sonnets` row with number, first_line, sonnet_text_full
3. Create 14 `sonnet_lines` rows with:
   - `section`: Q1 (1-4), Q2 (5-8), Q3 (9-12), COUPLET (13-14)
   - `rhyme_position`: lines 1,3→A; 2,4→B; 5,7→C; 6,8→D; 9,11→E; 10,12→F; 13→G; 14→G
   - `rhyme_word`: last word of each line
   - `global_line_number`: (sonnet_number - 1) * 14 + line_number
   - `syllable_count`: via CMU Pronouncing Dictionary (fallback: LLM for archaic words)
4. Create 4 `sonnet_sections` rows (Q1, Q2, Q3, COUPLET) with start/end lines

All of this is DETERMINISTIC / HIGH confidence.

## Stage 2: Extract (LLM-assisted) [PLANNED]

| Script | Populates | Pass | Method |
|--------|-----------|------|--------|
| `extract_full_analysis.py` | sonnets (addressee, volta), sonnet_characters, line_addressee_shifts, sonnet_figures, sonnet_analysis_modes, sonnet_sections (rhetorical_function) | Pass 1 | LLM_ASSISTED |
| `extract_scholarly.py` | scholarly_refs | Pass 2 | CORPUS_EXTRACTION |

### extract_full_analysis.py Detail

Processes sonnets in batches of 5-10. For each sonnet, Claude Code outputs structured JSON with:
- primary_addressee + confidence
- addressee_shifts (if any)
- rhetorical_figures (all, with salience)
- analysis_modes (priority-ranked)
- section rhetorical_functions (4)
- volta_type

**Validation before DB insert:**
- Line numbers must be 1-14
- device_id must exist in rhetorical_devices
- mode_id must exist in analysis_modes
- Enum values must match CHECK constraints
- quoted_text must appear in actual line text

### extract_scholarly.py Detail

Reads one corpus PDF at a time. Extracts:
- Which sonnets the PDF discusses
- Interpretation type (FORMAL/BIOGRAPHICAL/THEMATIC/etc.)
- Summary of the claim
- Page reference

**Priority order:** Vendler → Booth → Duncan-Jones (Arden) → Hotson → Chambers → Pequigney

## Stage 3: Enrich (LLM-assisted + deterministic) [PLANNED]

| Script | Populates | Pass | Method |
|--------|-----------|------|--------|
| `seed_annotations.py` | annotations | Pass 3 | LLM_ASSISTED |
| `seed_glossary.py` | glossary_terms, term_sonnet_refs | Pass 3 | LLM_ASSISTED |
| `link_intertexts.py` | intertextual_links | Pass 4 | LLM_ASSISTED + DETERMINISTIC |
| `build_analysis.py` | Assembled analysis HTML per sonnet | — | DETERMINISTIC (template assembly) |

### build_analysis.py Detail

NO LLM calls. Reads from DB and assembles analysis HTML per sonnet:

1. Query `sonnet_analysis_modes WHERE sonnet_id = N ORDER BY priority`
2. For priority-1 mode: focused section pulling from `sonnet_figures`
3. For priority-2+ modes: brief mention
4. Always include: addressee, volta analysis, sequence context
5. Optionally: scholarly debate, glossary notes, intertextual links

## Stage 4: Build [PLANNED]

| Script | Output | Method |
|--------|--------|--------|
| `build_site.py` | `site/*.html` + `site/style.css` + `site/script.js` | DETERMINISTIC |

Generates: homepage, sonnet index, 154 × 3 content pages (analyses, directing, contexts), essay pages, candidate pages, scholar pages, glossary, timeline, about.

## Stage 5: Validate [PLANNED]

| Script | Checks | Method |
|--------|--------|--------|
| `validate_sonnets.py` | 14 lines per sonnet, no orphaned refs, enum compliance, all FKs valid | DETERMINISTIC |

---

## Full Rebuild Command

```bash
rm -f db/sonnets.db
python scripts/init_db.py
python scripts/migrate_v2.py
python scripts/migrate_v3.py
python scripts/seed_sonnets.py
python scripts/seed_characters.py
python scripts/seed_scholars.py
python scripts/seed_devices.py
python scripts/seed_modes.py
python scripts/seed_sequence_groups.py
# --- LLM passes (interactive sessions) ---
python scripts/extract_full_analysis.py
python scripts/extract_scholarly.py
python scripts/seed_annotations.py
python scripts/seed_glossary.py
python scripts/link_intertexts.py
# --- Deterministic assembly ---
python scripts/build_analysis.py
python scripts/build_site.py
python scripts/validate_sonnets.py
```

## Dependencies

```
Stage 1 → Stage 1b → Stage 2 → Stage 3 → Stage 4 → Stage 5
                         ↑
                   (LLM sessions)
```

Stage 1b scripts can run in any order (no inter-dependencies).
Stage 2 scripts: extract_full_analysis.py must complete before extract_scholarly.py (scholarly extraction benefits from addressee context).
Stage 3 scripts: seed_annotations.py and seed_glossary.py can run in parallel. link_intertexts.py depends on both. build_analysis.py runs last in Stage 3.
