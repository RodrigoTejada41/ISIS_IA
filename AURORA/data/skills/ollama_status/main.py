import json
import shutil

print(json.dumps({"available": shutil.which("ollama") is not None}))
