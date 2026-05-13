"""Build script for Render deployment.

Creates empty data JSON files if missing, then runs initial data refresh.
"""
import json
from pathlib import Path

DATA = Path(__file__).parent / "data"
DATA.mkdir(exist_ok=True)

# Ensure data files exist (empty but valid JSON)
defaults = {
    "summary": {},
    "predictions": [],
    "historical": [],
    "team_stats": [],
    "performance": {},
    "insights": [],
}

for name, default in defaults.items():
    p = DATA / f"{name}.json"
    if not p.exists():
        with open(p, "w") as f:
            json.dump(default, f)
        print(f"Created {name}.json")

# Run initial data refresh
import subprocess
import sys
print("Running initial data refresh...")
result = subprocess.run(
    [sys.executable, str(Path(__file__).parent / "refresh_data.py")],
    capture_output=True, text=True, timeout=120,
)
if result.returncode == 0:
    print("Initial data refresh successful")
else:
    print(f"Initial refresh failed (non-fatal): {result.stderr[-200:]}")
