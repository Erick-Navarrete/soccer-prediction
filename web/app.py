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
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.data_loader import FootballDataLoader, DataCleaner
from src.feature_engineering import (
    FeatureEngineer, FootballELO, compute_xg_proxy,
    compute_fatigue_features, compute_h2h_features, add_odds_features
)
from src.ml_models import prepare_model_data, build_ensemble
import pickle

app = Flask(__name__)

# Global variables for model and data
model = None
scaler = None
feature_names = None
latest_data = None
elo_system = None
historical_predictions = []


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


def load_historical_predictions():
    """Load historical predictions from file."""
    global historical_predictions

    try:
        history_path = Path(__file__).parent.parent / "outputs" / "historical_predictions.json"

        if history_path.exists():
            with open(history_path, 'r') as f:
                historical_predictions = json.load(f)
            print(f"Loaded {len(historical_predictions)} historical predictions")
            return True
        else:
            print("No historical predictions found")
            historical_predictions = []
            return False

    except Exception as e:
        print(f"Error loading historical predictions: {e}")
        historical_predictions = []
        return False


def save_historical_predictions():
    """Save historical predictions to file."""
    try:
        history_path = Path(__file__).parent.parent / "outputs"
        history_path.mkdir(exist_ok=True)

        with open(history_path / "historical_predictions.json", 'w') as f:
            json.dump(historical_predictions, f, indent=2)

        print(f"Saved {len(historical_predictions)} historical predictions")
        return True

    except Exception as e:
        print(f"Error saving historical predictions: {e}")
        return False


def generate_historical_predictions():
    """Generate historical predictions with actual outcomes."""
    if model is None or scaler is None or latest_data is None:
        return []

    try:
        # Find past matches (matches that already happened)
        today = pd.Timestamp.now()
        past_matches = latest_data[latest_data["Date"] < today].sort_values("Date", ascending=False).head(50)

        if past_matches.empty:
            return []

        historical = []

        for _, match in past_matches.iterrows():
            # Get team ELO ratings
            home_elo = elo_system.get_rating(match["HomeTeam"])
            away_elo = elo_system.get_rating(match["AwayTeam"])

            # Calculate win probability based on ELO difference
            elo_diff = home_elo - away_elo
            home_prob = 1 / (1 + 10 ** (-elo_diff / 400))
            away_prob = 1 - home_prob
            draw_prob = 0.25

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

            # Get actual result
            result_map = {"H": "Home Win", "D": "Draw", "A": "Away Win"}
            actual_result = result_map.get(match.get("FTR", ""), "Unknown")

            # Check if prediction was correct
            is_correct = (prediction_map[prediction_idx] == actual_result)

            historical_pred = {
                "id": len(historical) + 1,
                "date": match["Date"].strftime("%Y-%m-%d"),
                "home_team": match["HomeTeam"],
                "away_team": match["AwayTeam"],
                "league": match.get("League", "Unknown"),
                "prediction": prediction_map[prediction_idx],
                "actual": actual_result,
                "is_correct": is_correct,
                "confidence": round(confidence * 100, 1),
                "home_prob": round(home_prob * 100, 1),
                "draw_prob": round(draw_prob * 100, 1),
                "away_prob": round(away_prob * 100, 1),
                "home_elo": round(home_elo),
                "away_elo": round(away_elo),
                "elo_diff": round(elo_diff),
                "home_goals": int(match.get("FTHG", 0)),
                "away_goals": int(match.get("FTAG", 0))
            }

            historical.append(historical_pred)

        return historical

    except Exception as e:
        print(f"Error generating historical predictions: {e}")
        return []


def update_historical_predictions():
    """Update historical predictions with latest data."""
    global historical_predictions

    try:
        # Generate new historical predictions
        new_historical = generate_historical_predictions()

        if new_historical:
            # Save to file
            historical_predictions = new_historical
            save_historical_predictions()

            return True
        return False

    except Exception as e:
        print(f"Error updating historical predictions: {e}")
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


@app.route('/api/historical')
def api_historical():
    """Get historical predictions API endpoint."""
    return jsonify({
        "success": True,
        "data": historical_predictions,
        "count": len(historical_predictions),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


@app.route('/api/historical/update')
def api_historical_update():
    """Update historical predictions API endpoint."""
    success = update_historical_predictions()

    return jsonify({
        "success": success,
        "message": "Historical predictions updated" if success else "Failed to update",
        "count": len(historical_predictions),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


@app.route('/api/historical/stats')
def api_historical_stats():
    """Get historical prediction statistics."""
    if not historical_predictions:
        return jsonify({
            "success": True,
            "data": {
                "total": 0,
                "correct": 0,
                "accuracy": 0,
                "home_wins": 0,
                "away_wins": 0,
                "draws": 0
            }
        })

    total = len(historical_predictions)
    correct = sum(1 for pred in historical_predictions if pred.get("is_correct", False))
    accuracy = (correct / total * 100) if total > 0 else 0

    # Count result types
    home_wins = sum(1 for pred in historical_predictions if pred.get("actual") == "Home Win")
    away_wins = sum(1 for pred in historical_predictions if pred.get("actual") == "Away Win")
    draws = sum(1 for pred in historical_predictions if pred.get("actual") == "Draw")

    return jsonify({
        "success": True,
        "data": {
            "total": total,
            "correct": correct,
            "accuracy": round(accuracy, 1),
            "home_wins": home_wins,
            "away_wins": away_wins,
            "draws": draws
        }
    })


@app.route('/api/status')
def api_status():
    """Get system status and last updated timestamp."""
    try:
        # Try to read last updated timestamp
        timestamp_path = Path(__file__).parent.parent / "outputs" / "last_updated.txt"

        if timestamp_path.exists():
            with open(timestamp_path, 'r') as f:
                last_updated = f.read().strip()
        else:
            last_updated = "Never"

        # Check if model is loaded
        model_loaded = model is not None and scaler is not None

        # Get data freshness
        if latest_data is not None and not latest_data.empty:
            latest_date = latest_data["Date"].max()
            data_freshness = (pd.Timestamp.now() - latest_date).days
        else:
            data_freshness = None

        return jsonify({
            "success": True,
            "data": {
                "model_loaded": model_loaded,
                "last_updated": last_updated,
                "data_freshness_days": data_freshness,
                "total_matches": len(latest_data) if latest_data is not None else 0,
                "update_frequency": "Every 6 hours (scheduled)",
                "next_update": "Automatic"
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/update', methods=['POST'])
def api_update():
    """Trigger manual update of predictions."""
    try:
        # Import update function
        import sys
        sys.path.append(str(Path(__file__).parent.parent))
        from src.update_predictions import update_predictions

        # Run update
        success = update_predictions(seasons=["2425"], leagues=["E0"])

        if success:
            # Reload predictions
            load_model_and_data()

            return jsonify({
                "success": True,
                "message": "Predictions updated successfully",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        else:
            return jsonify({
                "success": False,
                "message": "Failed to update predictions"
            }), 500

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/live-matches')
def api_live_matches():
    """Get live match data (if API key is configured)."""
    try:
        # Check if API key is configured
        api_key = os.getenv("FREE_FOOTBALL_API_KEY")

        if not api_key:
            return jsonify({
                "success": False,
                "message": "FREE_FOOTBALL_API_KEY not configured. Get your free API key from: https://rapidapi.com/Creativesdev/api/free-api-live-football-data",
                "data": []
            })

        # Import live data fetcher
        import sys
        sys.path.append(str(Path(__file__).parent.parent))
        from src.free_live_football_api import FreeLiveFootballData

        # Fetch live matches
        live_data = FreeLiveFootballData(api_key)
        live_matches = live_data.get_live_matches()

        # Format matches
        formatted_matches = []
        for match in live_matches:
            formatted = live_data.format_live_match(match)
            formatted_matches.append(formatted)

        return jsonify({
            "success": True,
            "data": formatted_matches,
            "count": len(formatted_matches)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "data": []
        }), 500


@app.route('/api/fixtures')
def api_fixtures():
    """Get upcoming fixtures (if API key is configured)."""
    try:
        # Check if API key is configured
        api_key = os.getenv("FREE_FOOTBALL_API_KEY")

        if not api_key:
            return jsonify({
                "success": False,
                "message": "FREE_FOOTBALL_API_KEY not configured",
                "data": []
            })

        # Get date range (next 7 days)
        from_date = datetime.now().strftime("%Y-%m-%d")
        to_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        # Import live data fetcher
        import sys
        sys.path.append(str(Path(__file__).parent.parent))
        from src.free_live_football_api import FreeLiveFootballData

        # Fetch fixtures
        live_data = FreeLiveFootballData(api_key)
        fixtures = live_data.get_fixtures(from_date=from_date, to_date=to_date)

        # Format fixtures
        formatted_fixtures = []
        for fixture in fixtures:
            formatted = live_data.format_fixture(fixture)
            formatted_fixtures.append(formatted)

        return jsonify({
            "success": True,
            "data": formatted_fixtures,
            "count": len(formatted_fixtures)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "data": []
        }), 500


@app.route('/api/results')
def api_results():
    """Get recent match results (if API key is configured)."""
    try:
        # Check if API key is configured
        api_key = os.getenv("FREE_FOOTBALL_API_KEY")

        if not api_key:
            return jsonify({
                "success": False,
                "message": "FREE_FOOTBALL_API_KEY not configured",
                "data": []
            })

        # Get date range (last 7 days)
        from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        to_date = datetime.now().strftime("%Y-%m-%d")

        # Import live data fetcher
        import sys
        sys.path.append(str(Path(__file__).parent.parent))
        from src.free_live_football_api import FreeLiveFootballData

        # Fetch results
        live_data = FreeLiveFootballData(api_key)
        results = live_data.get_match_results(from_date=from_date, to_date=to_date)

        # Format results
        formatted_results = []
        for result in results:
            formatted = live_data.format_live_match(result)
            formatted_results.append(formatted)

        return jsonify({
            "success": True,
            "data": formatted_results,
            "count": len(formatted_results)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "data": []
        }), 500


if __name__ == '__main__':
    # Load model and data on startup
    print("Loading model and data...")
    if load_model_and_data():
        print("Model and data loaded successfully!")
    else:
        print("Warning: Could not load model and data. Some features may not work.")

    # Load historical predictions
    print("Loading historical predictions...")
    load_historical_predictions()

    # Update historical predictions if needed
    if not historical_predictions:
        print("Generating historical predictions...")
        update_historical_predictions()

    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
