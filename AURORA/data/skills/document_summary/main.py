import json
import sys

text = json.loads(sys.argv[1]).get("text", "") if len(sys.argv) > 1 else ""
sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
print(". ".join(sentences[:3]))
