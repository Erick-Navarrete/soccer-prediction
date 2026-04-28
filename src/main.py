"""
Main Orchestration Script

This script orchestrates the entire soccer prediction pipeline:
1. Load and clean data
2. Engineer features (rolling stats, ELO, xG, fatigue, H2H)
3. Add odds features
4. Prepare model data
5. Train and evaluate models
6. Build ensemble
7. Run backtesting
8. Generate visualizations
9. (Optional) Fetch Polymarket data
10. (Optional) Generate Claude analysis
"""

import argparse
import logging
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Import all modules
from data_loader import FootballDataLoader, DataCleaner
from feature_engineering import (
    FeatureEngineer, FootballELO, compute_xg_proxy,
    compute_fatigue_features, compute_h2h_features, add_odds_features
)
from ml_models import (
    prepare_model_data, train_and_evaluate,
    build_ensemble, get_feature_importance
)
from backtesting import WalkForwardBacktest, plot_calibration_curve
from visualization import (
    plot_model_comparison, plot_confusion_matrix,
    plot_feature_importance, plot_probability_distribution
)
from claude_integration import get_claude_client, generate_prediction_report
from polymarket_integration import PolymarketClient, TripleLayerFeatures

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('outputs/pipeline.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Soccer Prediction System'
    )
    parser.add_argument(
        '--seasons',
        type=str,
        default='2425,2324,2223,2122',
        help='Comma-separated list of seasons (default: 2425,2324,2223,2122)'
    )
    parser.add_argument(
        '--leagues',
        type=str,
        default='E0,SP1,D1',
        help='Comma-separated list of league codes (default: E0,SP1,D1)'
    )
    parser.add_argument(
        '--window',
        type=int,
        default=5,
        help='Rolling window size for features (default: 5)'
    )
    parser.add_argument(
        '--skip-polymarket',
        action='store_true',
        help='Skip Polymarket data fetching'
    )
    parser.add_argument(
        '--skip-claude',
        action='store_true',
        help='Skip Claude API integration'
    )
    parser.add_argument(
        '--skip-backtest',
        action='store_true',
        help='Skip walk-forward backtesting'
    )
    parser.add_argument(
        '--skip-visualization',
        action='store_true',
        help='Skip visualization generation'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='outputs',
        help='Output directory for results (default: outputs)'
    )
    return parser.parse_args()


def main():
    """Main orchestration function."""
    args = parse_arguments()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    logger.info("="*60)
    logger.info("SOCCER PREDICTION SYSTEM")
    logger.info("="*60)

    # Parse arguments
    seasons = args.seasons.split(',')
    leagues = args.leagues.split(',')

    logger.info(f"\nConfiguration:")
    logger.info(f"  Seasons: {seasons}")
    logger.info(f"  Leagues: {leagues}")
    logger.info(f"  Window size: {args.window}")
    logger.info(f"  Output directory: {output_dir}")

    # Step 1: Load and clean data
    logger.info("\n" + "="*60)
    logger.info("STEP 1: Loading and cleaning data")
    logger.info("="*60)

    loader = FootballDataLoader(seasons=seasons, leagues=leagues)
    raw_data = loader.load_all()

    if raw_data.empty:
        logger.error("No data loaded. Exiting.")
        return

    clean_data = DataCleaner.clean(raw_data)
    logger.info(f"Cleaned data: {len(clean_data)} matches")

    # Step 2: Feature engineering
    logger.info("\n" + "="*60)
    logger.info("STEP 2: Feature engineering")
    logger.info("="*60)

    engineer = FeatureEngineer(window=args.window)
    featured_data = engineer.build_match_features(clean_data)
    logger.info(f"Rolling features: {len(featured_data)} matches")

    # ELO ratings
    logger.info("Computing ELO ratings...")
    elo_system = FootballELO(k=32, home_advantage=65)
    featured_data = elo_system.compute_elo_features(featured_data)

    top_teams = sorted(elo_system.ratings.items(),
                       key=lambda x: -x[1])[:5]
    logger.info("Top 5 teams by ELO:")
    for team, rating in top_teams:
        logger.info(f"  {team:25s} {rating:.0f}")

    # xG proxy
    logger.info("Computing xG proxy...")
    featured_data = compute_xg_proxy(featured_data)

    # Fatigue features
    logger.info("Computing fatigue features...")
    featured_data = compute_fatigue_features(featured_data)

    # Head-to-head features
    logger.info("Computing head-to-head features...")
    featured_data = compute_h2h_features(featured_data)

    # Odds features
    logger.info("Adding odds features...")
    featured_data = add_odds_features(featured_data)

    logger.info(f"Total features: {len([c for c in featured_data.columns if c not in ['Date', 'HomeTeam', 'AwayTeam', 'FTR', 'Result', 'League', 'Season']])}")

    # Step 3: Prepare model data
    logger.info("\n" + "="*60)
    logger.info("STEP 3: Preparing model data")
    logger.info("="*60)

    X, y, feature_names = prepare_model_data(featured_data)

    # Step 4: Train and evaluate models
    logger.info("\n" + "="*60)
    logger.info("STEP 4: Training and evaluating models")
    logger.info("="*60)

    results, models = train_and_evaluate(X, y)

    # Step 5: Build ensemble
    logger.info("\n" + "="*60)
    logger.info("STEP 5: Building ensemble model")
    logger.info("="*60)

    ensemble, scaler = build_ensemble(X, y)

    # Step 6: Backtesting
    if not args.skip_backtest:
        logger.info("\n" + "="*60)
        logger.info("STEP 6: Walk-forward backtesting")
        logger.info("="*60)

        from sklearn.ensemble import RandomForestClassifier
        backtest_model = RandomForestClassifier(
            n_estimators=200, max_depth=8, random_state=42
        )

        backtester = WalkForwardBacktest(
            model=backtest_model,
            scaler=scaler,
            initial_train_size=500,
            step_size=50
        )

        backtest_results = backtester.run(X, y)

        # Plot calibration curve
        plot_calibration_curve(
            backtest_results["actuals"],
            backtest_results["probabilities"],
            class_idx=2,
            class_name="Home Win"
        )

    # Step 7: Visualizations
    if not args.skip_visualization:
        logger.info("\n" + "="*60)
        logger.info("STEP 7: Generating visualizations")
        logger.info("="*60)

        # Model comparison
        plot_model_comparison(results)

        # Confusion matrix
        split_idx = int(len(X) * 0.8)
        X_test = X.iloc[split_idx:]
        y_test = y.iloc[split_idx:]
        X_test_scaled = scaler.transform(X_test)
        preds = ensemble.predict(X_test_scaled)
        plot_confusion_matrix(y_test, preds)

        # Feature importance
        rf_model = models["Random Forest"]
        plot_feature_importance(rf_model, feature_names, top_n=15)

        # Probability distribution
        proba = ensemble.predict_proba(X_test_scaled)
        plot_probability_distribution(proba, y_test)

    # Step 8: Polymarket integration (optional)
    if not args.skip_polymarket:
        logger.info("\n" + "="*60)
        logger.info("STEP 8: Polymarket integration")
        logger.info("="*60)

        poly_client = PolymarketClient()
        football_markets = poly_client.search_football_markets(limit=100)

        logger.info(f"Found {len(football_markets)} football markets")

        for market in football_markets[:3]:
            odds = poly_client.extract_match_odds(market)
            if odds:
                logger.info(f"\n  {market['question']}")
                if odds.draw:
                    logger.info(f"    Home: {odds.home_win:.1%} | "
                               f"Draw: {odds.draw:.1%} | "
                               f"Away: {odds.away_win:.1%}")
                else:
                    logger.info(f"    Yes: {odds.home_win:.1%} | "
                               f"No: {odds.away_win:.1%}")

    # Step 9: Claude integration (optional)
    if not args.skip_claude:
        logger.info("\n" + "="*60)
        logger.info("STEP 9: Claude API integration")
        logger.info("="*60)

        claude_client = get_claude_client()

        if claude_client:
            # Generate a sample prediction report
            sample_match = featured_data.iloc[-1]
            home_team = sample_match["HomeTeam"]
            away_team = sample_match["AwayTeam"]

            # Get model probabilities
            sample_features = X.iloc[-1:].values
            sample_proba = ensemble.predict_proba(sample_features)[0]

            model_proba = {
                "home_win": sample_proba[2],
                "draw": sample_proba[1],
                "away_win": sample_proba[0]
            }

            # Get team stats
            stats = {
                "home_avg_GF": sample_match.get("home_avg_GF", 0),
                "home_avg_GA": sample_match.get("home_avg_GA", 0),
                "home_avg_SoT": sample_match.get("home_avg_SoT", 0),
                "home_Form": sample_match.get("home_Form", 0),
                "away_avg_GF": sample_match.get("away_avg_GF", 0),
                "away_avg_GA": sample_match.get("away_avg_GA", 0),
                "away_avg_SoT": sample_match.get("away_avg_SoT", 0),
                "away_Form": sample_match.get("away_Form", 0),
            }

            report = generate_prediction_report(
                home_team=home_team,
                away_team=away_team,
                model_proba=model_proba,
                stats=stats,
                league=sample_match.get("League", "Unknown"),
                client=claude_client
            )

            logger.info(f"\nPrediction Report for {home_team} vs {away_team}:")
            logger.info(report)
        else:
            logger.info("Claude API not available")

    # Final summary
    logger.info("\n" + "="*60)
    logger.info("PIPELINE COMPLETE")
    logger.info("="*60)
    logger.info(f"\nResults saved to: {output_dir}")
    logger.info(f"Total matches processed: {len(featured_data)}")
    logger.info(f"Total features: {len(feature_names)}")

    if not args.skip_backtest:
        logger.info(f"Backtest accuracy: {backtest_results['accuracy']:.4f}")
        logger.info(f"Backtest log loss: {backtest_results['log_loss']:.4f}")

    logger.info("\nBest model by accuracy:")
    best_model = max(results.items(), key=lambda x: x[1]['accuracy_mean'])
    logger.info(f"  {best_model[0]}: {best_model[1]['accuracy_mean']:.4f}")

    logger.info("\nBest model by log loss:")
    best_ll = min(results.items(), key=lambda x: x[1]['log_loss_mean'])
    logger.info(f"  {best_ll[0]}: {best_ll[1]['log_loss_mean']:.4f}")


if __name__ == "__main__":
    main()
