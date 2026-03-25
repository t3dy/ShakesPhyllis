"""
Generate the Shakespeare Sonnets data visualization dashboard.
Queries all visualization data from the SQLite database and outputs
a static HTML page with Chart.js charts in the SHWEP dark academic theme.

Usage:
    python scripts/build_visualizations.py

Output:
    site/visualizations/index.html
"""

import json
import sqlite3
import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, 'db', 'sonnets.db')
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'site', 'visualizations')


def query_all_data():
    """Query all visualization data from the database."""
    conn = sqlite3.connect(DB_PATH)

    data = {}

    # 1. Sequence arc
    data['sequence_arcs'] = conn.execute('''
        SELECT sequence_arc_state, COUNT(*), MIN(number), MAX(number)
        FROM sonnets GROUP BY sequence_arc_state ORDER BY MIN(number)
    ''').fetchall()

    # 2. Addressee distribution
    data['addressees'] = conn.execute('''
        SELECT addressee, COUNT(*) FROM sonnets GROUP BY addressee ORDER BY COUNT(*) DESC
    ''').fetchall()

    # 3. Theme distribution (top 25)
    data['themes'] = conn.execute('''
        SELECT theme, COUNT(*) as cnt,
               SUM(CASE WHEN prominence='PRIMARY' THEN 1 ELSE 0 END) as primary_cnt,
               SUM(CASE WHEN prominence='SECONDARY' THEN 1 ELSE 0 END) as secondary_cnt
        FROM sonnet_themes GROUP BY theme ORDER BY cnt DESC LIMIT 25
    ''').fetchall()

    # Total unique themes
    data['total_themes'] = conn.execute('SELECT COUNT(DISTINCT theme) FROM sonnet_themes').fetchone()[0]

    # 4. Theme × addressee heatmap
    data['theme_addressee'] = conn.execute('''
        SELECT s.addressee, st.theme, COUNT(*)
        FROM sonnet_themes st JOIN sonnets s ON s.number = st.sonnet_id
        WHERE st.theme IN (
            SELECT theme FROM sonnet_themes GROUP BY theme ORDER BY COUNT(*) DESC LIMIT 10
        )
        GROUP BY s.addressee, st.theme ORDER BY s.addressee
    ''').fetchall()

    # 5. Device frequency
    data['devices'] = conn.execute('''
        SELECT device_id, COUNT(*) FROM line_devices GROUP BY device_id ORDER BY COUNT(*) DESC
    ''').fetchall()

    # 6. Device density histogram
    data['device_density'] = conn.execute('''
        SELECT device_count, COUNT(*) FROM (
            SELECT COUNT(*) as device_count
            FROM line_devices ld JOIN lines l ON l.id = ld.line_id
            GROUP BY l.sonnet_id
        ) GROUP BY device_count ORDER BY device_count
    ''').fetchall()

    # Device density outliers
    data['device_outliers'] = conn.execute('''
        SELECT l.sonnet_id, s.first_line, COUNT(*) as cnt
        FROM line_devices ld
        JOIN lines l ON l.id = ld.line_id
        JOIN sonnets s ON s.number = l.sonnet_id
        GROUP BY l.sonnet_id ORDER BY cnt DESC LIMIT 5
    ''').fetchall()

    # 7. Volta types
    data['volta_types'] = conn.execute('''
        SELECT volta_type, COUNT(*) FROM sonnet_analyses GROUP BY volta_type ORDER BY COUNT(*) DESC
    ''').fetchall()

    # Couplet functions
    data['couplet_functions'] = conn.execute('''
        SELECT couplet_function, COUNT(*) FROM sonnet_analyses GROUP BY couplet_function ORDER BY COUNT(*) DESC
    ''').fetchall()

    # 8. Character presence by sonnet (for stream chart)
    data['character_stream'] = conn.execute('''
        SELECT ca.sonnet_id, ca.character_id, ca.role
        FROM character_appearances ca ORDER BY ca.sonnet_id
    ''').fetchall()

    # 9. Mode priorities
    data['modes'] = conn.execute('''
        SELECT mode_id, ROUND(AVG(priority), 2), COUNT(*) FROM sonnet_modes
        GROUP BY mode_id ORDER BY AVG(priority) DESC
    ''').fetchall()

    # 10. Group memberships
    data['groups'] = conn.execute('''
        SELECT sg.id, sg.name, COUNT(sgm.sonnet_id) as cnt
        FROM sonnet_groups sg LEFT JOIN sonnet_group_members sgm ON sg.id = sgm.group_id
        GROUP BY sg.id ORDER BY cnt DESC LIMIT 25
    ''').fetchall()

    # Group overlap (sonnets in multiple groups)
    data['group_overlap'] = conn.execute('''
        SELECT sonnet_id, COUNT(*) as group_count
        FROM sonnet_group_members GROUP BY sonnet_id HAVING group_count > 1
        ORDER BY group_count DESC LIMIT 10
    ''').fetchall()

    # 11. Annotation density by line position
    data['annotation_density'] = conn.execute('''
        SELECT l.line_number, COUNT(la.line_id) as cnt
        FROM lines l LEFT JOIN line_annotations la ON l.id = la.line_id
        GROUP BY l.line_number ORDER BY l.line_number
    ''').fetchall()

    # Summary stats
    data['stats'] = {
        'sonnets': conn.execute('SELECT COUNT(*) FROM sonnets').fetchone()[0],
        'lines': conn.execute('SELECT COUNT(*) FROM lines').fetchone()[0],
        'analyses': conn.execute('SELECT COUNT(*) FROM sonnet_analyses').fetchone()[0],
        'annotations': conn.execute('SELECT COUNT(*) FROM line_annotations').fetchone()[0],
        'devices': conn.execute('SELECT COUNT(*) FROM line_devices').fetchone()[0],
        'themes': conn.execute('SELECT COUNT(*) FROM sonnet_themes').fetchone()[0],
        'appearances': conn.execute('SELECT COUNT(*) FROM character_appearances').fetchone()[0],
        'directing': conn.execute('SELECT COUNT(*) FROM directing_notes').fetchone()[0],
        'modes': conn.execute('SELECT COUNT(*) FROM sonnet_modes').fetchone()[0],
    }

    conn.close()
    return data


def build_character_stream_data(raw):
    """Build per-sonnet character presence data for the stream chart."""
    # For each sonnet 1-154, count appearances per character
    chars = {'FYM': {}, 'DL': {}, 'RP': {}, 'SPEAKER': {}}
    for sonnet_id, char_id, role in raw:
        if char_id in chars:
            chars[char_id][sonnet_id] = chars[char_id].get(sonnet_id, 0) + 1

    result = {}
    for char_id in ['FYM', 'DL', 'RP', 'SPEAKER']:
        result[char_id] = [chars[char_id].get(n, 0) for n in range(1, 155)]
    return result


def build_heatmap_data(raw):
    """Build theme × addressee matrix."""
    # Get unique themes and addressees
    themes = sorted(set(r[1] for r in raw))
    addressees = ['FYM', 'DL', 'MIXED', 'NONE']
    matrix = {}
    for addr, theme, count in raw:
        if addr not in matrix:
            matrix[addr] = {}
        matrix[addr][theme] = count
    return themes, addressees, matrix


ARC_COLORS = {
    'PROCREATION': '#c4a44a',
    'DEVOTION': '#7ba3c9',
    'FIRST_BETRAYAL': '#c97b8b',
    'ABSENCE_JOURNEY': '#6b9bb8',
    'TIME_MORTALITY': '#a8856b',
    'POETRY_IMMORTALITY': '#c4a44a',
    'RIVAL_POET': '#9b7bb8',
    'ESTRANGEMENT': '#c4785c',
    'ABSENCE_BEAUTY': '#7ba882',
    'SPEAKERS_FAULT': '#d4896d',
    'PHILOSOPHY_ENVOI': '#8b9bb8',
    'DARK_LADY': '#c97b8b',
    'CUPID_CODA': '#d4c9b8',
}

ARC_LABELS = {
    'PROCREATION': 'Procreation',
    'DEVOTION': 'Devotion',
    'FIRST_BETRAYAL': 'First Betrayal',
    'ABSENCE_JOURNEY': 'Absence & Journey',
    'TIME_MORTALITY': 'Time & Mortality',
    'POETRY_IMMORTALITY': 'Poetry & Immortality',
    'RIVAL_POET': 'Rival Poet',
    'ESTRANGEMENT': 'Estrangement',
    'ABSENCE_BEAUTY': 'Absence & Beauty',
    'SPEAKERS_FAULT': "Speaker's Fault",
    'PHILOSOPHY_ENVOI': 'Philosophy & Envoi',
    'DARK_LADY': 'Dark Lady',
    'CUPID_CODA': 'Cupid Coda',
}


def generate_html(data):
    """Generate the full HTML page."""
    char_stream = build_character_stream_data(data['character_stream'])
    heatmap_themes, heatmap_addrs, heatmap_matrix = build_heatmap_data(data['theme_addressee'])

    # Build sequence arc segments for the timeline
    arc_segments_js = json.dumps([{
        'label': ARC_LABELS.get(arc, arc),
        'start': start,
        'end': end,
        'count': count,
        'color': ARC_COLORS.get(arc, '#666'),
    } for arc, count, start, end in data['sequence_arcs']])

    # Stats
    stats = data['stats']

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shakespeare's Sonnets — Data Visualizations</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <link rel="stylesheet" href="../css/style.css">
    <style>
        .viz-page {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem 1.5rem;
        }}
        .viz-header {{
            text-align: center;
            margin-bottom: 3rem;
            padding-bottom: 2rem;
            border-bottom: 1px solid var(--border-subtle);
        }}
        .viz-header h1 {{
            font-family: var(--font-heading);
            font-size: var(--text-4xl);
            color: var(--text-heading);
            margin-bottom: 0.5rem;
            letter-spacing: 0.02em;
        }}
        .viz-header .subtitle {{
            font-family: var(--font-heading);
            font-size: var(--text-lg);
            color: var(--text-muted);
            font-style: italic;
        }}
        .viz-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 1rem;
            margin-bottom: 3rem;
        }}
        .stat-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 6px;
            padding: 1rem;
            text-align: center;
        }}
        .stat-card .stat-number {{
            font-family: var(--font-heading);
            font-size: var(--text-2xl);
            color: var(--accent-gold);
            display: block;
        }}
        .stat-card .stat-label {{
            font-size: var(--text-xs);
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}
        .viz-section {{
            margin-bottom: 4rem;
        }}
        .viz-section h2 {{
            font-family: var(--font-heading);
            font-size: var(--text-2xl);
            color: var(--text-heading);
            margin-bottom: 0.5rem;
        }}
        .viz-section .section-desc {{
            font-size: var(--text-sm);
            color: var(--text-muted);
            margin-bottom: 1.5rem;
            max-width: 800px;
        }}
        .chart-container {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 8px;
            padding: 1.5rem;
            position: relative;
        }}
        .chart-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
        }}
        @media (max-width: 768px) {{
            .chart-row {{ grid-template-columns: 1fr; }}
        }}
        canvas {{
            max-height: 500px;
        }}
        /* Sequence arc timeline */
        .arc-timeline {{
            display: flex;
            height: 60px;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 1rem;
        }}
        .arc-segment {{
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.65rem;
            color: #1a1a1a;
            font-weight: 600;
            text-overflow: ellipsis;
            overflow: hidden;
            white-space: nowrap;
            padding: 0 4px;
            cursor: default;
            position: relative;
        }}
        .arc-segment:hover {{
            filter: brightness(1.2);
        }}
        .arc-legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            margin-top: 0.75rem;
        }}
        .arc-legend-item {{
            display: flex;
            align-items: center;
            gap: 0.35rem;
            font-size: var(--text-xs);
            color: var(--text-muted);
        }}
        .arc-legend-swatch {{
            width: 12px;
            height: 12px;
            border-radius: 2px;
            flex-shrink: 0;
        }}
        /* Heatmap */
        .heatmap-grid {{
            display: grid;
            gap: 2px;
            margin-top: 1rem;
        }}
        .heatmap-cell {{
            border-radius: 3px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.7rem;
            color: var(--text-primary);
            min-height: 36px;
            cursor: default;
        }}
        .heatmap-label {{
            font-size: var(--text-xs);
            color: var(--text-muted);
            display: flex;
            align-items: center;
            padding: 0 0.5rem;
        }}
        .heatmap-header {{
            font-size: var(--text-xs);
            color: var(--text-muted);
            text-align: center;
            padding: 0.25rem;
            font-weight: 600;
        }}
        .note {{
            font-size: var(--text-xs);
            color: var(--text-dim);
            font-style: italic;
            margin-top: 0.75rem;
        }}
    </style>
</head>
<body>
<div class="viz-page">

    <div class="viz-header">
        <h1>Shakespeare's Sonnets</h1>
        <div class="subtitle">A Quantitative Portrait of 154 Poems</div>
    </div>

    <!-- Summary Stats -->
    <div class="viz-stats">
        <div class="stat-card"><span class="stat-number">{stats['sonnets']}</span><span class="stat-label">Sonnets</span></div>
        <div class="stat-card"><span class="stat-number">{stats['lines']:,}</span><span class="stat-label">Lines</span></div>
        <div class="stat-card"><span class="stat-number">{stats['devices']:,}</span><span class="stat-label">Rhetorical Devices</span></div>
        <div class="stat-card"><span class="stat-number">{stats['annotations']:,}</span><span class="stat-label">Line Annotations</span></div>
        <div class="stat-card"><span class="stat-number">{stats['themes']}</span><span class="stat-label">Theme Tags</span></div>
        <div class="stat-card"><span class="stat-number">{stats['directing']}</span><span class="stat-label">Directing Notes</span></div>
    </div>

    <!-- 1. SEQUENCE ARC TIMELINE -->
    <div class="viz-section">
        <h2>The Dramatic Arc</h2>
        <p class="section-desc">The 154 sonnets tell a story in 13 phases. The Speaker moves from urging the Fair Young Man to marry, through devotion and betrayal, rivalry and estrangement, to the Dark Lady's devastating entry and a mythological coda that resolves nothing.</p>
        <div class="chart-container">
            <div class="arc-timeline" id="arcTimeline"></div>
            <div class="arc-legend" id="arcLegend"></div>
        </div>
    </div>

    <!-- 2. ADDRESSEE + 7. VOLTA/COUPLET -->
    <div class="viz-section">
        <h2>Who Is Being Addressed — and How Do the Sonnets Turn?</h2>
        <p class="section-desc">The Fair Young Man dominates the sequence. Most sonnets pivot through logical argument; the rarer ironic volta signals Shakespeare at his most psychologically complex.</p>
        <div class="chart-row">
            <div class="chart-container">
                <canvas id="addresseeChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="voltaChart"></canvas>
            </div>
        </div>
        <div class="chart-row" style="margin-top: 1.5rem">
            <div class="chart-container">
                <canvas id="coupletChart"></canvas>
            </div>
            <div class="chart-container" style="display:flex; align-items:center; justify-content:center; flex-direction:column; padding:2rem;">
                <p style="color:var(--text-muted); font-size:var(--text-sm); text-align:center; max-width:300px;">The couplet is the Shakespearean sonnet's signature move. Resolution and epigram dominate, but a third of all couplets are <em>ironic</em> — saying one thing while meaning another.</p>
            </div>
        </div>
    </div>

    <!-- 3. THEMES -->
    <div class="viz-section">
        <h2>What the Sonnets Are About</h2>
        <p class="section-desc">{data['total_themes']} distinct themes tagged across 154 sonnets. Beauty and Time tower over everything else — the two great antagonists of the sequence.</p>
        <div class="chart-container">
            <canvas id="themeChart" style="max-height:600px;"></canvas>
        </div>
        <p class="note">Showing top 25 of {data['total_themes']} themes. Color indicates PRIMARY (gold) vs SECONDARY (muted) prominence.</p>
    </div>

    <!-- 4. THEME × ADDRESSEE HEATMAP -->
    <div class="viz-section">
        <h2>Themes by Character</h2>
        <p class="section-desc">What the Speaker talks about changes depending on whom he addresses. The FYM gets beauty and time; the Dark Lady gets self-deception and appearance vs reality.</p>
        <div class="chart-container">
            <div id="heatmapContainer"></div>
        </div>
    </div>

    <!-- 5. RHETORICAL DEVICES -->
    <div class="viz-section">
        <h2>Shakespeare's Rhetorical Fingerprint</h2>
        <p class="section-desc">Metaphor is the dominant device — nearly a quarter of all annotations. But paradox, pun, and antithesis form the real engine: Shakespeare thinks in oppositions, double meanings, and seeming contradictions.</p>
        <div class="chart-container">
            <canvas id="deviceChart" style="max-height:650px;"></canvas>
        </div>
    </div>

    <!-- 6. DEVICE DENSITY -->
    <div class="viz-section">
        <h2>Rhetorical Density: How Many Devices Per Sonnet?</h2>
        <p class="section-desc">Most sonnets carry 7-8 rhetorical devices. The densest is Sonnet 151 (14 devices) — the most sexually explicit sonnet, where every line operates on double entendre.</p>
        <div class="chart-container">
            <canvas id="densityChart"></canvas>
        </div>
    </div>

    <!-- 8. CHARACTER PRESENCE -->
    <div class="viz-section">
        <h2>The Love Triangle Across 154 Sonnets</h2>
        <p class="section-desc">The Fair Young Man is present throughout sonnets 1-126. The Dark Lady appears at 127. The Rival Poet flickers through 78-86. The Speaker — always present — is the constant voice holding the triangle together.</p>
        <div class="chart-container">
            <canvas id="characterChart" style="max-height:400px;"></canvas>
        </div>
    </div>

    <!-- 9. ANALYTICAL MODES -->
    <div class="viz-section">
        <h2>How the Sonnets Want to Be Read</h2>
        <p class="section-desc">Each sonnet has been assigned analytical mode priorities. Rhetorical and Dramatic analysis dominate — these are poems that argue and perform. Prosodic and Historical modes appear where meter or biography drives the meaning.</p>
        <div class="chart-row">
            <div class="chart-container">
                <canvas id="modeChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="modeCountChart"></canvas>
            </div>
        </div>
    </div>

    <!-- 10. SCHOLARLY GROUPS -->
    <div class="viz-section">
        <h2>Scholarly Groupings</h2>
        <p class="section-desc">Scholars have identified 47 thematic and structural groupings within the 154 sonnets. The Procreation sonnets (1-17) are the largest single cluster. Many sonnets belong to multiple groups — the richer the sonnet, the more clusters claim it.</p>
        <div class="chart-container">
            <canvas id="groupChart" style="max-height:650px;"></canvas>
        </div>
    </div>

    <!-- 11. ANNOTATION DENSITY -->
    <div class="viz-section">
        <h2>Where Readers Focus: Annotation by Line Position</h2>
        <p class="section-desc">Line 1 draws the most scholarly attention — the opening gambit. Annotation dips through the middle quatrains, then spikes at the couplet (lines 13-14), where the sonnet delivers its verdict.</p>
        <div class="chart-container">
            <canvas id="annotationChart"></canvas>
        </div>
    </div>

</div>

<script>
// ============ SHWEP CHART THEME ============
Chart.defaults.color = '#a8a5a0';
Chart.defaults.borderColor = '#333333';
Chart.defaults.font.family = 'Georgia, "Times New Roman", serif';

const PALETTE = {{
    gold: '#c4a44a',
    terracotta: '#c4785c',
    blue: '#7ba3c9',
    rose: '#c97b8b',
    green: '#7ba882',
    purple: '#9b7bb8',
    muted: '#6b6966',
    cream: '#d4c9b8',
    coral: '#d4896d',
}};

// ============ 1. SEQUENCE ARC TIMELINE ============
(function() {{
    const arcs = {arc_segments_js};
    const timeline = document.getElementById('arcTimeline');
    const legend = document.getElementById('arcLegend');
    const total = 154;

    arcs.forEach(arc => {{
        const pct = (arc.count / total * 100).toFixed(1);
        const seg = document.createElement('div');
        seg.className = 'arc-segment';
        seg.style.width = pct + '%';
        seg.style.backgroundColor = arc.color;
        seg.title = `${{arc.label}} (Sonnets ${{arc.start}}-${{arc.end}}, ${{arc.count}} sonnets)`;
        seg.textContent = arc.count >= 8 ? arc.label : '';
        timeline.appendChild(seg);

        const item = document.createElement('div');
        item.className = 'arc-legend-item';
        item.innerHTML = `<span class="arc-legend-swatch" style="background:${{arc.color}}"></span>${{arc.label}} (${{arc.start}}-${{arc.end}})`;
        legend.appendChild(item);
    }});
}})();

// ============ 2. ADDRESSEE DONUT ============
new Chart(document.getElementById('addresseeChart'), {{
    type: 'doughnut',
    data: {{
        labels: {json.dumps([a[0] for a in data['addressees']])},
        datasets: [{{
            data: {json.dumps([a[1] for a in data['addressees']])},
            backgroundColor: [PALETTE.blue, PALETTE.rose, PALETTE.purple, PALETTE.muted],
            borderColor: '#1a1a1a',
            borderWidth: 2,
        }}]
    }},
    options: {{
        responsive: true,
        plugins: {{
            title: {{ display: true, text: 'Addressee', color: '#e8e6e3', font: {{ size: 16, family: 'Georgia' }} }},
            legend: {{ position: 'bottom', labels: {{ padding: 15 }} }}
        }}
    }}
}});

// ============ 7a. VOLTA TYPES ============
new Chart(document.getElementById('voltaChart'), {{
    type: 'doughnut',
    data: {{
        labels: {json.dumps([v[0] for v in data['volta_types']])},
        datasets: [{{
            data: {json.dumps([v[1] for v in data['volta_types']])},
            backgroundColor: [PALETTE.blue, PALETTE.green, PALETTE.terracotta, PALETTE.rose],
            borderColor: '#1a1a1a',
            borderWidth: 2,
        }}]
    }},
    options: {{
        responsive: true,
        plugins: {{
            title: {{ display: true, text: 'How Sonnets Turn (Volta Type)', color: '#e8e6e3', font: {{ size: 16, family: 'Georgia' }} }},
            legend: {{ position: 'bottom', labels: {{ padding: 15 }} }}
        }}
    }}
}});

// ============ 7b. COUPLET FUNCTIONS ============
new Chart(document.getElementById('coupletChart'), {{
    type: 'doughnut',
    data: {{
        labels: {json.dumps([c[0] for c in data['couplet_functions']])},
        datasets: [{{
            data: {json.dumps([c[1] for c in data['couplet_functions']])},
            backgroundColor: [PALETTE.gold, PALETTE.terracotta, PALETTE.rose, PALETTE.purple, PALETTE.muted],
            borderColor: '#1a1a1a',
            borderWidth: 2,
        }}]
    }},
    options: {{
        responsive: true,
        plugins: {{
            title: {{ display: true, text: 'Couplet Function', color: '#e8e6e3', font: {{ size: 16, family: 'Georgia' }} }},
            legend: {{ position: 'bottom', labels: {{ padding: 15 }} }}
        }}
    }}
}});

// ============ 3. THEMES BAR ============
new Chart(document.getElementById('themeChart'), {{
    type: 'bar',
    data: {{
        labels: {json.dumps([t[0].replace('_', ' ').title() for t in data['themes']])},
        datasets: [
            {{
                label: 'Primary',
                data: {json.dumps([t[2] for t in data['themes']])},
                backgroundColor: PALETTE.gold,
            }},
            {{
                label: 'Secondary',
                data: {json.dumps([t[3] for t in data['themes']])},
                backgroundColor: PALETTE.muted,
            }}
        ]
    }},
    options: {{
        indexAxis: 'y',
        responsive: true,
        scales: {{
            x: {{ stacked: true, grid: {{ color: '#2a2a2a' }} }},
            y: {{ stacked: true, grid: {{ display: false }} }}
        }},
        plugins: {{
            legend: {{ position: 'top' }},
        }}
    }}
}});

// ============ 4. HEATMAP ============
(function() {{
    const themes = {json.dumps(heatmap_themes)};
    const addressees = ['FYM', 'DL', 'MIXED', 'NONE'];
    const matrix = {json.dumps(heatmap_matrix)};
    const container = document.getElementById('heatmapContainer');

    const cols = addressees.length + 1;
    const grid = document.createElement('div');
    grid.className = 'heatmap-grid';
    grid.style.gridTemplateColumns = '140px ' + 'repeat(' + addressees.length + ', 1fr)';

    // Header row
    grid.innerHTML += '<div class="heatmap-header"></div>';
    addressees.forEach(a => {{
        grid.innerHTML += `<div class="heatmap-header">${{a}}</div>`;
    }});

    // Find max for color scaling
    let maxVal = 0;
    Object.values(matrix).forEach(m => Object.values(m).forEach(v => {{ if(v>maxVal) maxVal=v; }}));

    themes.forEach(theme => {{
        grid.innerHTML += `<div class="heatmap-label">${{theme.replace(/_/g,' ')}}</div>`;
        addressees.forEach(addr => {{
            const val = (matrix[addr] && matrix[addr][theme]) || 0;
            const intensity = val / maxVal;
            const bg = val > 0
                ? `rgba(196, 164, 74, ${{0.15 + intensity * 0.7}})`
                : 'rgba(255,255,255,0.03)';
            grid.innerHTML += `<div class="heatmap-cell" style="background:${{bg}}" title="${{theme}} / ${{addr}}: ${{val}}">${{val || ''}}</div>`;
        }});
    }});

    container.appendChild(grid);
}})();

// ============ 5. DEVICE FREQUENCY ============
new Chart(document.getElementById('deviceChart'), {{
    type: 'bar',
    data: {{
        labels: {json.dumps([d[0].replace('_', ' ').title() for d in data['devices']])},
        datasets: [{{
            data: {json.dumps([d[1] for d in data['devices']])},
            backgroundColor: PALETTE.gold,
            borderRadius: 3,
        }}]
    }},
    options: {{
        indexAxis: 'y',
        responsive: true,
        scales: {{
            x: {{ grid: {{ color: '#2a2a2a' }} }},
            y: {{ grid: {{ display: false }} }}
        }},
        plugins: {{ legend: {{ display: false }} }}
    }}
}});

// ============ 6. DEVICE DENSITY HISTOGRAM ============
new Chart(document.getElementById('densityChart'), {{
    type: 'bar',
    data: {{
        labels: {json.dumps([d[0] for d in data['device_density']])},
        datasets: [{{
            label: 'Sonnets',
            data: {json.dumps([d[1] for d in data['device_density']])},
            backgroundColor: PALETTE.terracotta,
            borderRadius: 3,
        }}]
    }},
    options: {{
        responsive: true,
        scales: {{
            x: {{ title: {{ display: true, text: 'Rhetorical devices per sonnet', color: '#a8a5a0' }}, grid: {{ display: false }} }},
            y: {{ title: {{ display: true, text: 'Number of sonnets', color: '#a8a5a0' }}, grid: {{ color: '#2a2a2a' }} }}
        }},
        plugins: {{ legend: {{ display: false }} }}
    }}
}});

// ============ 8. CHARACTER STREAM ============
new Chart(document.getElementById('characterChart'), {{
    type: 'line',
    data: {{
        labels: Array.from({{length: 154}}, (_, i) => i + 1),
        datasets: [
            {{
                label: 'Fair Young Man',
                data: {json.dumps(char_stream['FYM'])},
                fill: true,
                backgroundColor: 'rgba(123, 163, 201, 0.4)',
                borderColor: PALETTE.blue,
                borderWidth: 1.5,
                pointRadius: 0,
                tension: 0.3,
            }},
            {{
                label: 'Dark Lady',
                data: {json.dumps(char_stream['DL'])},
                fill: true,
                backgroundColor: 'rgba(201, 123, 139, 0.5)',
                borderColor: PALETTE.rose,
                borderWidth: 1.5,
                pointRadius: 0,
                tension: 0.3,
            }},
            {{
                label: 'Rival Poet',
                data: {json.dumps(char_stream['RP'])},
                fill: true,
                backgroundColor: 'rgba(155, 123, 184, 0.4)',
                borderColor: PALETTE.purple,
                borderWidth: 1.5,
                pointRadius: 0,
                tension: 0.3,
            }},
        ]
    }},
    options: {{
        responsive: true,
        scales: {{
            x: {{ title: {{ display: true, text: 'Sonnet Number', color: '#a8a5a0' }}, grid: {{ display: false }},
                 ticks: {{ maxTicksLimit: 20 }} }},
            y: {{ title: {{ display: true, text: 'Appearances', color: '#a8a5a0' }}, grid: {{ color: '#2a2a2a' }},
                 stacked: false }}
        }},
        plugins: {{ legend: {{ position: 'top' }} }}
    }}
}});

// ============ 9a. MODE RADAR ============
new Chart(document.getElementById('modeChart'), {{
    type: 'radar',
    data: {{
        labels: {json.dumps([m[0].title() for m in data['modes']])},
        datasets: [{{
            label: 'Avg Priority',
            data: {json.dumps([m[1] for m in data['modes']])},
            backgroundColor: 'rgba(196, 164, 74, 0.2)',
            borderColor: PALETTE.gold,
            borderWidth: 2,
            pointBackgroundColor: PALETTE.gold,
        }}]
    }},
    options: {{
        responsive: true,
        scales: {{
            r: {{
                grid: {{ color: '#333' }},
                angleLines: {{ color: '#333' }},
                ticks: {{ display: false }},
                suggestedMin: 0,
                suggestedMax: 3,
            }}
        }},
        plugins: {{
            title: {{ display: true, text: 'Average Mode Priority', color: '#e8e6e3', font: {{ size: 14 }} }},
            legend: {{ display: false }}
        }}
    }}
}});

// ============ 9b. MODE COUNT ============
new Chart(document.getElementById('modeCountChart'), {{
    type: 'bar',
    data: {{
        labels: {json.dumps([m[0].title() for m in data['modes']])},
        datasets: [{{
            label: 'Sonnets using this mode',
            data: {json.dumps([m[2] for m in data['modes']])},
            backgroundColor: PALETTE.green,
            borderRadius: 3,
        }}]
    }},
    options: {{
        indexAxis: 'y',
        responsive: true,
        scales: {{
            x: {{ grid: {{ color: '#2a2a2a' }} }},
            y: {{ grid: {{ display: false }} }}
        }},
        plugins: {{
            title: {{ display: true, text: 'Mode Frequency', color: '#e8e6e3', font: {{ size: 14 }} }},
            legend: {{ display: false }}
        }}
    }}
}});

// ============ 10. SCHOLARLY GROUPS ============
new Chart(document.getElementById('groupChart'), {{
    type: 'bar',
    data: {{
        labels: {json.dumps([g[1] for g in data['groups']])},
        datasets: [{{
            data: {json.dumps([g[2] for g in data['groups']])},
            backgroundColor: PALETTE.purple,
            borderRadius: 3,
        }}]
    }},
    options: {{
        indexAxis: 'y',
        responsive: true,
        scales: {{
            x: {{ grid: {{ color: '#2a2a2a' }} }},
            y: {{ grid: {{ display: false }} }}
        }},
        plugins: {{ legend: {{ display: false }} }}
    }}
}});

// ============ 11. ANNOTATION DENSITY ============
new Chart(document.getElementById('annotationChart'), {{
    type: 'line',
    data: {{
        labels: {json.dumps([f'Line {d[0]}' for d in data['annotation_density'] if d[0] <= 14])},
        datasets: [{{
            label: 'Annotations',
            data: {json.dumps([d[1] for d in data['annotation_density'] if d[0] <= 14])},
            fill: true,
            backgroundColor: 'rgba(196, 120, 92, 0.3)',
            borderColor: PALETTE.terracotta,
            borderWidth: 2,
            pointBackgroundColor: PALETTE.terracotta,
            pointRadius: 5,
            tension: 0.3,
        }}]
    }},
    options: {{
        responsive: true,
        scales: {{
            x: {{ grid: {{ display: false }} }},
            y: {{ title: {{ display: true, text: 'Annotation Count', color: '#a8a5a0' }}, grid: {{ color: '#2a2a2a' }} }}
        }},
        plugins: {{ legend: {{ display: false }} }}
    }}
}});
</script>
</body>
</html>'''

    return html


def main():
    print("Querying database...")
    data = query_all_data()

    print("Generating visualizations...")
    html = generate_html(data)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, 'index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Written to {output_path}")
    print(f"Stats: {data['stats']}")


if __name__ == '__main__':
    main()
