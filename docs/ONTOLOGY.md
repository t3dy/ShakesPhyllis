# Database Ontology — Shakespeare Sonnets

Database: `db/sonnets.db` (SQLite 3)

22 tables in a single `init_db.py` script, organized in 5 layers. All enrichment tables include provenance fields: `source_method`, `review_status`, `confidence`.

---

## Layer 1: Core Text (DETERMINISTIC)

Source: 1609 Quarto via Project Gutenberg. All rows are VERIFIED / HIGH.

### sonnets — BUILT (154 rows)

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | 1-154 |
| number | INTEGER UNIQUE NOT NULL | 1-154 |
| first_line | TEXT NOT NULL | |
| line_count | INTEGER NOT NULL DEFAULT 14 | 15 for #99, 12 for #126 |
| addressee | TEXT | FYM, DL, MIXED, NONE |
| source | TEXT DEFAULT '1609_QUARTO_GUTENBERG' | |
| source_method | TEXT DEFAULT 'DETERMINISTIC' | |
| review_status | TEXT DEFAULT 'VERIFIED' | |
| confidence | TEXT DEFAULT 'HIGH' | |

### stanzas — BUILT (615 rows)

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK AUTOINCREMENT | |
| sonnet_id | INTEGER FK → sonnets | |
| stanza_number | INTEGER NOT NULL | 1-4 (Q1, Q2, Q3, Couplet) |
| stanza_type | TEXT NOT NULL | QUATRAIN_1, QUATRAIN_2, QUATRAIN_3, COUPLET |
| start_line | INTEGER NOT NULL | |
| end_line | INTEGER NOT NULL | |
| UNIQUE(sonnet_id, stanza_number) | | |

Note: Sonnet 126 has NO couplet stanza (3 stanzas only). Sonnet 99 has Q1 spanning 5 lines.

### lines — BUILT (2,155 rows)

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK AUTOINCREMENT | |
| sonnet_id | INTEGER FK → sonnets | |
| line_number | INTEGER NOT NULL | 1-based within sonnet |
| line_text | TEXT NOT NULL | |
| stanza_id | INTEGER FK → stanzas | |
| meter_pattern | TEXT | (enrichment) |
| has_enjambment | INTEGER | 0/1 (enrichment) |
| has_caesura | INTEGER | 0/1 (enrichment) |
| is_volta | INTEGER DEFAULT 0 | 0/1 (enrichment) |
| UNIQUE(sonnet_id, line_number) | | |

---

## Layer 2: Characters & Scholarly Apparatus (SEED_DATA)

### characters — BUILT (4 rows: FYM, DL, RP, SPEAKER)

| Column | Type | Notes |
|--------|------|-------|
| id | TEXT PK | FYM, DL, RP, SPEAKER |
| name | TEXT NOT NULL | |
| aka | TEXT | JSON array of alternate names |
| description | TEXT | |

### character_candidates — BUILT (10 rows)

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK AUTOINCREMENT | |
| character_id | TEXT FK → characters | |
| candidate_name | TEXT NOT NULL | |
| strength | TEXT NOT NULL | STRONG, MODERATE, SPECULATIVE |
| evidence | TEXT | |
| UNIQUE(character_id, candidate_name) | | |

### scholars — BUILT (13 rows)

| Column | Type | Notes |
|--------|------|-------|
| id | TEXT PK | VENDLER, BOOTH, etc. |
| name | TEXT NOT NULL | |
| primary_work | TEXT | |
| approach | TEXT | |

### bibliography — BUILT (15 rows)

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK AUTOINCREMENT | |
| cite_key | TEXT UNIQUE NOT NULL | vendler1997, booth1977, etc. |
| citation | TEXT NOT NULL | |

### sonnet_groups — BUILT (8 rows)

| Column | Type | Notes |
|--------|------|-------|
| id | TEXT PK | PROCREATION, IMMORTALITY, etc. |
| name | TEXT NOT NULL | |
| description | TEXT | |
| addressee | TEXT | FYM, DL, MIXED, NONE |
| themes | TEXT | JSON array |

### sonnet_group_members — BUILT (101 rows)

| Column | Type | Notes |
|--------|------|-------|
| group_id | TEXT FK → sonnet_groups | |
| sonnet_id | INTEGER FK → sonnets | |
| UNIQUE(group_id, sonnet_id) | | |

---

## Layer 3: Rhetoric & Poetics

### rhetorical_devices — BUILT (20 rows)

| Column | Type | Notes |
|--------|------|-------|
| id | TEXT PK | METAPHOR, SIMILE, PUN, IRONY, CONCEIT, PERSONIFICATION, APOSTROPHE, ANTITHESIS, PARADOX, HYPERBOLE, SYNECDOCHE, METONYMY, ALLITERATION, ASSONANCE, ENJAMBMENT, CAESURA, VOLTA, BLAZON, CHIASMUS, ANAPHORA |
| name | TEXT NOT NULL | |
| description | TEXT | |

### analytical_modes — BUILT (8 rows)

| Column | Type | Notes |
|--------|------|-------|
| id | TEXT PK | RHETORICAL, DRAMATIC, PROSODIC, IMAGISTIC, STRUCTURAL, INTERTEXTUAL, HISTORICAL, THEMATIC |
| name | TEXT NOT NULL | |
| description | TEXT | |

### line_devices — ENRICHING (89 rows across 17 sonnets)

Join: line × device. Each row is a specific instance of a rhetorical device on a specific line.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK AUTOINCREMENT | |
| line_id | INTEGER FK → lines | |
| device_id | TEXT FK → rhetorical_devices | |
| quotation | TEXT | Specific text exhibiting the device |
| explanation | TEXT | Why this is this device HERE |
| source_method | TEXT DEFAULT 'LLM_ASSISTED' | |
| review_status | TEXT DEFAULT 'DRAFT' | |
| confidence | TEXT DEFAULT 'MEDIUM' | |

### sonnet_modes — ENRICHING (54 rows across 17 sonnets)

Join: sonnet × mode. Priority-ranked analytical lenses per sonnet.

| Column | Type | Notes |
|--------|------|-------|
| sonnet_id | INTEGER FK → sonnets | |
| mode_id | TEXT FK → analytical_modes | |
| priority | INTEGER DEFAULT 0 | Higher = more important |
| rationale | TEXT | Why this mode matters here |

---

## Layer 4: Enrichment (LLM_ASSISTED)

All rows default to: source_method='LLM_ASSISTED', review_status='DRAFT', confidence='MEDIUM'.

### sonnet_analyses — ENRICHING (17 rows)

Per-sonnet close reading and dramatic analysis.

| Column | Type | Notes |
|--------|------|-------|
| sonnet_id | INTEGER FK → sonnets (UNIQUE) | |
| volta_line | INTEGER | Which line has the turn |
| volta_type | TEXT | DRAMATIC, LOGICAL, TONAL, IRONIC |
| couplet_function | TEXT | RESOLUTION, REVERSAL, EXTENSION, EPIGRAM, IRONIC |
| argument_summary | TEXT | One-sentence summary of the sonnet's rhetorical 'move' |
| speaker_stance | TEXT | e.g. 'pleading', 'bitter', 'self-mocking' |
| emotional_arc | TEXT | e.g. 'adoration → doubt → resigned acceptance' |
| dramatic_situation | TEXT | What's happening between the characters |
| subtext | TEXT | What the Speaker means but doesn't say |
| analysis_text | TEXT | Complete close-reading prose |

### line_annotations — ENRICHING (88 rows)

Per-line directing and scholarly notes.

| Column | Type | Notes |
|--------|------|-------|
| line_id | INTEGER FK → lines (UNIQUE) | |
| emphasis_words | TEXT | JSON array of words to stress |
| emotional_note | TEXT | Acting direction for this line |
| delivery_note | TEXT | How to speak it (pace, volume, tone) |
| gloss | TEXT | Paraphrase / modernization |
| commentary | TEXT | Scholarly annotation |

### sonnet_themes — ENRICHING (86 rows)

| Column | Type | Notes |
|--------|------|-------|
| sonnet_id | INTEGER FK → sonnets | |
| theme | TEXT NOT NULL | e.g. 'time', 'beauty', 'mortality' |
| prominence | TEXT | PRIMARY, SECONDARY |

### character_appearances — ENRICHING (38 rows)

| Column | Type | Notes |
|--------|------|-------|
| sonnet_id | INTEGER FK → sonnets | |
| character_id | TEXT FK → characters | |
| role | TEXT | ADDRESSED, MENTIONED, IMPLIED, ABSENT_PRESENCE |
| evidence | TEXT | Textual basis |

### directing_notes — ENRICHING (17 rows)

Per-sonnet performance interpretation.

| Column | Type | Notes |
|--------|------|-------|
| sonnet_id | INTEGER FK → sonnets (UNIQUE) | |
| scene_setting | TEXT | Physical/emotional context for performance |
| character_note | TEXT | Who is the Speaker in this moment |
| fym_note | TEXT | How FYM relates to this sonnet |
| dl_note | TEXT | How DL relates to this sonnet |
| overall_arc | TEXT | Performance arc across the 14 lines |
| key_moments | TEXT | JSON array of {line, note} |

---

## Layer 5: Essays & Context

### essays — EMPTY

| Column | Type | Notes |
|--------|------|-------|
| slug | TEXT UNIQUE NOT NULL | URL-friendly identifier |
| title | TEXT NOT NULL | |
| subtitle | TEXT | |
| abstract | TEXT | |
| body_html | TEXT | Generated HTML |
| body_markdown | TEXT | Source markdown |
| essay_type | TEXT | THEMATIC, CHARACTER, STRUCTURAL, HISTORICAL |

### essay_sonnet_links — EMPTY

| Column | Type | Notes |
|--------|------|-------|
| essay_id | INTEGER FK → essays | |
| sonnet_id | INTEGER FK → sonnets | |
| relevance | TEXT | DISCUSSED, CITED, CENTRAL |

### contexts — EMPTY

| Column | Type | Notes |
|--------|------|-------|
| sonnet_id | INTEGER FK → sonnets | NULL for general |
| context_type | TEXT | BIOGRAPHICAL, PUBLICATION, HISTORICAL, CANDIDATE |
| title | TEXT | |
| body_text | TEXT | |

---

## Entity Relationships

```
sonnets ──< stanzas ──< lines
sonnets ──< sonnet_group_members >── sonnet_groups
sonnets ──< sonnet_analyses
sonnets ──< directing_notes
sonnets ──< sonnet_themes
sonnets ──< character_appearances >── characters
sonnets ──< sonnet_modes >── analytical_modes
lines   ──< line_annotations
lines   ──< line_devices >── rhetorical_devices
characters ──< character_candidates
essays  ──< essay_sonnet_links >── sonnets
sonnets ──< contexts
```

---

## How the Schema Serves the Audiobook/Directing Project

| Table | Use |
|-------|-----|
| lines + stanzas | Ground truth for quoting. Query exact text by line/stanza. |
| sonnet_analyses | Speaker stance, emotional arc, dramatic situation — shapes the performance reading. |
| line_annotations | emphasis_words, delivery_note, emotional_note — line-by-line directing. |
| directing_notes | scene_setting, overall_arc, key_moments — the director's frame for each sonnet. |
| line_devices | Which rhetorical devices drive delivery choices (stress the pun, land the paradox). |
| sonnet_modes | Priority-ranked analytical lenses — what to LEAD with in each sonnet's analysis. |
| character_appearances | Who is present, addressed, or implied — essential for dramatic reading. |
| character_candidates | Historical FYM/DL identification — grounds the performance in scholarship. |

---

## Enrichment Status

| Batch | Sonnets | Status |
|-------|---------|--------|
| batch_01_procreation | 1, 3, 12, 17, 18 | COMPLETE |
| batch_02_triangle | 40, 42, 93, 94, 129, 130, 138, 144 | COMPLETE |
| batch_03_immortality | 55, 73, 116, 126 | COMPLETE |
| Remaining 137 sonnets | 2, 4-11, 13-16, 19-39, 41, 43-54, 56-72, 74-92, 95-115, 117-125, 127-128, 131-137, 139-143, 145-154 | PENDING |
