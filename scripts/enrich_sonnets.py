"""
Insert LLM-generated enrichment data into the database.

Reads JSON files from data/enrichment/ and populates:
  - sonnet_analyses
  - line_annotations
  - sonnet_themes
  - character_appearances
  - directing_notes
  - line_devices
  - sonnet_modes

Each enrichment file covers one or more sonnets.
All inserted data gets: source_method='LLM_ASSISTED', review_status='DRAFT', confidence='MEDIUM'

Usage:
    python scripts/enrich_sonnets.py                    # process all files in data/enrichment/
    python scripts/enrich_sonnets.py batch_01.json      # process one file
"""

import json
import sqlite3
import os
import sys
import glob

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, 'db', 'sonnets.db')
ENRICHMENT_DIR = os.path.join(PROJECT_DIR, 'data', 'enrichment')


def get_line_id(cur, sonnet_num, line_num):
    row = cur.execute(
        "SELECT id FROM lines WHERE sonnet_id = ? AND line_number = ?",
        (sonnet_num, line_num)
    ).fetchone()
    return row[0] if row else None


def enrich_sonnet(cur, s):
    """Insert enrichment data for one sonnet."""
    num = s['number']
    inserted = {'analyses': 0, 'annotations': 0, 'themes': 0,
                'appearances': 0, 'directing': 0, 'devices': 0, 'modes': 0}

    # --- sonnet_analyses ---
    if 'analysis' in s:
        a = s['analysis']
        cur.execute("""
            INSERT OR REPLACE INTO sonnet_analyses
            (sonnet_id, volta_line, volta_type, couplet_function,
             argument_summary, speaker_stance, emotional_arc,
             dramatic_situation, subtext, analysis_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (num, a.get('volta_line'), a.get('volta_type'),
              a.get('couplet_function'), a.get('argument_summary'),
              a.get('speaker_stance'), a.get('emotional_arc'),
              a.get('dramatic_situation'), a.get('subtext'),
              a.get('analysis_text')))
        inserted['analyses'] = 1

    # --- line_annotations ---
    for la in s.get('line_annotations', []):
        line_id = get_line_id(cur, num, la['line_number'])
        if not line_id:
            print(f"  WARNING: Sonnet {num}, line {la['line_number']} not found")
            continue
        cur.execute("""
            INSERT OR REPLACE INTO line_annotations
            (line_id, emphasis_words, emotional_note, delivery_note, gloss, commentary)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (line_id, json.dumps(la.get('emphasis_words', [])),
              la.get('emotional_note'), la.get('delivery_note'),
              la.get('gloss'), la.get('commentary')))
        inserted['annotations'] += 1

    # --- sonnet_themes ---
    for t in s.get('themes', []):
        cur.execute("""
            INSERT OR IGNORE INTO sonnet_themes (sonnet_id, theme, prominence)
            VALUES (?, ?, ?)
        """, (num, t['theme'], t.get('prominence', 'SECONDARY')))
        inserted['themes'] += 1

    # --- character_appearances ---
    for ca in s.get('character_appearances', []):
        cur.execute("""
            INSERT OR IGNORE INTO character_appearances
            (sonnet_id, character_id, role, evidence)
            VALUES (?, ?, ?, ?)
        """, (num, ca['character_id'], ca.get('role'), ca.get('evidence')))
        inserted['appearances'] += 1

    # --- directing_notes ---
    if 'directing' in s:
        d = s['directing']
        cur.execute("""
            INSERT OR REPLACE INTO directing_notes
            (sonnet_id, scene_setting, character_note, fym_note, dl_note,
             overall_arc, key_moments)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (num, d.get('scene_setting'), d.get('character_note'),
              d.get('fym_note'), d.get('dl_note'), d.get('overall_arc'),
              json.dumps(d.get('key_moments', []))))
        inserted['directing'] = 1

    # --- line_devices ---
    for ld in s.get('line_devices', []):
        line_id = get_line_id(cur, num, ld['line_number'])
        if not line_id:
            continue
        cur.execute("""
            INSERT OR IGNORE INTO line_devices
            (line_id, device_id, quotation, explanation)
            VALUES (?, ?, ?, ?)
        """, (line_id, ld['device_id'], ld.get('quotation'), ld.get('explanation')))
        inserted['devices'] += 1

    # --- sonnet_modes ---
    for sm in s.get('modes', []):
        cur.execute("""
            INSERT OR IGNORE INTO sonnet_modes
            (sonnet_id, mode_id, priority, rationale)
            VALUES (?, ?, ?, ?)
        """, (num, sm['mode_id'], sm.get('priority', 0), sm.get('rationale')))
        inserted['modes'] += 1

    return inserted


def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=ON")
    cur = conn.cursor()

    sonnets = data if isinstance(data, list) else data.get('sonnets', [data])
    totals = {'analyses': 0, 'annotations': 0, 'themes': 0,
              'appearances': 0, 'directing': 0, 'devices': 0, 'modes': 0}

    for s in sonnets:
        result = enrich_sonnet(cur, s)
        for k, v in result.items():
            totals[k] += v
        print(f"  Sonnet {s['number']}: {result}")

    conn.commit()
    conn.close()

    print(f"  TOTALS: {totals}")
    return totals


def main():
    os.makedirs(ENRICHMENT_DIR, exist_ok=True)

    if len(sys.argv) > 1:
        filepath = os.path.join(ENRICHMENT_DIR, sys.argv[1])
        if not os.path.exists(filepath):
            filepath = sys.argv[1]
        print(f"Processing {filepath}")
        process_file(filepath)
    else:
        files = sorted(glob.glob(os.path.join(ENRICHMENT_DIR, '*.json')))
        if not files:
            print(f"No JSON files found in {ENRICHMENT_DIR}")
            return
        for filepath in files:
            print(f"\nProcessing {os.path.basename(filepath)}")
            process_file(filepath)


if __name__ == '__main__':
    main()
