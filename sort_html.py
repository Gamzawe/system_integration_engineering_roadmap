import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Isolate the canvas children
canvas_match = re.search(r'(<div class="roadmap-canvas" id="roadmapCanvas">.*?<svg class="connectors" id="connectorSvg"></svg>)(.*?)(</div>\s*<!-- \/Roadmap Canvas -->|</div>\s*</body>)', html, flags=re.DOTALL)

if not canvas_match:
    print("Could not find canvas")
    exit(1)

canvas_start = canvas_match.group(1)
canvas_content = canvas_match.group(2)
canvas_end = canvas_match.group(3)

# Extract rules callout
rules_match = re.search(r'(<div class="tip-callout"[^>]*>.*?</div>)', canvas_content, flags=re.DOTALL)
rules_callout = rules_match.group(1) if rules_match else ""

# Extract Phase labels (year-label)
phase_labels = {}
for m in re.finditer(r'(<div class="year-label[^>]*id="phase(\d+)Label"[^>]*>.*?</div>)', canvas_content, flags=re.DOTALL):
    phase_labels[int(m.group(2))] = m.group(1)

# Extract Month nodes (main-node)
month_nodes = {}
for m in re.finditer(r'(<!-- MONTH \d+ -->\s*<div class="node main-node"[^>]*id="month(\d+)"[^>]*>.*?</div>)', canvas_content, flags=re.DOTALL):
    month_nodes[int(m.group(2))] = m.group(1)
# if the <!-- MONTH --> comment isn't attached perfectly, just grab the div
month_nodes_fallback = {}
for m in re.finditer(r'(<div class="node main-node"[^>]*id="month(\d+)"[^>]*>.*?</div>)', canvas_content, flags=re.DOTALL):
    month_nodes_fallback[int(m.group(2))] = m.group(1)

for i in range(1, 17):
    if i not in month_nodes and i in month_nodes_fallback:
        month_nodes[i] = "  <!-- MONTH " + str(i) + " -->\n  " + month_nodes_fallback[i]

# Extract Sub nodes (Weeks) and their children
# We need to grab the sub-node and all day-nodes immediately following it.
# Instead of complex regex, we can just split the document by `<div class="node sub-node"` and parse.
# Actually, since Vis.js doesn't care if week nodes are grouped per month, we can just grab all `sub-node` and `day-node` and `tip-node` and re-inject them per month.
# Wait! Tip node for Year 1 ending!
year1_tip_match = re.search(r'(<div class="node tip-node" id="year1_complete"[^>]*>.*?</div>)', canvas_content, flags=re.DOTALL)
year1_tip = year1_tip_match.group(1) if year1_tip_match else ""

# Let's extract all weeks
weeks = {}
# A week block is the sub-node and any following day-nodes.
# It ends when another sub-node, main-node, year-label, or tip-node starts.
# To be safe, let's extract each week block by its ID.
week_blocks = {}
for m in range(1, 25):
    for w in range(1, 7): # some months had up to 4, some might have up to 6? Wait, IDs are 1..24 and 1..4.
        orig_id = f"m{m}w{w}"
        # Find this sub-node and all its day-nodes
        # Week starts at `<div class="node sub-node" id="<orig_id>"`
        # We can extract it by regex
        regex = f'(<div class="node sub-node" id="{orig_id}".*?(?=(<div class="node (?:sub|main|tip|phase|year)|</div>)))'
        # This regex might be tricky if it's the last element.
        pass

# Better approach: We know all weeks are mapped to months accurately by `data-parent="monthX"`.
# Let's just extract EVERYTHING into a list of nodes, and then sort them!
# A node is ideally `<div class="node ...` or `<div class="year-label ...` or `<div class="tip-callout ...`
node_matches = re.finditer(r'(<!--.*?-->\s*)?(<div class="(?:node|year-label|tip-callout)[^>]*>.*?</div>)', canvas_content, flags=re.DOTALL)
nodes = []
# Wait! Day nodes don't contain other divs, but sub-nodes don't either. The HTML is perfectly flat!
# Every node is just `<div class="..."> ... </div>`.

# Let's verify flat structure.
import bs4
soup = bs4.BeautifulSoup(html, "html.parser")
canvas = soup.find(id="roadmapCanvas")

# We can just iterate over `canvas.contents` (or children) and rebuild it.
new_canvas_children = []
connector_svg = soup.find(id="connectorSvg")
new_canvas_children.append(connector_svg)

rules_callout_el = soup.find(id="rulesCallout")
if rules_callout_el:
    new_canvas_children.append(rules_callout_el)

for phase_idx in range(1, 9):
    phase_label = soup.find(id=f"phase{phase_idx}Label")
    if phase_label:
        new_canvas_children.append(phase_label)
    
    # Months for this phase
    for m in range(1, 17):
        # Is this month in this phase?
        if (m - 1) // 2 + 1 == phase_idx:
            month_node = soup.find(id=f"month{m}")
            if month_node:
                # Add a comment
                new_canvas_children.append(bs4.Comment(f" MONTH {m} "))
                new_canvas_children.append(month_node)
            
            # Find all weeks that belong to this month
            weeks_in_month = canvas.find_all(lambda tag: tag.name == "div" and tag.get("data-parent") == f"month{m}" and "sub-node" in tag.get("class", []))
            for week in weeks_in_month:
                new_canvas_children.append(week)
                # Find all days that belong to this week
                days = canvas.find_all(lambda tag: tag.name == "div" and tag.get("data-parent") == week.get("id") and "day-node" in tag.get("class", []))
                for day in days:
                    new_canvas_children.append(day)
                    
            # Check for tip nodes belonging to this month
            tips = canvas.find_all(lambda tag: tag.name == "div" and tag.get("data-parent") == f"month{m}" and "tip-node" in tag.get("class", []))
            for tip in tips:
                new_canvas_children.append(tip)

# Clear canvas and append new children
canvas.clear()
for child in new_canvas_children:
    canvas.append(child)
    canvas.append("\n  ")

with open('index_sorted.html', 'w', encoding='utf-8') as f:
    f.write(str(soup))
print("Sorted HTML generated.")
