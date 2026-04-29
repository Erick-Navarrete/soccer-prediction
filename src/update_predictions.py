"""
Update Predictions Script

This script updates the soccer predictions with fresh data.
Can be run on a schedule (e.g., every 6 hours) via cron jobs.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd
import pickle

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.data_loader import FootballDataLoader, DataCleaner
from src.feature_engineering import (
    FeatureEngineer, FootballELO, compute_xg_proxy,
    compute_fatigue_features, compute_h2h_features, add_odds_features
)
from src.ml_models import prepare_model_data, build_ensemble

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('outputs/update.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def update_predictions(seasons: list = ["2425"], leagues: list = ["E0"]):
    """
    Update predictions with fresh data.

    Args:
        seasons: List of seasons to load
        leagues: List of leagues to load
    """
    logger.info("="*60)
    logger.info("UPDATING PREDICTIONS")
    logger.info("="*60)
    logger.info(f"Update time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Step 1: Load fresh data
        logger.info("\nStep 1: Loading fresh data...")
        loader = FootballDataLoader()
        raw_data = loader.load_multiple_seasons(seasons, leagues)

        if raw_data.empty:
            logger.error("No data loaded!")
            return False

        cleaner = DataCleaner()
        clean_data = cleaner.clean_data(raw_data)
        logger.info(f"Loaded {len(clean_data)} matches")

        # Step 2: Feature engineering
        logger.info("\nStep 2: Engineering features...")
        engineer = FeatureEngineer(window_size=5)
        featured_data = engineer.build_match_features(clean_data)

        # Step 3: Prepare model data
        logger.info("\nStep 3: Preparing model data...")
        X, y, feature_names = prepare_model_data(featured_data)

        # Step 4: Load existing model
        logger.info("\nStep 4: Loading existing model...")
        model_path = Path(__file__).parent.parent / "outputs" / "ensemble_model.pkl"
        scaler_path = Path(__file__).parent.parent / "outputs" / "scaler.pkl"

        if not model_path.exists() or not scaler_path.exists():
            logger.error("Model files not found! Run main.py first.")
            return False

        with open(model_path, 'rb') as f:
            model = pickle.load(f)

        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)

        # Step 5: Generate predictions for latest matches
        logger.info("\nStep 5: Generating predictions...")
        latest_matches = featured_data.tail(10).copy()
        latest_X = X.tail(10)
        latest_X_scaled = scaler.transform(latest_X)

        predictions = model.predict(latest_X_scaled)
        probabilities = model.predict_proba(latest_X_scaled)

        # Step 6: Create predictions dataframe
        predictions_data = []
        ftr_map = {'H': 2, 'D': 1, 'A': 0}

        for i, (idx, match) in enumerate(latest_matches.iterrows()):
            actual_result = ftr_map.get(match.get("FTR", ""), -1) if "FTR" in match else None

            pred_data = {
                "date": match.get("Date", ""),
                "home_team": match.get("HomeTeam", ""),
                "away_team": match.get("AwayTeam", ""),
                "home_win_prob": float(probabilities[i][2]),
                "draw_prob": float(probabilities[i][1]),
                "away_win_prob": float(probabilities[i][0]),
                "prediction": int(predictions[i]),
                "actual_result": actual_result,
                "league": match.get("League", "E0"),
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            predictions_data.append(pred_data)

        # Step 7: Save predictions
        logger.info("\nStep 6: Saving predictions...")
        predictions_df = pd.DataFrame(predictions_data)
        predictions_path = Path(__file__).parent.parent / "outputs" / "predictions.csv"
        predictions_df.to_csv(predictions_path, index=False)

        logger.info(f"✓ Predictions updated successfully!")
        logger.info(f"✓ Generated {len(predictions_df)} predictions")
        logger.info(f"✓ Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Step 8: Update timestamp file
        timestamp_path = Path(__file__).parent.parent / "outputs" / "last_updated.txt"
        with open(timestamp_path, 'w') as f:
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        return True

    except Exception as e:
        logger.error(f"Error updating predictions: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Update predictions for current season
    success = update_predictions(seasons=["2425"], leagues=["E0"])

    if success:
        logger.info("\n✓ UPDATE COMPLETE")
        sys.exit(0)
    else:
        logger.error("\n✗ UPDATE FAILED")
        sys.exit(1)
