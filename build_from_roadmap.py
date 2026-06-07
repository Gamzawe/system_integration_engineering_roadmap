#!/usr/bin/env python3
"""
Parse roadmap.txt and generate index.html for the interactive flowchart engine.

Handles:
- ## Pre-Flight: Week 0  (auto-creates Week 0, 4-column table, duplicate day 0s)
- ## Phase N: Title       (standard phases with ### Week N: sub-headers)
- ## Post-Week 20: ...    (auto-creates Week 21, bold month ranges like **7–9**)
- Day rows: | 0 |, | N |, | **N** |, | **N–M** |
"""

import re
import html


def escape_attr(text):
    return html.escape(text, quote=True).replace('|', '&#124;')


def escape_detail(text):
    return text.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')


def parse_roadmap(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    sections = []
    current_section = None
    current_week = None

    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\r')

        # Pre-Flight section (auto-creates Week 0)
        preflight_match = re.match(r'^## Pre-Flight:\s*Week\s*0', line)
        if preflight_match:
            current_section = {
                'title': 'Pre-Flight',
                'type': 'preflight',
                'weeks': []
            }
            current_week = {
                'num': 0,
                'title': 'Pre-Flight Checklist',
                'full_title': 'Week 0 — Pre-Flight Checklist',
                'days': [],
                '_day_counter': 0,  # auto-increment for duplicate day 0s
            }
            current_section['weeks'].append(current_week)
            sections.append(current_section)
            i += 1
            continue

        # Post-Week 20 section (auto-creates Week 21)
        postweek_match = re.match(r'^## Post-Week 20:', line)
        if postweek_match:
            current_section = {
                'title': 'Post-Sprint: Month 6–27',
                'type': 'postsprint',
                'weeks': []
            }
            current_week = {
                'num': 21,
                'title': 'Month 6–27 Plan',
                'full_title': 'Week 21 — Month 6–27 Plan',
                'days': [],
                '_day_counter': 0,
            }
            current_section['weeks'].append(current_week)
            sections.append(current_section)
            i += 1
            continue

        # Standard Phase section: ## Phase N: Title
        section_match = re.match(r'^## (Phase \d+:.+)', line)
        if section_match:
            current_section = {
                'title': section_match.group(1).strip(),
                'type': 'phase',
                'weeks': []
            }
            sections.append(current_section)
            current_week = None
            i += 1
            continue

        # Any other ## header (reference sections, kill-switches, etc.)
        # — stop parsing day rows into the previous section
        if re.match(r'^## ', line) and not preflight_match and not postweek_match:
            current_week = None
            current_section = None
            i += 1
            continue

        # Week header: ### Week N: Title  OR  ### Week N — Title
        week_match = re.match(r'^### (Week (\d+)\s*[–—\-:]\s*(.+))', line)
        if week_match:
            week_num = int(week_match.group(2))
            week_title = week_match.group(3).strip()
            current_week = {
                'num': week_num,
                'title': week_title,
                'full_title': week_match.group(1).strip(),
                'days': [],
                '_day_counter': 0,
            }
            if current_section:
                current_section['weeks'].append(current_week)
            i += 1
            continue

        # Day/month rows: | 0 |, | N |, | **N** |, | **N–M** |
        day_match = re.match(r'^\|\s*(?:\*\*)?(\d+(?:[–\-]\d+)?)(?:\*\*)?\s*\|(.+)$', line)
        if day_match and current_week:
            raw_num = day_match.group(1)
            rest = day_match.group(2)

            cells = [c.strip() for c in rest.split('|')]
            while cells and cells[-1] == '':
                cells.pop()

            morning = cells[0] if len(cells) > 0 else ''
            evening = cells[1] if len(cells) > 1 else ''

            # Auto-increment for unique IDs (handles duplicate day 0s)
            current_week['_day_counter'] += 1
            seq_num = current_week['_day_counter']

            current_week['days'].append({
                'num': seq_num,        # unique sequential number for IDs
                'raw_num': raw_num,    # original display number ("0", "7–9")
                'morning': morning,
                'evening': evening,
            })
            i += 1
            continue

        i += 1

    return sections


def build_day_details(day):
    parts = []
    if day['morning']:
        parts.append(f"🌅 {day['morning']}")
    if day['evening']:
        parts.append(f"🌙 {day['evening']}")
    return '|'.join(parts)


def build_week_details(week):
    parts = [f"⏱️ {len(week['days'])} items"]
    for day in week['days']:
        short = day['morning'][:80] if day['morning'] else f"Item {day['raw_num']}"
        parts.append(f"{day['raw_num']}: {short}")
    return '|'.join(parts)


def generate_html(sections):
    phase_config = {
        'preflight': {
            'num': 0,
            'label': 'PRE-FLIGHT',
            'emoji': '🚀',
            'short': 'Pre-Flight',
            'year_class': 'year-label-1',
        },
        'Phase 1': {
            'num': 1,
            'label': 'FOUNDATION REPAIR',
            'emoji': '⚡',
            'short': 'Foundation Repair',
            'year_class': 'year-label-1',
        },
        'Phase 2': {
            'num': 2,
            'label': 'CLOUD & DISTRIBUTION',
            'emoji': '☁️',
            'short': 'Cloud & Distribution',
            'year_class': 'year-label-1',
        },
        'Phase 3': {
            'num': 3,
            'label': 'DOCUMENTATION & PROOF',
            'emoji': '📋',
            'short': 'Documentation & Proof',
            'year_class': 'year-label-2',
        },
        'Phase 4': {
            'num': 4,
            'label': 'KSA/GCC MARKET ENTRY',
            'emoji': '🎯',
            'short': 'KSA/GCC Market Entry',
            'year_class': 'year-label-2',
        },
        'postsprint': {
            'num': 5,
            'label': 'POST-SPRINT',
            'emoji': '🔄',
            'short': 'Post-Sprint (Month 6–27)',
            'year_class': 'year-label-2',
        },
    }

    def get_phase(section):
        if section['type'] == 'preflight':
            return phase_config['preflight']
        elif section['type'] == 'postsprint':
            return phase_config['postsprint']
        else:
            # Extract "Phase N" from title
            m = re.match(r'(Phase \d+)', section['title'])
            key = m.group(1) if m else None
            return phase_config.get(key, phase_config['Phase 1'])

    total_weeks = sum(len(s['weeks']) for s in sections)
    total_days = sum(len(w['days']) for s in sections for w in s['weeks'])

    nodes_html = []

    for sec_idx, section in enumerate(sections):
        phase = get_phase(section)

        # Phase label
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

        # Main-node per phase
        phase_node_id = f"phase{phase['num']}"
        day_count = sum(len(w['days']) for w in weeks)
        phase_details = escape_detail(
            f"{phase['emoji']} {phase['short']}|"
            f"⏱️ {num_weeks} week{'s' if num_weeks != 1 else ''}|"
            f"📅 {day_count} items"
        )

        nodes_html.append(f'\n    <!-- PHASE {phase["num"]} BLOCK -->')
        nodes_html.append(
            f'    <div class="node main-node" id="{phase_node_id}" '
            f'data-parent="{phase_id}" data-side="center"\n'
            f'      data-details="{phase_details}">\n'
            f'      {phase["emoji"]} {escape_detail(phase["short"])}\n'
            f'      <span class="months-badge">{num_weeks} week{"s" if num_weeks != 1 else ""}</span>\n'
            f'    </div>'
        )

        # Weeks as sub-nodes
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

            # Day nodes
            for day in week['days']:
                day_id = f"{week_id}_d{day['num']}"
                day_details = escape_detail(build_day_details(day))

                day_label = day['morning'][:40] if day['morning'] else f"Item {day['raw_num']}"
                if day['morning'] and len(day['morning']) > 40:
                    day_label = day_label[:37] + '...'
                day_label = escape_detail(day_label)

                # Use raw_num for display (shows "0", "7–9", etc.)
                display_num = day['raw_num']

                nodes_html.append(
                    f'    <div class="node day-node" id="{day_id}" '
                    f'data-parent="{week_id}" data-side="{side}"\n'
                    f'      data-details="{day_details}">\n'
                    f'      Day {display_num} — {day_label}\n'
                    f'    </div>'
                )

        # Milestones
        if phase['num'] == 2:
            nodes_html.append(
                f'    <div class="node milestone-node" id="milestone_cloud" '
                f'data-parent="{phase_node_id}" data-side="center"\n'
                f'      data-details="🎉 Cloud pipeline working. Docker, CI/CD, Azure telemetry, industrial protocols integrated.">\n'
                f'      🎉 Cloud & Industrial Foundation Complete\n'
                f'    </div>'
            )
        elif phase['num'] == 3:
            nodes_html.append(
                f'    <div class="node milestone-node" id="milestone_portfolio" '
                f'data-parent="{phase_node_id}" data-side="center"\n'
                f'      data-details="🎉 Portfolio v1.0 locked. C4 diagrams, ADRs, video demo, CV EN+AR ready. 5 test apps sent.">\n'
                f'      🎉 Portfolio v1.0 Locked\n'
                f'    </div>'
            )

    # Final milestone
    nodes_html.append(
        f'    <div class="node milestone-node" id="milestone_final" '
        f'data-parent="phase5" data-side="center"\n'
        f'      data-details="🏆 KSA/GCC offer secured → 2-3 years experience → Blue Card experience route → Germany. No degree required.">\n'
        f'      🏆 Bridge Built — Germany Next\n'
        f'    </div>'
    )

    nodes_content = '\n'.join(nodes_html)

    full_html = f'''<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>20-Week KSA/GCC Extraction Roadmap</title>
  <meta name="description"
    content="A 20-week sprint roadmap for C#/.NET Integration Engineer — Biometric, Kiosk, Identity & Edge Systems targeting KSA/GCC as bridge to Germany.">
  <link rel="stylesheet" href="style.css">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>

<body>

  <!-- Header -->
  <header class="roadmap-header">
    <h1>20-Week KSA/GCC Extraction Roadmap</h1>
    <p class="header-subtitle">C#/.NET Integration Engineer &middot; Biometric & Kiosk Systems &middot; KSA &rarr; Germany &middot; {total_weeks} Weeks &middot; {total_days} Exercises</p>
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
      Daily: 45&ndash;90 min C# (Morning) + 15 min Anki (Evening).
      KSA &rarr; Germany. Right-click nodes to track progress.
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

    total_weeks = sum(len(s['weeks']) for s in sections)
    total_days = sum(len(w['days']) for s in sections for w in s['weeks'])
    print(f"Parsed {len(sections)} sections, {total_weeks} weeks, {total_days} days")

    for i, sec in enumerate(sections):
        print(f"  Section {i+1}: {sec['title']} ({sec['type']}) — {len(sec['weeks'])} weeks")
        for w in sec['weeks']:
            print(f"    Week {w['num']}: {w['title']} — {len(w['days'])} days")

    html_content = generate_html(sections)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\nGenerated index.html successfully ({len(html_content):,} bytes)")


if __name__ == '__main__':
    main()
