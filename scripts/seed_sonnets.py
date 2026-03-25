"""
Seed the sonnets, stanzas, and lines tables from sonnet_texts.json.

All data is DETERMINISTIC — derived directly from the 1609 Quarto text.
Stanza boundaries are structural (every sonnet follows English sonnet form
except Sonnet 99 [15 lines: 5+4+4+2] and Sonnet 126 [12 lines: 6 couplets, no couplet-close]).

Usage:
    python scripts/seed_sonnets.py
"""

import json
import sqlite3
import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, 'db', 'sonnets.db')
TEXTS_PATH = os.path.join(PROJECT_DIR, 'data', 'sonnet_texts.json')

# Addressee assignments based on scholarly consensus
# FYM = 1-126 (with some debate), DL = 127-152, Cupid = 153-154
ADDRESSEES = {}
for n in range(1, 127):
    ADDRESSEES[n] = 'FYM'
for n in range(127, 153):
    ADDRESSEES[n] = 'DL'
ADDRESSEES[153] = 'NONE'  # Cupid/Anacreontic
ADDRESSEES[154] = 'NONE'  # Cupid/Anacreontic
# Overrides for specific sonnets with mixed addressees
ADDRESSEES[40] = 'MIXED'  # Betrayal triangle
ADDRESSEES[41] = 'MIXED'
ADDRESSEES[42] = 'MIXED'
ADDRESSEES[133] = 'MIXED'  # DL sequence but about the triangle
ADDRESSEES[134] = 'MIXED'
ADDRESSEES[144] = 'MIXED'  # 'Two loves I have of comfort and despair'


def get_stanza_plan(sonnet_number, line_count):
    """
    Return stanza decomposition for a sonnet.
    Standard English sonnet: Q1(1-4), Q2(5-8), Q3(9-12), C(13-14)
    Exceptions:
      Sonnet 99: 15 lines — Q1(1-5), Q2(6-9), Q3(10-13), C(14-15)
                 (first quatrain has 5 lines)
      Sonnet 126: 12 lines — six couplets, no final couplet
                 We model as Q1(1-4), Q2(5-8), Q3(9-12), no couplet
    """
    if sonnet_number == 99:
        return [
            (1, 'QUATRAIN_1', 1, 5),
            (2, 'QUATRAIN_2', 6, 9),
            (3, 'QUATRAIN_3', 10, 13),
            (4, 'COUPLET', 14, 15),
        ]
    elif sonnet_number == 126:
        # 12 lines, 6 couplets — modeled as three "quatrains" of 4 lines
        return [
            (1, 'QUATRAIN_1', 1, 4),
            (2, 'QUATRAIN_2', 5, 8),
            (3, 'QUATRAIN_3', 9, 12),
            # No couplet — the absence is significant (envoi to FYM)
        ]
    else:
        # Standard 14-line English sonnet
        return [
            (1, 'QUATRAIN_1', 1, 4),
            (2, 'QUATRAIN_2', 5, 8),
            (3, 'QUATRAIN_3', 9, 12),
            (4, 'COUPLET', 13, 14),
        ]


def main():
    with open(TEXTS_PATH, 'r', encoding='utf-8') as f:
        sonnets_data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=ON")
    cur = conn.cursor()

    # Check if already seeded
    count = cur.execute("SELECT COUNT(*) FROM sonnets").fetchone()[0]
    if count > 0:
        print(f"sonnets table already has {count} rows. Skipping.")
        conn.close()
        return

    total_lines = 0
    total_stanzas = 0

    for s in sonnets_data:
        number = s['number']
        first_line = s['first_line']
        line_count = s['line_count']
        addressee = ADDRESSEES.get(number, 'FYM')

        # Insert sonnet
        cur.execute("""
            INSERT INTO sonnets (id, number, first_line, line_count, addressee, source)
            VALUES (?, ?, ?, ?, ?, '1609_QUARTO_GUTENBERG')
        """, (number, number, first_line, line_count, addressee))

        # Insert stanzas
        stanza_plan = get_stanza_plan(number, line_count)
        stanza_id_map = {}  # stanza_number -> stanza_id

        for stanza_num, stanza_type, start, end in stanza_plan:
            cur.execute("""
                INSERT INTO stanzas (sonnet_id, stanza_number, stanza_type, start_line, end_line)
                VALUES (?, ?, ?, ?, ?)
            """, (number, stanza_num, stanza_type, start, end))
            stanza_id_map[stanza_num] = cur.lastrowid
            total_stanzas += 1

        # Insert lines with stanza assignment
        for i, line_text in enumerate(s['lines']):
            line_num = i + 1

            # Find which stanza this line belongs to
            stanza_id = None
            for stanza_num, stanza_type, start, end in stanza_plan:
                if start <= line_num <= end:
                    stanza_id = stanza_id_map[stanza_num]
                    break

            cur.execute("""
                INSERT INTO lines (sonnet_id, line_number, line_text, stanza_id)
                VALUES (?, ?, ?, ?)
            """, (number, line_num, line_text, stanza_id))
            total_lines += 1

    conn.commit()
    conn.close()

    print(f"Seeded {len(sonnets_data)} sonnets, {total_stanzas} stanzas, {total_lines} lines")


if __name__ == '__main__':
    main()
