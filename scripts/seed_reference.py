"""
Seed reference/lookup tables from sonnets_seed.json:
  - characters + character_candidates
  - scholars
  - bibliography
  - rhetorical_devices
  - analytical_modes
  - sonnet_groups + sonnet_group_members

All data is SEED_DATA provenance.

Usage:
    python scripts/seed_reference.py
"""

import json
import sqlite3
import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, 'db', 'sonnets.db')
SEED_PATH = os.path.join(PROJECT_DIR, 'data', 'sonnets_seed.json')


def main():
    with open(SEED_PATH, 'r', encoding='utf-8') as f:
        seed = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=ON")
    cur = conn.cursor()

    # --- Characters ---
    for c in seed['characters']:
        cur.execute("""
            INSERT OR IGNORE INTO characters (id, name, aka, description)
            VALUES (?, ?, ?, ?)
        """, (c['id'], c['name'], json.dumps(c.get('aka', [])), c.get('description')))

        for cand in c.get('candidates', []):
            cur.execute("""
                INSERT OR IGNORE INTO character_candidates (character_id, candidate_name, strength, evidence)
                VALUES (?, ?, ?, ?)
            """, (c['id'], cand['name'], cand['strength'], cand.get('evidence')))

    chars = cur.execute("SELECT COUNT(*) FROM characters").fetchone()[0]
    cands = cur.execute("SELECT COUNT(*) FROM character_candidates").fetchone()[0]
    print(f"Characters: {chars}, Candidates: {cands}")

    # --- Scholars ---
    for s in seed['scholars']:
        cur.execute("""
            INSERT OR IGNORE INTO scholars (id, name, primary_work, approach)
            VALUES (?, ?, ?, ?)
        """, (s['id'], s['name'], s.get('work'), s.get('approach')))

    scholars = cur.execute("SELECT COUNT(*) FROM scholars").fetchone()[0]
    print(f"Scholars: {scholars}")

    # --- Bibliography ---
    for b in seed['bibliography']:
        cur.execute("""
            INSERT OR IGNORE INTO bibliography (cite_key, citation)
            VALUES (?, ?)
        """, (b['key'], b['citation']))

    bibs = cur.execute("SELECT COUNT(*) FROM bibliography").fetchone()[0]
    print(f"Bibliography entries: {bibs}")

    # --- Rhetorical Devices ---
    for d in seed['rhetorical_devices']:
        cur.execute("""
            INSERT OR IGNORE INTO rhetorical_devices (id, name, description)
            VALUES (?, ?, ?)
        """, (d['id'], d['name'], d.get('description')))

    devices = cur.execute("SELECT COUNT(*) FROM rhetorical_devices").fetchone()[0]
    print(f"Rhetorical devices: {devices}")

    # --- Analytical Modes ---
    for m in seed['analytical_modes']:
        cur.execute("""
            INSERT OR IGNORE INTO analytical_modes (id, name, description)
            VALUES (?, ?, ?)
        """, (m['id'], m['name'], m.get('description')))

    modes = cur.execute("SELECT COUNT(*) FROM analytical_modes").fetchone()[0]
    print(f"Analytical modes: {modes}")

    # --- Sonnet Groups ---
    for g in seed['sonnet_groups']:
        cur.execute("""
            INSERT OR IGNORE INTO sonnet_groups (id, name, description, addressee, themes)
            VALUES (?, ?, ?, ?, ?)
        """, (g['id'], g['name'], g.get('description'), g.get('addressee'),
              json.dumps(g.get('themes', []))))

        for sonnet_num in g.get('sonnets', []):
            cur.execute("""
                INSERT OR IGNORE INTO sonnet_group_members (group_id, sonnet_id)
                VALUES (?, ?)
            """, (g['id'], sonnet_num))

    groups = cur.execute("SELECT COUNT(*) FROM sonnet_groups").fetchone()[0]
    members = cur.execute("SELECT COUNT(*) FROM sonnet_group_members").fetchone()[0]
    print(f"Sonnet groups: {groups}, Group memberships: {members}")

    conn.commit()
    conn.close()
    print("Done.")


if __name__ == '__main__':
    main()
