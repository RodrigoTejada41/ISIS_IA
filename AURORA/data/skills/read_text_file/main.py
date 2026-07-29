import sys
from pathlib import Path

path = Path((__import__("json").loads(sys.argv[1]) if len(sys.argv) > 1 else {}).get("path", ""))
if path.suffix.lower() not in {".txt", ".md"}:
    raise SystemExit("unsupported file type")
print(path.read_text(encoding="utf-8")[:12000])
