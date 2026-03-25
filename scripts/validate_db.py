"""
Validate the Shakespeare Sonnets database for integrity and completeness.

Checks:
  1. All 154 sonnets present
  2. Correct line counts (14 standard, 15 for #99, 12 for #126)
  3. Every line has a stanza assignment
  4. Stanza boundaries are correct
  5. Addressee assignments present
  6. Reference tables populated
  7. Foreign key integrity
  8. No orphaned records

Usage:
    python scripts/validate_db.py
"""

import sqlite3
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, 'db', 'sonnets.db')

errors = []
warnings = []


def check(condition, msg, warn=False):
    if not condition:
        if warn:
            warnings.append(msg)
            print(f"  WARN: {msg}")
        else:
            errors.append(msg)
            print(f"  FAIL: {msg}")
    else:
        print(f"  OK:   {msg}")


def main():
    if not os.path.exists(DB_PATH):
        print(f"Database not found: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=ON")
    cur = conn.cursor()

    print("=== LAYER 1: Core Text ===")

    # Sonnets count
    count = cur.execute("SELECT COUNT(*) FROM sonnets").fetchone()[0]
    check(count == 154, f"154 sonnets present (found {count})")

    # Sonnet number range
    nums = set(r[0] for r in cur.execute("SELECT number FROM sonnets").fetchall())
    expected = set(range(1, 155))
    missing = expected - nums
    extra = nums - expected
    check(not missing, f"No missing sonnet numbers (missing: {missing or 'none'})")
    check(not extra, f"No extra sonnet numbers (extra: {extra or 'none'})")

    # Line counts
    irregular = cur.execute("""
        SELECT number, line_count FROM sonnets
        WHERE (number = 99 AND line_count != 15)
           OR (number = 126 AND line_count != 12)
           OR (number NOT IN (99, 126) AND line_count != 14)
    """).fetchall()
    check(not irregular, f"Line counts correct (violations: {irregular or 'none'})")

    # Total lines
    total_lines = cur.execute("SELECT COUNT(*) FROM lines").fetchone()[0]
    expected_lines = 152 * 14 + 15 + 12  # 152 standard + sonnet 99 + sonnet 126
    check(total_lines == expected_lines, f"Total lines = {expected_lines} (found {total_lines})")

    # Every line has stanza
    orphan_lines = cur.execute(
        "SELECT COUNT(*) FROM lines WHERE stanza_id IS NULL"
    ).fetchone()[0]
    check(orphan_lines == 0, f"All lines have stanza assignments (orphans: {orphan_lines})")

    # Stanza counts
    total_stanzas = cur.execute("SELECT COUNT(*) FROM stanzas").fetchone()[0]
    # 152 standard sonnets * 4 stanzas + sonnet 99 (4) + sonnet 126 (3) = 615
    expected_stanzas = 152 * 4 + 4 + 3
    check(total_stanzas == expected_stanzas, f"Total stanzas = {expected_stanzas} (found {total_stanzas})")

    # Sonnet 126 has no couplet
    s126_couplet = cur.execute("""
        SELECT COUNT(*) FROM stanzas
        WHERE sonnet_id = 126 AND stanza_type = 'COUPLET'
    """).fetchone()[0]
    check(s126_couplet == 0, "Sonnet 126 has no couplet (the absent ending)")

    print("\n=== LAYER 2: Characters & Apparatus ===")

    chars = cur.execute("SELECT COUNT(*) FROM characters").fetchone()[0]
    check(chars == 4, f"4 characters (found {chars})")

    cands = cur.execute("SELECT COUNT(*) FROM character_candidates").fetchone()[0]
    check(cands >= 8, f"At least 8 candidates (found {cands})")

    scholars = cur.execute("SELECT COUNT(*) FROM scholars").fetchone()[0]
    check(scholars >= 10, f"At least 10 scholars (found {scholars})")

    bibs = cur.execute("SELECT COUNT(*) FROM bibliography").fetchone()[0]
    check(bibs >= 10, f"At least 10 bibliography entries (found {bibs})")

    groups = cur.execute("SELECT COUNT(*) FROM sonnet_groups").fetchone()[0]
    check(groups >= 6, f"At least 6 sonnet groups (found {groups})")

    # Addressees
    no_addr = cur.execute(
        "SELECT COUNT(*) FROM sonnets WHERE addressee IS NULL"
    ).fetchone()[0]
    check(no_addr == 0, f"All sonnets have addressee (missing: {no_addr})")

    print("\n=== LAYER 3: Rhetoric & Poetics ===")

    devices = cur.execute("SELECT COUNT(*) FROM rhetorical_devices").fetchone()[0]
    check(devices >= 15, f"At least 15 rhetorical devices (found {devices})")

    modes = cur.execute("SELECT COUNT(*) FROM analytical_modes").fetchone()[0]
    check(modes >= 6, f"At least 6 analytical modes (found {modes})")

    print("\n=== LAYER 4: Enrichment (empty at scaffold) ===")

    for table in ['sonnet_analyses', 'line_annotations', 'sonnet_themes',
                  'character_appearances', 'directing_notes']:
        count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        check(True, f"{table}: {count} rows (enrichment pending)", warn=count == 0)

    print("\n=== Foreign Key Integrity ===")

    # Check FK violations
    fk_violations = cur.execute("PRAGMA foreign_key_check").fetchall()
    check(not fk_violations, f"No FK violations (found {len(fk_violations)})")

    print("\n=== Spot Checks ===")

    # Sonnet 18 first line
    s18 = cur.execute(
        "SELECT first_line FROM sonnets WHERE number = 18"
    ).fetchone()[0]
    check("compare thee to a summer" in s18, f"Sonnet 18: '{s18[:40]}...'")

    # Sonnet 130 first line
    s130 = cur.execute(
        "SELECT first_line FROM sonnets WHERE number = 130"
    ).fetchone()[0]
    check("My mistress" in s130, f"Sonnet 130: '{s130[:40]}...'")

    # Line 13 of Sonnet 18 should be in the couplet
    s18_couplet = cur.execute("""
        SELECT s.stanza_type FROM lines l
        JOIN stanzas s ON l.stanza_id = s.id
        WHERE l.sonnet_id = 18 AND l.line_number = 13
    """).fetchone()[0]
    check(s18_couplet == 'COUPLET', f"Sonnet 18, line 13 in COUPLET (found {s18_couplet})")

    conn.close()

    # Summary
    print(f"\n{'='*50}")
    print(f"ERRORS:   {len(errors)}")
    print(f"WARNINGS: {len(warnings)}")

    if errors:
        print("\nFailed checks:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("\nAll checks passed.")
        sys.exit(0)


if __name__ == '__main__':
    main()
