# How It's Being Saved — Shakespeare Sonnets Project

Last updated: 2026-03-24

## Where Everything Lives

All project data is on your local machine at:

```
C:\Dev\Shakespeare\
```

Nothing is in the cloud, nothing is on a server. It's all local files. Here's exactly what's where:

---

## 1. The Database (the source of truth)

```
C:\Dev\Shakespeare\db\sonnets.db     (1,184 KB — SQLite 3)
```

This single file contains ALL structured data — 21 tables, ~4,000 rows. Everything the site will be built from. Current contents:

| Table | Rows | What's in it |
|-------|------|-------------|
| sonnets | 154 | Every sonnet: number, first line, addressee, line count |
| stanzas | 615 | Q1/Q2/Q3/Couplet boundaries for every sonnet |
| lines | 2,155 | Every line of every sonnet, linked to its stanza |
| characters | 4 | FYM, DL, Rival Poet, Speaker |
| character_candidates | 10 | Southampton, Pembroke, Lanier, Fitton, etc. |
| scholars | 13 | Vendler, Booth, Duncan-Jones, etc. |
| bibliography | 15 | Key scholarly works |
| rhetorical_devices | 21 | Metaphor, pun, irony, volta, etc. |
| analytical_modes | 8 | Rhetorical, dramatic, prosodic, etc. |
| sonnet_groups | 47 | 32 narrative sequences + 14 diptychs/triptychs + 1 transitional |
| sonnet_group_members | 188 | Which sonnets belong to which groups |
| **sonnet_analyses** | **54** | Close readings: volta, argument, emotional arc, subtext |
| **line_annotations** | **201** | Per-line: emphasis words, delivery notes, glosses |
| **line_devices** | **218** | Rhetorical device instances with quotation + explanation |
| **directing_notes** | **54** | Scene setting, character notes, key performance moments |
| **sonnet_themes** | **268** | Theme tags (PRIMARY/SECONDARY) per sonnet |
| **character_appearances** | **118** | Who appears in each sonnet (ADDRESSED/MENTIONED/IMPLIED) |
| **sonnet_modes** | **165** | Priority-ranked analytical lenses per sonnet |
| essays | 1 | "Unresolved Questions" essay |
| essay_sonnet_links | 20 | Which sonnets the essay discusses |

**Bold = LLM-enriched data (the work we're doing this session).**

---

## 2. Source Data Files (JSON)

```
C:\Dev\Shakespeare\data\
├── gutenberg_sonnets.txt          ← Raw download from Project Gutenberg
├── sonnet_texts.json              ← 154 sonnets parsed into structured JSON (139 KB)
├── sonnets_seed.json              ← Characters, scholars, devices, modes, groups (24 KB)
└── enrichment\                    ← LLM-generated enrichment batches
    ├── batch_01_procreation.json       (48 KB — sonnets 1, 3, 12, 17, 18)
    ├── batch_02_triangle.json          (66 KB — sonnets 40, 42, 93, 94, 129, 130, 138, 144)
    ├── batch_03_immortality.json       (35 KB — sonnets 55, 73, 116, 126)
    ├── batch_04_fym_core.json          (60 KB — sonnets 19, 20, 29, 30, 33, 57, 87)
    ├── batch_05_dark_lady.json         (39 KB — sonnets 127, 128, 141, 147, 152)
    ├── batch_06_rival_poet.json        (24 KB — sonnets 78, 80, 86)
    ├── batch_07_procreation_remaining.json (67 KB — sonnets 2, 4, 5, 6, 7, 8, 9, 10, 11)
    ├── batch_08_procreation_tail.json  (42 KB — sonnets 13, 15, 16, 21, 23, 24)
    └── batch_09_mixed.json             (47 KB — sonnets 14, 22, 25, 27, 28, 31, 32)
```

**Total enrichment JSON: 426 KB across 9 batch files.**

These JSON files are the backup/audit trail. The database is the source of truth, but the JSON files contain the raw enrichment data that was loaded into it. If the database is corrupted, the enrichment can be replayed from these files.

---

## 3. Scripts (the pipeline)

```
C:\Dev\Shakespeare\scripts\
├── parse_gutenberg.py         ← One-time: Gutenberg text → sonnet_texts.json
├── init_db.py                 ← Creates 22-table database from scratch
├── seed_sonnets.py            ← Loads sonnets, stanzas, lines from JSON
├── seed_reference.py          ← Loads characters, scholars, devices, modes, groups
├── seed_groups_v2.py          ← Expanded scholarly groupings (47 groups)
├── enrich_sonnets.py          ← Loads LLM enrichment from batch JSON files
├── seed_essay_unresolved.py   ← Inserts the Unresolved Questions essay
└── validate_db.py             ← Integrity checks (all passing)
```

**Full rebuild command** (recreates everything from source files):
```bash
python scripts/init_db.py --force
python scripts/seed_sonnets.py
python scripts/seed_reference.py
python scripts/seed_groups_v2.py
python scripts/enrich_sonnets.py          # processes all batch files
python scripts/seed_essay_unresolved.py
python scripts/validate_db.py
```

---

## 4. Documentation

```
C:\Dev\Shakespeare\
├── CLAUDE.md                          ← Project instructions for Claude Code
├── DOCUMENTAIRTRAFFICCONTROL.md       ← Which doc to read for which task
├── SONNETSTUDYDECKARDANALYSIS.md      ← Python vs LLM boundary
├── PHASESTATUS.md                     ← Session log
├── HOWITSBEINGSAVED.md                ← This file
├── docs\
│   ├── SYSTEM.md                      ← Architecture
│   ├── ONTOLOGY.md                    ← Database schema (updated to reflect actual)
│   ├── PIPELINE.md                    ← Script execution order (updated)
│   ├── INTERFACE.md                   ← Site page types and theme
│   └── ROADMAP.md                     ← Phase status (updated)
└── site\content\
    ├── FORMAT_SPECS.md
    └── TEMPLATES.md                   ← Dominic templates for all 5 page types
```

---

## 5. What's NOT Saved Yet

- **Git**: The project has a git repo but the enrichment work from this session is NOT committed. You should commit when you're ready.
- **GitHub**: Nothing is pushed to a remote. The data exists only on your local machine.
- **Site HTML**: `build_site.py` doesn't exist yet — no generated HTML pages.
- **100 sonnets**: 54/154 enriched. 100 sonnets still need enrichment.

---

## How to Verify Nothing is Lost

```bash
# Check database integrity
python scripts/validate_db.py

# Count enriched sonnets
python -c "import sqlite3; c=sqlite3.connect('db/sonnets.db'); print(f'Enriched: {c.execute(\"SELECT COUNT(*) FROM sonnet_analyses\").fetchone()[0]}/154')"

# List enrichment batch files
ls -la data/enrichment/

# Check total data size
du -sh db/ data/
```

---

## Safety: How the Data is Protected

1. **JSON backups**: Every enrichment batch is saved as a separate JSON file BEFORE being loaded into the database. If the DB is corrupted, replay from JSON.
2. **Idempotent scripts**: All seed/enrich scripts use INSERT OR REPLACE — safe to re-run.
3. **Full rebuild**: The entire database can be recreated from `data/` files using the scripts above.
4. **No destructive operations**: The pipeline only adds/replaces, never deletes (except `init_db.py --force`).
