import re

with open('index.html', encoding='utf-8') as f:
    html = f.read()

months = set(re.findall(r'id="(month\d+)"', html))
expected = {f'month{i}' for i in range(1, 25)}
missing = expected - months

print("Missing months:", sorted(list(missing), key=lambda x: int(x[5:])))

missing_weeks = []
for m in range(1, 25):
    for w in range(1, 5):
        wid = f'm{m}w{w}'
        if f'id="{wid}"' not in html:
            missing_weeks.append(wid)

print(f"Missing weeks ({len(missing_weeks)}):", missing_weeks)

missing_days = []
for m in range(1, 25):
    for w in range(1, 5):
        for d in range(1, 6):
            did = f'm{m}w{w}_d{d}'
            if f'id="{did}"' not in html:
                missing_days.append(did)

print(f"Missing days ({len(missing_days)}):", missing_days)
