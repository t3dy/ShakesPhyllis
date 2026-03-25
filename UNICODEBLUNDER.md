# The Unicode Print Issue on Windows

## What Happened

During the swarm enrichment run, `validate_enrichment.py --fix` crashed with:

```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2192' in position 52:
character maps to <undefined>
```

The character `\u2192` is `→` (a right arrow). The script was printing a fix message like:

```
FIXED: Sonnet 74, line 5: device 'POLYPTOTON' → 'ANAPHORA'
```

## Why It Happened

Windows console (cmd.exe, PowerShell) defaults to a legacy code page — usually **cp1252** (Windows-1252) for Western European locales. This encoding covers ASCII plus accented Latin characters, but it cannot represent:

- `→` (U+2192, rightwards arrow)
- `—` (U+2014, em dash)
- Most non-Latin scripts
- Many common typographic characters

When Python's `print()` tries to write a character that cp1252 can't encode, it raises `UnicodeEncodeError` and the script crashes.

This is a **Windows-specific** problem. On macOS and Linux, the terminal defaults to UTF-8, which can represent all Unicode characters.

## Why It's Insidious

1. **The data was fine.** The JSON files contained valid UTF-8 text. The database stored it correctly. Only the *console output* broke.
2. **It only happens on print.** File I/O with `encoding='utf-8'` works perfectly. The crash occurs only when printing to stdout.
3. **It's intermittent.** Scripts that only print ASCII never trigger it. The bug hides until someone uses an arrow, em dash, or non-Latin character in a print statement.
4. **It's a development-environment bug, not a code bug.** The same script runs fine on Linux or in Windows Terminal with UTF-8 enabled.

## The Fix

Add this near the top of any Python script that might print non-ASCII:

```python
import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
```

This wraps stdout in a UTF-8 encoder. The `errors='replace'` means that if even UTF-8 can't handle something (unlikely), it replaces instead of crashing.

## Alternative Fixes

### Option A: Set the environment variable
```bash
set PYTHONIOENCODING=utf-8
```
This tells Python to use UTF-8 for all I/O. Can be set permanently in system environment variables.

### Option B: Use Windows Terminal
Windows Terminal (the modern replacement for cmd.exe) supports UTF-8 natively. If you're using it, add to your profile:
```json
"profiles": { "defaults": { "commandline": "cmd.exe /K chcp 65001" } }
```

### Option C: Avoid non-ASCII in print statements
Replace `→` with `->`, `—` with `--`, etc. Pragmatic but ugly.

## Lesson for the Project

Every Python script in `scripts/` that prints diagnostic output should include the UTF-8 stdout wrapper. This is a **deterministic layer** concern — the fix belongs in the code, not in the operator's environment, because the pipeline should be reproducible on any Windows machine without manual configuration.

Scripts affected:
- `validate_enrichment.py` (fixed)
- Any future script that prints non-ASCII characters

The enrichment JSON files themselves are always written with `encoding='utf-8'`, so they're safe. The database uses SQLite's native UTF-8 storage, so it's safe. Only console output was vulnerable.
