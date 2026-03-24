import re

with open('index.html', encoding='utf-8') as f:
    html = f.read()

days = re.findall(r'class="node day-node"', html)
print(f"Total day nodes found: {len(days)}")

expected = 96 * 5
print(f"Expected: {expected}")
