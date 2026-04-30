"""
Simple Tableau Data Refresh

A simplified version that's easier to run and troubleshoot.
"""

import os
import sys
from pathlib import Path

def main():
    """Simple refresh function."""
    print("="*60)
    print("SIMPLE TABLEAU DATA REFRESH")
    print("="*60)

    # Get current directory
    current_dir = Path.cwd()
    print(f"Current directory: {current_dir}")

    # Check if we're in the right place
    if not (current_dir / "export_tableau_data.py").exists():
        print("ERROR: export_tableau_data.py not found!")
        print("Please run this script from the soccer-prediction directory")
        print("Expected location: D:\\Project_App\\soccer-prediction")
        return False

    try:
        print("\nStep 1: Running export script...")
        import subprocess
        result = subprocess.run(
            ["python", "export_tableau_data.py"],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            print("[OK] Export completed successfully!")
            print("\nStep 2: Checking output files...")

            tableau_dir = current_dir / "outputs" / "tableau_data"
            csv_files = list(tableau_dir.glob("*.csv"))

            print(f"[OK] Found {len(csv_files)} CSV files")
            print("\nData files ready for Tableau:")
            for csv_file in sorted(csv_files):
                size = csv_file.stat().st_size
                print(f"  - {csv_file.name} ({size} bytes)")

            print("\n" + "="*60)
            print("REFRESH COMPLETE!")
            print("="*60)
            print(f"Data location: {tableau_dir}")
            print("Ready to use in Tableau Desktop 2019.3")
            return True

        else:
            print("[ERROR] Export failed!")
            print(f"Error: {result.stderr}")
            return False

    except Exception as e:
        print(f"[ERROR] Error occurred: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)