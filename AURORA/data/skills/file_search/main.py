import json
import sys
from pathlib import Path

args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
root = Path(args.get("root", ".")).resolve()
query = str(args.get("query", "")).lower()
matches = [str(p) for p in root.rglob("*") if query in p.name.lower()][:100]
print(json.dumps(matches))
