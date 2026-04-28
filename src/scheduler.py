"""
Regular Data Updates Module

This module provides automated scheduling for regular data fetching and
prediction generation using the schedule library.
"""

import schedule
import time
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd
import json

from main import main as run_pipeline
from claude_integration import get_claude_client, generate_prediction_report
from ml_models import predict_match

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('outputs/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PredictionScheduler:
    """
    Scheduler for automated data updates and prediction generation.
    """

    def __init__(self, output_dir: str = "outputs"):
        """
        Initialize the scheduler.

        Args:
            output_dir: Directory for storing predictions and logs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.predictions_dir = self.output_dir / "predictions"
        self.predictions_dir.mkdir(exist_ok=True)

    def run_full_pipeline(self):
        """Run the full prediction pipeline."""
        logger.info("="*60)
        logger.info("Running full prediction pipeline")
        logger.info("="*60)

        try:
            # Run the main pipeline
            import sys
            import argparse

            # Simulate command line arguments
            sys.argv = [
                'main.py',
                '--seasons', '2425,2324,2223',
                '--leagues', 'E0,SP1,D1',
                '--skip-polymarket',
                '--skip-claude',
                '--skip-backtest',
                '--skip-visualization'
            ]

            run_pipeline()

            logger.info("Pipeline completed successfully")

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise

    def fetch_latest_data(self):
        """Fetch the latest match data."""
        logger.info("Fetching latest match data...")

        try:
            from data_loader import FootballDataLoader, DataCleaner

            # Load current season data
            loader = FootballDataLoader(
                seasons=["2425"],
                leagues=["E0", "SP1", "D1", "I1", "F1"]
            )
            raw_data = loader.load_all()

            if not raw_data.empty:
                clean_data = DataCleaner.clean(raw_data)

                # Save to file
                data_file = self.output_dir / "latest_data.csv"
                clean_data.to_csv(data_file, index=False)
                logger.info(f"Saved {len(clean_data)} matches to {data_file}")

                return clean_data
            else:
                logger.warning("No new data found")
                return None

        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return None

    def generate_upcoming_predictions(self):
        """Generate predictions for upcoming matches."""
        logger.info("Generating predictions for upcoming matches...")

        try:
            # Load latest data
            data_file = self.output_dir / "latest_data.csv"

            if not data_file.exists():
                logger.warning("No data file found. Run fetch_latest_data first.")
                return

            data = pd.read_csv(data_file)
            data["Date"] = pd.to_datetime(data["Date"])

            # Find upcoming matches (matches in the future)
            today = pd.Timestamp.now()
            upcoming = data[data["Date"] > today].sort_values("Date")

            if upcoming.empty:
                logger.info("No upcoming matches found")
                return

            logger.info(f"Found {len(upcoming)} upcoming matches")

            # Load trained model
            model_file = self.output_dir / "ensemble_model.pkl"
            scaler_file = self.output_dir / "scaler.pkl"

            if not (model_file.exists() and scaler_file.exists()):
                logger.warning("Trained model not found. Run full pipeline first.")
                return

            import pickle
            with open(model_file, 'rb') as f:
                ensemble = pickle.load(f)
            with open(scaler_file, 'rb') as f:
                scaler = pickle.load(f)

            # Generate predictions
            predictions = []

            for _, match in upcoming.iterrows():
                # Extract features (simplified - in practice, you'd need to
                # recreate the full feature engineering pipeline)
                prediction = {
                    "date": match["Date"].strftime("%Y-%m-%d"),
                    "home_team": match["HomeTeam"],
                    "away_team": match["AwayTeam"],
                    "league": match.get("League", "Unknown"),
                    "prediction": "TBD",  # Would need proper feature extraction
                    "confidence": 0.0,
                    "home_prob": 0.0,
                    "draw_prob": 0.0,
                    "away_prob": 0.0
                }
                predictions.append(prediction)

            # Save predictions
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pred_file = self.predictions_dir / f"predictions_{timestamp}.json"

            with open(pred_file, 'w') as f:
                json.dump(predictions, f, indent=2)

            logger.info(f"Saved {len(predictions)} predictions to {pred_file}")

            return predictions

        except Exception as e:
            logger.error(f"Failed to generate predictions: {e}")
            return None

    def generate_daily_report(self):
        """Generate a daily prediction report."""
        logger.info("Generating daily report...")

        try:
            # Get latest predictions
            pred_files = sorted(self.predictions_dir.glob("predictions_*.json"))

            if not pred_files:
                logger.warning("No prediction files found")
                return

            latest_pred_file = pred_files[-1]

            with open(latest_pred_file, 'r') as f:
                predictions = json.load(f)

            # Generate report
            report = {
                "generated_at": datetime.now().isoformat(),
                "total_predictions": len(predictions),
                "predictions": predictions[:10]  # First 10 predictions
            }

            report_file = self.output_dir / "daily_report.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)

            logger.info(f"Daily report saved to {report_file}")

            return report

        except Exception as e:
            logger.error(f"Failed to generate daily report: {e}")
            return None

    def cleanup_old_files(self, days: int = 7):
        """Clean up old prediction files."""
        logger.info(f"Cleaning up files older than {days} days...")

        try:
            from datetime import timedelta

            cutoff = datetime.now() - timedelta(days=days)

            # Clean up old prediction files
            for file in self.predictions_dir.glob("predictions_*.json"):
                file_time = datetime.fromtimestamp(file.stat().st_mtime)
                if file_time < cutoff:
                    file.unlink()
                    logger.info(f"Deleted old file: {file}")

            logger.info("Cleanup completed")

        except Exception as e:
            logger.error(f"Failed to cleanup: {e}")


def run_scheduler():
    """Run the scheduler with predefined jobs."""
    scheduler = PredictionScheduler()

    # Schedule jobs
    schedule.every().day.at("06:00").do(scheduler.run_full_pipeline)
    schedule.every().day.at("12:00").do(scheduler.fetch_latest_data)
    schedule.every().day.at("18:00").do(scheduler.generate_upcoming_predictions)
    schedule.every().day.at("20:00").do(scheduler.generate_daily_report)
    schedule.every().sunday.at("03:00").do(scheduler.cleanup_old_files)

    logger.info("Scheduler started. Press Ctrl+C to stop.")
    logger.info("Scheduled jobs:")
    logger.info("  06:00 - Run full pipeline")
    logger.info("  12:00 - Fetch latest data")
    logger.info("  18:00 - Generate upcoming predictions")
    logger.info("  20:00 - Generate daily report")
    logger.info("  Sunday 03:00 - Cleanup old files")

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")


def run_once():
    """Run all jobs once immediately."""
    scheduler = PredictionScheduler()

    logger.info("Running all jobs once...")

    scheduler.run_full_pipeline()
    scheduler.fetch_latest_data()
    scheduler.generate_upcoming_predictions()
    scheduler.generate_daily_report()

    logger.info("All jobs completed")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Soccer Prediction Scheduler'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run all jobs once and exit'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='outputs',
        help='Output directory (default: outputs)'
    )

    args = parser.parse_args()

    if args.once:
        run_once()
    else:
        run_scheduler()
