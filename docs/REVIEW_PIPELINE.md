# Review Pipeline — Provenance Promotion

## Status Progression

```
DRAFT  →  REVIEWED  →  VERIFIED
```

Promotion is forward-only. No demotion. No skipping.

## Promotion Criteria

### DRAFT → REVIEWED

**Who:** Human reviewer (the project owner) or a sequential review pass by Claude with explicit user approval.

**Criteria:**
- Analysis is factually accurate (no invented citations, correct line references)
- Rhetorical devices correctly identified (metaphor is metaphor, not simile)
- Dramatic situation consistent with sequence position
- No contradictions with established readings of adjacent sonnets
- Directing notes are performable (not vague abstractions)
- All controlled vocabulary values are valid

**Process:**
1. Read the analysis alongside the sonnet text
2. Check device identifications against the actual lines
3. Verify character appearances match the text
4. Mark as REVIEWED if criteria met
5. Log the review in PHASESTATUS.md

### REVIEWED → VERIFIED

**Who:** Human expert only. Not automated. Not LLM-promotable.

**Criteria:**
- Cross-referenced with at least one scholarly source (Vendler, Booth, Duncan-Jones, etc.)
- Dramatic arc consistent across the full subsequence (not just adjacent sonnets)
- Performance notes tested against actual reading/recording
- No remaining factual errors

**Process:**
1. Compare against scholarly edition annotations
2. Read aloud using directing notes (the audiobook test)
3. Mark as VERIFIED only if both checks pass
4. Log the verification with source citation

## Rules

1. LLM output ALWAYS enters as DRAFT / MEDIUM confidence
2. No automated promotion from DRAFT to REVIEWED
3. No promotion from REVIEWED to VERIFIED without human expert
4. VERIFIED data is never overwritten — only appended with discrepancy notes
5. Batch promotions are allowed (e.g., "reviewed sonnets 1-17") but must be logged

## Database Fields

All enrichment tables carry:

| Field | Type | Default |
|-------|------|---------|
| `source_method` | TEXT | 'LLM_ASSISTED' |
| `review_status` | TEXT | 'DRAFT' |
| `confidence` | TEXT | 'MEDIUM' |

## Promotion SQL

```sql
-- Promote a single sonnet's analysis from DRAFT to REVIEWED
UPDATE sonnet_analyses SET review_status = 'REVIEWED' WHERE sonnet_id = 18;

-- Promote a batch
UPDATE sonnet_analyses SET review_status = 'REVIEWED' WHERE sonnet_id IN (1,2,3,4,5);

-- Check what's still DRAFT
SELECT sa.sonnet_id, s.first_line FROM sonnet_analyses sa
JOIN sonnets s ON s.number = sa.sonnet_id
WHERE sa.review_status = 'DRAFT' ORDER BY sa.sonnet_id;
```
