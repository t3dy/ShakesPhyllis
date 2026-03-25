"""
Seed the first essay: Unresolved Questions in Shakespeare's Sonnets.
"""

import sqlite3
import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, 'db', 'sonnets.db')

ESSAY = {
    "slug": "unresolved-questions",
    "title": "What We Still Don't Know: Unresolved Questions in Shakespeare's Sonnets",
    "subtitle": "Textual, historical, and interpretive mysteries that four centuries of scholarship have not settled",
    "abstract": "Despite being the most studied lyric sequence in English, Shakespeare's Sonnets remain riddled with unresolved questions — about their ordering, their addressees, their occasion, and even the meaning of individual words. This essay maps the major open questions and assesses where fresh scholarship or new approaches might break through.",
    "essay_type": "THEMATIC",
    "body_markdown": """# What We Still Don't Know: Unresolved Questions in Shakespeare's Sonnets

## I. The Ordering Problem

The 1609 Quarto, published by Thomas Thorpe, is our only authority for the sonnets' sequence. But was the order Shakespeare's? Thorpe's title page says "never before imprinted" — but two sonnets (138 and 144) had appeared in *The Passionate Pilgrim* (1599) in slightly different versions. Key open questions:

- **Did Shakespeare authorize the publication?** Thorpe's dedication is to "Mr. W.H.," not to Shakespeare. Some scholars (Duncan-Jones) argue the publication was authorized; others (Burrow) are agnostic.
- **Is the 1-126 / 127-152 / 153-154 division authorial?** The break at 126 (the envoi) feels deliberate — a 12-line poem with no couplet, ending the FYM sequence with silence. But the Dark Lady sequence's internal order is less clearly narrative. Were sonnets 127-152 arranged by Shakespeare or by Thorpe?
- **Are there displaced sonnets?** Vendler suspects 37-38 disrupt the flow between 36 and 39 (which share three rhyme sets). Sonnet 145, with its tetrameter and apparent pun on "hate away" / "Hathaway," may be an early poem misplaced in the DL sequence.
- **What about Sonnet 99's 15 lines and 126's 12?** Sonnet 99's extra line may be a printer's error or Shakespeare's deliberate anomaly. Sonnet 126's missing couplet is almost certainly deliberate — the 1609 Quarto prints empty parentheses where lines 13-14 should be — but what exactly did Shakespeare intend by the absence?

## II. The Identity Questions

### Mr. W.H.

Thorpe's dedication to "the only begetter of these ensuing sonnets, Mr. W.H." is the most debated sentence in English literary studies. Options:

- **William Herbert, Earl of Pembroke** — initials match, resisted marriage (procreation sonnets), dedicatee of the First Folio (1623). But would an earl be addressed as "Mr."?
- **Henry Wriothesley, Earl of Southampton** — initials reversed (H.W. not W.H.), dedicatee of *Venus and Adonis* and *Lucrece*, whose dedications grow markedly more intimate. But the reversal is awkward.
- **Sir William Harvey** — Southampton's stepfather, proposed by Leslie Hotson. "Begetter" meaning "procurer of the manuscript" rather than "inspirer."
- **A misprint or fiction** — "Mr. W.H." may be a Thorpe invention, a coded reference, or a simple error.

No new documentary evidence has emerged since the 18th century. Unless a letter or manuscript surfaces, this question may be permanently open.

### The Dark Lady

Candidates remain speculative. A.L. Rowse's identification of Emilia Lanier (based on Simon Forman's manuscripts) is the most detailed but relies on circumstantial evidence. The sonnets describe a woman who is dark-complexioned, musical (128), sexually available, unfaithful, and possibly of lower social status than the Speaker. No candidate matches all criteria perfectly.

**What could settle it:** Discovery of correspondence, diary entries, or legal records linking Shakespeare to a specific woman matching the sonnets' description.

### The Rival Poet

Christopher Marlowe and George Chapman are the leading candidates. The "proud full sail of his great verse" (86) fits Chapman's Homer translation; the supernatural imagery ("spirits taught to write") fits Marlowe's Faustian associations. But the Rival Poet may be a composite or a fiction.

## III. The Dating Problem

We don't know when the sonnets were written. The window is roughly 1592-1604, but:

- **Sonnet 104** mentions "three years" since the relationship began — but three years from when?
- **Sonnet 107** ("The mortal moon hath her eclipse endur'd") may allude to the death of Elizabeth I (1603), the Armada (1588), or an illness of the Queen. Each reading yields a different date.
- **Sonnets 138 and 144** appeared in 1599 — so the sequence was at least partly written by then. But were the *Passionate Pilgrim* versions early drafts or pirated copies?
- **The vocabulary and style** of some sonnets (1-17 especially) suggest early composition, while others (the Dark Lady sequence) feel more mature.

**What could help:** Computational stylometry might narrow the dating by comparing vocabulary and syntax with Shakespeare's dated plays.

## IV. Textual Cruces

Several lines remain genuinely unclear even after four centuries of editorial work:

- **Sonnet 20, line 7:** "A man in hew all Hews in his controwling" — the Quarto's capitalization of "Hews" has prompted theories about a man named Hughes (cf. Oscar Wilde's *Portrait of Mr. W.H.*). Most editors emend to "A man in hue, all hues in his controlling" but the Quarto reading may be deliberate.
- **Sonnet 146, line 2:** "My sinful earth [_____] these rebel powers" — the Quarto repeats "My sinful earth" as the first three words of line 2, which is metrically impossible. The original words were likely lost in typesetting. Emendations include "Fool'd by," "Starv'd by," "Press'd by," and dozens of others. We will never know Shakespeare's words.
- **Sonnet 126's parentheses:** The Quarto prints ( ) ( ) where lines 13-14 should be. Are these authorial (marking the deliberate absence) or compositorial (the printer indicating missing text)?

## V. Interpretive Cruxes

### Is the FYM relationship sexual?

Joseph Pequigney (*Such Is My Love*, 1985) argued yes — the sonnets describe a fully consummated homosexual relationship. The traditional reading sees intense but platonic friendship. Sonnet 20's couplet ("Mine be thy love and thy love's use their treasure") is the crux: does the distinction between "love" and "love's use" hold, or does the sonnet's erotic energy overwhelm it?

This debate is ultimately irresolvable from the text alone — it depends on how one reads the relationship between what the sonnets say and what they mean.

### Is Sonnet 94 praise or blame?

"They that have power to hurt, and will do none" — is this admiration for the FYM's cold restraint or an indictment of his emotional unavailability? William Empson called it the most ambiguous poem in English. The tone refuses to resolve.

### Does Sonnet 116 mean what it says?

"Let me not to the marriage of true minds / Admit impediments" — the most quoted definition of love. But read in sequence after the betrayals of 109-115 and before the self-accusations of 117-121, the absolute idealism looks more desperate than triumphant. Is 116 the sequence's philosophical center or its most elaborate act of denial?

## VI. What New Approaches Might Reveal

- **Digital humanities:** Computational analysis of the sonnets' vocabulary, imagery clusters, and syntactic patterns across the full 154-poem sequence could reveal structural patterns invisible to traditional close reading.
- **Performance studies:** Reading the sonnets aloud — as dramatic utterances by a character in a situation — foregrounds elements that page-based scholarship minimizes: tone, address, the physical act of speaking.
- **Manuscript studies:** If any of Shakespeare's holograph sonnet manuscripts survive (none are currently known), they would transform our understanding of composition, revision, and ordering.
- **Archival research:** New documentary discoveries about Southampton, Pembroke, Emilia Lanier, or the London literary world of the 1590s could illuminate the biographical questions.
- **This project:** By building a database that tracks every line's rhetorical devices, every sonnet's dramatic situation, and every character's appearance across the sequence, we create infrastructure for pattern-recognition at a scale impossible through traditional reading alone.

## VII. Why the Questions Matter

The unresolved questions are not failures of scholarship — they are features of the text. Shakespeare's Sonnets resist resolution because they are built on ambiguity: the Speaker who knows he is deceived and chooses to believe; the FYM whose beauty conceals his heart; the DL whose darkness is both beauty and corruption; the poem that promises immortality while its own form (Sonnet 126) demonstrates poetry's limits.

The questions keep the Sonnets alive. Four hundred years of readers have not exhausted them.
"""
}

DISCUSSED_SONNETS = [20, 36, 37, 38, 39, 86, 94, 99, 104, 107, 109, 116, 117, 126, 128, 138, 144, 145, 146, 152]


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=ON")
    cur = conn.cursor()

    cur.execute("""
        INSERT OR REPLACE INTO essays (slug, title, subtitle, abstract, essay_type, body_markdown,
                                       source_method, review_status, confidence)
        VALUES (?, ?, ?, ?, ?, ?, 'LLM_ASSISTED', 'DRAFT', 'MEDIUM')
    """, (ESSAY["slug"], ESSAY["title"], ESSAY["subtitle"], ESSAY["abstract"],
          ESSAY["essay_type"], ESSAY["body_markdown"]))

    essay_id = cur.lastrowid

    for s in DISCUSSED_SONNETS:
        cur.execute("""
            INSERT OR IGNORE INTO essay_sonnet_links (essay_id, sonnet_id, relevance)
            VALUES (?, ?, 'DISCUSSED')
        """, (essay_id, s))

    conn.commit()
    print(f"Essay inserted: id={essay_id}, slug={ESSAY['slug']}")
    print(f"Linked to {len(DISCUSSED_SONNETS)} sonnets")
    conn.close()


if __name__ == '__main__':
    main()
