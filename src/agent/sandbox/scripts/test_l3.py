
import json
from datetime import datetime

data = {
    "timestamp": datetime.now().isoformat(),
    "message": "Hello from L3 script!"
}

print(json.dumps(data, ensure_ascii=False, indent=2))
