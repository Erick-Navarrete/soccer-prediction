"""Refresh soccer prediction data from free sources.

Fetches latest PL results from football-data.co.uk CSVs,
upcoming fixtures from TheSportsDB, generates ELO-based predictions,
and updates all JSON data files.
"""

import json
import requests
import csv
import io
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
HOME_ADVANTAGE = 65

# Team name mapping: TheSportsDB name -> our internal name
TEAM_NAME_MAP = {
    "Arsenal": "Arsenal",
    "Aston Villa": "Aston Villa",
    "Bournemouth": "Bournemouth",
    "AFC Bournemouth": "Bournemouth",
    "Brentford": "Brentford",
    "Brighton and Hove Albion": "Brighton",
    "Brighton & Hove Albion": "Brighton",
    "Burnley": "Burnley",
    "Chelsea": "Chelsea",
    "Crystal Palace": "Crystal Palace",
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
    "Tottenham Hotspur": "Tottenham",
    "Tottenham": "Tottenham",
    "West Ham United": "West Ham",
    "West Ham": "West Ham",
    "Wolverhampton Wanderers": "Wolves",
    "Wolves": "Wolves",
    "Sunderland": "Sunderland",
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
    print(f"  Updated {name}.json ({len(data) if isinstance(data, list) else 'dict'})")


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
        # Betting odds if available
            "b365h": row.get("B365H", "").strip() or None,
            "b365d": row.get("B365D", "").strip() or None,
            "b365a": row.get("B365A", "").strip() or None,
        }

        if ftr:
            match["result"] = {"H": "Home Win", "D": "Draw", "A": "Away Win"}.get(ftr, "Unknown")

        matches.append(match)

    print(f"  Found {len(matches)} matches from CSV")
    return matches


def fetch_upcoming_fixtures():
    """Fetch upcoming PL fixtures from TheSportsDB."""
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
                # Skip already played matches
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
            print(f"  Warning: round {rnd} fetch failed: {e}")

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

    print(f"  Found {len(all_fixtures)} upcoming fixtures")
    return all_fixtures


def elo_predict(home_elo, away_elo, home_advantage=HOME_ADVANTAGE):
    """Generate ELO-based prediction probabilities."""
    r_home = home_elo + home_advantage
    r_away = away_elo
    elo_diff = r_home - r_away

    e_home = 1.0 / (1.0 + 10 ** ((r_away - r_home) / 400.0))

    # Draw probability peaks when teams are equal (~24%), drops as gap grows
    draw_prob = max(12.0, 24.0 - abs(elo_diff) * 0.06)
    draw_prob = round(draw_prob, 1)

    remaining = 100.0 - draw_prob
    home_win_prob = round(remaining * e_home, 1)
    away_win_prob = round(100.0 - home_win_prob - draw_prob, 1)

    # Pick outcome
    if home_win_prob >= draw_prob and home_win_prob >= away_win_prob:
        prediction, prediction_code = "Home Win", 2
    elif away_win_prob >= draw_prob:
        prediction, prediction_code = "Away Win", 0
    else:
        prediction, prediction_code = "Draw", 1

    confidence = round(max(home_win_prob, draw_prob, away_win_prob), 1)
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


def update_historical(csv_matches, existing_historical):
    """Build full historical data from CSV, merging with existing predictions."""
    existing_map = {}
    for m in existing_historical:
        key = f"{m.get('date','')[:10]}|{m.get('home_team','')}|{m.get('away_team','')}"
        existing_map[key] = m

    team_elos = {t["team"]: t["elo"] for t in load_json("team_stats")}
    new_historical = []
    match_id = 1

    for cm in csv_matches:
        if cm["home_goals"] is None:
            continue  # Skip unplayed

        key = f"{cm['date']}|{cm['home_team']}|{cm['away_team']}"
        existing = existing_map.get(key, {})

        dt = datetime.strptime(cm["date"], "%Y-%m-%d")
        home_elo = team_elos.get(cm["home_team"], 1500)
        away_elo = team_elos.get(cm["away_team"], 1500)
        pred = elo_predict(home_elo, away_elo)

        actual = cm.get("result", "Unknown")
        is_correct = pred["prediction"] == actual if actual != "Unknown" else False

        entry = {
            "id": match_id,
            "date": f"{cm['date']} 15:00",
            "home_team": cm["home_team"],
            "away_team": cm["away_team"],
            "league": "Premier League",
            "prediction": existing.get("prediction", pred["prediction"]),
            "actual": actual,
            "is_correct": existing.get("is_correct", is_correct),
            "confidence": existing.get("confidence", pred["confidence"]),
            "home_prob": round(existing.get("home_prob", pred["home_win_prob"]), 1),
            "draw_prob": round(existing.get("draw_prob", pred["draw_prob"]), 1),
            "away_prob": round(existing.get("away_prob", pred["away_win_prob"]), 1),
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

    return new_historical


def update_predictions(upcoming_fixtures):
    """Build predictions.json from upcoming fixtures."""
    team_elos = {t["team"]: t["elo"] for t in load_json("team_stats")}
    predictions = []

    for i, fx in enumerate(upcoming_fixtures, 1):
        home_elo = team_elos.get(fx["home_team"], 1500)
        away_elo = team_elos.get(fx["away_team"], 1500)
        pred = elo_predict(home_elo, away_elo)

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


def update_team_stats(csv_matches, existing_teams):
    """Update team standings from CSV results."""
    teams_map = {}
    for t in existing_teams:
        teams_map[t["team"]] = t.copy()

    # Recalculate from all played CSV matches
    stats = {}
    for cm in csv_matches:
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

    # Sort by points, then GD, then GF
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

    # Week number from the next upcoming fixture
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


def main():
    print("=== Soccer Prediction Data Refresh ===\n")

    # 1. Fetch data
    csv_matches = fetch_csv_results()
    upcoming = fetch_upcoming_fixtures()

    if not csv_matches and not upcoming:
        print("ERROR: No data fetched from any source!")
        sys.exit(1)

    # 2. Load existing data
    existing_historical = load_json("historical")
    existing_teams = load_json("team_stats")

    # 3. Update all JSON files
    print("\nUpdating data files...")
    historical = update_historical(csv_matches, existing_historical)
    save_json("historical", historical)

    predictions = update_predictions(upcoming)
    save_json("predictions", predictions)

    team_stats = update_team_stats(csv_matches, existing_teams)
    save_json("team_stats", team_stats)

    summary = update_summary(predictions, historical, team_stats)
    save_json("summary", summary)

    print(f"\nDone! {len(predictions)} upcoming predictions, {len(historical)} historical matches, {len(team_stats)} teams.")


if __name__ == "__main__":
    main()
