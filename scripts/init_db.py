"""
Initialize the Shakespeare Sonnets database with full schema.

Creates all tables in a single pass — no separate migration scripts needed.
Tables are organized in layers:

  LAYER 1 — Core Text (deterministic, from 1609 Quarto)
    sonnets, stanzas, lines

  LAYER 2 — Characters & Scholarly Apparatus
    characters, character_candidates, scholars, bibliography,
    sonnet_groups, sonnet_group_members

  LAYER 3 — Rhetoric & Poetics
    rhetorical_devices, analytical_modes,
    line_devices (join: line × device), sonnet_modes (join: sonnet × mode)

  LAYER 4 — Enrichment (LLM-assisted)
    sonnet_analyses, line_annotations, sonnet_themes,
    character_appearances, directing_notes

  LAYER 5 — Essays & Context
    essays, essay_sonnet_links, contexts

Usage:
    python scripts/init_db.py          # creates db/sonnets.db
    python scripts/init_db.py --force  # drops and recreates
"""

import sqlite3
import os
import sys

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db')
DB_PATH = os.path.join(DB_DIR, 'sonnets.db')

SCHEMA = """
-- ============================================================
-- LAYER 1: Core Text
-- Source: 1609 Quarto via Project Gutenberg
-- Provenance: DETERMINISTIC / HIGH / VERIFIED
-- ============================================================

CREATE TABLE IF NOT EXISTS sonnets (
    id              INTEGER PRIMARY KEY,         -- 1-154
    number          INTEGER NOT NULL UNIQUE,     -- 1-154
    first_line      TEXT NOT NULL,
    line_count      INTEGER NOT NULL DEFAULT 14, -- 14 standard; 15 for 99, 12 for 126
    addressee       TEXT,                        -- FYM, DL, RP, SELF, MIXED, NONE
    source          TEXT NOT NULL DEFAULT '1609_QUARTO_GUTENBERG',
    source_method   TEXT NOT NULL DEFAULT 'DETERMINISTIC',
    review_status   TEXT NOT NULL DEFAULT 'VERIFIED',
    confidence      TEXT NOT NULL DEFAULT 'HIGH',
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS stanzas (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sonnet_id       INTEGER NOT NULL REFERENCES sonnets(id),
    stanza_number   INTEGER NOT NULL,            -- 1-4 (Q1, Q2, Q3, Couplet) for standard
    stanza_type     TEXT NOT NULL,               -- QUATRAIN_1, QUATRAIN_2, QUATRAIN_3, COUPLET
    start_line      INTEGER NOT NULL,            -- 1-based line number within sonnet
    end_line        INTEGER NOT NULL,
    source_method   TEXT NOT NULL DEFAULT 'DETERMINISTIC',
    UNIQUE(sonnet_id, stanza_number)
);

CREATE TABLE IF NOT EXISTS lines (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sonnet_id       INTEGER NOT NULL REFERENCES sonnets(id),
    line_number     INTEGER NOT NULL,            -- 1-based within sonnet
    line_text       TEXT NOT NULL,
    stanza_id       INTEGER REFERENCES stanzas(id),
    -- Prosodic fields (populated by enrichment)
    meter_pattern   TEXT,                        -- e.g. 'xX xX xX xX xX' for regular iambic pentameter
    has_enjambment  INTEGER,                     -- 0/1
    has_caesura     INTEGER,                     -- 0/1
    is_volta        INTEGER DEFAULT 0,           -- 0/1 — marks the argumentative turn
    source_method   TEXT NOT NULL DEFAULT 'DETERMINISTIC',
    review_status   TEXT NOT NULL DEFAULT 'VERIFIED',
    confidence      TEXT NOT NULL DEFAULT 'HIGH',
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(sonnet_id, line_number)
);

-- Global line index for the entire sequence (1-2156)
CREATE INDEX IF NOT EXISTS idx_lines_sonnet ON lines(sonnet_id);

-- ============================================================
-- LAYER 2: Characters & Scholarly Apparatus
-- Source: SEED_DATA from sonnets_seed.json
-- ============================================================

CREATE TABLE IF NOT EXISTS characters (
    id              TEXT PRIMARY KEY,            -- FYM, DL, RP, SPEAKER
    name            TEXT NOT NULL,
    aka             TEXT,                        -- JSON array of alternate names
    description     TEXT,
    source_method   TEXT NOT NULL DEFAULT 'SEED_DATA',
    review_status   TEXT NOT NULL DEFAULT 'VERIFIED',
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS character_candidates (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id    TEXT NOT NULL REFERENCES characters(id),
    candidate_name  TEXT NOT NULL,
    strength        TEXT NOT NULL,               -- STRONG, MODERATE, SPECULATIVE
    evidence        TEXT,
    source_method   TEXT NOT NULL DEFAULT 'SEED_DATA',
    review_status   TEXT NOT NULL DEFAULT 'VERIFIED',
    UNIQUE(character_id, candidate_name)
);

CREATE TABLE IF NOT EXISTS scholars (
    id              TEXT PRIMARY KEY,            -- VENDLER, BOOTH, etc.
    name            TEXT NOT NULL,
    primary_work    TEXT,
    approach        TEXT,
    source_method   TEXT NOT NULL DEFAULT 'SEED_DATA',
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS bibliography (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    cite_key        TEXT NOT NULL UNIQUE,        -- vendler1997, booth1977, etc.
    citation        TEXT NOT NULL,
    source_method   TEXT NOT NULL DEFAULT 'SEED_DATA',
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sonnet_groups (
    id              TEXT PRIMARY KEY,            -- PROCREATION, IMMORTALITY, etc.
    name            TEXT NOT NULL,
    description     TEXT,
    addressee       TEXT,                        -- FYM, DL, MIXED, NONE
    themes          TEXT,                        -- JSON array
    source_method   TEXT NOT NULL DEFAULT 'SEED_DATA',
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sonnet_group_members (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id        TEXT NOT NULL REFERENCES sonnet_groups(id),
    sonnet_id       INTEGER NOT NULL REFERENCES sonnets(id),
    UNIQUE(group_id, sonnet_id)
);

-- ============================================================
-- LAYER 3: Rhetoric & Poetics
-- Source: SEED_DATA (device/mode definitions), LLM_ASSISTED (annotations)
-- ============================================================

CREATE TABLE IF NOT EXISTS rhetorical_devices (
    id              TEXT PRIMARY KEY,            -- METAPHOR, SIMILE, PUN, etc.
    name            TEXT NOT NULL,
    description     TEXT,
    source_method   TEXT NOT NULL DEFAULT 'SEED_DATA',
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS analytical_modes (
    id              TEXT PRIMARY KEY,            -- RHETORICAL, DRAMATIC, etc.
    name            TEXT NOT NULL,
    description     TEXT,
    source_method   TEXT NOT NULL DEFAULT 'SEED_DATA',
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Join table: which devices appear on which lines
CREATE TABLE IF NOT EXISTS line_devices (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    line_id         INTEGER NOT NULL REFERENCES lines(id),
    device_id       TEXT NOT NULL REFERENCES rhetorical_devices(id),
    quotation       TEXT,                        -- the specific text exhibiting the device
    explanation     TEXT,                        -- why this is this device
    source_method   TEXT NOT NULL DEFAULT 'LLM_ASSISTED',
    review_status   TEXT NOT NULL DEFAULT 'DRAFT',
    confidence      TEXT NOT NULL DEFAULT 'MEDIUM',
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(line_id, device_id, quotation)
);

-- Join table: which analytical modes are applied to which sonnets
CREATE TABLE IF NOT EXISTS sonnet_modes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sonnet_id       INTEGER NOT NULL REFERENCES sonnets(id),
    mode_id         TEXT NOT NULL REFERENCES analytical_modes(id),
    priority        INTEGER DEFAULT 0,           -- higher = more important for this sonnet
    rationale       TEXT,                        -- why this mode is relevant here
    source_method   TEXT NOT NULL DEFAULT 'LLM_ASSISTED',
    review_status   TEXT NOT NULL DEFAULT 'DRAFT',
    confidence      TEXT NOT NULL DEFAULT 'MEDIUM',
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(sonnet_id, mode_id)
);

-- ============================================================
-- LAYER 4: Enrichment (LLM-Assisted)
-- All default to: LLM_ASSISTED / DRAFT / MEDIUM
-- ============================================================

-- Per-sonnet analysis (the main scholarly close-reading)
CREATE TABLE IF NOT EXISTS sonnet_analyses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sonnet_id       INTEGER NOT NULL REFERENCES sonnets(id),
    -- Structural analysis
    volta_line      INTEGER,                     -- which line has the turn
    volta_type      TEXT,                        -- DRAMATIC, LOGICAL, TONAL, IRONIC
    couplet_function TEXT,                       -- RESOLUTION, REVERSAL, EXTENSION, EPIGRAM, IRONIC
    argument_summary TEXT,                       -- one-sentence summary of the sonnet's rhetorical 'move'
    -- Dramatic analysis (for the FYM/DL directing project)
    speaker_stance  TEXT,                        -- e.g. 'pleading', 'bitter', 'self-mocking', 'defiant'
    emotional_arc   TEXT,                        -- e.g. 'adoration → doubt → resigned acceptance'
    dramatic_situation TEXT,                     -- what's happening between the characters
    subtext         TEXT,                        -- what the Speaker means but doesn't say
    -- Full analysis
    analysis_text   TEXT,                        -- the complete close-reading prose
    -- Provenance
    source_method   TEXT NOT NULL DEFAULT 'LLM_ASSISTED',
    review_status   TEXT NOT NULL DEFAULT 'DRAFT',
    confidence      TEXT NOT NULL DEFAULT 'MEDIUM',
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(sonnet_id)
);

-- Per-line annotation (for the directing/performance dimension)
CREATE TABLE IF NOT EXISTS line_annotations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    line_id         INTEGER NOT NULL REFERENCES lines(id),
    -- Directing notes
    emphasis_words  TEXT,                        -- JSON array of words to stress
    emotional_note  TEXT,                        -- acting direction for this line
    delivery_note   TEXT,                        -- how to speak it (pace, volume, tone)
    -- Scholarly notes
    gloss           TEXT,                        -- paraphrase / modernization
    commentary      TEXT,                        -- scholarly annotation
    -- Provenance
    source_method   TEXT NOT NULL DEFAULT 'LLM_ASSISTED',
    review_status   TEXT NOT NULL DEFAULT 'DRAFT',
    confidence      TEXT NOT NULL DEFAULT 'MEDIUM',
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(line_id)
);

-- Per-sonnet themes (many-to-many with controlled vocabulary)
CREATE TABLE IF NOT EXISTS sonnet_themes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sonnet_id       INTEGER NOT NULL REFERENCES sonnets(id),
    theme           TEXT NOT NULL,               -- e.g. 'time', 'beauty', 'mortality'
    prominence      TEXT DEFAULT 'SECONDARY',    -- PRIMARY, SECONDARY
    source_method   TEXT NOT NULL DEFAULT 'LLM_ASSISTED',
    review_status   TEXT NOT NULL DEFAULT 'DRAFT',
    confidence      TEXT NOT NULL DEFAULT 'MEDIUM',
    UNIQUE(sonnet_id, theme)
);

-- Character appearances per sonnet (beyond the primary addressee)
CREATE TABLE IF NOT EXISTS character_appearances (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sonnet_id       INTEGER NOT NULL REFERENCES sonnets(id),
    character_id    TEXT NOT NULL REFERENCES characters(id),
    role            TEXT,                        -- ADDRESSED, MENTIONED, IMPLIED, ABSENT_PRESENCE
    evidence        TEXT,                        -- textual basis for this identification
    source_method   TEXT NOT NULL DEFAULT 'LLM_ASSISTED',
    review_status   TEXT NOT NULL DEFAULT 'DRAFT',
    confidence      TEXT NOT NULL DEFAULT 'MEDIUM',
    UNIQUE(sonnet_id, character_id)
);

-- Directing notes at the sonnet level (performance interpretation)
CREATE TABLE IF NOT EXISTS directing_notes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sonnet_id       INTEGER NOT NULL REFERENCES sonnets(id),
    -- Performance framing
    scene_setting   TEXT,                        -- physical/emotional context for performance
    character_note  TEXT,                        -- who is the Speaker in this moment
    fym_note        TEXT,                        -- how FYM relates to this sonnet
    dl_note         TEXT,                        -- how DL relates to this sonnet
    overall_arc     TEXT,                        -- performance arc across the 14 lines
    key_moments     TEXT,                        -- JSON array of {line, note} for pivotal moments
    -- Provenance
    source_method   TEXT NOT NULL DEFAULT 'LLM_ASSISTED',
    review_status   TEXT NOT NULL DEFAULT 'DRAFT',
    confidence      TEXT NOT NULL DEFAULT 'MEDIUM',
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(sonnet_id)
);

-- ============================================================
-- LAYER 5: Essays & Context
-- ============================================================

CREATE TABLE IF NOT EXISTS essays (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    slug            TEXT NOT NULL UNIQUE,         -- URL-friendly identifier
    title           TEXT NOT NULL,
    subtitle        TEXT,
    abstract        TEXT,
    body_html       TEXT,                         -- generated HTML
    body_markdown   TEXT,                         -- source markdown
    essay_type      TEXT DEFAULT 'THEMATIC',      -- THEMATIC, CHARACTER, STRUCTURAL, HISTORICAL
    source_method   TEXT NOT NULL DEFAULT 'LLM_ASSISTED',
    review_status   TEXT NOT NULL DEFAULT 'DRAFT',
    confidence      TEXT NOT NULL DEFAULT 'MEDIUM',
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS essay_sonnet_links (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    essay_id        INTEGER NOT NULL REFERENCES essays(id),
    sonnet_id       INTEGER NOT NULL REFERENCES sonnets(id),
    relevance       TEXT DEFAULT 'DISCUSSED',     -- DISCUSSED, CITED, CENTRAL
    UNIQUE(essay_id, sonnet_id)
);

CREATE TABLE IF NOT EXISTS contexts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sonnet_id       INTEGER REFERENCES sonnets(id), -- NULL for general contexts
    context_type    TEXT NOT NULL,                -- BIOGRAPHICAL, PUBLICATION, HISTORICAL, CANDIDATE
    title           TEXT,
    body_text       TEXT,
    source_method   TEXT NOT NULL DEFAULT 'LLM_ASSISTED',
    review_status   TEXT NOT NULL DEFAULT 'DRAFT',
    confidence      TEXT NOT NULL DEFAULT 'MEDIUM',
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- Indexes for common query patterns
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_stanzas_sonnet ON stanzas(sonnet_id);
CREATE INDEX IF NOT EXISTS idx_lines_stanza ON lines(stanza_id);
CREATE INDEX IF NOT EXISTS idx_line_devices_line ON line_devices(line_id);
CREATE INDEX IF NOT EXISTS idx_line_devices_device ON line_devices(device_id);
CREATE INDEX IF NOT EXISTS idx_sonnet_modes_sonnet ON sonnet_modes(sonnet_id);
CREATE INDEX IF NOT EXISTS idx_sonnet_modes_mode ON sonnet_modes(mode_id);
CREATE INDEX IF NOT EXISTS idx_sonnet_analyses_sonnet ON sonnet_analyses(sonnet_id);
CREATE INDEX IF NOT EXISTS idx_line_annotations_line ON line_annotations(line_id);
CREATE INDEX IF NOT EXISTS idx_sonnet_themes_sonnet ON sonnet_themes(sonnet_id);
CREATE INDEX IF NOT EXISTS idx_sonnet_themes_theme ON sonnet_themes(theme);
CREATE INDEX IF NOT EXISTS idx_character_appearances_sonnet ON character_appearances(sonnet_id);
CREATE INDEX IF NOT EXISTS idx_character_appearances_char ON character_appearances(character_id);
CREATE INDEX IF NOT EXISTS idx_directing_notes_sonnet ON directing_notes(sonnet_id);
CREATE INDEX IF NOT EXISTS idx_essay_sonnet_links_essay ON essay_sonnet_links(essay_id);
CREATE INDEX IF NOT EXISTS idx_essay_sonnet_links_sonnet ON essay_sonnet_links(sonnet_id);
CREATE INDEX IF NOT EXISTS idx_contexts_sonnet ON contexts(sonnet_id);
CREATE INDEX IF NOT EXISTS idx_group_members_group ON sonnet_group_members(group_id);
CREATE INDEX IF NOT EXISTS idx_group_members_sonnet ON sonnet_group_members(sonnet_id);
"""


def main():
    force = '--force' in sys.argv

    os.makedirs(DB_DIR, exist_ok=True)

    if force and os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing {DB_PATH}")

    if os.path.exists(DB_PATH) and not force:
        print(f"Database already exists at {DB_PATH}")
        print("Use --force to drop and recreate")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA)
    conn.close()

    print(f"Created database at {DB_PATH}")

    # Verify tables
    conn = sqlite3.connect(DB_PATH)
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    print(f"Tables ({len(tables)}):")
    for t in tables:
        print(f"  {t[0]}")
    conn.close()


if __name__ == '__main__':
    main()
