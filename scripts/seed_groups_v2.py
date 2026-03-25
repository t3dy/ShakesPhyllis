"""
Replace sonnet_groups with comprehensive scholarly groupings.
Based on Duncan-Jones (Arden), Booth, Vendler, Burrow, Kerrigan, Rudenstine,
Stirling, Alden, and consensus traditions.

Expands from 8 thematic groups to 32 sequence-based groups that map
the dramatic arc of the FYM, DL, and Speaker.

Usage:
    python scripts/seed_groups_v2.py
"""

import json
import sqlite3
import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, 'db', 'sonnets.db')

GROUPS = [
    # === FAIR YOUTH SEQUENCE (1-126) ===
    {
        "id": "PROCREATION",
        "name": "Procreation Sonnets",
        "sonnets": list(range(1, 18)),
        "description": "The Speaker urges the FYM to marry and beget children. Argument shifts from procreation to poetry as immortality by Sonnet 15-17. Economic metaphors (usury, debt, legacy) and natural imagery (seasons, distillation).",
        "addressee": "FYM",
        "themes": ["procreation", "beauty", "time", "mortality", "narcissism", "economic_metaphor"]
    },
    {
        "id": "IMMORTALITY_INTRO",
        "name": "Poetry as Immortality: Declaration",
        "sonnets": [18, 19],
        "description": "The Speaker abandons the procreation argument and bets everything on verse. Sonnet 18 is the pivot from children to poetry; Sonnet 19 directly challenges personified Time.",
        "addressee": "FYM",
        "themes": ["immortality", "poetry", "time", "defiance"]
    },
    {
        "id": "EARLY_PRAISE",
        "name": "Early Praise and Love Declarations",
        "sonnets": [20, 21, 22, 23, 24, 25],
        "description": "Individual love compositions. Sonnet 20 ('master-mistress') establishes the gender dynamics. Heart-and-eye conceits, the Speaker's humble station, sincere praise distinguished from conventional flattery.",
        "addressee": "FYM",
        "themes": ["beauty", "love", "gender", "sincerity", "social_station"]
    },
    {
        "id": "FIRST_ABSENCE",
        "name": "First Absence / Separation",
        "sonnets": [26, 27, 28, 29, 30, 31, 32],
        "description": "Written during separation from the FYM. Sleeplessness diptych (27-28), despair-to-salvation (29), memory-as-courtroom (30). The Speaker discovers that the thought of the FYM is enough to redeem all suffering.",
        "addressee": "FYM",
        "themes": ["absence", "longing", "melancholy", "redemption", "memory"]
    },
    {
        "id": "FIRST_BETRAYAL",
        "name": "First Betrayal: Sun and Cloud",
        "sonnets": [33, 34, 35, 36],
        "description": "The FYM commits an unspecified 'sensual fault.' Extended sun/cloud metaphor (33), accusation and tearful atonement (34), the Speaker corrupts himself by forgiving (35), resigned separation (36). The first appearance of the forgiveness-as-self-harm pattern.",
        "addressee": "FYM",
        "themes": ["betrayal", "forgiveness", "alchemy", "self_blame", "separation"]
    },
    {
        "id": "STOLEN_MISTRESS",
        "name": "The Stolen Mistress: Love Triangle",
        "sonnets": [40, 41, 42],
        "description": "Three linked sonnets accusing the FYM of stealing the Speaker's female lover. More severe than the first betrayal. The Speaker attempts absurd logical consolation: 'my friend and I are one.' The hierarchy of grief reveals that losing the FYM hurts more than losing the woman.",
        "addressee": "MIXED",
        "themes": ["betrayal", "jealousy", "self_deception", "sexuality", "forgiveness"]
    },
    {
        "id": "ABSENCE_TRAVEL",
        "name": "Absence and Travel",
        "sonnets": [43, 44, 45, 46, 47, 48, 49, 50, 51, 52],
        "description": "Sustained separation. Four elements diptych (44-45), Eye vs. Heart diptych (46-47), Journey diptych (50-51). The beloved's image sustains the Speaker across distance.",
        "addressee": "FYM",
        "themes": ["absence", "imagination", "travel", "elements", "longing"]
    },
    {
        "id": "ETERNIZING_VERSE",
        "name": "Beauty and the Eternizing Power of Verse",
        "sonnets": [53, 54, 55],
        "description": "The FYM's beauty as archetype and poetry's power to preserve it. Sonnet 55 ('Not marble, nor the gilded monuments') is the most sustained immortality-through-verse claim.",
        "addressee": "FYM",
        "themes": ["immortality", "poetry", "beauty", "time"]
    },
    {
        "id": "SERVANT_MASTER",
        "name": "Servant and Master",
        "sonnets": [56, 57, 58],
        "description": "The Speaker as the FYM's slave. Sonnet 57-58 diptych: the Speaker waits on the FYM's commands, not daring to question his absences. Suppressed jealousy leaks through the obsequious language. Power dynamics at their most explicit.",
        "addressee": "FYM",
        "themes": ["servitude", "power", "jealousy", "irony", "patience"]
    },
    {
        "id": "TIMES_RUIN",
        "name": "Time's Ruin",
        "sonnets": [59, 60, 61, 62, 63, 64, 65],
        "description": "Meditations on time's destruction. 63-65 form a triptych in third-person mode. Sonnet 60 ('Like as the waves') is the great time sonnet. Each moves from universal destruction to the particular threat to the beloved.",
        "addressee": "FYM",
        "themes": ["time", "mortality", "beauty", "decay", "defiance"]
    },
    {
        "id": "WORLD_CORRUPTION",
        "name": "The Former Age: World's Corruption",
        "sonnets": [66, 67, 68],
        "description": "Triptych: 66 lists reasons for despair at the world; 67-68 argue the FYM's beauty is a remnant of a purer age, set against cosmetic artifice and moral decay.",
        "addressee": "FYM",
        "themes": ["corruption", "beauty", "artifice", "despair", "nostalgia"]
    },
    {
        "id": "REPUTATION",
        "name": "The Youth's Reputation",
        "sonnets": [69, 70],
        "description": "The FYM's outward beauty is praised but his inner character is questioned by enemies. The Speaker defends the FYM: beauty always provokes such attacks.",
        "addressee": "FYM",
        "themes": ["reputation", "beauty", "slander", "appearance_vs_reality"]
    },
    {
        "id": "POETS_DEATH",
        "name": "Anticipation of Death",
        "sonnets": [71, 72, 73, 74],
        "description": "Memento mori quartet. 71-72: forget me when I'm dead. 73: the three images of aging (autumn, twilight, fire). 74: my spirit lives on in poetry. The Speaker's mortality makes the FYM's love more precious.",
        "addressee": "FYM",
        "themes": ["mortality", "age", "love", "memory", "poetry"]
    },
    {
        "id": "POETRY_PATRONAGE",
        "name": "Poetry and Patronage",
        "sonnets": [75, 76, 77],
        "description": "Transitional sonnets before the Rival Poet sequence. The Speaker reflects on his own style and its adequacy. Sonnet 77 may accompany the gift of a blank notebook.",
        "addressee": "FYM",
        "themes": ["poetry", "patronage", "style", "sincerity"]
    },
    {
        "id": "RIVAL_POET",
        "name": "The Rival Poet",
        "sonnets": [78, 79, 80, 81, 82, 83, 84, 85, 86],
        "description": "Another poet competes for the FYM's patronage. The Speaker oscillates between false modesty and genuine anxiety. The rival's 'great verse' threatens to displace Shakespeare's plainer style. Candidates: Marlowe, Chapman.",
        "addressee": "FYM",
        "themes": ["rivalry", "patronage", "poetic_style", "anxiety", "envy"]
    },
    {
        "id": "FAREWELL_ESTRANGEMENT",
        "name": "Farewell and Estrangement",
        "sonnets": [87, 88, 89, 90, 91, 92, 93],
        "description": "87: 'Farewell! thou art too dear for my possessing.' 88-90: the Speaker sacrifices himself for the FYM's reputation. 91-93: the FYM's beauty conceals possible falsehood. 93's Eve's apple image is devastating.",
        "addressee": "FYM",
        "themes": ["farewell", "self_worth", "power", "deception", "appearance_vs_reality"]
    },
    {
        "id": "MORAL_WARNINGS",
        "name": "Moral Warnings: Beauty and Corruption",
        "sonnets": [94, 95, 96],
        "description": "94: 'Lilies that fester' — those who have power to hurt. 95: beauty concealing corruption. 96: faults converted to graces. The Speaker warns the FYM that beauty corrupted is worse than plainness.",
        "addressee": "FYM",
        "themes": ["corruption", "beauty", "power", "moral_decay", "appearance_vs_reality"]
    },
    {
        "id": "GREAT_ABSENCE",
        "name": "The Great Absence: Seasons",
        "sonnets": [97, 98, 99],
        "description": "A long separation felt through seasonal imagery. 97: absence felt as winter though it was summer. 98: an April separation. 99: spring flowers accused of stealing from the FYM. (99 has 15 lines — anomalous.)",
        "addressee": "FYM",
        "themes": ["absence", "seasons", "nature", "longing"]
    },
    {
        "id": "MUSE_SILENCE",
        "name": "The Muse's Silence",
        "sonnets": [100, 101, 102, 103],
        "description": "The Speaker has failed to write and deflects blame onto the Muse. 100-101: direct invocations. 102: silence as deeper love. 103: the FYM's face surpasses praise.",
        "addressee": "FYM",
        "themes": ["poetry", "silence", "inspiration", "inadequacy"]
    },
    {
        "id": "THREE_YEARS",
        "name": "Three Years: Reassessment",
        "sonnets": [104, 105, 106, 107, 108],
        "description": "104: 'three years' since they met. 105: love bordering on idolatry. 106: old poets tried to describe such beauty. 107: external crisis resolved. 108: repeated praise as daily prayer.",
        "addressee": "FYM",
        "themes": ["time", "beauty", "constancy", "idolatry", "renewal"]
    },
    {
        "id": "POETS_BETRAYAL",
        "name": "The Poet's Own Betrayal",
        "sonnets": [109, 110, 111, 112],
        "description": "The Speaker confesses his own absences and infidelity — mirroring the FYM's earlier betrayals. 110: straying but love rejuvenated. 111: blames Fortune and his profession (the theater). 112: with the FYM's pity, ignores the world.",
        "addressee": "FYM",
        "themes": ["betrayal", "confession", "theater", "fortune", "forgiveness"]
    },
    {
        "id": "PHILOSOPHICAL_LOVE",
        "name": "Philosophical Love Sonnets",
        "sonnets": [113, 114, 115, 116],
        "description": "113-114: perception diptych (eye vs. mind). 115: growth of love. 116: the definitive definition of love — 'an ever-fixed mark' that is not Time's fool. Read against the betrayals on both sides, 116's absolute idealism is either triumphant or desperate.",
        "addressee": "FYM",
        "themes": ["love", "constancy", "time", "perception", "truth"]
    },
    {
        "id": "POETS_SELF_ACCUSATION",
        "name": "The Poet's Self-Accusation",
        "sonnets": [117, 118, 119, 120, 121],
        "description": "Mirrors the earlier groups where the FYM was at fault. 117: charges answered. 118-119: eating/purging analogies. 120: recalls the FYM's past unkindness as consolation. 121: responds to slurs with cynicism.",
        "addressee": "FYM",
        "themes": ["self_accusation", "betrayal", "reciprocity", "cynicism"]
    },
    {
        "id": "ENVOI_FYM",
        "name": "Final Affirmation and Envoi",
        "sonnets": [122, 123, 124, 125, 126],
        "description": "Closing of the FYM sequence. 122: memory surpasses objects. 123-125: final vows of constancy against Time. 126: the envoi — 12 lines, no closing couplet. Empty brackets represent the FYM's erasure. Nature must surrender him to Time.",
        "addressee": "FYM",
        "themes": ["farewell", "constancy", "time", "mortality", "silence"]
    },
    # === DARK LADY SEQUENCE (127-152) ===
    {
        "id": "ANTI_PETRARCHAN",
        "name": "Anti-Petrarchan: Dark Beauty",
        "sonnets": [127, 128, 129, 130],
        "description": "Introduces the DL and her unconventional beauty. 127: dark beauty as the new standard. 128: the DL at the keyboard. 129: lust as madness and shame. 130: the anti-blazon that is also a genuine love poem.",
        "addressee": "DL",
        "themes": ["anti_petrarchanism", "beauty_standards", "lust", "music", "irony"]
    },
    {
        "id": "TRIANGLE_EXPOSED",
        "name": "The Triangle Exposed: Debt and Forfeit",
        "sonnets": [131, 132, 133, 134],
        "description": "The love triangle becomes explicit. 131-132: conflicted attraction. 133-134: the DL has enslaved the FYM; language of debt, bonds, and forfeit. The three-way entanglement is now inescapable.",
        "addressee": "DL",
        "themes": ["betrayal", "jealousy", "debt", "sexuality", "power"]
    },
    {
        "id": "WILL_SONNETS",
        "name": "The 'Will' Sonnets",
        "sonnets": [135, 136],
        "description": "Elaborate wordplay on 'Will' as desire, sexual appetite, male and female genitalia, and the poet's own name. Sonnet 135 uses 'will' 13+ times. The puns are sexually aggressive and intellectually dazzling.",
        "addressee": "DL",
        "themes": ["wordplay", "sexuality", "identity", "desire"]
    },
    {
        "id": "LUST_DECEPTION",
        "name": "Lust, Deception, and Self-Loathing",
        "sonnets": [137, 138, 139, 140, 141, 142],
        "description": "The DL relationship as mutual deception. 137: why has the Speaker fastened on this woman? 138: mutual lying as the basis of the relationship. 139-142: intensifying shame, the DL's transactional sexuality.",
        "addressee": "DL",
        "themes": ["deception", "self_deception", "lust", "shame", "willful_blindness"]
    },
    {
        "id": "ALLEGORY_SOUL",
        "name": "Allegory, Two Loves, and the Soul",
        "sonnets": [143, 144, 145, 146],
        "description": "143: barnyard allegory. 144: 'Two loves I have of comfort and despair' — the only sonnet naming both FYM and DL. 145: playful (possibly early). 146: 'Poor soul' — the only sonnet focused entirely on the soul's relationship to the body.",
        "addressee": "MIXED",
        "themes": ["allegory", "good_vs_evil", "soul", "mortality", "sexuality"]
    },
    {
        "id": "LOVE_SICKNESS",
        "name": "Love as Sickness",
        "sonnets": [147, 148, 149, 150],
        "description": "Love as fever, disease, blindness. 147: 'My love is as a fever' — desire as illness that reason cannot cure. 148-150: the Speaker's eyes and judgment betrayed by desire.",
        "addressee": "DL",
        "themes": ["disease", "desire", "blindness", "self_disgust", "irrationality"]
    },
    {
        "id": "PERJURY_RECKONING",
        "name": "Perjury and Final Reckoning",
        "sonnets": [151, 152],
        "description": "The DL sequence's bitter conclusion. 151: overt sexuality and the body's betrayal of the mind. 152: perjury and broken vows — 'In loving thee thou know'st I am forsworn.' The darkest point in the entire sequence.",
        "addressee": "DL",
        "themes": ["perjury", "sexuality", "self_disgust", "broken_oaths", "despair"]
    },
    {
        "id": "CUPID_CODA",
        "name": "Cupid / Anacreontic Coda",
        "sonnets": [153, 154],
        "description": "Two variations on a Greek epigram about Cupid's brand quenched in a fountain. Often read as references to venereal disease and Bath's thermal waters. A classical coda standing outside the main narrative.",
        "addressee": "NONE",
        "themes": ["cupid", "mythology", "desire", "bathing", "convention"]
    }
]

PAIRS = [
    {"id": "PAIR_27_28", "name": "Sleeplessness Diptych", "sonnets": [27, 28], "description": "Sleepless nights during separation; night travel and daytime exhaustion."},
    {"id": "PAIR_33_35", "name": "Sun/Cloud/Forgiveness Triptych", "sonnets": [33, 34, 35], "description": "Metaphorical reproach (sun/cloud), accusation, self-blaming forgiveness."},
    {"id": "PAIR_40_42", "name": "Stolen Mistress Triptych", "sonnets": [40, 41, 42], "description": "The FYM takes the Speaker's lover; three attempts at forgiveness, each more strained."},
    {"id": "PAIR_44_45", "name": "Four Elements Diptych", "sonnets": [44, 45], "description": "Earth and water (heavy, slow) vs. air and fire (swift, reaching the beloved)."},
    {"id": "PAIR_46_47", "name": "Eye vs. Heart Diptych", "sonnets": [46, 47], "description": "Legal conceit: eye and heart contest ownership of the beloved's image."},
    {"id": "PAIR_50_51", "name": "Journey Diptych", "sonnets": [50, 51], "description": "Slow horse departing from the beloved; fast horse returning."},
    {"id": "PAIR_57_58", "name": "Servant/Master Diptych", "sonnets": [57, 58], "description": "The Speaker as the FYM's 'sad slave,' waiting on commands."},
    {"id": "PAIR_63_65", "name": "Time's Ruin Triptych", "sonnets": [63, 64, 65], "description": "Third-person meditations on time's destruction. Each moves from universal to particular."},
    {"id": "PAIR_66_68", "name": "World's Corruption Triptych", "sonnets": [66, 67, 68], "description": "World's decay; the FYM as remnant of a purer age."},
    {"id": "PAIR_71_74", "name": "Poet's Death Quartet", "sonnets": [71, 72, 73, 74], "description": "Four linked meditations on the Speaker's mortality and its meaning for the FYM."},
    {"id": "PAIR_113_114", "name": "Perception Diptych", "sonnets": [113, 114], "description": "Whether the beloved's image is truth or delusion."},
    {"id": "PAIR_133_134", "name": "Triangle/Debt Diptych", "sonnets": [133, 134], "description": "The DL has enslaved the FYM; language of bonds and forfeit."},
    {"id": "PAIR_135_136", "name": "'Will' Diptych", "sonnets": [135, 136], "description": "Elaborate puns on 'Will': desire, genitalia, the poet's name."},
    {"id": "PAIR_153_154", "name": "Cupid Diptych", "sonnets": [153, 154], "description": "Two variations on the same Greek epigram."}
]


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=ON")
    cur = conn.cursor()

    # Clear existing groups
    cur.execute("DELETE FROM sonnet_group_members")
    cur.execute("DELETE FROM sonnet_groups")

    # Insert sequence groups
    for g in GROUPS:
        cur.execute("""
            INSERT INTO sonnet_groups (id, name, description, addressee, themes)
            VALUES (?, ?, ?, ?, ?)
        """, (g["id"], g["name"], g["description"], g.get("addressee"),
              json.dumps(g.get("themes", []))))
        for s in g["sonnets"]:
            cur.execute("""
                INSERT OR IGNORE INTO sonnet_group_members (group_id, sonnet_id)
                VALUES (?, ?)
            """, (g["id"], s))

    # Insert paired/linked groups
    for p in PAIRS:
        cur.execute("""
            INSERT INTO sonnet_groups (id, name, description, addressee, themes)
            VALUES (?, ?, ?, ?, ?)
        """, (p["id"], p["name"], p["description"], None, json.dumps([])))
        for s in p["sonnets"]:
            cur.execute("""
                INSERT OR IGNORE INTO sonnet_group_members (group_id, sonnet_id)
                VALUES (?, ?)
            """, (p["id"], s))

    conn.commit()

    # Report
    groups = cur.execute("SELECT COUNT(*) FROM sonnet_groups").fetchone()[0]
    members = cur.execute("SELECT COUNT(*) FROM sonnet_group_members").fetchone()[0]
    # Check coverage: how many unique sonnets appear in at least one group?
    coverage = cur.execute("SELECT COUNT(DISTINCT sonnet_id) FROM sonnet_group_members").fetchone()[0]

    print(f"Sonnet groups: {groups} ({len(GROUPS)} sequences + {len(PAIRS)} pairs)")
    print(f"Group memberships: {members}")
    print(f"Sonnets covered: {coverage}/154")

    conn.close()


if __name__ == '__main__':
    main()
