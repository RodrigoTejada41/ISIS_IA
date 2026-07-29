import json
import shutil
import subprocess

if not shutil.which("ollama"):
    print(json.dumps({"available": False, "models": []}))
else:
    out = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=8)
    print(json.dumps({"available": True, "output": out.stdout}))
