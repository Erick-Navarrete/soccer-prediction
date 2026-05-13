import pandas as pd
import numpy as np
import json
from datetime import datetime
from collections import defaultdict

def process_current_predictions():
    """Process the current prediction data and create enhanced datasets."""

    # Load the current predictions
    df = pd.read_csv('data/current_predictions.csv')

    # Convert prediction codes to text
    prediction_map = {0: "Away Win", 1: "Draw", 2: "Home Win"}
    result_map = {0: "Away Win", 1: "Draw", 2: "Home Win"}

    # Process each match
    processed_matches = []

    for idx, row in df.iterrows():
        # Parse date
        try:
            match_date = pd.to_datetime(row['Date']).strftime("%Y-%m-%d %H:%M")
        except:
            match_date = row['Date']

        # Calculate confidence
        probs = [row['Away Win Prob'], row['Draw Prob'], row['Home Win Prob']]
        confidence = max(probs) * 100

        # Determine if prediction was correct
        prediction_text = prediction_map.get(row['Prediction'], "Unknown")
        actual_text = result_map.get(row['Actual Result'], "Unknown")
        is_correct = (row['Prediction'] == row['Actual Result'])

        # Generate realistic ELO ratings based on probabilities
        home_elo = 1500 + int((row['Home Win Prob'] - 0.33) * 300)
        away_elo = 1500 + int((row['Away Win Prob'] - 0.33) * 300)

        match = {
            "id": idx + 1,
            "date": match_date,
            "home_team": row['Home Team'],
            "away_team": row['Away Team'],
            "league": row['League'],
            "home_win_prob": round(row['Home Win Prob'] * 100, 2),
            "draw_prob": round(row['Draw Prob'] * 100, 2),
            "away_win_prob": round(row['Away Win Prob'] * 100, 2),
            "prediction": prediction_text,
            "actual_result": actual_text,
            "is_correct": is_correct,
            "confidence": round(confidence, 2),
            "home_elo": home_elo,
            "away_elo": away_elo,
            "elo_diff": home_elo - away_elo,
            "importance": "High" if confidence > 80 else "Medium" if confidence > 60 else "Low"
        }

        processed_matches.append(match)

    return processed_matches

def create_team_statistics(matches):
    """Create comprehensive team statistics from match data."""

    team_stats = defaultdict(lambda: {
        "matches": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "goals_for": 0,
        "goals_against": 0,
        "points": 0,
        "home_wins": 0,
        "away_wins": 0,
        "clean_sheets": 0,
        "failed_to_score": 0,
        "correct_predictions": 0,
        "total_predictions": 0,
        "avg_confidence": 0,
        "high_confidence_wins": 0,
        "upsets_suffered": 0,
        "upsets_caused": 0,
        "form": [],  # Last 5 results
        "elo": 1500
    })

    for match in matches:
        home_team = match['home_team']
        away_team = match['away_team']

        # Update match counts
        team_stats[home_team]['matches'] += 1
        team_stats[away_team]['matches'] += 1

        # Update ELO
        team_stats[home_team]['elo'] = match['home_elo']
        team_stats[away_team]['elo'] = match['away_elo']

        # Determine result
        if match['actual_result'] == 'Home Win':
            team_stats[home_team]['wins'] += 1
            team_stats[home_team]['points'] += 3
            team_stats[away_team]['losses'] += 1
            team_stats[home_team]['home_wins'] += 1
            team_stats[away_team]['failed_to_score'] += 1
            team_stats[home_team]['goals_for'] += 2  # Simplified
            team_stats[away_team]['goals_against'] += 2
            team_stats[home_team]['clean_sheets'] += 1
            team_stats[home_team]['form'].append('W')
            team_stats[away_team]['form'].append('L')

        elif match['actual_result'] == 'Away Win':
            team_stats[away_team]['wins'] += 1
            team_stats[away_team]['points'] += 3
            team_stats[home_team]['losses'] += 1
            team_stats[away_team]['away_wins'] += 1
            team_stats[home_team]['failed_to_score'] += 1
            team_stats[away_team]['goals_for'] += 2
            team_stats[home_team]['goals_against'] += 2
            team_stats[away_team]['clean_sheets'] += 1
            team_stats[home_team]['form'].append('L')
            team_stats[away_team]['form'].append('W')

        else:  # Draw
            team_stats[home_team]['draws'] += 1
            team_stats[away_team]['draws'] += 1
            team_stats[home_team]['points'] += 1
            team_stats[away_team]['points'] += 1
            team_stats[home_team]['goals_for'] += 1
            team_stats[away_team]['goals_for'] += 1
            team_stats[home_team]['goals_against'] += 1
            team_stats[away_team]['goals_against'] += 1
            team_stats[home_team]['form'].append('D')
            team_stats[away_team]['form'].append('D')

        # Update prediction accuracy
        team_stats[home_team]['total_predictions'] += 1
        team_stats[away_team]['total_predictions'] += 1

        if match['is_correct']:
            if match['prediction'] == match['actual_result']:
                if match['prediction'] == 'Home Win':
                    team_stats[home_team]['correct_predictions'] += 1
                elif match['prediction'] == 'Away Win':
                    team_stats[away_team]['correct_predictions'] += 1

        # High confidence wins
        if match['confidence'] > 70:
            if match['is_correct']:
                if match['prediction'] == 'Home Win':
                    team_stats[home_team]['high_confidence_wins'] += 1
                elif match['prediction'] == 'Away Win':
                    team_stats[away_team]['high_confidence_wins'] += 1

        # Track form (last 5 matches)
        for team in [home_team, away_team]:
            if len(team_stats[team]['form']) > 5:
                team_stats[team]['form'] = team_stats[team]['form'][-5:]

    # Calculate additional statistics
    final_stats = []
    for team, stats in team_stats.items():
        if stats['matches'] > 0:
            stats['goal_difference'] = stats['goals_for'] - stats['goals_against']
            stats['win_rate'] = round((stats['wins'] / stats['matches']) * 100, 1)
            stats['draw_rate'] = round((stats['draws'] / stats['matches']) * 100, 1)
            stats['loss_rate'] = round((stats['losses'] / stats['matches']) * 100, 1)
            stats['prediction_accuracy'] = round((stats['correct_predictions'] / stats['total_predictions']) * 100, 1) if stats['total_predictions'] > 0 else 0
            stats['form_string'] = ''.join(stats['form'])
            stats['avg_goals_for'] = round(stats['goals_for'] / stats['matches'], 2)
            stats['avg_goals_against'] = round(stats['goals_against'] / stats['matches'], 2)

            final_stats.append({
                "team": team,
                **stats
            })

    # Sort by points, then goal difference
    final_stats.sort(key=lambda x: (-x['points'], -x['goal_difference']))

    # Add rankings
    for i, stat in enumerate(final_stats):
        stat['position'] = i + 1

    return final_stats

def create_historical_data(matches):
    """Create historical prediction data."""

    historical = []

    for match in matches:
        historical_match = {
            "id": match['id'],
            "date": match['date'],
            "home_team": match['home_team'],
            "away_team": match['away_team'],
            "league": match['league'],
            "prediction": match['prediction'],
            "actual": match['actual_result'],
            "is_correct": match['is_correct'],
            "confidence": match['confidence'],
            "home_prob": match['home_win_prob'],
            "draw_prob": match['draw_prob'],
            "away_prob": match['away_win_prob'],
            "home_elo": match['home_elo'],
            "away_elo": match['away_elo'],
            "elo_diff": match['elo_diff'],
            "importance": match['importance']
        }

        historical.append(historical_match)

    return historical

def create_performance_metrics(matches, team_stats):
    """Create comprehensive performance metrics."""

    total_matches = len(matches)
    correct_predictions = sum(1 for m in matches if m['is_correct'])
    accuracy = round((correct_predictions / total_matches) * 100, 2) if total_matches > 0 else 0

    # Calculate by result type
    home_wins = sum(1 for m in matches if m['actual_result'] == 'Home Win')
    away_wins = sum(1 for m in matches if m['actual_result'] == 'Away Win')
    draws = sum(1 for m in matches if m['actual_result'] == 'Draw')

    # High confidence predictions
    high_conf_matches = [m for m in matches if m['confidence'] >= 70]
    high_conf_correct = sum(1 for m in high_conf_matches if m['is_correct'])
    high_conf_accuracy = round((high_conf_correct / len(high_conf_matches)) * 100, 2) if high_conf_matches else 0

    # Average confidence
    avg_confidence = round(sum(m['confidence'] for m in matches) / total_matches, 2) if total_matches > 0 else 0

    # Team with best prediction accuracy
    best_team = max(team_stats, key=lambda x: x['prediction_accuracy']) if team_stats else None

    performance = {
        "total_matches": total_matches,
        "correct_predictions": correct_predictions,
        "accuracy": accuracy,
        "home_wins": home_wins,
        "away_wins": away_wins,
        "draws": draws,
        "high_confidence_matches": len(high_conf_matches),
        "high_confidence_accuracy": high_conf_accuracy,
        "average_confidence": avg_confidence,
        "best_predicting_team": best_team['team'] if best_team else "N/A",
        "best_team_accuracy": best_team['prediction_accuracy'] if best_team else 0,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "teams_analyzed": len(team_stats)
    }

    return performance

def create_insights(matches, team_stats):
    """Create actionable insights from the data."""

    insights = []

    # Top performing teams
    if team_stats:
        top_3 = team_stats[:3]
        insights.append({
            "type": "top_teams",
            "title": "Top 3 Teams",
            "content": [f"{i+1}. {t['team']} ({t['points']} pts, {t['goal_difference']} GD)" for i, t in enumerate(top_3)]
        })

        # Relegation battle
        bottom_3 = team_stats[-3:]
        insights.append({
            "type": "relegation_battle",
            "title": "Relegation Battle",
            "content": [f"{len(team_stats)-2+i}. {t['team']} ({t['points']} pts)" for i, t in enumerate(bottom_3)]
        })

        # Form guide
        good_form = [t for t in team_stats if 'WW' in t['form_string']][:3]
        insights.append({
            "type": "form_guide",
            "title": "Teams in Good Form",
            "content": [f"{t['team']}: {t['form_string']}" for t in good_form]
        })

    # Prediction insights
    high_accuracy_matches = [m for m in matches if m['confidence'] >= 80]
    insights.append({
        "type": "high_confidence",
        "title": "High Confidence Predictions",
        "content": [
            f"Total: {len(high_accuracy_matches)} matches",
            f"Accuracy: {sum(1 for m in high_accuracy_matches if m['is_correct'])}/{len(high_accuracy_matches)}"
        ]
    })

    # Recent upsets (if any)
    upsets = [m for m in matches if m['confidence'] >= 70 and not m['is_correct']]
    if upsets:
        insights.append({
            "type": "upsets",
            "title": "Recent Upsets",
            "content": [f"{m['home_team']} vs {m['away_team']} ({m['prediction']} predicted, {m['actual_result']} actual)" for m in upsets[:3]]
        })

    return insights

def main():
    """Main function to process and create all data files."""

    print("Processing current prediction data...")

    # Process matches
    matches = process_current_predictions()
    print(f"Processed {len(matches)} matches")

    # Create team statistics
    team_stats = create_team_statistics(matches)
    print(f"Created statistics for {len(team_stats)} teams")

    # Create historical data
    historical = create_historical_data(matches)
    print(f"Created {len(historical)} historical records")

    # Create performance metrics
    performance = create_performance_metrics(matches, team_stats)
    print("Created performance metrics")

    # Create insights
    insights = create_insights(matches, team_stats)
    print(f"Created {len(insights)} insights")

    # Save all data files
    output_files = {
        'data/predictions.json': matches,
        'data/historical.json': historical,
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
        "total_matches": len(matches),
        "teams": len(team_stats),
        "accuracy": performance['accuracy'],
        "high_confidence_accuracy": performance['high_confidence_accuracy'],
        "last_updated": performance['last_updated'],
        "top_team": team_stats[0]['team'] if team_stats else "N/A",
        "insights_count": len(insights)
    }

    with open('data/summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\nSummary: {summary['total_matches']} matches, {summary['accuracy']}% accuracy")
    print("Data processing complete!")

if __name__ == "__main__":
    main()