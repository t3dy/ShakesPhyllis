"""
Parse Project Gutenberg Shakespeare's Sonnets into structured JSON.
One-time utility script — not part of the main pipeline.

Input:  data/gutenberg_sonnets.txt
Output: data/sonnet_texts.json
"""

import json
import re
import os

ROMAN_TO_INT = {}
# Build Roman numeral lookup for I-CLIV (1-154)
def roman_to_int(s):
    vals = {'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000}
    total = 0
    for i, c in enumerate(s):
        if i + 1 < len(s) and vals[c] < vals[s[i+1]]:
            total -= vals[c]
        else:
            total += vals[c]
    return total

def parse_sonnets(filepath):
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        text = f.read()

    # Find the start marker
    start_marker = "*** START OF THE PROJECT GUTENBERG EBOOK"
    end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK"

    start_idx = text.find(start_marker)
    end_idx = text.find(end_marker)

    if start_idx == -1 or end_idx == -1:
        raise ValueError("Could not find Gutenberg markers")

    # Get content between markers
    content = text[start_idx:end_idx]

    # Split into lines
    lines = content.split('\n')

    sonnets = []
    current_number = None
    current_lines = []

    # Roman numeral pattern: a line that is ONLY a Roman numeral (I through CLIV)
    roman_pattern = re.compile(r'^([IVXLC]+)$')

    for line in lines:
        stripped = line.strip()

        # Check if this line is a Roman numeral (sonnet header)
        match = roman_pattern.match(stripped)
        if match:
            candidate = match.group(1)
            try:
                num = roman_to_int(candidate)
                if 1 <= num <= 154:
                    # Save previous sonnet if exists
                    if current_number is not None and current_lines:
                        sonnets.append({
                            'number': current_number,
                            'lines': current_lines
                        })
                    current_number = num
                    current_lines = []
                    continue
            except (ValueError, KeyError):
                pass

        # If we're in a sonnet, collect non-empty lines
        if current_number is not None and stripped:
            # Skip the title lines at the top
            if stripped in ('THE SONNETS', 'by William Shakespeare'):
                continue
            current_lines.append(stripped)

    # Don't forget the last sonnet
    if current_number is not None and current_lines:
        sonnets.append({
            'number': current_number,
            'lines': current_lines
        })

    return sonnets


def build_json(sonnets):
    """Build the final JSON structure."""
    result = []
    for s in sonnets:
        # Some Gutenberg sonnets have the couplet indented with spaces
        # Normalize: strip all lines
        lines = [l.strip() for l in s['lines']]

        # Validate: should be 14 lines
        if len(lines) != 14:
            print(f"WARNING: Sonnet {s['number']} has {len(lines)} lines: {lines[:3]}...")

        result.append({
            'number': s['number'],
            'first_line': lines[0] if lines else '',
            'lines': lines,
            'line_count': len(lines),
            'source': '1609_QUARTO_GUTENBERG'
        })

    return result


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    input_path = os.path.join(project_dir, 'data', 'gutenberg_sonnets.txt')
    output_path = os.path.join(project_dir, 'data', 'sonnet_texts.json')

    print(f"Parsing {input_path}...")
    sonnets = parse_sonnets(input_path)
    print(f"Found {len(sonnets)} sonnets")

    result = build_json(sonnets)

    # Sort by number
    result.sort(key=lambda s: s['number'])

    # Check for gaps
    numbers = {s['number'] for s in result}
    missing = [n for n in range(1, 155) if n not in numbers]
    if missing:
        print(f"MISSING sonnets: {missing}")

    # Check line counts
    bad = [s for s in result if s['line_count'] != 14]
    if bad:
        for s in bad:
            print(f"  Sonnet {s['number']}: {s['line_count']} lines")
    else:
        print("All sonnets have exactly 14 lines")

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Written to {output_path}")
    print(f"Total lines: {sum(s['line_count'] for s in result)}")


if __name__ == '__main__':
    main()
