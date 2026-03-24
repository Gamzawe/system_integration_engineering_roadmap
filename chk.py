import re

try:
    with open('index.html', encoding='utf-8') as f:
        html = f.read()

    months = re.findall(r'id="(month\d+)"', html)
    print("Found months:")
    print(sorted(set(months), key=lambda x: int(x[5:])))
except Exception as e:
    print("Error:", e)
