import json
import os
import platform

print(json.dumps({"platform": platform.platform(), "processor": platform.processor(), "cpu_count": os.cpu_count()}))
