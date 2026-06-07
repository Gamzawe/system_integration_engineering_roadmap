#!/usr/bin/env python3
"""
Parse roadmap.txt (markdown with week/day tables) and generate index.html
for the interactive flowchart engine.

New format: 4 phases, 20 weeks, 2-column day tables (Morning / Evening).
"""

import re
import html


def escape_attr(text):
    """Escape text for use in HTML attribute values."""
    return html.escape(text, quote=True).replace('|', '&#124;')


def escape_detail(text):
    """Escape for data-details pipe-delimited attribute."""
    return text.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')


def parse_roadmap(filepath):
    """Parse roadmap.txt into structured data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    sections = []  # Top-level sections (## Phase N: ...)
    current_section = None
    current_week = None

    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\r')

        # Match top-level section: ## Phase N: Title (Weeks X–Y)
        section_match = re.match(r'^## (Phase \d+:.+)', line)
        if section_match:
            current_section = {
                'title': section_match.group(1).strip(),
                'weeks': []
            }
            sections.append(current_section)
            i += 1
            continue

        # Match week header: ### Week N — Title
        week_match = re.match(r'^### (Week (\d+)\s*[–—-]\s*(.+))', line)
        if week_match:
            week_num = int(week_match.group(2))
            week_title = week_match.group(3).strip()
            current_week = {
                'num': week_num,
                'title': week_title,
                'full_title': week_match.group(1).strip(),
                'days': []
            }
            if current_section:
                current_section['weeks'].append(current_week)
            i += 1
            continue

        # Match table rows: | **N** | Morning text | Evening text |
        day_match = re.match(r'^\|\s*\*\*(\d+)\*\*\s*\|(.+)$', line)
        if day_match and current_week:
            day_num = int(day_match.group(1))
            rest = day_match.group(2)

            # Split by | but handle the trailing |
            cells = [c.strip() for c in rest.split('|')]
            # Remove empty trailing cell
            while cells and cells[-1] == '':
                cells.pop()

            morning = cells[0] if len(cells) > 0 else ''
            evening = cells[1] if len(cells) > 1 else ''

            current_week['days'].append({
                'num': day_num,
                'morning': morning,
                'evening': evening,
            })
            i += 1
            continue

        i += 1

    return sections


def build_day_details(day):
    """Build pipe-delimited data-details string for a day node."""
    parts = []
    if day['morning']:
        parts.append(f"🌅 Morning: {day['morning']}")
    if day['evening']:
        parts.append(f"🌙 Evening: {day['evening']}")
    return '|'.join(parts)


def build_week_details(week):
    """Build pipe-delimited data-details string for a week node."""
    parts = [f"⏱️ 5 days"]
    for day in week['days']:
        short = day['morning'][:80] if day['morning'] else f"Day {day['num']}"
        parts.append(f"Day {day['num']}: {short}")
    return '|'.join(parts)


def generate_html(sections):
    """Generate the full index.html content."""

    phase_config = [
        {
            'num': 0,
            'label': 'PRE-FLIGHT',
            'emoji': '🚀',
            'short': 'Pre-Flight',
            'year_class': 'year-label-1',
        },
        {
            'num': 1,
            'label': 'FOUNDATION REPAIR',
            'emoji': '⚡',
            'short': 'Foundation Repair',
            'year_class': 'year-label-1',
        },
        {
            'num': 2,
            'label': 'CLOUD & DISTRIBUTION',
            'emoji': '☁️',
            'short': 'Cloud & Distribution',
            'year_class': 'year-label-1',
        },
        {
            'num': 3,
            'label': 'DOCUMENTATION & PROOF',
            'emoji': '📋',
            'short': 'Documentation & Proof',
            'year_class': 'year-label-2',
        },
        {
            'num': 4,
            'label': 'MARKET ENTRY',
            'emoji': '🎯',
            'short': 'Market Entry',
            'year_class': 'year-label-2',
        },
        {
            'num': 5,
            'label': 'POST-SPRINT',
            'emoji': '🔄',
            'short': 'Post-Sprint (Month 6–18)',
            'year_class': 'year-label-2',
        },
    ]

    total_weeks = sum(len(s['weeks']) for s in sections)
    total_days = sum(len(w['days']) for s in sections for w in s['weeks'])

    # Build all nodes
    nodes_html = []

    for sec_idx, section in enumerate(sections):
        phase = phase_config[sec_idx] if sec_idx < len(phase_config) else phase_config[-1]

        # Phase label (year-label on center spine)
        phase_id = f"phase{phase['num']}Label"
        phase_html = (
            f'    <div class="year-label {phase["year_class"]}" id="{phase_id}" '
            f'data-parent="" data-side="center">'
            f'{phase["emoji"]} PHASE {phase["num"]}<br>'
            f'<small>{escape_detail(phase["short"])}</small></div>'
        )
        nodes_html.append(f'\n    <!-- ======= PHASE {phase["num"]}: {phase["label"]} ======= -->')
        nodes_html.append(phase_html)

        weeks = section['weeks']
        num_weeks = len(weeks)

        # Single main-node per phase (replaces month nodes)
        phase_node_id = f"phase{phase['num']}"
        phase_details = escape_detail(
            f"{phase['emoji']} {phase['short']}|"
            f"⏱️ {num_weeks} weeks|"
            f"📅 {num_weeks * 5} study days"
        )

        nodes_html.append(f'\n    <!-- PHASE {phase["num"]} BLOCK -->')
        nodes_html.append(
            f'    <div class="node main-node" id="{phase_node_id}" '
            f'data-parent="{phase_id}" data-side="center"\n'
            f'      data-details="{phase_details}">\n'
            f'      {phase["emoji"]} {escape_detail(phase["short"])}\n'
            f'      <span class="months-badge">{num_weeks} weeks</span>\n'
            f'    </div>'
        )

        # Add weeks as sub-nodes (alternating left/right)
        for w_idx, week in enumerate(weeks):
            week_num = week['num']
            week_id = f"w{week_num}"
            side = "left" if w_idx % 2 == 0 else "right"

            week_details = escape_detail(build_week_details(week))
            week_label = escape_detail(week['title'])

            has_days_class = ' has-days' if week['days'] else ''

            nodes_html.append(
                f'    <div class="node sub-node{has_days_class}" id="{week_id}" '
                f'data-parent="{phase_node_id}" data-side="{side}"\n'
                f'      data-details="{week_details}">\n'
                f'      📅 Week {week_num}: {week_label}\n'
                f'    </div>'
            )

            # Add day nodes
            for day in week['days']:
                day_id = f"{week_id}_d{day['num']}"
                day_details = escape_detail(build_day_details(day))

                # Short day label from morning session
                day_label = day['morning'][:40] if day['morning'] else f"Day {day['num']}"
                if day['morning'] and len(day['morning']) > 40:
                    day_label = day_label[:37] + '...'
                day_label = escape_detail(day_label)

                nodes_html.append(
                    f'    <div class="node day-node" id="{day_id}" '
                    f'data-parent="{week_id}" data-side="{side}"\n'
                    f'      data-details="{day_details}">\n'
                    f'      Day {day["num"]} — {day_label}\n'
                    f'    </div>'
                )

        # Add milestones after key phases
        if sec_idx == 2:  # After Phase 2 (Cloud & Distribution)
            nodes_html.append(
                f'    <div class="node milestone-node" id="milestone_cloud" '
                f'data-parent="{phase_node_id}" data-side="center"\n'
                f'      data-details="🎉 Cloud pipeline working. Docker, CI/CD, Azure telemetry, industrial protocols integrated.">\n'
                f'      🎉 Cloud & Industrial Foundation Complete\n'
                f'    </div>'
            )
        elif sec_idx == 3:  # After Phase 3 (Documentation & Proof)
            nodes_html.append(
                f'    <div class="node milestone-node" id="milestone_portfolio" '
                f'data-parent="{phase_node_id}" data-side="center"\n'
                f'      data-details="🎉 Portfolio v1.0 locked. C4 diagrams, ADRs, video demo, bilingual README, CV ready.">\n'
                f'      🎉 Portfolio v1.0 Locked\n'
                f'    </div>'
            )

    # Final milestone
    nodes_html.append(
        f'    <div class="node milestone-node" id="milestone_final" '
        f'data-parent="phase5" data-side="center"\n'
        f'      data-details="🏆 40+ applications sent. Interview pipeline active. Contract negotiation or relocation.">\n'
        f'      🏆 Mission Complete — Contract Signed\n'
        f'    </div>'
    )

    nodes_content = '\n'.join(nodes_html)

    full_html = f'''<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>20-Week Market-Readiness Sprint</title>
  <meta name="description"
    content="A 20-week sprint roadmap for C#/.NET Integration Engineer — Biometric, Kiosk, Identity & Edge Systems targeting Germany.">
  <link rel="stylesheet" href="style.css">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>

<body>

  <!-- Header -->
  <header class="roadmap-header">
    <h1>20-Week Market-Readiness Sprint</h1>
    <p class="header-subtitle">C#/.NET Integration Engineer &middot; Biometric & Kiosk Systems &middot; Germany &middot; {total_weeks} Weeks &middot; {total_days} Exercises</p>
    <div class="progress-bar-container">
      <div class="progress-bar" id="progressBar">
        <span class="progress-text" id="progressText">0%</span>
      </div>
    </div>
  </header>

  <!-- Legend -->
  <div class="legend">
    <div class="legend-item"><span class="legend-swatch main-swatch"></span> Phase</div>
    <div class="legend-item"><span class="legend-swatch sub-swatch"></span> Week</div>
    <div class="legend-item"><span class="legend-swatch day-swatch"></span> Day</div>
    <div class="legend-item"><span class="legend-swatch milestone-swatch"></span> Milestone</div>
    <div class="legend-item"><span class="legend-swatch done-swatch"></span> Done</div>
    <div class="legend-item"><span class="legend-swatch progress-swatch"></span> In Progress</div>
    <div class="legend-item"><span class="legend-swatch skip-swatch"></span> Skip</div>
  </div>

  <!-- Roadmap Canvas -->
  <div class="roadmap-canvas" id="roadmapCanvas">
    <svg class="connectors" id="connectorSvg"></svg>
    <div class="tip-callout" id="rulesCallout" data-parent="" data-side="right">
      Daily: 45&ndash;90 min C# (Morning) + 15&ndash;45 min German (Evening).
      Right-click nodes to track progress.
    </div>
{nodes_content}
  </div>

  <!-- Status Context Menu -->
  <div class="status-menu" id="statusMenu">
    <button class="status-menu-item" data-status="done">
      <span class="status-dot done-dot"></span> Done
      <span class="status-shortcut">D</span>
    </button>
    <button class="status-menu-item" data-status="in-progress">
      <span class="status-dot progress-dot"></span> In Progress
      <span class="status-shortcut">L</span>
    </button>
    <button class="status-menu-item" data-status="reset">
      <span class="status-dot reset-dot"></span> Reset
      <span class="status-shortcut">R</span>
    </button>
    <button class="status-menu-item" data-status="skip">
      <span class="status-dot skip-dot"></span> Skip
      <span class="status-shortcut">S</span>
    </button>
    <button class="status-menu-close" id="statusMenuClose">&times;</button>
  </div>

  <!-- Detail Drawer -->
  <div class="drawer-overlay" id="drawerOverlay"></div>
  <div class="detail-drawer" id="detailDrawer">
    <button class="drawer-close" id="drawerClose">&times;</button>
    <h2 class="drawer-title" id="drawerTitle"></h2>
    <ul class="drawer-list" id="drawerList"></ul>
  </div>

  <script src="script.js"></script>
</body>

</html>'''

    return full_html


def main():
    sections = parse_roadmap('roadmap.txt')

    # Debug output
    total_weeks = sum(len(s['weeks']) for s in sections)
    total_days = sum(len(w['days']) for s in sections for w in s['weeks'])
    print(f"Parsed {len(sections)} sections, {total_weeks} weeks, {total_days} days")

    for i, sec in enumerate(sections):
        print(f"  Section {i+1}: {sec['title']} — {len(sec['weeks'])} weeks")
        for w in sec['weeks']:
            print(f"    Week {w['num']}: {w['title']} — {len(w['days'])} days")

    html_content = generate_html(sections)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\nGenerated index.html successfully ({len(html_content):,} bytes)")


if __name__ == '__main__':
    main()
