import re

# Read original 24-month index.html
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update Header metadata
html = html.replace('24-Month .NET Backend Roadmap', '16-Month .NET Backend Roadmap')
html = re.sub(r'<p class="header-subtitle">.*?</p>', '<p class="header-subtitle">Backend Engineering &middot; Systems Integration &middot; 15 hrs/week</p>', html)

# Isolate the canvas children
canvas_match = re.search(r'(<div class="roadmap-canvas"[^>]*>)(.*?)(</div>\s*<!-- \/Roadmap Canvas -->|</div>\s*</body>|<script src="script.js"></script>)', html, flags=re.DOTALL | re.IGNORECASE)
if not canvas_match:
    print("Could not find canvas")
    exit(1)

canvas_start = canvas_match.group(1)
canvas_content = canvas_match.group(2)
# Reconstruct canvas_end correctly
canvas_end_index = canvas_match.end(2)
canvas_end = html[canvas_end_index:]

# Extract SVG
svg_match = re.search(r'(<svg class="connectors"[^>]*>.*?</svg>)', canvas_content, flags=re.DOTALL)
connector_svg = svg_match.group(1) if svg_match else ''

# Extract Rules Callout
rules_match = re.search(r'(<div class="tip-callout"[^>]*id="rulesCallout"[^>]*>.*?</div>)', canvas_content, flags=re.DOTALL)
if rules_match:
    rules_callout = rules_match.group(1)
    rules_callout = re.sub(r'Weekly pattern: .*?refactor\.', 'Weekly pattern: 6 hrs learning &middot; 6 hrs building &middot; 3 hrs review/refactor/notes. Every month: 1 deliverable, 1 GitHub push, 1 README update, 1 refactor.', rules_callout)
else:
    rules_callout = ''

# Parse all nodes from canvas
node_pattern = r'(<!--.*?-->\s*)?(<div class="(?:node|year-label|tip-callout)[^>]*id="([^"]+)"[^>]*>.*?</div>)'
all_nodes = {}
for m in re.finditer(node_pattern, canvas_content, flags=re.DOTALL):
    full_html = m.group(0)
    node_id = m.group(3)
    all_nodes[node_id] = m.group(2) # just the div, ignore comments

# Also grab day nodes which might not have been matched or what?
# Wait, day nodes have class="node day-node", they MATCH the regex!
# Tip nodes: class="node tip-node" MATCH!

# Map old weeks 1..96
# We need an ordered list of all weeks to distribute them 6 per month.
ordered_weeks = []
for m in range(1, 25):
    for w in range(1, 5): # original was 4 weeks per month
        wid = f"m{m}w{w}"
        if wid in all_nodes:
            ordered_weeks.append(wid)

# Start building the new canvas content in exact physical DOM order
new_content = [connector_svg, rules_callout]

phase_titles = [
    ("Core Language and Logic", "🏁"),
    ("Object-Oriented Design", "🏗️"),
    ("APIs and Data", "🔌"),
    ("Reliability and Operability", "🛡️"),
    ("Advanced Messaging", "📨"),
    ("Cloud and Delivery", "☁️"),
    ("Real-World Experience", "🛠️"),
    ("Interview Preparation", "🎯")
]

# Extract the year1 milestone if it exists
year1_milestone = all_nodes.get("year1_complete", "")

week_index = 0
for new_m in range(1, 17):
    phase_idx = (new_m - 1) // 2
    part = 1 if new_m % 2 != 0 else 2
    phase_num = phase_idx + 1
    
    # If first month of phase, Output Phase Label
    if part == 1:
        phase_label_id = f"phase{phase_num}Label"
        if phase_label_id in all_nodes:
            new_content.append(all_nodes[phase_label_id])
        else:
            # Fallback Phase Label creation
            title, emoji = phase_titles[phase_idx]
            new_content.append(f'<div class="year-label year-label-1" id="phase{phase_num}Label" data-parent="" data-side="center">⚡ PHASE {phase_num}<br><small>{title}</small></div>')
            
    # Determine parent for the Month Node
    if part == 1:
        parent = f'phase{phase_num}Label'
    else:
        parent = f'month{new_m-1}'
        
    # Output Month Node
    title, emoji = phase_titles[phase_idx]
    month_html = f'''  <!-- MONTH {new_m} -->
  <div class="node main-node" id="month{new_m}" data-parent="{parent}" data-side="center"
       data-details="{emoji} {title}|⏱️ ~60 hrs (6 weeks × 10 hrs)|📅 15 hours per week">
    {emoji} Month {new_m}: {title} (Part {part})
    <span class="months-badge">~60 hrs</span>
  </div>'''
    new_content.append(month_html)
    
    # 6 Weeks for this month
    for w in range(6):
        if week_index < len(ordered_weeks):
            week_id = ordered_weeks[week_index]
            week_html = all_nodes[week_id]
            
            # Update data-parent and data-side!
            # Weeks 0, 1, 2 on left. Weeks 3, 4, 5 on right. This creates visual balance!
            side = "left" if w < 3 else "right"
            
            week_html = re.sub(r'data-parent="[^"]+"', f'data-parent="month{new_m}"', week_html)
            week_html = re.sub(r'data-side="[^"]+"', f'data-side="{side}"', week_html)
            new_content.append(week_html)
            
            # Find and output DAY nodes for this week
            for d in range(1, 8):
                day_id = f"{week_id}_d{d}"
                if day_id in all_nodes:
                    day_html = all_nodes[day_id]
                    # Update day side to match week side!
                    day_html = re.sub(r'data-side="[^"]+"', f'data-side="{side}"', day_html)
                    new_content.append(day_html)
                    
            week_index += 1
            
    # At the end of Month 8, insert the year 1 milestone!
    if new_m == 8:
        if year1_milestone:
            # Update its data-parent to month8
            y1_html = re.sub(r'data-parent="[^"]+"', 'data-parent="month8"', year1_milestone)
            new_content.append(y1_html)
        else:
            # Fallback creation
            new_content.append(f'''  <div class="node tip-node" id="year1_complete" data-parent="month8" data-side="center"
       data-details="Milestone reached: From absolute beginner to persistent, integrated backend architecture.">
    🎉 Year 1 complete (~480 hrs)
  </div>''')

new_canvas_html = canvas_start + "\n  " + "\n  ".join(new_content) + "\n"

final_html = html[:canvas_match.start()] + new_canvas_html + canvas_end

with open('index_built.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

print("Generated index_built.html successfully.")
