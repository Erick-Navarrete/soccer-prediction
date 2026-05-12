"""Soccer Predictions - Clean Excel-style viewer with data refresh."""
from flask import Flask, render_template, jsonify
import json
import subprocess
import sys
from pathlib import Path

app = Flask(__name__)
DATA = Path(__file__).parent.parent / "data"
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
