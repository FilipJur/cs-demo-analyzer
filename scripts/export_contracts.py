"""Export the real route/DTO schema without starting a runtime or opening data."""
import json
from pathlib import Path

from cs_demo_analyzer.api.routes import create_app

root = Path(__file__).resolve().parents[1]
output = root / "contracts/openapi.json"
output.parent.mkdir(exist_ok=True)
output.write_text(json.dumps(create_app(None, manage_lifetime=False).openapi(), indent=2) + "\n")
print(output)
