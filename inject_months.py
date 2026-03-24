import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

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

new_months = []
for m in range(1, 17):
    phase_idx = (m - 1) // 2
    phase_num = phase_idx + 1
    part = 1 if m % 2 != 0 else 2
    title, emoji = phase_titles[phase_idx]

    # For odd months, parent is phase Label. For even months, parent is the previous month.
    if part == 1:
        parent = f'phase{phase_num}Label'
    else:
        parent = f'month{m-1}'

    month_html = f'''  <!-- MONTH {m} -->
  <div class="node main-node" id="month{m}" data-parent="{parent}" data-side="center"
       data-details="{emoji} {title}|⏱️ ~60 hrs (6 weeks × 10 hrs)|📅 15 hours per week">
    {emoji} Month {m}: {title} (Part {part})
    <span class="months-badge">~60 hrs</span>
  </div>'''
    new_months.append(month_html)

months_str = '\\n'.join(new_months)

# Inject them right before the closing div of roadmapCanvas
# <div class="roadmap-canvas" id="roadmapCanvas"> ... </div>
# Finding the final </div> of the file is easy, but better to inject anywhere safe.
# Let's insert right after `<svg class="connectors" id="connectorSvg"></svg>`
html = re.sub(r'(<svg class="connectors" id="connectorSvg"></svg>)', f'\\g<1>\\n{months_str}\\n', html)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Injected month nodes.")
