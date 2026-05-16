"""Auto-refresh scheduler for soccer prediction data.

Runs refresh_data.py at a regular interval (default: every 4 hours).
6x/day for timely ESPN result pickup.
"""

import time
import sys
import subprocess
from pathlib import Path
from datetime import datetime

REFRESH_SCRIPT = Path(__file__).parent / "refresh_data.py"
DEFAULT_INTERVAL = 4 * 60 * 60  # 4 hours (6x/day)


def run_refresh():
    """Execute the data refresh script."""
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Running data refresh...")
    result = subprocess.run(
        [sys.executable, str(REFRESH_SCRIPT)],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode == 0:
        print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Refresh completed")
    else:
        print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Refresh failed: {result.stderr[-200:]}")
    return result.returncode == 0


def main(interval_seconds=DEFAULT_INTERVAL):
    """Run refresh on a loop with the given interval."""
    hours = interval_seconds / 3600
    print(f"Auto-refresh started (every {hours:.0f} hours)")
    print(f"Press Ctrl+C to stop\n")

    while True:
        run_refresh()
        print(f"\nNext refresh in {hours:.0f} hours...\n")
        try:
            time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\nAuto-refresh stopped")
            break


if __name__ == "__main__":
    interval = DEFAULT_INTERVAL
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1]) * 60  # argument in minutes
        except ValueError:
            print("Usage: python auto_refresh.py [interval_minutes]")
            print("  Default: 240 minutes (4 hours)")
            sys.exit(1)
    main(interval)
