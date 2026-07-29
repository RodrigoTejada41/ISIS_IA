import json
import sys
from pathlib import Path

query = (json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}).get("query", "").lower()
matches = []
for item in Path("notes").glob("*.md"):
    text = item.read_text(encoding="utf-8")
    if query in text.lower():
        matches.append({"path": str(item), "preview": text[:200]})
print(json.dumps(matches))
