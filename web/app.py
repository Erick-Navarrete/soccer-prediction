"""Soccer Predictions - Clean Excel-style viewer with data refresh."""
from flask import Flask, render_template, jsonify
import json
import pickle
import subprocess
import sys
from pathlib import Path

app = Flask(__name__)
DATA = Path(__file__).parent.parent / "data"
OUTPUTS = Path(__file__).parent.parent / "outputs"
REFRESH_SCRIPT = Path(__file__).parent.parent / "refresh_data.py"


def load(name):
    p = DATA / f"{name}.json"
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/summary")
def api_summary():
    return jsonify({"success": True, "data": load("summary")})


@app.route("/api/predictions")
def api_predictions():
    data = load("predictions")
    return jsonify({"success": True, "data": data, "count": len(data)})


@app.route("/api/historical")
def api_historical():
    data = load("historical")
    return jsonify({"success": True, "data": data, "count": len(data)})


@app.route("/api/teams")
def api_teams():
    data = load("team_stats")
    return jsonify({"success": True, "data": data, "count": len(data)})


@app.route("/api/performance")
def api_performance():
    data = load("performance")
    return jsonify({"success": True, "data": data if data else {}})


@app.route("/api/insights")
def api_insights():
    data = load("insights")
    return jsonify({"success": True, "data": data if data else []})


@app.route("/api/model-info")
def api_model_info():
    info = {
        "ensemble": {"type": "VotingClassifier", "estimators": 3},
        "elo": {"k_factor": 32, "home_advantage": 65, "initial_rating": 1500, "draw_margin": 8},
        "blend": {"ml_weight": 0.5, "elo_weight": 0.5},
        "features": [],
        "feature_count": 0,
        "feature_importances": [],
        "models": [],
        "performance": {},
    }

    try:
        features = pickle.load(open(OUTPUTS / "feature_names.pkl", "rb"))
        info["features"] = list(features)
        info["feature_count"] = len(features)
    except Exception:
        pass

    try:
        model = pickle.load(open(OUTPUTS / "ensemble_model.pkl", "rb"))
        rf = model.named_estimators_["rf"]
        gb = model.named_estimators_["gb"]
        lr = model.named_estimators_["lr"]
        importances = rf.feature_importances_
        paired = sorted(
            zip(info["features"], importances), key=lambda x: -x[1]
        )
        info["feature_importances"] = [
            {"feature": n, "importance": round(float(v), 4)} for n, v in paired
        ]
        info["models"] = [
            {
                "name": "Logistic Regression",
                "type": "LogisticRegression",
                "params": {"C": 0.5, "max_iter": 1000, "penalty": "l2"},
            },
            {
                "name": "Random Forest",
                "type": "RandomForestClassifier",
                "params": {
                    "n_estimators": rf.n_estimators,
                    "max_depth": rf.max_depth,
                    "min_samples_leaf": rf.min_samples_leaf,
                    "random_state": rf.random_state,
                },
            },
            {
                "name": "Gradient Boosting",
                "type": "GradientBoostingClassifier",
                "params": {
                    "n_estimators": gb.n_estimators,
                    "max_depth": gb.max_depth,
                    "learning_rate": gb.learning_rate,
                    "random_state": gb.random_state,
                },
            },
        ]
        info["ensemble"]["voting"] = model.voting
        info["ensemble"]["weights"] = list(model.weights) if hasattr(model, "weights") and model.weights else [1, 1, 1]
    except Exception:
        info["models"] = [
            {"name": "Logistic Regression", "type": "LogisticRegression", "params": {"C": 0.5}},
            {"name": "Random Forest", "type": "RandomForestClassifier", "params": {"n_estimators": 200, "max_depth": 8}},
            {"name": "Gradient Boosting", "type": "GradientBoostingClassifier", "params": {"n_estimators": 150, "learning_rate": 0.08}},
        ]

    perf = load("performance")
    if perf:
        info["performance"] = {
            "accuracy": perf.get("accuracy"),
            "total_matches": perf.get("total_matches"),
            "correct_predictions": perf.get("correct_predictions"),
            "high_conf_accuracy": perf.get("high_confidence_accuracy"),
            "avg_confidence": perf.get("average_confidence"),
        }

    return jsonify({"success": True, "data": info})


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    """Trigger a data refresh from external sources."""
    try:
        result = subprocess.run(
            [sys.executable, str(REFRESH_SCRIPT)],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0:
            return jsonify({"success": True, "message": "Data refreshed successfully"})
        return jsonify({
            "success": False,
            "message": f"Refresh failed: {result.stderr[-500:]}",
        }), 500
    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "message": "Refresh timed out"}), 504
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
