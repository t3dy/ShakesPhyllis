"""
Pre-load validation gate for enrichment JSON files.
Runs BEFORE enrich_sonnets.py. Rejects invalid data with clear errors.
Fixes mappable issues (invented device_ids, mode_ids, character_ids).

Usage:
    python scripts/validate_enrichment.py                    # validate all
    python scripts/validate_enrichment.py batch_13.json      # validate one
    python scripts/validate_enrichment.py --fix              # validate and fix all
    python scripts/validate_enrichment.py --fix batch_13.json  # validate and fix one

Exit codes:
    0 = all valid (or all fixed)
    1 = validation errors remain after fix attempt
"""

import json
import sqlite3
import os
import sys
import glob
import io

# Fix Windows console encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, 'db', 'sonnets.db')
ENRICHMENT_DIR = os.path.join(PROJECT_DIR, 'data', 'enrichment')

# --- Controlled Vocabularies ---

VALID_VOLTA_TYPES = {'DRAMATIC', 'LOGICAL', 'TONAL', 'IRONIC'}
VALID_COUPLET_FUNCTIONS = {'RESOLUTION', 'REVERSAL', 'EXTENSION', 'EPIGRAM', 'IRONIC'}
VALID_ROLES = {'ADDRESSED', 'MENTIONED', 'IMPLIED', 'ABSENT_PRESENCE'}
VALID_PROMINENCES = {'PRIMARY', 'SECONDARY'}

# --- Mapping tables for LLM-invented values ---

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
    'INTERTEXTUAL': 'ALLUSION',
    'INTERTEXTUALITY': 'ALLUSION',
}

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

CHAR_MAP = {
    'RIVAL_POET': 'RP', 'RIVAL': 'RP',
    'DARK_LADY': 'DL', 'FAIR_YOUNG_MAN': 'FYM',
    'POET': 'SPEAKER', 'SHAKESPEARE': 'SPEAKER',
}


def load_valid_sets():
    """Load valid IDs from the database."""
    conn = sqlite3.connect(DB_PATH)
    devices = {r[0] for r in conn.execute('SELECT id FROM rhetorical_devices').fetchall()}
    modes = {r[0] for r in conn.execute('SELECT id FROM analytical_modes').fetchall()}
    chars = {r[0] for r in conn.execute('SELECT id FROM characters').fetchall()}
    sonnet_ids = {r[0] for r in conn.execute('SELECT number FROM sonnets').fetchall()}
    # Build line count map
    line_counts = {}
    for row in conn.execute('SELECT sonnet_id, MAX(line_number) FROM lines GROUP BY sonnet_id'):
        line_counts[row[0]] = row[1]
    conn.close()
    return devices, modes, chars, sonnet_ids, line_counts


def validate_sonnet(s, valid_devices, valid_modes, valid_chars, sonnet_ids, line_counts, fix=False):
    """Validate one sonnet's enrichment data. Returns (errors, warnings, fixes)."""
    errors = []
    warnings = []
    fixes = []
    num = s.get('number')

    if num is None:
        errors.append("Missing 'number' field")
        return errors, warnings, fixes

    if num not in sonnet_ids:
        errors.append(f"Sonnet {num} does not exist in database")
        return errors, warnings, fixes

    max_line = line_counts.get(num, 14)

    # --- Validate analysis ---
    if 'analysis' in s:
        a = s['analysis']
        vt = a.get('volta_type', '')
        if vt and vt not in VALID_VOLTA_TYPES:
            if fix:
                a['volta_type'] = 'TONAL'
                fixes.append(f"Sonnet {num}: volta_type '{vt}' → 'TONAL'")
            else:
                errors.append(f"Sonnet {num}: invalid volta_type '{vt}'")

        cf = a.get('couplet_function', '')
        if cf and cf not in VALID_COUPLET_FUNCTIONS:
            if fix:
                a['couplet_function'] = 'RESOLUTION'
                fixes.append(f"Sonnet {num}: couplet_function '{cf}' → 'RESOLUTION'")
            else:
                errors.append(f"Sonnet {num}: invalid couplet_function '{cf}'")

        vl = a.get('volta_line')
        if vl is not None and (not isinstance(vl, int) or vl < 1 or vl > max_line):
            errors.append(f"Sonnet {num}: volta_line {vl} out of range 1-{max_line}")

        if not a.get('analysis_text'):
            warnings.append(f"Sonnet {num}: missing analysis_text")

    # --- Validate line_annotations ---
    for la in s.get('line_annotations', []):
        ln = la.get('line_number')
        if ln is None or not isinstance(ln, int) or ln < 1 or ln > max_line:
            errors.append(f"Sonnet {num}: annotation line_number {ln} out of range 1-{max_line}")

    # --- Validate line_devices ---
    new_devices = []
    for ld in s.get('line_devices', []):
        ln = ld.get('line_number')
        if ln is None or not isinstance(ln, int) or ln < 1 or ln > max_line:
            errors.append(f"Sonnet {num}: device line_number {ln} out of range 1-{max_line}")
            continue

        did = ld.get('device_id', '')
        if did in valid_devices:
            new_devices.append(ld)
        elif did in DEVICE_MAP:
            if fix:
                old = did
                ld['device_id'] = DEVICE_MAP[did]
                new_devices.append(ld)
                fixes.append(f"Sonnet {num}, line {ln}: device '{old}' → '{DEVICE_MAP[old]}'")
            else:
                errors.append(f"Sonnet {num}, line {ln}: invalid device_id '{did}' (mappable to '{DEVICE_MAP[did]}')")
                new_devices.append(ld)
        else:
            if fix:
                fixes.append(f"Sonnet {num}, line {ln}: REMOVED unknown device '{did}'")
            else:
                errors.append(f"Sonnet {num}, line {ln}: unknown device_id '{did}' (no mapping)")
    if fix:
        s['line_devices'] = new_devices

    # --- Validate modes ---
    new_modes = []
    for sm in s.get('modes', []):
        mid = sm.get('mode_id', '')
        if mid in valid_modes:
            new_modes.append(sm)
        elif mid in MODE_MAP:
            if fix:
                old = mid
                sm['mode_id'] = MODE_MAP[mid]
                new_modes.append(sm)
                fixes.append(f"Sonnet {num}: mode '{old}' → '{MODE_MAP[old]}'")
            else:
                errors.append(f"Sonnet {num}: invalid mode_id '{mid}' (mappable to '{MODE_MAP[mid]}')")
                new_modes.append(sm)
        else:
            if fix:
                fixes.append(f"Sonnet {num}: REMOVED unknown mode '{mid}'")
            else:
                errors.append(f"Sonnet {num}: unknown mode_id '{mid}' (no mapping)")
    if fix:
        s['modes'] = new_modes

    # --- Validate character_appearances ---
    new_appearances = []
    for ca in s.get('character_appearances', []):
        cid = ca.get('character_id', '')
        if cid in CHAR_MAP:
            if fix:
                ca['character_id'] = CHAR_MAP[cid]
                fixes.append(f"Sonnet {num}: character '{cid}' → '{CHAR_MAP[cid]}'")
            cid = CHAR_MAP.get(cid, cid)

        if cid not in valid_chars:
            if fix:
                fixes.append(f"Sonnet {num}: REMOVED unknown character '{ca.get('character_id')}'")
            else:
                errors.append(f"Sonnet {num}: invalid character_id '{ca.get('character_id')}'")
            continue

        role = ca.get('role', '')
        if role and role not in VALID_ROLES:
            warnings.append(f"Sonnet {num}: unusual role '{role}' for {cid}")

        new_appearances.append(ca)
    if fix:
        s['character_appearances'] = new_appearances

    # --- Validate themes ---
    for t in s.get('themes', []):
        p = t.get('prominence', '')
        if p and p not in VALID_PROMINENCES:
            if fix:
                t['prominence'] = 'SECONDARY'
                fixes.append(f"Sonnet {num}: theme prominence '{p}' → 'SECONDARY'")
            else:
                warnings.append(f"Sonnet {num}: unusual theme prominence '{p}'")

    return errors, warnings, fixes


def validate_file(filepath, fix=False):
    """Validate an enrichment JSON file. Returns (errors, warnings, fixes)."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"], [], []

    # Handle both {"sonnets": [...]} and bare [...] formats
    if isinstance(data, list):
        sonnets = data
        data = {"batch": os.path.basename(filepath).replace('.json', ''), "sonnets": data}
    else:
        sonnets = data.get('sonnets', [data])

    valid_devices, valid_modes, valid_chars, sonnet_ids, line_counts = load_valid_sets()

    all_errors = []
    all_warnings = []
    all_fixes = []

    for s in sonnets:
        errs, warns, fxs = validate_sonnet(
            s, valid_devices, valid_modes, valid_chars, sonnet_ids, line_counts, fix=fix
        )
        all_errors.extend(errs)
        all_warnings.extend(warns)
        all_fixes.extend(fxs)

    if fix and all_fixes:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    return all_errors, all_warnings, all_fixes


def main():
    fix = '--fix' in sys.argv
    args = [a for a in sys.argv[1:] if a != '--fix']

    if args:
        filepath = os.path.join(ENRICHMENT_DIR, args[0])
        if not os.path.exists(filepath):
            filepath = args[0]
        files = [filepath]
    else:
        files = sorted(glob.glob(os.path.join(ENRICHMENT_DIR, 'batch_*.json')))

    if not files:
        print("No enrichment files found")
        return

    total_errors = 0
    total_warnings = 0
    total_fixes = 0

    for filepath in files:
        name = os.path.basename(filepath)
        errors, warnings, fixes = validate_file(filepath, fix=fix)

        status = "PASS" if not errors else "FAIL"
        print(f"\n{name}: {status}")

        for f in fixes:
            print(f"  FIXED: {f}")
        for e in errors:
            print(f"  ERROR: {e}")
        for w in warnings:
            print(f"  WARN:  {w}")

        total_errors += len(errors)
        total_warnings += len(warnings)
        total_fixes += len(fixes)

    print(f"\n{'='*50}")
    print(f"Files:    {len(files)}")
    print(f"Errors:   {total_errors}")
    print(f"Warnings: {total_warnings}")
    if fix:
        print(f"Fixes:    {total_fixes}")

    sys.exit(1 if total_errors > 0 else 0)


if __name__ == '__main__':
    main()
