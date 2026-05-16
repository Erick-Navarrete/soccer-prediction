"""Refresh soccer prediction data from free sources.

Fetches latest PL results from football-data.co.uk CSVs + ESPN API
(for real-time scores before CSV updates), upcoming fixtures from
football-data.org / ESPN / TheSportsDB, generates ML+ELO blended
predictions, and updates all JSON data files.
"""

import json
import requests
import csv
import io
import sys
import pickle
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
HOME_ADVANTAGE = 65

# Team name mapping: external name -> our internal name
# Covers TheSportsDB, football-data.org, and ESPN shortDisplayName variants
TEAM_NAME_MAP = {
    "Arsenal": "Arsenal",
    "Aston Villa": "Aston Villa",
    "Bournemouth": "Bournemouth",
    "AFC Bournemouth": "Bournemouth",
    "Brentford": "Brentford",
    "Brighton and Hove Albion": "Brighton",
    "Brighton & Hove Albion": "Brighton",
    "Brighton": "Brighton",
    "Burnley": "Burnley",
    "Chelsea": "Chelsea",
    "Crystal Palace": "Crystal Palace",
    "C Palace": "Crystal Palace",
    "Everton": "Everton",
    "Fulham": "Fulham",
    "Leeds United": "Leeds",
    "Leeds": "Leeds",
    "Liverpool": "Liverpool",
    "Manchester City": "Man City",
    "Man City": "Man City",
    "Manchester United": "Man United",
    "Man United": "Man United",
    "Newcastle United": "Newcastle",
    "Newcastle": "Newcastle",
    "Nottingham Forest": "Nott'm Forest",
    "Nott'm Forest": "Nott'm Forest",
    "Nottm Forest": "Nott'm Forest",
    "Tottenham Hotspur": "Tottenham",
    "Tottenham": "Tottenham",
    "Spurs": "Tottenham",
    "West Ham United": "West Ham",
    "West Ham": "West Ham",
    "Wolverhampton Wanderers": "Wolves",
    "Wolves": "Wolves",
    "Wolv": "Wolves",
    "Sunderland": "Sunderland",
    "Ipswich Town": "Ipswich",
    "Ipswich": "Ipswich",
    "Leicester City": "Leicester",
    "Leicester": "Leicester",
    "Southampton": "Southampton",
    "Brighton Hove": "Brighton",
    "Nottingham": "Nott'm Forest",
    "Wolverhampton": "Wolves",
}

# Reverse map: our name -> football-data.co.uk CSV name
CSV_NAME_MAP = {
    "Arsenal": "Arsenal",
    "Aston Villa": "Aston Villa",
    "Bournemouth": "Bournemouth",
    "Brentford": "Brentford",
    "Brighton": "Brighton",
    "Burnley": "Burnley",
    "Chelsea": "Chelsea",
    "Crystal Palace": "Crystal Palace",
    "Everton": "Everton",
    "Fulham": "Fulham",
    "Leeds": "Leeds United",
    "Liverpool": "Liverpool",
    "Man City": "Man City",
    "Man United": "Man United",
    "Newcastle": "Newcastle",
    "Nott'm Forest": "Nott'm Forest",
    "Tottenham": "Tottenham",
    "West Ham": "West Ham",
    "Wolves": "Wolves",
    "Sunderland": "Sunderland",
    "Ipswich": "Ipswich",
    "Leicester": "Leicester",
    "Southampton": "Southampton",
}


def normalize_team(name):
    return TEAM_NAME_MAP.get(name, name)


def load_json(name):
    p = DATA_DIR / f"{name}.json"
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return [] if name != "summary" else {}


def save_json(name, data):
    p = DATA_DIR / f"{name}.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f" Updated {name}.json ({len(data) if isinstance(data, list) else 'dict'})")


def fetch_csv_results():
    """Fetch all PL results from football-data.co.uk CSV."""
    url = "https://www.football-data.co.uk/mmz4281/2526/E0.csv"
    print("Fetching results from football-data.co.uk...")
    r = requests.get(url, timeout=30)
    r.raise_for_status()

    reader = csv.DictReader(io.StringIO(r.text))
    matches = []
    for row in reader:
        home = row.get("HomeTeam", "").strip()
        away = row.get("AwayTeam", "").strip()
        fthg = row.get("FTHG", "").strip()
        ftag = row.get("FTAG", "").strip()
        ftr = row.get("FTR", "").strip()
        date_str = row.get("Date", "").strip()

        if not home or not away:
            continue

        # Parse date (DD/MM/YYYY)
        try:
            dt = datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            continue

        match = {
            "date": dt.strftime("%Y-%m-%d"),
            "home_team": normalize_team(home),
            "away_team": normalize_team(away),
            "home_goals": int(fthg) if fthg else None,
            "away_goals": int(ftag) if ftag else None,
            "ftr": ftr,  # H/D/A
            "b365h": row.get("B365H", "").strip() or None,
            "b365d": row.get("B365D", "").strip() or None,
            "b365a": row.get("B365A", "").strip() or None,
        }

        if ftr:
            match["result"] = {"H": "Home Win", "D": "Draw", "A": "Away Win"}.get(ftr, "Unknown")

        matches.append(match)

    print(f" Found {len(matches)} matches from CSV")
    return matches


ROOT_DIR = Path(__file__).parent


def _load_env_key(key_name):
    """Load an API key from .env file or environment variable."""
    import os
    val = os.environ.get(key_name, "").strip()
    if val and "your_" not in val:
        return val
    env_path = ROOT_DIR / ".env"
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"{key_name}="):
                    val = line.split("=", 1)[1].strip()
                    if val and "your_" not in val:
                        return val
    return None


def fetch_upcoming_fixtures():
    """Fetch upcoming PL fixtures from football-data.org (primary) or TheSportsDB (fallback)."""
    all_fixtures = []
    seen = set()

    # Try football-data.org first (better coverage, requires free API key)
    api_key = _load_env_key("FOOTBALL_DATA_API_KEY")
    if api_key:
        print("Fetching upcoming fixtures from football-data.org...")
        try:
            url = "https://api.football-data.org/v4/competitions/PL/matches"
            params = {"status": "SCHEDULED", "limit": 50}
            r = requests.get(url, headers={"X-Auth-Token": api_key}, params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                for match in data.get("matches", []):
                    home = normalize_team(match.get("homeTeam", {}).get("shortName", "") or
                                          match.get("homeTeam", {}).get("name", ""))
                    away = normalize_team(match.get("awayTeam", {}).get("shortName", "") or
                                          match.get("awayTeam", {}).get("name", ""))
                    date_str = (match.get("utcDate") or "")[:10]
                    time_str = (match.get("utcDate") or "T15:00")[11:16] or "15:00"
                    round_num = match.get("matchday", 0)
                    venue = match.get("venue", "Unknown Stadium")
                    key = f"{date_str}|{home}|{away}"
                    if key in seen:
                        continue
                    seen.add(key)
                    all_fixtures.append({
                        "round": round_num,
                        "date": date_str,
                        "time": time_str,
                        "home_team": home,
                        "away_team": away,
                        "venue": venue,
                    })
                print(f" Found {len(all_fixtures)} fixtures from football-data.org")
            else:
                print(f" football-data.org returned {r.status_code}, falling back to TheSportsDB")
        except Exception as e:
            print(f" football-data.org failed ({e}), falling back to TheSportsDB")

    # Fallback: TheSportsDB (free, no key needed)
    if not all_fixtures:
        print("Fetching upcoming fixtures from TheSportsDB...")
        all_fixtures = []
        seen = set()

        for rnd in range(31, 39):
            url = f"https://www.thesportsdb.com/api/v1/json/3/eventsround.php?id=4328&r={rnd}&s=2025-2026"
            try:
                r = requests.get(url, timeout=10)
                if r.status_code != 200:
                    continue

                data = r.json()
                events = data.get("events") or []

                for ev in events:
                    if ev.get("intHomeScore") is not None:
                        continue

                    home = normalize_team(ev.get("strHomeTeam", ""))
                    away = normalize_team(ev.get("strAwayTeam", ""))
                    date_str = ev.get("dateEvent", "")
                    time_str = ev.get("strTime", "") or "15:00"
                    key = f"{date_str}|{home}|{away}"

                    if key in seen:
                        continue
                    seen.add(key)

                    all_fixtures.append({
                        "round": rnd,
                        "date": date_str,
                        "time": time_str[:5] if len(time_str) >= 5 else "15:00",
                        "home_team": home,
                        "away_team": away,
                        "venue": ev.get("strVenue", "Unknown Stadium"),
                    })
            except Exception as e:
                print(f" Warning: round {rnd} fetch failed: {e}")

        # Also fetch from next events endpoint
        try:
            url = "https://www.thesportsdb.com/api/v1/json/3/eventsnextleague.php?id=4328"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                for ev in (data.get("events") or []):
                    if ev.get("intHomeScore") is not None:
                        continue
                    home = normalize_team(ev.get("strHomeTeam", ""))
                    away = normalize_team(ev.get("strAwayTeam", ""))
                    date_str = ev.get("dateEvent", "")
                    key = f"{date_str}|{home}|{away}"
                    if key in seen:
                        continue
                    seen.add(key)
                    all_fixtures.append({
                        "round": int(ev.get("intRound", 0)),
                        "date": date_str,
                        "time": "15:00",
                        "home_team": home,
                        "away_team": away,
                        "venue": ev.get("strVenue", "Unknown Stadium"),
                    })
        except Exception:
            pass

    print(f" Found {len(all_fixtures)} upcoming fixtures")
    return all_fixtures


def fetch_espn_results(days_back=5):
    """Fetch recently completed PL matches from ESPN scoreboard.

    ESPN provides real-time final scores (STATUS_FULL_TIME/STATUS_END_TIME)
    with no auth needed. This catches completed matches hours/days before
    the football-data.co.uk CSV updates.

    Returns list of match dicts: date, home_team, away_team, home_goals,
    away_goals, result, source="espn".
    """
    results = []
    today = datetime.now(timezone.utc).date()

    for i in range(days_back):
        d = today - timedelta(days=i)
        date_str = d.strftime("%Y%m%d")
        try:
            url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard?dates={date_str}"
            r = requests.get(url, timeout=10)
            if r.status_code != 200:
                continue
            data = r.json()
            for ev in data.get("events", []):
                status = ev.get("status", {}).get("type", {})
                state = status.get("state", "")
                # Only pick completed matches
                if state != "post":
                    continue
                comp = ev.get("competitions", [{}])[0]
                competitors = comp.get("competitors", [])
                if len(competitors) != 2:
                    continue

                home = away = None
                home_goals = away_goals = 0
                for c in competitors:
                    name = normalize_team(c["team"].get("shortDisplayName", ""))
                    score = int(c.get("score", 0))
                    if c.get("homeAway") == "home":
                        home = name
                        home_goals = score
                    else:
                        away = name
                        away_goals = score

                if not home or not away:
                    continue

                # Determine result
                if home_goals > away_goals:
                    result = "Home Win"
                elif away_goals > home_goals:
                    result = "Away Win"
                else:
                    result = "Draw"

                # Parse ESPN ISO date
                event_date = (ev.get("date", "")[:10])
                if not event_date:
                    event_date = d.strftime("%Y-%m-%d")

                results.append({
                    "date": event_date,
                    "home_team": home,
                    "away_team": away,
                    "home_goals": home_goals,
                    "away_goals": away_goals,
                    "ftr": {"Home Win": "H", "Draw": "D", "Away Win": "A"}.get(result, ""),
                    "result": result,
                    "source": "espn",
                })
        except Exception as e:
            print(f"  Warning: ESPN fetch for {d} failed: {e}")

    print(f" Found {len(results)} completed matches from ESPN (last {days_back} days)")
    return results


def fetch_espn_upcoming(days_ahead=10):
    """Fetch upcoming PL fixtures from ESPN scoreboard.

    ESPN provides scheduled matches with venue, no auth needed.
    Returns list of fixture dicts compatible with fetch_upcoming_fixtures().
    """
    fixtures = []
    seen = set()
    today = datetime.now(timezone.utc).date()

    for i in range(days_ahead):
        d = today + timedelta(days=i)
        date_str = d.strftime("%Y%m%d")
        try:
            url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard?dates={date_str}"
            r = requests.get(url, timeout=10)
            if r.status_code != 200:
                continue
            data = r.json()
            for ev in data.get("events", []):
                status = ev.get("status", {}).get("type", {})
                state = status.get("state", "")
                # Only pick scheduled matches
                if state != "pre":
                    continue

                comp = ev.get("competitions", [{}])[0]
                competitors = comp.get("competitors", [])
                if len(competitors) != 2:
                    continue

                home = away = None
                venue = "Unknown Stadium"
                for c in competitors:
                    name = normalize_team(c["team"].get("shortDisplayName", ""))
                    if c.get("homeAway") == "home":
                        home = name
                        venue = comp.get("venue", {}).get("fullName", "Unknown Stadium")
                    else:
                        away = name

                if not home or not away:
                    continue

                event_date = (ev.get("date", "")[:10]) or d.strftime("%Y-%m-%d")
                time_str = (ev.get("date", "")[11:16]) or "15:00"

                key = f"{event_date}|{home}|{away}"
                if key in seen:
                    continue
                seen.add(key)

                fixtures.append({
                    "date": event_date,
                    "time": time_str,
                    "home_team": home,
                    "away_team": away,
                    "venue": venue,
                    "round": 0,
                })
        except Exception as e:
            print(f"  Warning: ESPN fetch for {d} failed: {e}")

    print(f" Found {len(fixtures)} upcoming fixtures from ESPN (next {days_ahead} days)")
    return fixtures


DRAW_MARGIN = 8  # predict Draw when gap between top and draw_prob < this


def elo_predict(home_elo, away_elo, home_advantage=HOME_ADVANTAGE):
    """Generate ELO-based prediction probabilities.

    Draw probability calibrated to PL data: max 26% at equal teams,
    decaying with ELO gap. When top outcome margin over draw is small,
    predict Draw (backtested to 51.8% accuracy on 359 matches).
    """
    r_home = home_elo + home_advantage
    r_away = away_elo
    elo_diff = r_home - r_away

    e_home = 1.0 / (1.0 + 10 ** ((r_away - r_home) / 400.0))

    draw_prob = max(12.0, 26.0 - abs(elo_diff) * 0.06)
    draw_prob = round(draw_prob, 1)

    remaining = 100.0 - draw_prob
    home_win_prob = round(remaining * e_home, 1)
    away_win_prob = round(100.0 - home_win_prob - draw_prob, 1)

    top = max(home_win_prob, draw_prob, away_win_prob)
    if top - draw_prob < DRAW_MARGIN:
        prediction, prediction_code = "Draw", 1
    elif home_win_prob >= draw_prob and home_win_prob >= away_win_prob:
        prediction, prediction_code = "Home Win", 2
    elif away_win_prob >= draw_prob:
        prediction, prediction_code = "Away Win", 0
    else:
        prediction, prediction_code = "Draw", 1

    confidence = round(top, 1)
    confidence_level = "High" if confidence >= 70 else "Medium" if confidence >= 50 else "Low"

    return {
        "home_win_prob": home_win_prob,
        "draw_prob": draw_prob,
        "away_win_prob": away_win_prob,
        "prediction": prediction,
        "prediction_code": prediction_code,
        "confidence": confidence,
        "confidence_level": confidence_level,
    }


def ml_predict_upcoming(upcoming_fixtures):
    """Use the ML ensemble model to predict upcoming fixtures.

    Strategy: compute features from historical matches, then for each
    upcoming fixture, look up the most recent per-team rolling stats
    and construct feature rows without append-and-dropna hacks.

    Returns dict mapping (home, away, date) -> ML prediction result.
    """
    try:
        from src.data_loader import FootballDataLoader
        from src.feature_engineering import (
            FeatureEngineer, FootballELO,
            compute_fatigue_features, compute_h2h_features,
        )
    except ImportError as e:
        print(f" Warning: ML modules unavailable ({e}), using ELO only")
        return {}

    model_path = ROOT_DIR / "outputs" / "ensemble_model.pkl"
    scaler_path = ROOT_DIR / "outputs" / "scaler.pkl"
    feat_path = ROOT_DIR / "outputs" / "feature_names.pkl"

    if not model_path.exists() or not scaler_path.exists() or not feat_path.exists():
        print(" Warning: ML model files not found, using ELO only")
        return {}

    print(" Loading ML ensemble model...")
    model = pickle.load(open(model_path, "rb"))
    scaler = pickle.load(open(scaler_path, "rb"))
    feat_names = pickle.load(open(feat_path, "rb"))

    # Load historical data (3 seasons for richer stats)
    print(" Loading historical data for feature computation...")
    loader = FootballDataLoader(seasons=["2526", "2425", "2324"], leagues=["E0"])
    raw = loader.load_all()
    df = raw.copy()
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date"])

    num_cols = ["FTHG", "FTAG", "HTHG", "HTAG", "HS", "AS", "HST", "AST",
                "HF", "AF", "HC", "AC", "HY", "AY", "HR", "AR"]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    result_map = {"H": 2, "D": 1, "A": 0}
    df["Result"] = df["FTR"].map(result_map)

    # Only use historical (played) matches for feature computation
    hist = df[df["Result"].notna()].copy()
    hist = hist.sort_values("Date").reset_index(drop=True)

    # Build features on historical data
    print(" Computing features from historical matches...")
    fe = FeatureEngineer(window=5)
    featured = fe.build_match_features(hist)

    elo_sys = FootballELO(k=32, home_advantage=65)
    featured = elo_sys.compute_elo_features(featured)
    featured = compute_fatigue_features(featured)
    featured = compute_h2h_features(featured)

    # Build lookup: team -> most recent row's stats
    # For each team, get the latest match they played (home or away)
    # and extract their rolling averages from that row
    team_home_stats = {}
    team_away_stats = {}

    for team in set(hist["HomeTeam"].unique()) | set(hist["AwayTeam"].unique()):
        # Latest home match for this team
        home_rows = featured[featured["HomeTeam"] == team].sort_values("Date")
        if not home_rows.empty:
            team_home_stats[team] = home_rows.iloc[-1]
        # Latest away match
        away_rows = featured[featured["AwayTeam"] == team].sort_values("Date")
        if not away_rows.empty:
            team_away_stats[team] = away_rows.iloc[-1]

    # Median values for fallback
    medians = featured[feat_names].median()

    # Predict each upcoming fixture
    label = {0: "Away Win", 1: "Draw", 2: "Home Win"}
    results = {}

    for fx in upcoming_fixtures:
        home_raw = fx["home_team"]
        away_raw = fx["away_team"]
        home_csv = CSV_NAME_MAP.get(home_raw, home_raw)
        away_csv = CSV_NAME_MAP.get(away_raw, away_raw)

        row = {}

        # Get latest stats for each team
        # For home team: prefer their latest home match row (has home_avg_* already)
        # Fall back to away match row and map away_* -> home_*
        h_home = team_home_stats.get(home_csv)
        h_away = team_away_stats.get(home_csv)
        a_home = team_home_stats.get(away_csv)
        a_away = team_away_stats.get(away_csv)

        for feat in feat_names:
            if feat.startswith("home_") and not feat.startswith("home_fatigued"):
                # Try getting this from home team's latest home match
                val = None
                if h_home is not None and feat in h_home.index and pd.notna(h_home[feat]):
                    val = h_home[feat]
                elif h_away is not None:
                    # Map: home_avg_GF from away match -> use away_avg_GF
                    away_feat = feat.replace("home_", "away_", 1)
                    if away_feat in h_away.index and pd.notna(h_away[away_feat]):
                        val = h_away[away_feat]
                row[feat] = val if val is not None else medians.get(feat, 0)

            elif feat.startswith("away_") and not feat.startswith("away_fatigued"):
                val = None
                if a_away is not None and feat in a_away.index and pd.notna(a_away[feat]):
                    val = a_away[feat]
                elif a_home is not None:
                    home_feat = feat.replace("away_", "home_", 1)
                    if home_feat in a_home.index and pd.notna(a_home[home_feat]):
                        val = a_home[home_feat]
                row[feat] = val if val is not None else medians.get(feat, 0)

            elif feat.startswith("diff_"):
                home_key = feat.replace("diff_", "home_", 1)
                away_key = feat.replace("diff_", "away_", 1)
                h_val = row.get(home_key, medians.get(home_key, 0))
                a_val = row.get(away_key, medians.get(away_key, 0))
                row[feat] = h_val - a_val

            elif feat.startswith("elo_"):
                r_home = elo_sys.get_rating(home_csv)
                r_away = elo_sys.get_rating(away_csv)
                if feat == "elo_home":
                    row[feat] = r_home
                elif feat == "elo_away":
                    row[feat] = r_away
                elif feat == "elo_diff":
                    row[feat] = r_home - r_away
                elif feat == "elo_expected_home":
                    row[feat] = elo_sys.expected_score(r_home + 65, r_away)
                elif feat == "elo_expected_away":
                    row[feat] = 1 - elo_sys.expected_score(r_home + 65, r_away)

            elif feat.startswith("rest_") or feat in ("home_fatigued", "away_fatigued", "is_midweek"):
                if feat == "home_rest_days":
                    row[feat] = 7
                elif feat == "away_rest_days":
                    row[feat] = 7
                elif feat == "rest_advantage":
                    row[feat] = 0
                elif feat in ("home_fatigued", "away_fatigued"):
                    row[feat] = 0
                elif feat == "is_midweek":
                    dt = pd.Timestamp(fx["date"])
                    row[feat] = 1 if dt.dayofweek in (1, 2) else 0

            elif feat.startswith("h2h_"):
                row[feat] = medians.get(feat, 0)

            else:
                row[feat] = medians.get(feat, 0)

        # Predict
        X_row = pd.DataFrame([row], columns=feat_names).fillna(medians)
        X_scaled = scaler.transform(X_row)
        pred = model.predict(X_scaled)[0]
        prob = model.predict_proba(X_scaled)[0]

        key = (home_raw, away_raw, fx["date"])
        results[key] = {
            "prediction": label[pred],
            "prediction_code": int(pred),
            "home_win_prob": round(prob[2] * 100, 1),
            "draw_prob": round(prob[1] * 100, 1),
            "away_win_prob": round(prob[0] * 100, 1),
            "confidence": round(prob.max() * 100, 1),
            "source": "ml",
        }

    print(f" ML predictions generated for {len(results)} fixtures")
    return results


def blend_predictions(elo_pred, ml_pred, ml_weight=0.50):
    """Blend ELO and ML predictions.

    ML model trained without odds features gets ~48% OOS accuracy vs ELO's ~50%.
    Use 50/50 ELO/ML split (backtested to 51.3% OOS with margin=8),
    with ML weight reduced when it seems uncertain.
    Apply draw margin threshold after blending.
    """
    if not ml_pred:
        return elo_pred

    ml_home = ml_pred["home_win_prob"]
    ml_draw = ml_pred["draw_prob"]
    ml_away = ml_pred["away_win_prob"]

    # Reduce ML weight when draw probability is inflated (a sign of uncertainty)
    effective_weight = ml_weight
    if ml_draw > 40:
        effective_weight = max(0.1, ml_weight * (1 - (ml_draw - 40) / 25))

    elo_home = elo_pred["home_win_prob"]
    elo_draw = elo_pred["draw_prob"]
    elo_away = elo_pred["away_win_prob"]

    w = effective_weight
    home = round(elo_home * (1 - w) + ml_home * w, 1)
    draw = round(elo_draw * (1 - w) + ml_draw * w, 1)
    away = round(100.0 - home - draw, 1)

    top = max(home, draw, away)
    if top - draw < DRAW_MARGIN:
        prediction, prediction_code = "Draw", 1
    elif home >= draw and home >= away:
        prediction, prediction_code = "Home Win", 2
    elif away >= draw:
        prediction, prediction_code = "Away Win", 0
    else:
        prediction, prediction_code = "Draw", 1

    confidence = round(top, 1)
    confidence_level = "High" if confidence >= 70 else "Medium" if confidence >= 50 else "Low"

    return {
        "home_win_prob": home,
        "draw_prob": draw,
        "away_win_prob": away,
        "prediction": prediction,
        "prediction_code": prediction_code,
        "confidence": confidence,
        "confidence_level": confidence_level,
    }


LOCKED_FILE = DATA_DIR / "locked_predictions.json"


def _load_locked():
    """Load locked predictions (made before match results were known)."""
    if LOCKED_FILE.exists():
        with open(LOCKED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_locked(locked):
    """Save locked predictions."""
    with open(LOCKED_FILE, "w", encoding="utf-8") as f:
        json.dump(locked, f, indent=2, ensure_ascii=False)


def merge_completed_matches(csv_matches, espn_results):
    """Merge ESPN completed matches into CSV match list.

    ESPN provides real-time scores that can arrive hours/days before
    the football-data.co.uk CSV updates. For each ESPN result, if the
    match is not already in the CSV results (keyed by date|home|away),
    add it. If it is already in CSV but without goals, fill in the result.
    """
    csv_keys = {}
    for m in csv_matches:
        key = f"{m['date']}|{m['home_team']}|{m['away_team']}"
        csv_keys[key] = m

    added = 0
    for em in espn_results:
        key = f"{em['date']}|{em['home_team']}|{em['away_team']}"
        if key in csv_keys:
            # CSV already has this match — if it has goals, CSV wins (more reliable)
            # If CSV row has no goals yet, fill from ESPN
            if csv_keys[key]["home_goals"] is None:
                csv_keys[key]["home_goals"] = em["home_goals"]
                csv_keys[key]["away_goals"] = em["away_goals"]
                csv_keys[key]["ftr"] = em["ftr"]
                csv_keys[key]["result"] = em["result"]
                added += 1
        else:
            # ESPN has a completed match not in CSV yet — add it
            csv_matches.append(em)
            csv_keys[key] = em
            added += 1

    if added:
        print(f" ESPN added/filled {added} results not yet in CSV")
    return csv_matches


def update_historical(all_matches, existing_historical):
    """Build full historical data from matches, merging with existing predictions.

    all_matches combines CSV results + ESPN completed matches.
    Predictions are 'locked' once a match has a result — the original
    prediction made before the result was known is preserved forever.
    This prevents retrodiction bias where changing ELO ratings would
    silently alter historical predictions and accuracy.
    """
    existing_map = {}
    for m in existing_historical:
        key = f"{m.get('date','')[:10]}|{m.get('home_team','')}|{m.get('away_team','')}"
        existing_map[key] = m

    locked = _load_locked()
    team_elos = {t["team"]: t["elo"] for t in load_json("team_stats")}
    new_historical = []
    new_locked = {}
    match_id = 1

    # Load current predictions to lock in pre-result predictions
    predictions_map = {}
    for p in load_json("predictions"):
        key = f"{p.get('date','')[:10]}|{p.get('home_team','')}|{p.get('away_team','')}"
        predictions_map[key] = p

    for cm in all_matches:
        if cm["home_goals"] is None:
            continue

        key = f"{cm['date']}|{cm['home_team']}|{cm['away_team']}"
        existing = existing_map.get(key, {})

        dt = datetime.strptime(cm["date"], "%Y-%m-%d")
        home_elo = team_elos.get(cm["home_team"], 1500)
        away_elo = team_elos.get(cm["away_team"], 1500)

        actual = cm.get("result", "Unknown")

        # Priority: locked prediction > existing historical > current predictions > ELO fallback
        lock = locked.get(key)
        if lock:
            prediction = lock["prediction"]
            is_correct = lock.get("is_correct", prediction == actual) if actual != "Unknown" else None
            confidence = lock["confidence"]
            home_prob = lock["home_prob"]
            draw_prob = lock["draw_prob"]
            away_prob = lock["away_prob"]
        elif existing.get("prediction"):
            # Use existing historical entry (from previous refresh)
            prediction = existing["prediction"]
            is_correct = existing.get("is_correct", prediction == actual) if actual != "Unknown" else None
            confidence = existing.get("confidence", 0)
            home_prob = existing.get("home_prob", 0)
            draw_prob = existing.get("draw_prob", 0)
            away_prob = existing.get("away_prob", 0)
        elif key in predictions_map:
            # Lock in the current prediction for this newly-resulted match
            cp = predictions_map[key]
            prediction = cp["prediction"]
            is_correct = prediction == actual if actual != "Unknown" else None
            confidence = cp.get("confidence", 0)
            home_prob = cp.get("home_win_prob", cp.get("home_prob", 0))
            draw_prob = cp.get("draw_prob", 0)
            away_prob = cp.get("away_win_prob", cp.get("away_prob", 0))
        else:
            # Fallback: ELO prediction (only for matches with no prior prediction)
            pred = elo_predict(home_elo, away_elo)
            prediction = pred["prediction"]
            is_correct = prediction == actual if actual != "Unknown" else None
            confidence = pred["confidence"]
            home_prob = pred["home_win_prob"]
            draw_prob = pred["draw_prob"]
            away_prob = pred["away_win_prob"]

        # Lock this prediction so it's never recalculated
        if actual not in ("Unknown", None, ""):
            new_locked[key] = {
                "prediction": prediction,
                "confidence": confidence,
                "home_prob": home_prob,
                "draw_prob": draw_prob,
                "away_prob": away_prob,
                "is_correct": is_correct,
            }

        entry = {
            "id": match_id,
            "date": f"{cm['date']} 15:00",
            "home_team": cm["home_team"],
            "away_team": cm["away_team"],
            "league": "Premier League",
            "prediction": prediction,
            "actual": actual,
            "is_correct": is_correct,
            "confidence": confidence,
            "home_prob": round(home_prob, 1),
            "draw_prob": round(draw_prob, 1),
            "away_prob": round(away_prob, 1),
            "home_elo": home_elo,
            "away_elo": away_elo,
            "elo_diff": home_elo - away_elo,
            "importance": existing.get("importance", "Low"),
            "home_goals": cm["home_goals"],
            "away_goals": cm["away_goals"],
            "week_number": dt.isocalendar()[1],
            "year": dt.year,
            "month": dt.month,
        }
        new_historical.append(entry)
        match_id += 1

    # Save locked predictions for future refreshes
    _save_locked(new_locked)
    print(f" Locked {len(new_locked)} historical predictions")

    return new_historical


def update_predictions(upcoming_fixtures):
    """Build predictions.json from upcoming fixtures using ML+ELO blend.

    Filters out fixtures whose date has already passed (to avoid showing
    stale predictions for matches that may have already been played).
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    future_fixtures = [fx for fx in upcoming_fixtures if fx.get("date", "") >= today]
    if len(future_fixtures) < len(upcoming_fixtures):
        print(f" Filtered out {len(upcoming_fixtures) - len(future_fixtures)} past fixtures")

    team_elos = {t["team"]: t["elo"] for t in load_json("team_stats")}

    ml_preds = ml_predict_upcoming(future_fixtures) if future_fixtures else {}

    predictions = []

    for i, fx in enumerate(future_fixtures, 1):
        home_elo = team_elos.get(fx["home_team"], 1500)
        away_elo = team_elos.get(fx["away_team"], 1500)
        elo_pred = elo_predict(home_elo, away_elo)

        ml_key = (fx["home_team"], fx["away_team"], fx["date"])
        ml_p = ml_preds.get(ml_key, {})

        pred = blend_predictions(elo_pred, ml_p)

        dt = datetime.strptime(fx["date"], "%Y-%m-%d")
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        predictions.append({
            "id": i,
            "date": f"{fx['date']} {fx['time']}",
            "time": fx["time"],
            "home_team": fx["home_team"],
            "away_team": fx["away_team"],
            "venue": fx.get("venue", "Unknown Stadium"),
            "tv": "Unknown",
            "league": "Premier League",
            "home_win_prob": pred["home_win_prob"],
            "draw_prob": pred["draw_prob"],
            "away_win_prob": pred["away_win_prob"],
            "prediction": pred["prediction"],
            "prediction_code": pred["prediction_code"],
            "actual_result": "Not Played",
            "home_goals": None,
            "away_goals": None,
            "is_correct": None,
            "confidence": pred["confidence"],
            "confidence_level": pred["confidence_level"],
            "home_elo": home_elo,
            "away_elo": away_elo,
            "elo_diff": home_elo - away_elo,
            "importance": pred["confidence_level"],
            "odds_home": None,
            "odds_away": None,
            "over_under": 2.5,
            "year": dt.year,
            "month": dt.month,
            "day_of_week": day_names[dt.weekday()],
            "week_number": dt.isocalendar()[1],
        })

    return predictions


def update_team_stats(completed_matches, existing_teams):
    """Update team standings from completed match results."""
    teams_map = {}
    for t in existing_teams:
        teams_map[t["team"]] = t.copy()

    stats = {}
    for cm in completed_matches:
        if cm["home_goals"] is None:
            continue
        home = cm["home_team"]
        away = cm["away_team"]

        for team, is_home, gf, ga in [
            (home, True, cm["home_goals"], cm["away_goals"]),
            (away, False, cm["away_goals"], cm["home_goals"]),
        ]:
            if team not in stats:
                stats[team] = {
                    "matches": 0, "wins": 0, "draws": 0, "losses": 0,
                    "goals_for": 0, "goals_against": 0,
                    "home_wins": 0, "home_draws": 0, "home_losses": 0,
                    "away_wins": 0, "away_draws": 0, "away_losses": 0,
                    "recent": [],
                }
            s = stats[team]
            s["matches"] += 1
            s["goals_for"] += gf
            s["goals_against"] += ga

            if gf > ga:
                s["wins"] += 1
                s["recent"].append("W")
                if is_home:
                    s["home_wins"] += 1
                else:
                    s["away_wins"] += 1
            elif gf == ga:
                s["draws"] += 1
                s["recent"].append("D")
                if is_home:
                    s["home_draws"] += 1
                else:
                    s["away_draws"] += 1
            else:
                s["losses"] += 1
                s["recent"].append("L")
                if is_home:
                    s["home_losses"] += 1
                else:
                    s["away_losses"] += 1

    result = []
    for team, s in stats.items():
        existing = teams_map.get(team, {})
        points = s["wins"] * 3 + s["draws"]
        gd = s["goals_for"] - s["goals_against"]
        form = "".join(s["recent"][-5:])

        result.append({
            "team": team,
            "league": "Premier League",
            "season": "2025-2026",
            "matches": s["matches"],
            "points": points,
            "wins": s["wins"],
            "draws": s["draws"],
            "losses": s["losses"],
            "goals_for": s["goals_for"],
            "goals_against": s["goals_against"],
            "goal_difference": gd,
            "win_rate": round(s["wins"] / s["matches"] * 100, 1) if s["matches"] else 0,
            "home_wins": s["home_wins"],
            "home_draws": s["home_draws"],
            "home_losses": s["home_losses"],
            "away_wins": s["away_wins"],
            "away_draws": s["away_draws"],
            "away_losses": s["away_losses"],
            "form": form,
            "form_string": form,
            "elo": existing.get("elo", 1500),
            "goals_per_game": round(s["goals_for"] / s["matches"], 2) if s["matches"] else 0,
            "goals_conceded_per_game": round(s["goals_against"] / s["matches"], 2) if s["matches"] else 0,
        })

    result.sort(key=lambda t: (-(t["points"] or 0), -(t["goal_difference"] or 0), -(t["goals_for"] or 0)))
    for i, t in enumerate(result, 1):
        t["position"] = i

    return result


def update_summary(predictions, historical, team_stats):
    """Update summary.json."""
    total_hist = len(historical)
    correct = sum(1 for h in historical if h.get("is_correct"))
    acc = round(correct / total_hist * 100, 1) if total_hist else 0

    high = sum(1 for p in predictions if p.get("confidence_level") == "High")
    med = sum(1 for p in predictions if p.get("confidence_level") == "Medium")
    low = sum(1 for p in predictions if p.get("confidence_level") == "Low")
    home_pred = sum(1 for p in predictions if p.get("prediction") == "Home Win")
    draw_pred = sum(1 for p in predictions if p.get("prediction") == "Draw")
    away_pred = sum(1 for p in predictions if p.get("prediction") == "Away Win")

    current_week = predictions[0]["week_number"] if predictions else 0

    return {
        "current_week_matches": len(predictions),
        "total_historical": total_hist,
        "weeks_available": len(set(h.get("week_number") for h in historical)) if historical else 0,
        "teams": len(team_stats),
        "accuracy": acc,
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "current_week": current_week,
        "high_confidence": high,
        "medium_confidence": med,
        "low_confidence": low,
        "home_wins_predicted": home_pred,
        "draws_predicted": draw_pred,
        "away_wins_predicted": away_pred,
    }


def update_elo_ratings(completed_matches, team_stats):
    """Recalculate ELO ratings from all completed matches."""
    from src.feature_engineering import FootballELO

    elo = FootballELO(k=32, home_advantage=65)
    for cm in completed_matches:
        if cm["home_goals"] is None:
            continue
        home = CSV_NAME_MAP.get(cm["home_team"], cm["home_team"])
        away = CSV_NAME_MAP.get(cm["away_team"], cm["away_team"])
        elo.update(home, away, cm["home_goals"], cm["away_goals"])

    # Update ELO in team stats
    for t in team_stats:
        csv_name = CSV_NAME_MAP.get(t["team"], t["team"])
        t["elo"] = round(elo.get_rating(csv_name))

    return team_stats


def main():
    print("=== Soccer Prediction Data Refresh ===\n")

    # 1. Fetch data from all sources
    csv_matches = fetch_csv_results()
    espn_results = fetch_espn_results(days_back=5)

    # 2. Merge ESPN completed matches into CSV results
    #    ESPN catches results before CSV updates, moving games to history faster
    all_matches = merge_completed_matches(csv_matches, espn_results)

    # 3. Fetch upcoming fixtures (football-data.org + ESPN + TheSportsDB fallback)
    upcoming = fetch_upcoming_fixtures()

    # Add ESPN upcoming fixtures (deduped by date|home|away key)
    espn_upcoming = fetch_espn_upcoming(days_ahead=10)
    seen_keys = {f"{fx['date']}|{fx['home_team']}|{fx['away_team']}" for fx in upcoming}
    for fx in espn_upcoming:
        key = f"{fx['date']}|{fx['home_team']}|{fx['away_team']}"
        if key not in seen_keys:
            upcoming.append(fx)
            seen_keys.add(key)
    if espn_upcoming:
        print(f" Total upcoming fixtures after merging all sources: {len(upcoming)}")

    if not all_matches and not upcoming:
        print("ERROR: No data fetched from any source!")
        sys.exit(1)

    # 4. Load existing data
    existing_historical = load_json("historical")
    existing_teams = load_json("team_stats")

    # 5. Update team stats (standings from all completed matches)
    print("\nUpdating data files...")
    team_stats = update_team_stats(all_matches, existing_teams)

    # 6. Recalculate ELO ratings
    print("Recalculating ELO ratings...")
    try:
        team_stats = update_elo_ratings(all_matches, team_stats)
    except ImportError:
        print(" Warning: Could not import FootballELO, keeping existing ELO ratings")

    save_json("team_stats", team_stats)

    # 7. Update historical (needs ELO from team_stats)
    historical = update_historical(all_matches, existing_historical)
    save_json("historical", historical)

    # 8. Update predictions (uses ML+ELO blend, filters out past dates)
    predictions = update_predictions(upcoming)
    save_json("predictions", predictions)

    # 9. Update summary
    summary = update_summary(predictions, historical, team_stats)
    save_json("summary", summary)

    print(f"\nDone! {len(predictions)} upcoming predictions, {len(historical)} historical matches, {len(team_stats)} teams.")


if __name__ == "__main__":
    main()
