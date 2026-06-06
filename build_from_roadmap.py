#!/usr/bin/env python3
"""
Parse roadmap.txt (markdown with week/day tables) and generate index.html
for the interactive flowchart engine.
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
    
    sections = []  # Top-level sections (## MONTHS X-Y: ...)
    current_section = None
    current_week = None
    
    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\r')
        
        # Match top-level section: ## MONTHS 1–3: ...
        section_match = re.match(r'^## (MONTHS? \d+[–-]\d+:.+)', line)
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
        
        # Match table rows: | **N** | Study | Practice | Build | Output | Self-Check |
        day_match = re.match(r'^\|\s*\*\*(\d+)\*\*\s*\|(.+)$', line)
        if day_match and current_week:
            day_num = int(day_match.group(1))
            rest = day_match.group(2)
            
            # Split by | but handle the trailing |
            cells = [c.strip() for c in rest.split('|')]
            # Remove empty trailing cell
            while cells and cells[-1] == '':
                cells.pop()
            
            # Cells: Study, Practice, Build & Push, Output, Self-Check
            study = cells[0] if len(cells) > 0 else ''
            practice = cells[1] if len(cells) > 1 else ''
            build = cells[2] if len(cells) > 2 else ''
            output = cells[3] if len(cells) > 3 else ''
            check = cells[4] if len(cells) > 4 else ''
            
            current_week['days'].append({
                'num': day_num,
                'study': study,
                'practice': practice,
                'build': build,
                'output': output,
                'check': check
            })
            i += 1
            continue
        
        # Handle the special last section (Weeks 46-52)
        special_match = re.match(r'^\|\s*\*\*(Daily Operations|Negotiation Phase|Final Output)\*\*\s*\|(.+)$', line)
        if special_match and current_week:
            label = special_match.group(1)
            desc = special_match.group(2).strip().rstrip('|').strip()
            # Clean up multi-line formatting
            desc = re.sub(r'\s*\*\*\d+\.\*\*\s*', ' ', desc)
            desc = desc.replace('  ', ' ').strip()
            current_week['days'].append({
                'num': len(current_week['days']) + 1,
                'study': f'{label}: {desc}',
                'practice': '',
                'build': '',
                'output': '',
                'check': ''
            })
            i += 1
            continue
        
        i += 1
    
    return sections


def build_day_details(day, week_title):
    """Build pipe-delimited data-details string for a day node."""
    parts = []
    if day['study']:
        parts.append(f"📖 Study: {day['study']}")
    if day['practice']:
        parts.append(f"🔧 Practice: {day['practice']}")
    if day['build']:
        parts.append(f"🏗️ Build: {day['build']}")
    if day['output']:
        parts.append(f"📦 Output: {day['output']}")
    if day['check']:
        parts.append(f"✅ Self-Check: {day['check']}")
    return '|'.join(parts)


def build_week_details(week):
    """Build pipe-delimited data-details string for a week node."""
    parts = [f"⏱️ ~10 hours"]
    for day in week['days']:
        short = day['study'][:80] if day['study'] else f"Day {day['num']}"
        parts.append(f"Day {day['num']}: {short}")
    return '|'.join(parts)


def generate_html(sections):
    """Generate the full index.html content."""
    
    # Define phase groupings based on sections
    phase_config = [
        {
            'num': 1,
            'label': 'ZERO-ALLOCATION C#, PYTHON INJECTION & INTEROP',
            'emoji': '⚡',
            'short': 'Zero-Allocation C# & Interop',
            'year_class': 'year-label-1',
            'months_range': 'Months 1–3'
        },
        {
            'num': 2,
            'label': 'EDGE ORCHESTRATION & INDUSTRIAL PROTOCOLS',
            'emoji': '🏭',
            'short': 'Edge Orchestration & Protocols',
            'year_class': 'year-label-1',
            'months_range': 'Months 4–7'
        },
        {
            'num': 3,
            'label': 'CQRS, KAFKA, & OBSERVABILITY',
            'emoji': '📊',
            'short': 'CQRS, Kafka & Observability',
            'year_class': 'year-label-2',
            'months_range': 'Months 8–10'
        },
        {
            'num': 4,
            'label': 'CLOUD SOVEREIGNTY & CYBERSECURITY',
            'emoji': '🔐',
            'short': 'Cloud Sovereignty & Security',
            'year_class': 'year-label-2',
            'months_range': 'Months 11–13'
        },
        {
            'num': 5,
            'label': 'CAPSTONE, UI, C4 MODELS, & MARKET EXECUTION',
            'emoji': '🎯',
            'short': 'Capstone & Market Execution',
            'year_class': 'year-label-2',
            'months_range': 'Months 14–19'
        },
    ]
    
    # Count total weeks and days for subtitle
    total_weeks = sum(len(s['weeks']) for s in sections)
    total_days = sum(len(w['days']) for s in sections for w in s['weeks'])
    
    # Build all nodes
    nodes_html = []
    
    week_global_idx = 0
    
    for sec_idx, section in enumerate(sections):
        phase = phase_config[sec_idx] if sec_idx < len(phase_config) else phase_config[-1]
        
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
        
        # Group weeks into months (4 weeks per month roughly, matching original structure)
        weeks = section['weeks']
        
        # Calculate months for this section
        # Map section month ranges
        month_ranges = [
            (1, 3),   # Section 0: Months 1-3
            (4, 7),   # Section 1: Months 4-7
            (8, 10),  # Section 2: Months 8-10
            (11, 13), # Section 3: Months 11-13
            (14, 19), # Section 4: Months 14-19
        ]
        
        start_month, end_month = month_ranges[sec_idx] if sec_idx < len(month_ranges) else (1, 1)
        num_months = end_month - start_month + 1
        
        # Distribute weeks across months as evenly as possible
        weeks_per_month = []
        total_section_weeks = len(weeks)
        base = total_section_weeks // num_months
        remainder = total_section_weeks % num_months
        
        for m in range(num_months):
            count = base + (1 if m < remainder else 0)
            weeks_per_month.append(count)
        
        week_offset = 0
        for m_idx in range(num_months):
            month_num = start_month + m_idx
            month_id = f"month{month_num}"
            
            # Determine parent
            if m_idx == 0:
                parent = phase_id
            else:
                parent = f"month{month_num - 1}"
            
            # Month title
            month_week_count = weeks_per_month[m_idx]
            month_hours = month_week_count * 10
            
            month_details = escape_detail(
                f"{phase['emoji']} {phase['short']}|"
                f"⏱️ ~{month_hours} hrs ({month_week_count} weeks × 10 hrs)|"
                f"📅 15 hours per week"
            )
            
            nodes_html.append(f'\n    <!-- MONTH {month_num} -->')
            nodes_html.append(
                f'    <div class="node main-node" id="{month_id}" '
                f'data-parent="{parent}" data-side="center"\n'
                f'      data-details="{month_details}">\n'
                f'      {phase["emoji"]} Month {month_num}: {escape_detail(phase["short"])}\n'
                f'      <span class="months-badge">~{month_hours} hrs</span>\n'
                f'    </div>'
            )
            
            # Add weeks for this month
            for w_local in range(month_week_count):
                if week_offset >= len(weeks):
                    break
                    
                week = weeks[week_offset]
                week_num = week['num']
                week_id = f"w{week_num}"
                side = "left" if w_local % 2 == 0 else "right"
                
                week_details = escape_detail(build_week_details(week))
                week_label = escape_detail(week['title'])
                
                # Check if week has days
                has_days_class = ' has-days' if week['days'] else ''
                
                nodes_html.append(
                    f'    <div class="node sub-node{has_days_class}" id="{week_id}" '
                    f'data-parent="{month_id}" data-side="{side}"\n'
                    f'      data-details="{week_details}">\n'
                    f'      📅 Week {week_num}: {week_label}\n'
                    f'    </div>'
                )
                
                # Add day nodes
                for day in week['days']:
                    day_id = f"{week_id}_d{day['num']}"
                    day_details = escape_detail(build_day_details(day, week['title']))
                    
                    # Short day label
                    day_label = day['study'][:40] if day['study'] else f"Day {day['num']}"
                    # Truncate with ellipsis if needed
                    if len(day['study']) > 40:
                        day_label = day_label[:37] + '...'
                    day_label = escape_detail(day_label)
                    
                    nodes_html.append(
                        f'    <div class="node day-node" id="{day_id}" '
                        f'data-parent="{week_id}" data-side="{side}"\n'
                        f'      data-details="{day_details}">\n'
                        f'      Day {day["num"]} — {day_label}\n'
                        f'    </div>'
                    )
                
                week_offset += 1
                week_global_idx += 1
        
        # Add milestone after section if appropriate
        if sec_idx == 1:  # After Phase 2 (Edge Orchestration)
            nodes_html.append(
                f'    <div class="node milestone-node" id="milestone_edge" '
                f'data-parent="month{end_month}" data-side="center"\n'
                f'      data-details="🎉 Edge foundations complete — you can build, deploy, and communicate with industrial hardware.">\n'
                f'      🎉 Edge Foundations Complete\n'
                f'    </div>'
            )
        elif sec_idx == 3:  # After Phase 4 (Cloud & Security)
            nodes_html.append(
                f'    <div class="node milestone-node" id="milestone_cloud" '
                f'data-parent="month{end_month}" data-side="center"\n'
                f'      data-details="🎉 Cloud sovereignty and cybersecurity — your system is production-grade and compliant.">\n'
                f'      🎉 Production-Grade Architecture\n'
                f'    </div>'
            )
    
    # Final milestone
    nodes_html.append(
        f'    <div class="node milestone-node" id="milestone_final" '
        f'data-parent="month19" data-side="center"\n'
        f'      data-details="🏆 The Contract is Signed. The Extraction is Complete.">\n'
        f'      🏆 Mission Complete — Contract Signed\n'
        f'    </div>'
    )
    
    nodes_content = '\n'.join(nodes_html)
    
    # Total weeks for subtitle
    total_weeks_display = total_weeks
    total_days_display = total_days
    
    full_html = f'''<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Systems Integration Engineering Roadmap</title>
  <meta name="description"
    content="A structured learning roadmap for .NET Systems Integration Engineering — from zero-allocation C# to dual-cloud sovereignty.">
  <link rel="stylesheet" href="style.css">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>

<body>

  <!-- Header -->
  <header class="roadmap-header">
    <h1>Systems Integration Engineering Roadmap</h1>
    <p class="header-subtitle">Zero-Allocation C# &middot; Industrial Protocols &middot; Dual-Cloud Sovereignty &middot; {total_weeks_display} Weeks &middot; {total_days_display} Exercises</p>
    <div class="progress-bar-container">
      <div class="progress-bar" id="progressBar">
        <span class="progress-text" id="progressText">0%</span>
      </div>
    </div>
  </header>

  <!-- Legend -->
  <div class="legend">
    <div class="legend-item"><span class="legend-swatch main-swatch"></span> Month</div>
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
      Weekly pattern: Study &middot; Practice &middot; Build &amp; Push &middot; Self-Check.
      Each week has 5 focused days. Right-click nodes to track progress.
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
