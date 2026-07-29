import json
from pathlib import Path

roots = [Path(r"C:\Program Files"), Path(r"C:\Program Files (x86)")]
items = []
for root in roots:
    if root.exists():
        items.extend(p.name for p in root.iterdir() if p.is_dir())
print(json.dumps(sorted(items)[:200]))
