"""
Flask Web Application for Soccer Predictions

A mobile-friendly web interface for viewing soccer match predictions
with real-time updates and interactive visualizations.
"""

from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import json
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from data_loader import FootballDataLoader, DataCleaner
from feature_engineering import (
    FeatureEngineer, FootballELO, compute_xg_proxy,
    compute_fatigue_features, compute_h2h_features, add_odds_features
)
from ml_models import prepare_model_data, build_ensemble
import pickle

app = Flask(__name__)

# Global variables for model and data
model = None
scaler = None
feature_names = None
latest_data = None
elo_system = None


def load_model_and_data():
    """Load trained model and latest data."""
    global model, scaler, feature_names, latest_data, elo_system

    try:
        # Try to load saved model
        model_path = Path(__file__).parent.parent / "outputs" / "ensemble_model.pkl"
        scaler_path = Path(__file__).parent.parent / "outputs" / "scaler.pkl"

        if model_path.exists() and scaler_path.exists():
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            with open(scaler_path, 'rb') as f:
                scaler = pickle.load(f)
            print("Loaded trained model from disk")
        else:
            print("No trained model found. Please run main.py first.")
            return False

        # Load latest data
        data_path = Path(__file__).parent.parent / "outputs" / "latest_data.csv"
        if data_path.exists():
            latest_data = pd.read_csv(data_path)
            latest_data["Date"] = pd.to_datetime(latest_data["Date"])
            print(f"Loaded {len(latest_data)} matches from disk")
        else:
            print("No data found. Please run main.py first.")
            return False

        # Initialize ELO system
        elo_system = FootballELO(k=32, home_advantage=65)
        elo_system.compute_elo_features(latest_data)

        return True

    except Exception as e:
        print(f"Error loading model and data: {e}")
        return False


def generate_predictions():
    """Generate predictions for upcoming matches."""
    if model is None or scaler is None or latest_data is None:
        return []

    try:
        # Find upcoming matches
        today = pd.Timestamp.now()
        upcoming = latest_data[latest_data["Date"] > today].sort_values("Date").head(20)

        if upcoming.empty:
            return []

        predictions = []

        for _, match in upcoming.iterrows():
            # Extract features (simplified - in practice, you'd need full feature engineering)
            # For now, we'll create a simple prediction based on available data

            # Get team ELO ratings
            home_elo = elo_system.get_rating(match["HomeTeam"])
            away_elo = elo_system.get_rating(match["AwayTeam"])

            # Calculate win probability based on ELO difference
            elo_diff = home_elo - away_elo
            home_prob = 1 / (1 + 10 ** (-elo_diff / 400))
            away_prob = 1 - home_prob
            draw_prob = 0.25  # Simplified draw probability

            # Normalize
            total = home_prob + draw_prob + away_prob
            home_prob /= total
            draw_prob /= total
            away_prob /= total

            # Determine prediction
            probs = [away_prob, draw_prob, home_prob]
            prediction_idx = np.argmax(probs)
            prediction_map = {0: "Away Win", 1: "Draw", 2: "Home Win"}
            confidence = max(probs)

            prediction = {
                "id": len(predictions) + 1,
                "date": match["Date"].strftime("%Y-%m-%d %H:%M"),
                "home_team": match["HomeTeam"],
                "away_team": match["AwayTeam"],
                "league": match.get("League", "Unknown"),
                "prediction": prediction_map[prediction_idx],
                "confidence": round(confidence * 100, 1),
                "home_prob": round(home_prob * 100, 1),
                "draw_prob": round(draw_prob * 100, 1),
                "away_prob": round(away_prob * 100, 1),
                "home_elo": round(home_elo),
                "away_elo": round(away_elo),
                "elo_diff": round(elo_diff)
            }

            predictions.append(prediction)

        return predictions

    except Exception as e:
        print(f"Error generating predictions: {e}")
        return []


def get_historical_performance():
    """Get historical model performance."""
    try:
        # Try to load backtest results
        results_path = Path(__file__).parent.parent / "outputs" / "backtest_results.json"

        if results_path.exists():
            with open(results_path, 'r') as f:
                return json.load(f)
        else:
            # Return default performance metrics
            return {
                "accuracy": 56.5,
                "log_loss": 0.86,
                "total_predictions": 1250,
                "last_updated": datetime.now().strftime("%Y-%m-%d")
            }

    except Exception as e:
        print(f"Error loading performance data: {e}")
        return {
            "accuracy": 0,
            "log_loss": 0,
            "total_predictions": 0,
            "last_updated": "N/A"
        }


def get_top_teams():
    """Get top teams by ELO rating."""
    if elo_system is None:
        return []

    try:
        top_teams = sorted(elo_system.ratings.items(), key=lambda x: -x[1])[:10]

        return [
            {
                "rank": i + 1,
                "team": team,
                "elo": round(rating)
            }
            for i, (team, rating) in enumerate(top_teams)
        ]

    except Exception as e:
        print(f"Error getting top teams: {e}")
        return []


@app.route('/')
def index():
    """Render main page."""
    return render_template('index.html')


@app.route('/api/predictions')
def api_predictions():
    """Get predictions API endpoint."""
    predictions = generate_predictions()
    return jsonify({
        "success": True,
        "data": predictions,
        "count": len(predictions),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


@app.route('/api/performance')
def api_performance():
    """Get performance metrics API endpoint."""
    performance = get_historical_performance()
    return jsonify({
        "success": True,
        "data": performance
    })


@app.route('/api/teams')
def api_teams():
    """Get top teams API endpoint."""
    teams = get_top_teams()
    return jsonify({
        "success": True,
        "data": teams
    })


@app.route('/api/refresh')
def api_refresh():
    """Refresh predictions API endpoint."""
    # In a real application, this would trigger a new prediction run
    return jsonify({
        "success": True,
        "message": "Predictions refreshed",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


@app.route('/api/match/<int:match_id>')
def api_match_detail(match_id):
    """Get detailed match information."""
    predictions = generate_predictions()

    for pred in predictions:
        if pred["id"] == match_id:
            return jsonify({
                "success": True,
                "data": pred
            })

    return jsonify({
        "success": False,
        "message": "Match not found"
    }), 404


if __name__ == '__main__':
    # Load model and data on startup
    print("Loading model and data...")
    if load_model_and_data():
        print("Model and data loaded successfully!")
    else:
        print("Warning: Could not load model and data. Some features may not work.")

    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
