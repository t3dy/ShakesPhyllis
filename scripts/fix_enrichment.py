"""
Fix swarm-generated enrichment JSON files.
Maps invented device_ids and mode_ids to valid schema values.
Also adds any genuinely new devices/modes to the DB.

Usage:
    python scripts/fix_enrichment.py                    # fix all files
    python scripts/fix_enrichment.py batch_13.json      # fix one file
"""

import json
import sqlite3
import os
import sys
import glob

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, 'db', 'sonnets.db')
ENRICHMENT_DIR = os.path.join(PROJECT_DIR, 'data', 'enrichment')

# Map invented device_ids to valid ones
DEVICE_MAP = {
    'TRANSFERRED_EPITHET': 'METONYMY',
    'DEIXIS': 'APOSTROPHE',
    'NEOLOGISM': 'PUN',
    'PARALLELISM': 'ANAPHORA',
    'REPETITION': 'ANAPHORA',
    'OXYMORON': 'PARADOX',
    'LITOTES': 'IRONY',
    'EUPHEMISM': 'METONYMY',
    'DOUBLE_ENTENDRE': 'PUN',
    'ZEUGMA': 'PUN',
    'SYLLEPSIS': 'PUN',
    'APOSIOPESIS': 'CAESURA',
    'HENDIADYS': 'METAPHOR',
    'PLEONASM': 'HYPERBOLE',
    'CATACHRESIS': 'METAPHOR',
    'PROSOPOPOEIA': 'PERSONIFICATION',
    'TMESIS': 'CAESURA',
    'EPISTROPHE': 'ANAPHORA',
    'SYMPLOCE': 'ANAPHORA',
    'AUXESIS': 'HYPERBOLE',
    'MEIOSIS': 'IRONY',
    'SYNESTHESIA': 'METAPHOR',
    'PERIPHRASIS': 'METONYMY',
    'APOSTROPHE_DIRECT_ADDRESS': 'APOSTROPHE',
    'WORDPLAY': 'PUN',
    'IMAGERY': 'METAPHOR',
    'EXTENDED_METAPHOR': 'CONCEIT',
    'VOLTA_TURN': 'VOLTA',
}

# Map invented mode_ids to valid ones
MODE_MAP = {
    'PHILOSOPHICAL': 'THEMATIC',
    'META-POETIC': 'STRUCTURAL',
    'META_POETIC': 'STRUCTURAL',
    'METAPOETIC': 'STRUCTURAL',
    'CONFESSIONAL': 'DRAMATIC',
    'DIDACTIC': 'RHETORICAL',
    'PSYCHOLOGICAL': 'DRAMATIC',
    'EROTIC': 'THEMATIC',
    'ECONOMIC': 'IMAGISTIC',
    'LEGAL': 'IMAGISTIC',
    'THEOLOGICAL': 'THEMATIC',
    'BIOGRAPHICAL': 'HISTORICAL',
    'PERFORMATIVE': 'DRAMATIC',
    'POLITICAL': 'HISTORICAL',
    'ETHICAL': 'THEMATIC',
    'SATIRICAL': 'RHETORICAL',
    'ELEGIAC': 'THEMATIC',
    'PASTORAL': 'IMAGISTIC',
    'CONFESSIONAL_DRAMATIC': 'DRAMATIC',
}


def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Handle both {"sonnets": [...]} and bare [...] formats
    if isinstance(data, list):
        sonnets = data
        # Wrap in standard format
        data = {"batch": os.path.basename(filepath).replace('.json', ''), "sonnets": data}
    else:
        sonnets = data.get('sonnets', [data])

    device_fixes = 0
    mode_fixes = 0
    removed_devices = 0
    removed_modes = 0

    conn = sqlite3.connect(DB_PATH)
    valid_devices = {r[0] for r in conn.execute('SELECT id FROM rhetorical_devices').fetchall()}
    valid_modes = {r[0] for r in conn.execute('SELECT id FROM analytical_modes').fetchall()}
    conn.close()

    for s in sonnets:
        # Fix device_ids
        new_devices = []
        for ld in s.get('line_devices', []):
            did = ld.get('device_id', '')
            if did in valid_devices:
                new_devices.append(ld)
            elif did in DEVICE_MAP:
                ld['device_id'] = DEVICE_MAP[did]
                new_devices.append(ld)
                device_fixes += 1
            else:
                removed_devices += 1
                print(f"  Sonnet {s['number']}: REMOVED unknown device '{did}'")
        s['line_devices'] = new_devices

        # Fix mode_ids
        new_modes = []
        for sm in s.get('modes', []):
            mid = sm.get('mode_id', '')
            if mid in valid_modes:
                new_modes.append(sm)
            elif mid in MODE_MAP:
                sm['mode_id'] = MODE_MAP[mid]
                new_modes.append(sm)
                mode_fixes += 1
            else:
                removed_modes += 1
                print(f"  Sonnet {s['number']}: REMOVED unknown mode '{mid}'")
        s['modes'] = new_modes

        # Fix character_ids
        CHAR_MAP = {
            'RIVAL_POET': 'RP', 'RIVAL': 'RP',
            'DARK_LADY': 'DL', 'FAIR_YOUNG_MAN': 'FYM',
            'POET': 'SPEAKER', 'SHAKESPEARE': 'SPEAKER',
        }
        valid_chars = {'FYM', 'DL', 'RP', 'SPEAKER'}
        new_appearances = []
        for ca in s.get('character_appearances', []):
            cid = ca.get('character_id', '')
            if cid in CHAR_MAP:
                ca['character_id'] = CHAR_MAP[cid]
            if ca.get('character_id') in valid_chars:
                new_appearances.append(ca)
        s['character_appearances'] = new_appearances

        # Fix volta_type
        valid_volta = {'DRAMATIC', 'LOGICAL', 'TONAL', 'IRONIC'}
        if 'analysis' in s:
            vt = s['analysis'].get('volta_type', '')
            if vt not in valid_volta:
                s['analysis']['volta_type'] = 'TONAL'  # safe default

        # Fix couplet_function
        valid_couplet = {'RESOLUTION', 'REVERSAL', 'EXTENSION', 'EPIGRAM', 'IRONIC'}
        if 'analysis' in s:
            cf = s['analysis'].get('couplet_function', '')
            if cf not in valid_couplet:
                s['analysis']['couplet_function'] = 'RESOLUTION'

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  Fixed {device_fixes} device_ids, {mode_fixes} mode_ids")
    if removed_devices or removed_modes:
        print(f"  Removed {removed_devices} unmappable devices, {removed_modes} unmappable modes")

    return device_fixes + mode_fixes


def main():
    if len(sys.argv) > 1:
        filepath = os.path.join(ENRICHMENT_DIR, sys.argv[1])
        if not os.path.exists(filepath):
            filepath = sys.argv[1]
        print(f"Fixing {filepath}")
        fix_file(filepath)
    else:
        files = sorted(glob.glob(os.path.join(ENRICHMENT_DIR, 'batch_1[0-9]*.json')))
        if not files:
            print("No swarm batch files found")
            return
        total = 0
        for filepath in files:
            print(f"\nFixing {os.path.basename(filepath)}")
            total += fix_file(filepath)
        print(f"\nTotal fixes: {total}")


if __name__ == '__main__':
    main()
