"""
Prepare enrichment batch prompts for LLM agents.
Outputs a self-contained prompt file with locked vocabulary,
sonnet texts, and the expected JSON schema.

Usage:
    python scripts/prep_batch.py 26 34 35 36 37 38 39 --name fym_devotion
    python scripts/prep_batch.py --range 41 54 --name fym_absence
    python scripts/prep_batch.py --remaining --batch-size 10

Output:
    data/batch_prompts/batch_NN_name.prompt.md
    data/batch_prompts/batch_NN_name.template.json
"""

import json
import sqlite3
import os
import sys
import argparse

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, 'db', 'sonnets.db')
PROMPT_DIR = os.path.join(PROJECT_DIR, 'data', 'batch_prompts')
ENRICHMENT_DIR = os.path.join(PROJECT_DIR, 'data', 'enrichment')


def get_enriched_sonnets():
    """Return set of already-enriched sonnet numbers."""
    conn = sqlite3.connect(DB_PATH)
    enriched = {r[0] for r in conn.execute('SELECT sonnet_id FROM sonnet_analyses').fetchall()}
    conn.close()
    return enriched


def get_sonnet_data(sonnet_ids):
    """Fetch sonnet texts, addressees, and group memberships."""
    conn = sqlite3.connect(DB_PATH)
    sonnets = []
    for sid in sorted(sonnet_ids):
        row = conn.execute(
            'SELECT number, first_line, addressee, line_count FROM sonnets WHERE number = ?',
            (sid,)
        ).fetchone()
        if not row:
            print(f"WARNING: Sonnet {sid} not found in DB")
            continue

        lines = conn.execute(
            'SELECT line_number, line_text FROM lines WHERE sonnet_id = ? ORDER BY line_number',
            (sid,)
        ).fetchall()

        groups = conn.execute(
            '''SELECT sg.id, sg.name FROM sonnet_group_members sgm
               JOIN sonnet_groups sg ON sg.id = sgm.group_id
               WHERE sgm.sonnet_id = ?''',
            (sid,)
        ).fetchall()

        sonnets.append({
            'number': row[0],
            'first_line': row[1],
            'addressee': row[2],
            'line_count': row[3],
            'text': '\n'.join(l[1] for l in lines),
            'groups': [f"{g[0]} ({g[1]})" for g in groups],
        })
    conn.close()
    return sonnets


def get_controlled_vocabularies():
    """Fetch all controlled vocabulary lists from DB."""
    conn = sqlite3.connect(DB_PATH)
    devices = [r[0] for r in conn.execute('SELECT id FROM rhetorical_devices ORDER BY id').fetchall()]
    modes = [r[0] for r in conn.execute('SELECT id FROM analytical_modes ORDER BY id').fetchall()]
    conn.close()

    return {
        'device_ids': devices,
        'mode_ids': modes,
        'character_ids': ['FYM', 'DL', 'RP', 'SPEAKER'],
        'volta_types': ['DRAMATIC', 'LOGICAL', 'TONAL', 'IRONIC'],
        'couplet_functions': ['RESOLUTION', 'REVERSAL', 'EXTENSION', 'EPIGRAM', 'IRONIC'],
        'roles': ['ADDRESSED', 'MENTIONED', 'IMPLIED', 'ABSENT_PRESENCE'],
        'prominences': ['PRIMARY', 'SECONDARY'],
    }


def next_batch_number():
    """Find the next available batch number."""
    existing = []
    for d in [ENRICHMENT_DIR, PROMPT_DIR]:
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.startswith('batch_') and '_' in f[6:]:
                    try:
                        num = int(f[6:f.index('_', 6)])
                        existing.append(num)
                    except ValueError:
                        pass
    return max(existing, default=0) + 1


def generate_prompt(batch_num, batch_name, sonnets, vocabs):
    """Generate the agent prompt markdown."""
    lines = []
    lines.append(f"# Enrichment Batch {batch_num}: {batch_name}")
    lines.append("")
    lines.append(f"Enrich {len(sonnets)} sonnets for the Shakespeare Sonnets digital humanities database.")
    lines.append("")

    # Vocabulary lock
    lines.append("## CONTROLLED VOCABULARIES (use ONLY these values)")
    lines.append("")
    lines.append(f"**device_id**: {', '.join(vocabs['device_ids'])}")
    lines.append(f"**mode_id**: {', '.join(vocabs['mode_ids'])}")
    lines.append(f"**character_id**: {', '.join(vocabs['character_ids'])}")
    lines.append(f"**volta_type**: {', '.join(vocabs['volta_types'])}")
    lines.append(f"**couplet_function**: {', '.join(vocabs['couplet_functions'])}")
    lines.append(f"**role**: {', '.join(vocabs['roles'])}")
    lines.append(f"**prominence**: {', '.join(vocabs['prominences'])}")
    lines.append("")
    lines.append("**CRITICAL: Do NOT invent new values. Use ONLY the IDs listed above.**")
    lines.append("If a concept doesn't fit any listed ID, use the closest match.")
    lines.append("")

    # Output format
    lines.append("## OUTPUT FORMAT")
    lines.append("")
    lines.append("Write ONLY valid JSON. No markdown, no commentary.")
    lines.append(f"Write to: data/enrichment/batch_{batch_num:02d}_{batch_name}.json")
    lines.append("")

    # Sonnet texts
    lines.append("## SONNETS TO ENRICH")
    lines.append("")
    for s in sonnets:
        lines.append(f"### Sonnet {s['number']} (addressee: {s['addressee']}, groups: {', '.join(s['groups']) or 'none'})")
        lines.append("```")
        lines.append(s['text'])
        lines.append("```")
        lines.append("")

    return '\n'.join(lines)


def generate_template(batch_num, batch_name, sonnets):
    """Generate the JSON template with pre-filled structure."""
    template = {
        "batch": f"{batch_num:02d}_{batch_name}",
        "description": f"Enrichment batch {batch_num}: {batch_name}",
        "sonnets": []
    }

    for s in sonnets:
        template["sonnets"].append({
            "number": s['number'],
            "analysis": {
                "volta_line": None,
                "volta_type": "",
                "couplet_function": "",
                "argument_summary": "",
                "speaker_stance": "",
                "emotional_arc": "",
                "dramatic_situation": "",
                "subtext": "",
                "analysis_text": ""
            },
            "directing": {
                "scene_setting": "",
                "character_note": "",
                "fym_note": "",
                "dl_note": "",
                "overall_arc": "",
                "key_moments": []
            },
            "line_annotations": [
                {"line_number": ln, "emphasis_words": [], "emotional_note": "", "delivery_note": "", "gloss": "", "commentary": ""}
                for ln in range(1, s['line_count'] + 1)
            ],
            "themes": [],
            "character_appearances": [],
            "line_devices": [],
            "modes": []
        })

    return template


def main():
    parser = argparse.ArgumentParser(description='Prepare enrichment batch prompts')
    parser.add_argument('sonnet_ids', nargs='*', type=int, help='Sonnet numbers to include')
    parser.add_argument('--range', nargs=2, type=int, metavar=('START', 'END'), help='Range of sonnet numbers')
    parser.add_argument('--remaining', action='store_true', help='All unenriched sonnets')
    parser.add_argument('--batch-size', type=int, default=10, help='Sonnets per batch (with --remaining)')
    parser.add_argument('--name', type=str, default='batch', help='Batch name')

    args = parser.parse_args()

    # Determine sonnet IDs
    if args.remaining:
        enriched = get_enriched_sonnets()
        all_ids = sorted(set(range(1, 155)) - enriched)
        # Split into batches
        batches = [all_ids[i:i+args.batch_size] for i in range(0, len(all_ids), args.batch_size)]
        print(f"Found {len(all_ids)} unenriched sonnets → {len(batches)} batches of ≤{args.batch_size}")
        for i, batch_ids in enumerate(batches):
            batch_num = next_batch_number()
            _write_batch(batch_num, f"{args.name}_{i+1}", batch_ids)
        return

    if args.range:
        sonnet_ids = list(range(args.range[0], args.range[1] + 1))
    elif args.sonnet_ids:
        sonnet_ids = args.sonnet_ids
    else:
        parser.print_help()
        return

    batch_num = next_batch_number()
    _write_batch(batch_num, args.name, sonnet_ids)


def _write_batch(batch_num, batch_name, sonnet_ids):
    """Write prompt and template files for a batch."""
    os.makedirs(PROMPT_DIR, exist_ok=True)

    sonnets = get_sonnet_data(sonnet_ids)
    vocabs = get_controlled_vocabularies()

    prompt = generate_prompt(batch_num, batch_name, sonnets, vocabs)
    template = generate_template(batch_num, batch_name, sonnets)

    prompt_path = os.path.join(PROMPT_DIR, f"batch_{batch_num:02d}_{batch_name}.prompt.md")
    template_path = os.path.join(PROMPT_DIR, f"batch_{batch_num:02d}_{batch_name}.template.json")

    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(prompt)

    with open(template_path, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)

    print(f"Batch {batch_num} ({batch_name}): {len(sonnets)} sonnets")
    print(f"  Prompt:   {prompt_path}")
    print(f"  Template: {template_path}")


if __name__ == '__main__':
    main()
