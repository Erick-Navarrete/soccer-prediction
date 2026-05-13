"""
Tableau Data Refresh Script

This script automates the data refresh process for Tableau dashboards.
It can be scheduled to run periodically to update prediction data.

Author: Soccer Prediction System
Date: 2026-04-29
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from datetime import datetime
import subprocess
import shutil
import json
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('outputs/tableau_data/refresh.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TableauDataRefresher:
    """Automated data refresh system for Tableau dashboards."""

    def __init__(self, base_dir="outputs"):
        """Initialize the refresher."""
        self.base_dir = Path(base_dir)
        self.tableau_dir = self.base_dir / "tableau_data"
        self.backup_dir = self.tableau_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)

        logger.info("Tableau Data Refresher initialized")
        logger.info(f"Base directory: {self.base_dir}")
        logger.info(f"Tableau directory: {self.tableau_dir}")

    def backup_current_data(self):
        """Backup current Tableau data files."""
        logger.info("Creating backup of current data files...")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)

        # Copy all CSV files
        for csv_file in self.tableau_dir.glob("*.csv"):
            shutil.copy2(csv_file, backup_path / csv_file.name)
            logger.info(f"Backed up: {csv_file.name}")

        # Copy JSON files
        for json_file in self.tableau_dir.glob("*.json"):
            shutil.copy2(json_file, backup_path / json_file.name)
            logger.info(f"Backed up: {json_file.name}")

        logger.info(f"Backup created at: {backup_path}")
        return backup_path

    def check_model_updates(self):
        """Check if the prediction model has been updated."""
        logger.info("Checking for model updates...")

        model_path = self.base_dir / "ensemble_model.pkl"
        predictions_path = self.base_dir / "predictions.csv"

        if not model_path.exists():
            logger.warning("Model file not found")
            return False

        if not predictions_path.exists():
            logger.warning("Predictions file not found")
            return False

        # Check file modification times
        model_mtime = model_path.stat().st_mtime
        predictions_mtime = predictions_path.stat().st_mtime

        # Check if predictions are newer than the last export
        export_marker = self.tableau_dir / "last_export.txt"
        if export_marker.exists():
            last_export_time = export_marker.stat().st_mtime
            if predictions_mtime > last_export_time:
                logger.info("New predictions available")
                return True
            else:
                logger.info("No new predictions since last export")
                return False
        else:
            logger.info("No previous export found - will export")
            return True

    def run_prediction_pipeline(self):
        """Run the main prediction pipeline to generate new data."""
        logger.info("Running prediction pipeline...")

        try:
            # Run the main prediction script
            result = subprocess.run(
                ["python", "src/main.py"],
                cwd=self.base_dir.parent,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                logger.info("Prediction pipeline completed successfully")
                return True
            else:
                logger.error(f"Prediction pipeline failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("Prediction pipeline timed out")
            return False
        except Exception as e:
            logger.error(f"Error running prediction pipeline: {e}")
            return False

    def export_tableau_data(self):
        """Export data in Tableau-ready format."""
        logger.info("Exporting Tableau-ready data...")

        try:
            # Run the export script
            result = subprocess.run(
                ["python", "export_tableau_data.py"],
                cwd=self.base_dir.parent,
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout
            )

            if result.returncode == 0:
                logger.info("Tableau data export completed successfully")
                return True
            else:
                logger.error(f"Tableau data export failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("Tableau data export timed out")
            return False
        except Exception as e:
            logger.error(f"Error exporting Tableau data: {e}")
            return False

    def create_refresh_summary(self):
        """Create a summary of the refresh process."""
        logger.info("Creating refresh summary...")

        summary = {
            "refresh_timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "refresh_status": "completed",
            "data_files": [],
            "model_info": {},
            "prediction_count": 0,
            "last_model_update": None
        }

        # Get data file information
        for csv_file in sorted(self.tableau_dir.glob("*.csv")):
            file_info = {
                "filename": csv_file.name,
                "size_bytes": csv_file.stat().st_size,
                "last_modified": datetime.fromtimestamp(csv_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                "record_count": len(pd.read_csv(csv_file)) if csv_file.stat().st_size > 0 else 0
            }
            summary["data_files"].append(file_info)

        # Get model information
        model_path = self.base_dir / "ensemble_model.pkl"
        if model_path.exists():
            summary["model_info"] = {
                "model_file": "ensemble_model.pkl",
                "size_bytes": model_path.stat().st_size,
                "last_modified": datetime.fromtimestamp(model_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            }

        # Get prediction count
        predictions_path = self.base_dir / "predictions.csv"
        if predictions_path.exists():
            try:
                predictions_df = pd.read_csv(predictions_path)
                summary["prediction_count"] = len(predictions_df)
            except Exception as e:
                logger.warning(f"Could not read predictions file: {e}")

        # Save summary
        summary_path = self.tableau_dir / "refresh_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Refresh summary saved to: {summary_path}")
        return summary

    def update_export_marker(self):
        """Update the marker file to track last export time."""
        marker_path = self.tableau_dir / "last_export.txt"
        with open(marker_path, 'w') as f:
            f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        logger.info(f"Export marker updated: {marker_path}")

    def cleanup_old_backups(self, keep_days=7):
        """Clean up old backup files."""
        logger.info(f"Cleaning up backups older than {keep_days} days...")

        cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)

        for backup_dir in self.backup_dir.glob("backup_*"):
            if backup_dir.is_dir() and backup_dir.stat().st_mtime < cutoff_time:
                try:
                    shutil.rmtree(backup_dir)
                    logger.info(f"Removed old backup: {backup_dir.name}")
                except Exception as e:
                    logger.warning(f"Could not remove backup {backup_dir.name}: {e}")

    def run_full_refresh(self, run_pipeline=False):
        """Run the complete refresh process."""
        logger.info("="*60)
        logger.info("TABLEAU DATA REFRESH - FULL PROCESS")
        logger.info("="*60)

        try:
            # Step 1: Backup current data
            self.backup_current_data()

            # Step 2: Optionally run prediction pipeline
            if run_pipeline:
                logger.info("Running prediction pipeline...")
                if not self.run_prediction_pipeline():
                    logger.error("Prediction pipeline failed, aborting refresh")
                    return False
            else:
                logger.info("Skipping prediction pipeline (using existing data)")

            # Step 3: Check for updates
            if not self.check_model_updates():
                logger.info("No new data to export")
                return True

            # Step 4: Export Tableau data
            if not self.export_tableau_data():
                logger.error("Tableau data export failed")
                return False

            # Step 5: Create refresh summary
            summary = self.create_refresh_summary()

            # Step 6: Update export marker
            self.update_export_marker()

            # Step 7: Cleanup old backups
            self.cleanup_old_backups()

            logger.info("="*60)
            logger.info("REFRESH COMPLETE")
            logger.info("="*60)
            logger.info(f"Total predictions: {summary['prediction_count']}")
            logger.info(f"Data files created: {len(summary['data_files'])}")
            logger.info(f"Refresh timestamp: {summary['refresh_timestamp']}")

            return True

        except Exception as e:
            logger.error(f"Error during refresh process: {e}")
            return False

    def run_quick_refresh(self):
        """Run a quick refresh (export only, no pipeline)."""
        logger.info("Running quick refresh (export only)...")
        return self.run_full_refresh(run_pipeline=False)

    def run_scheduled_refresh(self):
        """Run a scheduled refresh with pipeline."""
        logger.info("Running scheduled refresh (with pipeline)...")
        return self.run_full_refresh(run_pipeline=True)


def main():
    """Main function to run the refresh process."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Tableau Data Refresh System'
    )
    parser.add_argument(
        '--mode',
        type=str,
        choices=['quick', 'scheduled', 'full'],
        default='quick',
        help='Refresh mode: quick (export only), scheduled (with pipeline), full (with pipeline)'
    )
    parser.add_argument(
        '--base-dir',
        type=str,
        default='outputs',
        help='Base directory for data files'
    )

    args = parser.parse_args()

    # Create refresher
    refresher = TableauDataRefresher(base_dir=args.base_dir)

    # Run appropriate refresh
    if args.mode == 'quick':
        success = refresher.run_quick_refresh()
    elif args.mode == 'scheduled':
        success = refresher.run_scheduled_refresh()
    else:  # full
        success = refresher.run_full_refresh(run_pipeline=True)

    # Exit with appropriate code
    exit(0 if success else 1)


if __name__ == "__main__":
    main()