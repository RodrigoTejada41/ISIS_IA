import json
import sys
from pathlib import Path

args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
root = Path(args.get("root", ".")).resolve()
items = [{"path": str(p), "mtime": p.stat().st_mtime} for p in root.iterdir() if p.is_dir()]
print(json.dumps(sorted(items, key=lambda x: x["mtime"], reverse=True)[:100]))
