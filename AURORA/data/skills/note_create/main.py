import json
import sys
import time
from pathlib import Path

args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
path = Path("notes")
path.mkdir(exist_ok=True)
out = path / f"{int(time.time())}.md"
out.write_text(args.get("text", ""), encoding="utf-8")
print(json.dumps({"path": str(out)}))
