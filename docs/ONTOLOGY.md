# Database Ontology — Shakespeare Sonnets

Database: `db/sonnets.db` (SQLite 3)

25 tables across 3 migration stages. All tables include provenance fields where applicable: `source_method`, `review_status`, `confidence`.

---

## Stage 1: Core Tables (init_db.py) — 11 tables

### sonnets [PLANNED]

The primary organizing unit. 154 rows.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| number | INTEGER UNIQUE NOT NULL | 1-154 |
| title | TEXT | "Sonnet 18" or alternate title |
| first_line | TEXT NOT NULL | "Shall I compare thee to a summer's day?" |
| primary_addressee | TEXT | CHECK: FYM, DL, BOTH, SELF, RIVAL_POET, TIME, MUSE, BEAUTY, UNKNOWN |
| addressee_confidence | TEXT | CHECK: HIGH, MEDIUM, LOW, DISPUTED |
| addressee_evidence | TEXT | Brief justification |
| sequence_group | TEXT | CHECK: PROCREATION, FYM_BEAUTY, FYM_ABSENCE, FYM_RIVAL, FYM_BETRAYAL, DL_DESIRE, DL_BETRAYAL, TRIANGLE, CODA, ANACREONTIC, DISPUTED |
| volta_line | INTEGER | Line where the turn occurs (typically 9 or 13) |
| volta_type | TEXT | CHECK: COUNTER_ARGUMENT, RESOLUTION, REVERSAL, AMPLIFICATION, QUALIFICATION, NONE |
| thematic_keywords | TEXT | JSON array: ["time","beauty","mortality"] |
| sonnet_text_full | TEXT NOT NULL | Full 14-line text, newline-separated |
| source_edition | TEXT DEFAULT '1609_QUARTO' | |
| source_method | TEXT DEFAULT 'SEED_DATA' | |
| review_status | TEXT DEFAULT 'DRAFT' | |
| confidence | TEXT DEFAULT 'MEDIUM' | |

### sonnet_lines [PLANNED]

Every line as a first-class entity. 2,156 rows (154 × 14).

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| sonnet_id | INTEGER FK → sonnets | |
| line_number | INTEGER NOT NULL | 1-14 within sonnet |
| global_line_number | INTEGER UNIQUE | 1-2156 across all sonnets |
| text | TEXT NOT NULL | The line text |
| section | TEXT NOT NULL | CHECK: Q1, Q2, Q3, COUPLET (deterministic from line_number) |
| rhyme_position | TEXT NOT NULL | A, B, C, D, E, F, G |
| rhyme_word | TEXT | Last word |
| syllable_count | INTEGER | Expected 10; deviations notable |
| metrical_pattern | TEXT | e.g. "u/u/u/u/u/" for regular iambic pentameter |
| has_metrical_variation | INTEGER DEFAULT 0 | Flag for notable departures |
| source_method | TEXT DEFAULT 'DETERMINISTIC' | |
| UNIQUE(sonnet_id, line_number) | | |

### sonnet_sections [PLANNED]

Structural units with commentary. 616 rows (154 × 4).

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| sonnet_id | INTEGER FK → sonnets | |
| section_type | TEXT NOT NULL | CHECK: Q1, Q2, Q3, COUPLET |
| start_line | INTEGER NOT NULL | 1, 5, 9, or 13 |
| end_line | INTEGER NOT NULL | 4, 8, 12, or 14 |
| rhetorical_function | TEXT | What this section DOES argumentatively |
| imagery_cluster | TEXT | Dominant image/conceit |
| commentary | TEXT | Section-level analytical note |
| source_method | TEXT DEFAULT 'SEED_DATA' | |
| review_status | TEXT DEFAULT 'DRAFT' | |
| confidence | TEXT DEFAULT 'MEDIUM' | |
| UNIQUE(sonnet_id, section_type) | | |

### characters [PLANNED]

Dramatic personae. ~6 rows.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| character_id | TEXT UNIQUE NOT NULL | FYM, DL, SPEAKER, RIVAL_POET, TIME, MUSE |
| name | TEXT NOT NULL | "Fair Young Man", "Dark Lady" |
| description | TEXT | |
| biographical_candidates | TEXT | JSON array: ["Henry Wriothesley","William Herbert"] |
| scholarly_debate_summary | TEXT | Summary of identification controversies |
| source_method | TEXT DEFAULT 'SEED_DATA' | |
| review_status | TEXT DEFAULT 'DRAFT' | |

### sonnet_characters [PLANNED]

Which characters appear in each sonnet. ~300 rows.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| sonnet_id | INTEGER FK → sonnets | |
| character_id | INTEGER FK → characters | |
| role | TEXT | CHECK: ADDRESSEE, SUBJECT, MENTIONED, IMPLIED |
| prominence | TEXT | CHECK: PRIMARY, SECONDARY, PASSING |
| evidence | TEXT | Brief textual/scholarly justification |
| source_method | TEXT DEFAULT 'SEED_DATA' | |
| confidence | TEXT DEFAULT 'MEDIUM' | |
| UNIQUE(sonnet_id, character_id, role) | | |

### line_addressee_shifts [PLANNED]

Mid-sonnet addressee changes. ~50 rows.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| sonnet_id | INTEGER FK → sonnets | |
| start_line_num | INTEGER NOT NULL | Line where addressee begins |
| end_line_num | INTEGER NOT NULL | Line where addressee ends |
| character_id | INTEGER FK → characters | |
| shift_marker | TEXT | Word/phrase signaling the shift |
| notes | TEXT | |
| source_method | TEXT DEFAULT 'LLM_ASSISTED' | |
| confidence | TEXT DEFAULT 'MEDIUM' | |

### scholars [PLANNED]

Scholar profiles. ~15 rows.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| name | TEXT UNIQUE NOT NULL | |
| birth_year | INTEGER | |
| death_year | INTEGER | |
| specialization | TEXT | "Form/rhetoric", "Identity/biography", "Thematic" |
| sonnets_focus | TEXT | What they study about the Sonnets |
| overview | TEXT | Bio paragraph |
| review_status | TEXT DEFAULT 'DRAFT' | |

### bibliography [PLANNED]

Source works. ~60 rows.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| source_id | TEXT UNIQUE | e.g. "vendler_1997", "booth_1977" |
| author | TEXT NOT NULL | |
| title | TEXT NOT NULL | |
| year | INTEGER | |
| journal | TEXT | |
| publisher | TEXT | |
| pub_type | TEXT | CHECK: MONOGRAPH, ARTICLE, REVIEW, EDITION, ANTHOLOGY |
| sonnets_relevance | TEXT | CHECK: PRIMARY, DIRECT, CONTEXTUAL |
| scholar_type | TEXT | CHECK: FORM_RHETORIC, IDENTITY_BIOGRAPHY, THEMATIC, EDITION, GENERAL |
| in_collection | INTEGER DEFAULT 1 | 1 if PDF in corpus/ |

### scholar_works [PLANNED]

Join: scholar ↔ bibliography. ~80 rows.

| Column | Type | Notes |
|--------|------|-------|
| scholar_id | INTEGER FK → scholars | |
| bib_id | INTEGER FK → bibliography | |
| PRIMARY KEY (scholar_id, bib_id) | | |

### scholarly_refs [PLANNED]

Scholar interpretations linked to specific sonnets. ~500+ rows.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| sonnet_id | INTEGER FK → sonnets | NULL for general claims |
| bib_id | INTEGER NOT NULL FK → bibliography | |
| interpretation_type | TEXT | CHECK: FORMAL, BIOGRAPHICAL, THEMATIC, TEXTUAL, HISTORICAL, RHETORICAL |
| summary | TEXT NOT NULL | |
| section_page | TEXT | Page reference in source |
| applies_to_lines | TEXT | JSON: [3,4,5] or null for whole-sonnet |
| confidence | TEXT DEFAULT 'HIGH' | |
| source_method | TEXT DEFAULT 'SEED_DATA' | |
| review_status | TEXT DEFAULT 'DRAFT' | |

### schema_version [PLANNED]

Migration tracking.

| Column | Type | Notes |
|--------|------|-------|
| version | INTEGER PK | |
| applied_at | TEXT | datetime('now') |
| description | TEXT | |

---

## Stage 2: Rhetoric & Analysis Tables (migrate_v2.py) — 4 tables

### rhetorical_devices [PLANNED]

Device catalog. ~30 rows.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| device_id | TEXT UNIQUE NOT NULL | METAPHOR, SIMILE, PUN, IRONY, ANTITHESIS, etc. |
| name | TEXT NOT NULL | |
| category | TEXT | CHECK: TROPE, SCHEME, SOUND, STRUCTURE |
| definition_short | TEXT | |
| definition_long | TEXT | |
| example_sonnet | INTEGER | Canonical example sonnet number |
| example_lines | TEXT | JSON: line range |

**Category definitions:**
- **TROPE**: metaphor, simile, metonymy, synecdoche, irony, pun, hyperbole, litotes, personification
- **SCHEME**: antithesis, chiasmus, anaphora, epistrophe, parallelism, zeugma
- **SOUND**: alliteration, assonance, consonance, onomatopoeia
- **STRUCTURE**: enjambment, caesura, volta, end-stop

### sonnet_figures [PLANNED]

Instances of rhetorical figures at line/span level. ~1500+ rows.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| sonnet_id | INTEGER NOT NULL FK → sonnets | |
| device_id | INTEGER NOT NULL FK → rhetorical_devices | |
| start_line_num | INTEGER NOT NULL | 1-14 |
| end_line_num | INTEGER NOT NULL | Same as start for single-line |
| quoted_text | TEXT | The specific words exhibiting the device |
| explanation | TEXT | What the device does HERE, in THIS context |
| analytical_salience | TEXT | CHECK: PRIMARY, SUPPORTING, MINOR |
| scholarly_source_id | INTEGER FK → bibliography | Who identified this |
| source_method | TEXT DEFAULT 'LLM_ASSISTED' | |
| review_status | TEXT DEFAULT 'DRAFT' | |
| confidence | TEXT DEFAULT 'MEDIUM' | |

**Salience definitions:**
- **PRIMARY**: This is a defining feature of the sonnet. Lead with it in analysis.
- **SUPPORTING**: Contributes to the sonnet's effect. Mention in analysis.
- **MINOR**: Present but not what makes this sonnet notable. Omit unless space permits.

### analysis_modes [PLANNED]

Analytical lens catalog. ~15 rows.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| mode_id | TEXT UNIQUE NOT NULL | See list below |
| name | TEXT NOT NULL | |
| description | TEXT | What this lens reveals |
| typical_indicators | TEXT | JSON: clues that suggest this mode is productive |

**Mode IDs:** PUN_WORDPLAY, EXTENDED_METAPHOR, IRONY, DRAMATIC_SITUATION, FORM_METER, SOUND_PATTERN, ADDRESSEE_AMBIGUITY, TEMPORAL_LOGIC, LEGAL_LANGUAGE, ECONOMIC_LANGUAGE, RELIGIOUS_LANGUAGE, PETRARCHAN_REVERSAL, PROCREATION_ARGUMENT, RIVAL_POET_DRAMA, SELF_REFERENCE

### sonnet_analysis_modes [PLANNED]

Priority-ranked modes per sonnet — the LLM's routing guide. ~300 rows.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| sonnet_id | INTEGER NOT NULL FK → sonnets | |
| mode_id | INTEGER NOT NULL FK → analysis_modes | |
| priority | INTEGER NOT NULL DEFAULT 1 | 1 = most important lens |
| rationale | TEXT | WHY this mode is productive here |
| key_lines | TEXT | JSON: [3,4] — lines where most visible |
| source_method | TEXT DEFAULT 'LLM_ASSISTED' | |
| review_status | TEXT DEFAULT 'DRAFT' | |
| confidence | TEXT DEFAULT 'MEDIUM' | |
| UNIQUE(sonnet_id, mode_id) | | |

---

## Stage 3: Enrichment Tables (migrate_v3.py) — 10 tables

### annotations [PLANNED]

Free-form annotations at any granularity. ~2000+ rows.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| sonnet_id | INTEGER NOT NULL FK → sonnets | |
| target_type | TEXT NOT NULL | CHECK: SONNET, SECTION, LINE, SPAN |
| target_section | TEXT | Q1/Q2/Q3/COUPLET (if SECTION) |
| start_line_num | INTEGER | (if LINE or SPAN) |
| end_line_num | INTEGER | (if SPAN) |
| annotation_type | TEXT | CHECK: GLOSS, PARAPHRASE, COMMENTARY, ALLUSION, VARIANT_READING, EMENDATION |
| content | TEXT NOT NULL | |
| scholarly_source_id | INTEGER FK → bibliography | |
| source_method | TEXT DEFAULT 'LLM_ASSISTED' | |
| review_status | TEXT DEFAULT 'DRAFT' | |
| confidence | TEXT DEFAULT 'MEDIUM' | |

### glossary_terms [PLANNED]

Early Modern English vocabulary. ~200 rows.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| slug | TEXT UNIQUE NOT NULL | |
| term | TEXT NOT NULL | "usury", "Will", "engross" |
| category | TEXT | CHECK: ARCHAIC, LEGAL, ECONOMIC, SEXUAL, RELIGIOUS, LITERARY |
| definition_short | TEXT | |
| definition_long | TEXT | |
| example_sonnet | INTEGER | |
| example_line | INTEGER | |
| review_status | TEXT DEFAULT 'DRAFT' | |

### term_sonnet_refs [PLANNED]

Where glossary terms appear. ~600 rows.

| Column | Type | Notes |
|--------|------|-------|
| term_id | INTEGER FK → glossary_terms | |
| sonnet_id | INTEGER FK → sonnets | |
| line_number | INTEGER | |
| context | TEXT | How the term is used HERE |
| PRIMARY KEY (term_id, sonnet_id, line_number) | | |

### intertextual_links [PLANNED]

Connections between sonnets and external works. ~300 rows.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| source_sonnet_id | INTEGER NOT NULL FK → sonnets | |
| target_type | TEXT NOT NULL | CHECK: SONNET, EXTERNAL_WORK |
| target_sonnet_id | INTEGER FK → sonnets | |
| target_work_title | TEXT | e.g. "Ovid, Metamorphoses XV" |
| link_type | TEXT | CHECK: ECHO, RESPONSE, PAIR, SEQUENCE, ALLUSION, CONTRAST |
| description | TEXT | |
| source_method | TEXT DEFAULT 'LLM_ASSISTED' | |
| confidence | TEXT DEFAULT 'MEDIUM' | |

### sequence_groups [PLANNED]

Named subsequences. ~10 rows.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| group_id | TEXT UNIQUE NOT NULL | PROCREATION_1_17, FYM_BEAUTY_18_77, etc. |
| name | TEXT NOT NULL | "Procreation Sonnets" |
| start_sonnet | INTEGER NOT NULL | |
| end_sonnet | INTEGER NOT NULL | |
| description | TEXT | |
| dramatic_situation | TEXT | Emotional/narrative arc |
| scholarly_consensus | TEXT | CHECK: STRONG, MODERATE, DISPUTED |
| source_method | TEXT DEFAULT 'SEED_DATA' | |
| review_status | TEXT DEFAULT 'DRAFT' | |

### thematic_threads [PLANNED]

Cross-cutting themes. ~15 rows.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| thread_id | TEXT UNIQUE NOT NULL | TIME_MORTALITY, BEAUTY_DECAY, POETIC_IMMORTALITY, etc. |
| name | TEXT NOT NULL | |
| description | TEXT | |

### sonnet_themes [PLANNED]

Join: sonnets ↔ themes. ~400 rows.

| Column | Type | Notes |
|--------|------|-------|
| sonnet_id | INTEGER FK → sonnets | |
| thread_id | INTEGER FK → thematic_threads | |
| prominence | TEXT | CHECK: PRIMARY, SECONDARY, PASSING |
| PRIMARY KEY (sonnet_id, thread_id) | | |

### timeline_events [PLANNED]

Publication and reception history. ~30 rows.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| year | INTEGER NOT NULL | |
| year_end | INTEGER | |
| event_type | TEXT | CHECK: PUBLICATION, EDITION, SCHOLARSHIP, PERFORMANCE, ADAPTATION, DIGITAL |
| title | TEXT NOT NULL | |
| description | TEXT | |
| description_long | TEXT | |
| scholar_id | INTEGER FK → scholars | |
| bib_id | INTEGER FK → bibliography | |
| confidence | TEXT DEFAULT 'HIGH' | |

### editions [PLANNED]

Key editions of the Sonnets. ~10 rows.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| edition_id | TEXT UNIQUE NOT NULL | quarto_1609, benson_1640, arden_1997 |
| editor | TEXT | |
| title | TEXT NOT NULL | |
| year | INTEGER NOT NULL | |
| publisher | TEXT | |
| significance | TEXT | Why this edition matters |
| sonnet_ordering | TEXT | ORIGINAL_1609, BENSON_1640, MODERN |
| in_collection | INTEGER DEFAULT 0 | |

### llm_analysis_queue [PLANNED]

Pipeline control for incremental LLM work. ~770 rows (154 × 5 analysis types).

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| sonnet_id | INTEGER NOT NULL FK → sonnets | |
| analysis_type | TEXT NOT NULL | FIGURES, ADDRESSEE, MODES, SECTIONS, ANNOTATIONS |
| status | TEXT | CHECK: PENDING, IN_PROGRESS, COMPLETE, SKIPPED |
| last_run_at | TEXT | |
| notes | TEXT | |
| UNIQUE(sonnet_id, analysis_type) | | |

---

## Entity Relationships

```
sonnets ──< sonnet_lines
sonnets ──< sonnet_sections
sonnets ──< sonnet_characters >── characters
sonnets ──< line_addressee_shifts >── characters
sonnets ──< sonnet_figures >── rhetorical_devices
sonnets ──< sonnet_analysis_modes >── analysis_modes
sonnets ──< annotations
sonnets ──< scholarly_refs >── bibliography
sonnets ──< sonnet_themes >── thematic_threads
sonnets ──< intertextual_links >── sonnets (self-referential)
sonnets ──< term_sonnet_refs >── glossary_terms
sonnets ──< llm_analysis_queue
scholars ──< scholar_works >── bibliography
sequence_groups ──< sonnets (via sequence_group column)
```

---

## How the Schema Serves LLM Analysis

| Table | LLM Use |
|-------|---------|
| sonnet_lines | **Ground truth for quoting.** Query exact text by line number. |
| sonnet_sections | Read rhetorical_function to understand argumentative structure. |
| sonnet_analysis_modes | **Query FIRST** to decide what kind of analysis to generate. Priority 1 shapes the whole output. |
| sonnet_figures | Query "what figures in lines 1-4?" — get structured results with salience. |
| characters | Read biographical_candidates for nuanced FYM/DL discussion. |
| scholarly_refs | Cite scholars accurately with page numbers. |
| glossary_terms | Explain archaic vocabulary in context. |
| sequence_groups | Situate individual sonnets within narrative arcs. |
