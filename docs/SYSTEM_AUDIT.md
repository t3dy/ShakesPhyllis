# System Audit — 2026-03-24

## Summary

**Risk Level: MEDIUM-HIGH**
- 0 data integrity errors (validate_db.py passes clean)
- 5 documentation/schema drift issues
- 3 undocumented scripts
- No CHECK constraints on any enum field
- 47 sonnet_groups (documented: 8)
- 71 sonnets enriched (documented: 17)
- 121 PDF files in project root (should be in corpus/)
- Swarm enrichment produced invalid device_ids/mode_ids (caught reactively, not structurally)

## Issue Register

### CRITICAL

| ID | Issue | Impact |
|----|-------|--------|
| C1 | No CHECK constraints on enum fields (addressee, source_method, review_status, confidence, volta_type, couplet_function) | Invalid values can be inserted silently |
| C2 | No pre-load validation gate for enrichment JSON | Swarm output hit FK errors in production; fix was reactive |
| C3 | Swarm agents invented device_ids and mode_ids not in schema | Ontology drifted under LLM pressure instead of editorial control |

### HIGH

| ID | Issue | Impact |
|----|-------|--------|
| H1 | 47 sonnet_groups exist but only 8 documented in ONTOLOGY.md | Major feature completely untracked |
| H2 | 3 scripts exist without PIPELINE.md entry (fix_enrichment.py, seed_essay_unresolved.py, seed_groups_v2.py) | Pipeline not reproducible from docs alone |
| H3 | PHASESTATUS.md claims 17 sonnets enriched; actual count is 71 | Session logging lapsed |
| H4 | Enrichment batch numbering has gaps (no 11, 12, 16-18) | Batches may be in-flight or lost |

### MEDIUM

| ID | Issue | Impact |
|----|-------|--------|
| M1 | 121 PDF files in project root (not in corpus/) | File organization violated |
| M2 | CLAUDE.md says "25 tables"; ONTOLOGY.md says "22 tables"; actual is 21 user tables | Conflicting claims |
| M3 | seed_groups_v2.py does DELETE→INSERT (not idempotent) | PIPELINE.md claims all scripts are idempotent |
| M4 | ROADMAP.md acceptance gates not updated (Phase 2 gate already passed) | Phase status inaccurate |
| M5 | 3 rhetorical devices added to DB during swarm cleanup (POLYPTOTON, RHETORICAL_QUESTION, ALLUSION) without ONTOLOGY.md update | Schema expanded without documentation |

### LOW

| ID | Issue | Impact |
|----|-------|--------|
| L1 | HOWITSBEINGSAVED.md exists with unknown purpose | Clutter |
| L2 | essays table has 1 row (documented as EMPTY) | Minor drift |
| L3 | Swarm temp files (data/swarm_*.json) not cleaned up | 10 temp files in data/ |

## Root Causes

1. **Documentation updates deferred**: Scripts were written and run but docs not updated in the same session.
2. **No structural validation gate**: enrich_sonnets.py trusts its input. When swarm output violated constraints, the failure was discovered at INSERT time, not before.
3. **Ontology drift under LLM pressure**: When agents invented device_ids, the response was to add them to the DB rather than reject them. This violates the principle that the schema is editorially controlled.
4. **Swarm prompts lacked vocabulary lock**: Agents were told "use these device_ids" but not "use ONLY these device_ids — reject anything else."

## Corrections Required

| Fix | Addresses | Priority |
|-----|-----------|----------|
| Add CHECK constraints to init_db.py | C1 | CRITICAL |
| Build validate_enrichment.py (pre-load gate) | C2 | CRITICAL |
| Lock swarm vocabulary in prep_batch.py | C3 | CRITICAL |
| Update ONTOLOGY.md with all 47 groups | H1 | HIGH |
| Add all scripts to PIPELINE.md | H2 | HIGH |
| Update PHASESTATUS.md to actual state | H3 | HIGH |
| Investigate batch gaps (in-flight swarm agents) | H4 | HIGH |
| Move PDFs to corpus/ | M1 | MEDIUM |
| Reconcile table counts in docs | M2 | MEDIUM |
| Make seed_groups_v2.py idempotent | M3 | MEDIUM |
| Update ROADMAP.md gates | M4 | MEDIUM |
| Review 3 added devices for editorial merit | M5 | MEDIUM |

## Data Integrity (PASSING)

```
=== LAYER 1: Core Text ===
  OK: 154 sonnets, 2155 lines, 615 stanzas
  OK: Sonnet 99 (15 lines), Sonnet 126 (12 lines, no couplet)
  OK: All lines have stanza assignments

=== LAYER 2: Characters & Apparatus ===
  OK: 4 characters, 10 candidates, 13 scholars, 15 bibliography
  OK: 47 sonnet_groups, all sonnets have addressee

=== LAYER 3: Rhetoric & Poetics ===
  OK: 24 rhetorical devices (was 20, +3 from swarm, +1 EPIGRAM)
  OK: 8 analytical modes

=== LAYER 4: Enrichment ===
  OK: 71 sonnet_analyses, 416 line_annotations, 360 themes
  OK: 159 character_appearances, 71 directing_notes
  OK: 381 line_devices, 225 sonnet_modes

=== Foreign Key Integrity ===
  OK: 0 FK violations

ERRORS: 0 | WARNINGS: 0
```
