"""
Update Tableau Reports with Current Data

This script updates the existing Tableau CSV files with current prediction data
while maintaining the same headers and format.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime

def load_predictions():
    """Load predictions from data file."""
    try:
        predictions_path = Path("data/predictions.json")
        if predictions_path.exists():
            with open(predictions_path, 'r') as f:
                predictions = json.load(f)
            print(f"Loaded {len(predictions)} predictions from data/predictions.json")
            return predictions
        else:
            print("No predictions file found")
            return []
    except Exception as e:
        print(f"Error loading predictions: {e}")
        return []

def update_confidence_intervals(predictions):
    """Update confidence intervals CSV maintaining current format."""
    print("Updating confidence_intervals.csv...")

    # Calculate confidence intervals by confidence level
    confidence_data = {
        'High': {'home_win_pct': [], 'draw_pct': [], 'away_win_pct': []},
        'Medium': {'home_win_pct': [], 'draw_pct': [], 'away_win_pct': []},
        'Low': {'home_win_pct': [], 'draw_pct': [], 'away_win_pct': []}
    }

    for pred in predictions:
        confidence = pred.get('confidence', 0)
        if confidence >= 70:
            level = 'High'
        elif confidence >= 50:
            level = 'Medium'
        else:
            level = 'Low'

        confidence_data[level]['home_win_pct'].append(pred.get('home_win_prob', 0))
        confidence_data[level]['draw_pct'].append(pred.get('draw_prob', 0))
        confidence_data[level]['away_win_pct'].append(pred.get('away_win_prob', 0))

    # Calculate averages for each confidence level
    result = []
    for level in ['High', 'Medium', 'Low']:
        data = confidence_data[level]
        if data['home_win_pct']:  # Only add if there's data
            # Values are already percentages, just average them
            avg_home = np.mean(data['home_win_pct'])
            avg_draw = np.mean(data['draw_pct'])
            avg_away = np.mean(data['away_win_pct'])

            result.append({
                'confidence_level': level,
                'home_win_pct': round(avg_home, 2),
                'draw_pct': round(avg_draw, 2),
                'away_win_pct': round(avg_away, 2)
            })

    # Create DataFrame and save
    df = pd.DataFrame(result)
    output_path = Path("outputs/tableau_data/confidence_intervals.csv")
    df.to_csv(output_path, index=False)
    print(f"Updated confidence_intervals.csv with {len(result)} rows")

def update_match_predictions(predictions):
    """Update match predictions CSV maintaining current format."""
    print("Updating match_predictions.csv...")

    # Convert predictions to Tableau format
    tableau_data = []
    for pred in predictions:
        # Parse date
        date_str = pred.get('date', '')
        try:
            # Handle different date formats
            if '/' in date_str:
                # Assume MM/DD/YYYY format
                date_obj = datetime.strptime(date_str.split(' ')[0], '%m/%d/%Y')
            else:
                date_obj = datetime.strptime(date_str.split(' ')[0], '%Y-%m-%d')
        except:
            date_obj = datetime.now()

        # Map prediction codes to text
        prediction_code = pred.get('prediction_code', pred.get('prediction', 2))
        if isinstance(prediction_code, str):
            if prediction_code == 'Home Win':
                prediction_code = 2
            elif prediction_code == 'Draw':
                prediction_code = 1
            elif prediction_code == 'Away Win':
                prediction_code = 0
            else:
                prediction_code = 2

        # Map actual result
        actual_result = pred.get('actual_result', 'Not Played')
        if actual_result == 'Not Played':
            actual_result_code = -1
            actual_result_text = 'Not Played'
        elif actual_result == 'Home Win':
            actual_result_code = 2
            actual_result_text = 'Home Win'
        elif actual_result == 'Draw':
            actual_result_code = 1
            actual_result_text = 'Draw'
        elif actual_result == 'Away Win':
            actual_result_code = 0
            actual_result_text = 'Away Win'
        else:
            actual_result_code = -1
            actual_result_text = 'Unknown'

        # Determine confidence level
        confidence = pred.get('confidence', 0)
        if confidence >= 70:
            confidence_level = 'High'
        elif confidence >= 50:
            confidence_level = 'Medium'
        else:
            confidence_level = 'Low'

        # Map prediction code to text
        prediction_map = {2: 'Home Win', 1: 'Draw', 0: 'Away Win'}
        prediction_text = prediction_map.get(prediction_code, 'Unknown')

        # Check if prediction is correct
        prediction_correct = (prediction_code == actual_result_code) if actual_result_code != -1 else False

        tableau_row = {
            'date': date_obj.strftime('%Y-%m-%d'),
            'home_team': pred.get('home_team', ''),
            'away_team': pred.get('away_team', ''),
            'home_win_prob': round(pred.get('home_win_prob', 0) / 100, 2),
            'draw_prob': round(pred.get('draw_prob', 0) / 100, 2),
            'away_win_prob': round(pred.get('away_win_prob', 0) / 100, 2),
            'prediction': prediction_code,
            'actual_result': actual_result_code,
            'league': pred.get('league', 'Premier League'),
            'confidence_level': confidence_level,
            'prediction_text': prediction_text,
            'actual_result_text': actual_result_text,
            'home_win_pct': round(pred.get('home_win_prob', 0), 1),
            'draw_pct': round(pred.get('draw_prob', 0), 1),
            'away_win_pct': round(pred.get('away_win_prob', 0), 1),
            'year': date_obj.year,
            'month': date_obj.month,
            'day_of_week': date_obj.strftime('%A'),
            'prediction_correct': prediction_correct
        }
        tableau_data.append(tableau_row)

    # Create DataFrame and save
    df = pd.DataFrame(tableau_data)
    output_path = Path("outputs/tableau_data/match_predictions.csv")
    df.to_csv(output_path, index=False)
    print(f"Updated match_predictions.csv with {len(tableau_data)} rows")

def update_model_performance(predictions):
    """Update model performance CSV maintaining current format."""
    print("Updating model_performance.csv...")

    # Calculate performance metrics
    total_predictions = len(predictions)

    # Count by confidence level
    high_confidence = sum(1 for p in predictions if p.get('confidence', 0) >= 70)
    medium_confidence = sum(1 for p in predictions if 50 <= p.get('confidence', 0) < 70)
    low_confidence = sum(1 for p in predictions if p.get('confidence', 0) < 50)

    # Calculate average probabilities
    avg_home_win = np.mean([p.get('home_win_prob', 0) for p in predictions]) / 100
    avg_draw = np.mean([p.get('draw_prob', 0) for p in predictions]) / 100
    avg_away = np.mean([p.get('away_win_prob', 0) for p in predictions]) / 100

    # Create performance data
    performance_data = [{
        'date': datetime.now().strftime('%Y-%m-%d'),
        'total_predictions': total_predictions,
        'high_confidence_matches': high_confidence,
        'medium_confidence_matches': medium_confidence,
        'low_confidence_matches': low_confidence,
        'avg_home_win_prob': round(avg_home_win, 3),
        'avg_draw_prob': round(avg_draw, 3),
        'avg_away_win_prob': round(avg_away, 3)
    }]

    # Create DataFrame and save
    df = pd.DataFrame(performance_data)
    output_path = Path("outputs/tableau_data/model_performance.csv")
    df.to_csv(output_path, index=False)
    print(f"Updated model_performance.csv")

def update_team_performance_trends(predictions):
    """Update team performance trends CSV maintaining current format."""
    print("Updating team_performance_trends.csv...")

    # Calculate team statistics
    team_stats = {}

    for pred in predictions:
        home_team = pred.get('home_team', '')
        away_team = pred.get('away_team', '')
        league = pred.get('league', 'Premier League')

        # Process home team
        if home_team not in team_stats:
            team_stats[home_team] = {
                'team': home_team,
                'league': league,
                'home_matches': 0,
                'away_matches': 0,
                'home_wins': 0,
                'away_wins': 0,
                'total_matches': 0
            }

        team_stats[home_team]['home_matches'] += 1
        team_stats[home_team]['total_matches'] += 1

        # Count home wins based on prediction
        if pred.get('prediction') == 'Home Win' or pred.get('prediction_code') == 2:
            team_stats[home_team]['home_wins'] += 1

        # Process away team
        if away_team not in team_stats:
            team_stats[away_team] = {
                'team': away_team,
                'league': league,
                'home_matches': 0,
                'away_matches': 0,
                'home_wins': 0,
                'away_wins': 0,
                'total_matches': 0
            }

        team_stats[away_team]['away_matches'] += 1
        team_stats[away_team]['total_matches'] += 1

        # Count away wins based on prediction
        if pred.get('prediction') == 'Away Win' or pred.get('prediction_code') == 0:
            team_stats[away_team]['away_wins'] += 1

    # Calculate derived metrics
    result = []
    for team, stats in team_stats.items():
        home_win_rate = stats['home_wins'] / stats['home_matches'] if stats['home_matches'] > 0 else 0
        away_win_rate = stats['away_wins'] / stats['away_matches'] if stats['away_matches'] > 0 else 0
        overall_strength = (home_win_rate + away_win_rate) / 2

        # Generate recent form (simplified)
        recent_form = "WWDD"  # Placeholder - would need actual historical data

        # Calculate strength ranking (inverse of overall strength)
        strength_ranking = int((1 - overall_strength) * 20) + 1

        team_row = {
            'team': team,
            'league': stats['league'],
            'home_win_rate': round(home_win_rate, 2),
            'away_win_rate': round(away_win_rate, 2),
            'overall_strength': round(overall_strength, 2),
            'recent_form': recent_form,
            'total_matches': stats['total_matches'],
            'strength_ranking': strength_ranking
        }
        result.append(team_row)

    # Sort by strength ranking
    result.sort(key=lambda x: x['strength_ranking'])

    # Create DataFrame and save
    df = pd.DataFrame(result)
    output_path = Path("outputs/tableau_data/team_performance_trends.csv")
    df.to_csv(output_path, index=False)
    print(f"Updated team_performance_trends.csv with {len(result)} teams")

def main():
    """Main function to update all Tableau reports."""
    print("=" * 60)
    print("Updating Tableau Reports")
    print("=" * 60)

    # Load predictions
    predictions = load_predictions()

    if not predictions:
        print("No predictions to process. Exiting.")
        return

    # Update all Tableau files
    try:
        update_confidence_intervals(predictions)
        update_match_predictions(predictions)
        update_model_performance(predictions)
        update_team_performance_trends(predictions)

        print("\n" + "=" * 60)
        print("Tableau Reports Updated Successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"Error updating Tableau reports: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()