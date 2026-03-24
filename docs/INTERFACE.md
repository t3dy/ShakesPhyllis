# Interface — Shakespeare Sonnets Site

SHWEP-style dark academic theme. Vanilla HTML/CSS/JS, no frameworks.

---

## Navigation (consistent across all pages)

```
Home | Sonnets | Analyses | Directing | Contexts | Essays | Characters | Scholars | Glossary | Timeline | About
```

The **Sonnets** tab links to the master index. **Analyses**, **Directing**, **Contexts** link to filtered views of the same index. **Essays** links to the freestanding essay collection.

---

## Page Types

### 1. Homepage (`/index.html`)

- Project title and tagline
- Brief explanation of the four content pillars
- Featured sonnet (rotating or curated)
- Quick stats: 154 sonnets, N analyses, N directing pages, N essays
- Links to FYM and DL candidate overview pages

### 2. Sonnet Index (`/sonnets/index.html`)

- All 154 sonnets in a filterable grid/list
- Filters: by sequence group (Procreation, FYM Beauty, DL, etc.), by addressee (FYM/DL/Both), by thematic thread
- Each card shows: sonnet number, first line, addressee badge, sequence group tag
- Links to all three per-sonnet content types (Analysis, Directing, Context)

### 3. Sonnet Analysis Page (`/analyses/sonnet-NNN.html`)

**Layout:** Sonnet text LEFT (40%), analysis RIGHT (60%).

**Left panel:**
- Full 14-line text with line numbers
- Structural markers: Q1, Q2, Q3, COUPLET labels
- Highlighted rhetorical figures (color-coded by category: trope, scheme, sound, structure)
- Volta marker

**Right panel (assembled by build_analysis.py):**
1. **Overview** — 2-3 sentence summary: what this sonnet is about, who it addresses, where it sits in the sequence
2. **Primary Analysis** — Focused treatment of the priority-1 analysis mode (from sonnet_analysis_modes). Verbatim line citations. Explanation of how the dominant device/mode works.
3. **FYM/DL Dynamics** — How this sonnet relates to the love triangle. Character roles and evidence. Addressee shifts if any.
4. **Scholarly Perspectives** — Summarized interpretations from corpus scholars. Page references.
5. **Close Reading Notes** — Section-by-section (Q1, Q2, Q3, Couplet) rhetorical function and imagery.
6. **Glossary** — Archaic/specialized terms with definitions in context.

**Navigation:** Prev/Next sonnet. Link to same sonnet's Directing and Context pages.

### 4. Sonnet Directing Page (`/directing/sonnet-NNN.html`)

**Layout:** Line-by-line format. Each line of the sonnet gets its own row.

**Per-line content:**
| Line # | Text | Meter | Directing Note |
|--------|------|-------|----------------|
| 1 | "From fairest creatures we desire increase," | u/u/u/u/u/ (regular) | Declarative opening. Emphasize "fairest" — sets the tone of admiration. Start warm, not pleading. |
| ... | ... | ... | ... |

**Additional sections:**
- **Emotional Arc** — How the feeling shifts across Q1→Q2→Q3→Couplet
- **The Volta** — How to handle the turn: pause length, tone shift, physical gesture
- **Addressee Notes** — Who the speaker is talking to; if FYM or DL, what this means for stance and intimacy
- **Staging Suggestions** — Optional: physical space, movement, eye contact
- **Metrical Variations** — Flagged lines where the meter departs from iambic pentameter and why that matters for delivery

**Navigation:** Prev/Next sonnet. Link to same sonnet's Analysis and Context pages.

### 5. Sonnet Context Page (`/contexts/sonnet-NNN.html`)

**Sections:**
1. **Publication** — Where this sonnet appeared in the 1609 Quarto; Benson's 1640 rearrangement (if applicable)
2. **Sequence Position** — Which group it belongs to, what the narrative arc of that group is
3. **The Fair Young Man** — If FYM-addressed: which candidates fit, what evidence this specific sonnet provides. Link to FYM candidate reference page.
4. **The Dark Lady** — If DL-addressed: same treatment. Link to DL candidate reference page.
5. **Shakespeare's World** — Relevant biographical context: dates, patron relationships, theatrical career, personal life
6. **Literary Context** — Contemporary sonnet sequences (Sidney's Astrophil, Daniel's Delia, Spenser's Amoretti), Petrarchan tradition, English sonnet innovation
7. **Critical Reception** — How this sonnet has been read across centuries

**Navigation:** Prev/Next sonnet. Link to same sonnet's Analysis and Directing pages.

### 6. Essay Page (`/essays/SLUG.html`)

**Freestanding thematic essays.** Not keyed to individual sonnets.

**Planned essay topics:**
- The Fair Young Man: Identity and Evidence
- The Dark Lady: Identity and Evidence
- The Speaker's Sexuality
- Irony in the Sonnets
- Sonnet Structure: The Shakespearean Form
- The Procreation Sonnets (1-17)
- The Rival Poet (78-86)
- Time and Mortality
- Beauty and Decay
- Poetic Immortality ("So long as men can breathe...")
- Economic Language in the Sonnets
- Alchemy and the Sonnets

**Format per essay:**
- Title + subtitle
- Abstract/summary (2-3 sentences)
- Body with section headings
- Verbatim sonnet citations with line numbers
- Scholarly references with page numbers
- AI-generated content banner (if applicable)

### 7. Essay Index (`/essays/index.html`)

- Grid of essay cards with title, abstract, and topic tags
- Grouped by theme cluster

### 8. Character/Candidate Pages (`/characters/SLUG.html`)

**One page per major candidate:**
- Henry Wriothesley, 3rd Earl of Southampton
- William Herbert, 3rd Earl of Pembroke
- Willie Hughes (Wilde's candidate)
- Emilia Lanier/Bassano
- Mary Fitton
- Lucy Negro
- The Skeptical View (no real person)

**Format per candidate:**
- Biographical summary
- Evidence for identification (which sonnets, what details)
- Evidence against
- Key scholars who argue for/against
- Links to relevant sonnets

### 9. Scholar Pages (`/scholar/SLUG.html`)

- Scholar profile: bio, specialization, key works
- Which sonnets they've written about
- Their major interpretive contributions

### 10. Glossary (`/glossary/index.html` + `/glossary/SLUG.html`)

- Terms grouped by category (ARCHAIC, LEGAL, ECONOMIC, SEXUAL, RELIGIOUS, LITERARY)
- Each term links to the sonnets where it appears

### 11. Timeline (`/timeline.html`)

- Vertical timeline: 1592-present
- Events: composition dates, 1609 Quarto, Benson 1640, major editions, critical milestones

### 12. About (`/about.html`)

- Project description and goals
- Methodology (how the database was built, what's deterministic vs LLM)
- Provenance model explanation
- AI disclosure
- Collaboration credit (the Will pitch)
- Link to GitHub repository

---

## SHWEP Dark Academic Theme

**Color palette:**
```css
--bg: #1a1a2e;              /* Deep navy/charcoal */
--bg-card: #16213e;         /* Slightly lighter card background */
--text: #e0d8c8;            /* Warm cream text */
--text-muted: #8a8278;      /* Muted brown-grey */
--accent: #c9a96e;          /* Gold accent */
--accent-light: #e8d5a3;    /* Light gold */
--header-bg: #0f0f1a;       /* Near-black header */
--header-text: #e0d8c8;     /* Cream header text */
--border: #2a2a4a;          /* Subtle border */
--link: #c9a96e;            /* Gold links */
--link-hover: #e8d5a3;      /* Lighter gold on hover */
```

**Typography:**
- Body: Serif font (Georgia, 'Times New Roman', serif)
- Headings: Small-caps serif
- Sonnet text: Slightly larger, distinguished typeface
- Line numbers: Monospace, muted color

**Components:**
- `.sonnet-text` — Dedicated styling for sonnet display with line numbers
- `.analysis-panel` — Side panel for scholarly apparatus
- `.directing-table` — Line-by-line table with meter and notes
- `.context-section` — Expandable sections for historical context
- `.candidate-card` — FYM/DL candidate summary cards
- `.confidence-badge` — Color-coded: HIGH (gold), MEDIUM (silver), LOW (bronze)
- `.addressee-badge` — FYM (blue-toned), DL (warm-toned), BOTH (split), UNKNOWN (grey)
- `.ai-banner` — Prominent AI-generated content disclosure
