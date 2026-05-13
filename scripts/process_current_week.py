import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from collections import defaultdict

def process_current_week_predictions():
    """Process the current week predictions with enhanced data."""
    try:
        # Load current week predictions
        df = pd.read_csv('data/current_week_predictions.csv')

        # Convert prediction codes to text
        prediction_map = {0: "Away Win", 1: "Draw", 2: "Home Win"}
        result_map = {0: "Away Win", 1: "Draw", 2: "Home Win"}

        processed_matches = []

        for idx in range(len(df)):
            row = df.iloc[idx]

            # Parse date and time
            try:
                date_str = str(row['date'])
                time_str = str(row['time'])
                match_date = f"{date_str} {time_str}"
            except Exception as e:
                print(f"Error parsing date for row {idx}: {e}")
                match_date = "Unknown"

            # Calculate confidence from probabilities
            try:
                home_win_prob = float(row['home_win_prob'])
                draw_prob = float(row['draw_prob'])
                away_win_prob = float(row['away_win_prob'])
                probs = [away_win_prob, draw_prob, home_win_prob]
                confidence = max(probs) * 100
            except Exception as e:
                print(f"Error calculating probabilities for row {idx}: {e}")
                probs = [0.33, 0.33, 0.34]
                confidence = 50.0

            # Determine prediction text
            prediction_text = str(row.get('prediction_text', 'Unknown'))
            actual_result_text = str(row.get('actual_result_text', 'Not Played'))

            # Check if prediction was correct
            prediction_correct = bool(row.get('prediction_correct', False))

            # Generate realistic ELO ratings based on probabilities
            home_elo = 1500 + int((home_win_prob - 0.33) * 300)
            away_elo = 1500 + int((away_win_prob - 0.33) * 300)

            # Parse odds
            try:
                odds_home = float(row['odds_home']) if pd.notna(row['odds_home']) else None
                odds_away = float(row['odds_away']) if pd.notna(row['odds_away']) else None
                over_under = float(row['over_under']) if pd.notna(row['over_under']) else None
            except:
                odds_home = None
                odds_away = None
                over_under = None

            # Get week number
            try:
                date_obj = datetime.strptime(date_str, "%m/%d/%Y")
                week_number = date_obj.isocalendar()[1]
            except:
                week_number = 1

            match = {
                "id": idx + 1,
                "date": match_date,
                "time": str(row['time']),
                "home_team": str(row['home_team']),
                "away_team": str(row['away_team']),
                "venue": str(row.get('venue', 'Unknown')),
                "tv": str(row.get('tv', 'Unknown')),
                "league": str(row['league']),
                "home_win_prob": round(home_win_prob * 100, 2),
                "draw_prob": round(draw_prob * 100, 2),
                "away_win_prob": round(away_win_prob * 100, 2),
                "prediction": prediction_text,
                "prediction_code": int(row['prediction']),
                "actual_result": actual_result_text,
                "actual_result_code": int(row['actual_result']) if pd.notna(row['actual_result']) and row['actual_result'] != -1 else None,
                "is_correct": prediction_correct,
                "confidence": round(confidence, 2),
                "confidence_level": str(row.get('confidence_level', 'Medium')),
                "home_elo": home_elo,
                "away_elo": away_elo,
                "elo_diff": home_elo - away_elo,
                "importance": str(row.get('confidence_level', 'Medium')),
                "odds_home": odds_home,
                "odds_away": odds_away,
                "over_under": over_under,
                "year": int(row['year']),
                "month": int(row['month']),
                "day_of_week": str(row['day_of_week']),
                "week_number": week_number
            }

            processed_matches.append(match)

        return processed_matches

    except Exception as e:
        print(f"Error processing current week predictions: {e}")
        import traceback
        traceback.print_exc()
        return []

def sort_predictions_by_confidence(predictions):
    """Sort predictions by confidence level in descending order."""
    return sorted(predictions, key=lambda x: x.get('confidence', 0), reverse=True)

def get_week_number(date_str):
    """Get week number from date string."""
    try:
        date_obj = datetime.strptime(date_str, "%m/%d/%Y")
        return date_obj.isocalendar()[1]
    except:
        return 1

def process_historical_with_weeks():
    """Process historical data with week filtering."""
    try:
        # Load historical data
        df = pd.read_csv('data/premier_league_matches_2526.csv')

        # Filter for completed matches
        completed_matches = df[df['FullTimeResult'].notna()].copy()

        # Convert result codes
        result_map = {'H': 'Home Win', 'D': 'Draw', 'A': 'Away Win'}

        historical_matches = []

        for idx, row in completed_matches.iterrows():
            # Parse date
            try:
                date_str = row['MatchDate']
                time_str = row['MatchTime']
                match_date = f"{date_str} {time_str}"

                # Get week number
                date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                week_number = date_obj.isocalendar()[1]
            except:
                match_date = "Unknown"
                week_number = 1

            # Get result
            actual_result = result_map.get(row['FullTimeResult'], "Unknown")

            # Calculate probabilities based on odds
            try:
                home_odds = float(row['AverageHomeOdds']) if pd.notna(row['AverageHomeOdds']) else 3.0
                draw_odds = float(row['AverageDrawOdds']) if pd.notna(row['AverageDrawOdds']) else 3.0
                away_odds = float(row['AverageAwayOdds']) if pd.notna(row['AverageAwayOdds']) else 3.0

                # Convert odds to probabilities
                home_prob = 1 / home_odds
                draw_prob = 1 / draw_odds
                away_prob = 1 / away_odds

                # Normalize
                total = home_prob + draw_prob + away_prob
                home_prob /= total
                draw_prob /= total
                away_prob /= total

                # Determine prediction
                probs = [away_prob, draw_prob, home_prob]
                prediction_idx = np.argmax(probs)
                prediction_map = {0: "Away Win", 1: "Draw", 2: "Home Win"}
                confidence = max(probs) * 100

                # Check if prediction was correct
                prediction_text = prediction_map[prediction_idx]
                is_correct = (prediction_text == actual_result)

            except:
                # Fallback
                home_prob = 0.33
                draw_prob = 0.33
                away_prob = 0.34
                prediction_text = actual_result
                confidence = 50.0
                is_correct = True

            # Generate ELO ratings
            home_elo = 1500 + int((home_prob - 0.33) * 300)
            away_elo = 1500 + int((away_prob - 0.33) * 300)

            match = {
                "id": idx + 1,
                "date": match_date,
                "home_team": row['HomeTeam'],
                "away_team": row['AwayTeam'],
                "league": row['League'],
                "prediction": prediction_text,
                "actual": actual_result,
                "is_correct": is_correct,
                "confidence": round(confidence, 2),
                "home_prob": round(home_prob * 100, 2),
                "draw_prob": round(draw_prob * 100, 2),
                "away_prob": round(away_prob * 100, 2),
                "home_elo": home_elo,
                "away_elo": away_elo,
                "elo_diff": home_elo - away_elo,
                "importance": "High" if confidence > 70 else "Medium" if confidence > 50 else "Low",
                "home_goals": int(row['FullTimeHomeGoals']) if pd.notna(row['FullTimeHomeGoals']) else 0,
                "away_goals": int(row['FullTimeAwayGoals']) if pd.notna(row['FullTimeAwayGoals']) else 0,
                "week_number": week_number,
                "year": date_obj.year if 'date_obj' in locals() else 2025,
                "month": date_obj.month if 'date_obj' in locals() else 5
            }

            historical_matches.append(match)

        return historical_matches

    except Exception as e:
        print(f"Error processing historical data: {e}")
        return []

def create_week_filter_data(historical_matches):
    """Create data for week filtering."""
    try:
        # Group matches by week
        weeks_data = defaultdict(list)

        for match in historical_matches:
            week_num = match.get('week_number', 1)
            weeks_data[week_num].append(match)

        # Create week summary
        week_summaries = []

        for week_num in sorted(weeks_data.keys()):
            matches = weeks_data[week_num]
            total = len(matches)
            correct = sum(1 for m in matches if m.get('is_correct', False))
            accuracy = round((correct / total) * 100, 2) if total > 0 else 0

            # Get date range for this week
            if matches:
                first_date = matches[0].get('date', 'Unknown')
                last_date = matches[-1].get('date', 'Unknown')
            else:
                first_date = 'Unknown'
                last_date = 'Unknown'

            week_summary = {
                "week_number": week_num,
                "total_matches": total,
                "correct_predictions": correct,
                "accuracy": accuracy,
                "first_date": first_date,
                "last_date": last_date,
                "matches": matches
            }

            week_summaries.append(week_summary)

        return week_summaries

    except Exception as e:
        print(f"Error creating week filter data: {e}")
        return []

def main():
    """Main function to process current week data and update all files."""
    print("Processing current week predictions...")

    # Process current week predictions
    current_predictions = process_current_week_predictions()
    print(f"Processed {len(current_predictions)} current week predictions")

    # Sort predictions by confidence level
    current_predictions = sort_predictions_by_confidence(current_predictions)
    print(f"Sorted predictions by confidence level")

    # Process historical data with weeks
    historical_matches = process_historical_with_weeks()
    print(f"Processed {len(historical_matches)} historical matches")

    # Create week filter data
    week_summaries = create_week_filter_data(historical_matches)
    print(f"Created {len(week_summaries)} week summaries")

    # Load existing team stats and performance
    try:
        with open('data/team_stats.json', 'r') as f:
            team_stats = json.load(f)
        print(f"Loaded {len(team_stats)} team statistics")
    except:
        team_stats = []

    try:
        with open('data/performance.json', 'r') as f:
            performance = json.load(f)
        print("Loaded performance metrics")
    except:
        performance = {}

    # Create comprehensive insights from current data
    insights = []

    # Current week insights
    if current_predictions:
        high_conf_matches = [p for p in current_predictions if p.get('confidence', 0) >= 70]
        medium_conf_matches = [p for p in current_predictions if 50 <= p.get('confidence', 0) < 70]
        low_conf_matches = [p for p in current_predictions if p.get('confidence', 0) < 50]

        # Count predictions by type
        home_wins = [p for p in current_predictions if p.get('prediction') == 'Home Win']
        draws = [p for p in current_predictions if p.get('prediction') == 'Draw']
        away_wins = [p for p in current_predictions if p.get('prediction') == 'Away Win']

        insights.append({
            "type": "current_week",
            "title": "Current Week Predictions",
            "content": [
                f"Total matches: {len(current_predictions)}",
                f"High confidence: {len(high_conf_matches)} matches",
                f"Medium confidence: {len(medium_conf_matches)} matches",
                f"Low confidence: {len(low_conf_matches)} matches",
                f"Average confidence: {round(sum(p.get('confidence', 0) for p in current_predictions) / len(current_predictions), 2)}%",
                f"Home wins predicted: {len(home_wins)}",
                f"Draws predicted: {len(draws)}",
                f"Away wins predicted: {len(away_wins)}"
            ]
        })

    # Historical performance insights
    if historical_matches:
        total_historical = len(historical_matches)
        correct_historical = sum(1 for m in historical_matches if m.get('is_correct', False))
        accuracy_historical = round((correct_historical / total_historical) * 100, 2) if total_historical > 0 else 0

        # Count result types
        home_wins_actual = [m for m in historical_matches if m.get('actual') == 'Home Win']
        draws_actual = [m for m in historical_matches if m.get('actual') == 'Draw']
        away_wins_actual = [m for m in historical_matches if m.get('actual') == 'Away Win']

        # High confidence accuracy
        high_conf_historical = [m for m in historical_matches if m.get('confidence', 0) >= 70]
        high_conf_correct = sum(1 for m in high_conf_historical if m.get('is_correct', False))
        high_conf_accuracy = round((high_conf_correct / len(high_conf_historical)) * 100, 2) if high_conf_historical else 0

        insights.append({
            "type": "historical_performance",
            "title": "Historical Performance",
            "content": [
                f"Total matches analyzed: {total_historical}",
                f"Overall accuracy: {accuracy_historical}%",
                f"Correct predictions: {correct_historical}",
                f"High confidence matches: {len(high_conf_historical)}",
                f"High confidence accuracy: {high_conf_accuracy}%",
                f"Home wins: {len(home_wins_actual)}",
                f"Draws: {len(draws_actual)}",
                f"Away wins: {len(away_wins_actual)}"
            ]
        })

    # Team performance insights
    if team_stats:
        # Get top teams
        top_teams = sorted(team_stats, key=lambda x: x.get('points', 0), reverse=True)[:5]

        insights.append({
            "type": "team_performance",
            "title": "Top Teams This Season",
            "content": [
                f"1. {top_teams[0].get('team', 'N/A')} - {top_teams[0].get('points', 0)} pts" if len(top_teams) > 0 else "",
                f"2. {top_teams[1].get('team', 'N/A')} - {top_teams[1].get('points', 0)} pts" if len(top_teams) > 1 else "",
                f"3. {top_teams[2].get('team', 'N/A')} - {top_teams[2].get('points', 0)} pts" if len(top_teams) > 2 else "",
                f"4. {top_teams[3].get('team', 'N/A')} - {top_teams[3].get('points', 0)} pts" if len(top_teams) > 3 else "",
                f"5. {top_teams[4].get('team', 'N/A')} - {top_teams[4].get('points', 0)} pts" if len(top_teams) > 4 else ""
            ]
        })

    # Week-by-week analysis
    if week_summaries:
        recent_weeks = week_summaries[-3:]  # Last 3 weeks
        week_insights = []
        for week in recent_weeks:
            week_insights.append(
                f"Week {week['week_number']}: {week['accuracy']}% accuracy ({week['correct_predictions']}/{week['total_matches']} correct)"
            )

        insights.append({
            "type": "weekly_analysis",
            "title": "Recent Weekly Performance",
            "content": week_insights if week_insights else ["No recent week data available"]
        })

    # Model performance insights
    if performance:
        insights.append({
            "type": "model_performance",
            "title": "Model Performance Metrics",
            "content": [
                f"Overall accuracy: {performance.get('accuracy', 0)}%",
                f"Total predictions: {performance.get('total_predictions', 0)}",
                f"High confidence accuracy: {performance.get('high_confidence_accuracy', 0)}%",
                f"Log loss: {performance.get('log_loss', 0):.3f}",
                f"Last updated: {performance.get('last_updated', 'N/A')}"
            ]
        })

    # Save all data files
    output_files = {
        'data/predictions.json': current_predictions,
        'data/historical.json': historical_matches,
        'data/week_summaries.json': week_summaries,
        'data/team_stats.json': team_stats,
        'data/performance.json': performance,
        'data/insights.json': insights
    }

    for filename, data in output_files.items():
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Saved {filename}")

    # Create summary
    summary = {
        "current_week_matches": len(current_predictions),
        "total_historical": len(historical_matches),
        "weeks_available": len(week_summaries),
        "teams": len(team_stats),
        "accuracy": performance.get('accuracy', 0),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "current_week": datetime.now().isocalendar()[1]
    }

    with open('data/summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\nSummary: {summary['current_week_matches']} current week predictions")
    print(f"Total historical: {summary['total_historical']} matches across {summary['weeks_available']} weeks")
    print("Data processing complete!")

if __name__ == "__main__":
    main()