"""
Rebuild Predictions Data to Match Tableau Format

This script rebuilds the predictions data to match the exact structure
expected by the Tableau reports and website.
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path

def load_tableau_match_predictions():
    """Load the Tableau match predictions CSV file."""
    try:
        tableau_path = Path("outputs/tableau_data/match_predictions.csv")
        if tableau_path.exists():
            df = pd.read_csv(tableau_path)
            print(f"Loaded {len(df)} matches from Tableau file")
            return df
        else:
            print("Tableau match_predictions.csv not found")
            return None
    except Exception as e:
        print(f"Error loading Tableau file: {e}")
        return None

def convert_tableau_to_predictions_format(tableau_df):
    """Convert Tableau format to website predictions format."""
    predictions = []

    for idx, row in tableau_df.iterrows():
        try:
            # Parse the date from Tableau format
            date_str = str(row['date'])

            # Create default time (noon if not specified)
            time_str = "15:00"  # Default 3:00 PM

            # Create combined date string for website
            combined_date = f"{date_str} {time_str}"

            # Get prediction code from prediction column
            prediction_code = int(row['prediction'])

            # Get prediction text from prediction_text column
            prediction_text = str(row['prediction_text'])

            # Get actual result code from actual_result column
            actual_result_code = int(row['actual_result']) if pd.notna(row['actual_result']) and row['actual_result'] != -1 else -1

            # Get actual result text
            actual_result_text = str(row['actual_result_text'])

            # Check if prediction was correct
            prediction_correct = bool(row.get('prediction_correct', False))

            # Calculate confidence from probabilities
            home_win_prob = float(row['home_win_prob'])
            draw_prob = float(row['draw_prob'])
            away_win_prob = float(row['away_win_prob'])

            probs = [away_win_prob, draw_prob, home_win_prob]
            confidence = max(probs) * 100

            # Calculate ELO ratings based on probabilities
            home_elo = 1500 + int((home_win_prob - 0.33) * 300)
            away_elo = 1500 + int((away_win_prob - 0.33) * 300)

            # Get confidence level
            confidence_level = str(row.get('confidence_level', 'Medium'))

            # Default values for missing fields
            venue = "Unknown Stadium"
            tv = "Unknown"

            # Default odds (not in Tableau file)
            odds_home = None
            odds_away = None
            over_under = 2.5

            # Parse date for year, month, day_of_week
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                year = date_obj.year
                month = date_obj.month
                day_of_week = date_obj.strftime("%A")
            except:
                year = 2026
                month = 5
                day_of_week = "Friday"

            # Create prediction object matching website format
            prediction = {
                "id": idx + 1,
                "date": combined_date,
                "time": time_str,
                "home_team": str(row['home_team']),
                "away_team": str(row['away_team']),
                "venue": venue,
                "tv": tv,
                "league": str(row['league']),
                "home_win_prob": round(float(row['home_win_pct']), 2),
                "draw_prob": round(float(row['draw_pct']), 2),
                "away_win_prob": round(float(row['away_win_pct']), 2),
                "prediction": prediction_text,
                "prediction_code": prediction_code,
                "actual_result": actual_result_text,
                "actual_result_code": actual_result_code,
                "is_correct": prediction_correct,
                "confidence": round(confidence, 2),
                "confidence_level": confidence_level,
                "home_elo": home_elo,
                "away_elo": away_elo,
                "elo_diff": home_elo - away_elo,
                "importance": confidence_level,
                "odds_home": odds_home,
                "odds_away": odds_away,
                "over_under": over_under,
                "year": year,
                "month": month,
                "day_of_week": day_of_week,
                "week_number": datetime.now().isocalendar()[1]
            }

            predictions.append(prediction)

        except Exception as e:
            print(f"Error processing row {idx}: {e}")
            import traceback
            traceback.print_exc()
            continue

    return predictions

def update_predictions_file(predictions):
    """Update the predictions.json file."""
    try:
        output_path = Path("data/predictions.json")
        with open(output_path, 'w') as f:
            json.dump(predictions, f, indent=2)
        print(f"Updated predictions.json with {len(predictions)} predictions")
        return True
    except Exception as e:
        print(f"Error updating predictions file: {e}")
        return False

def update_summary_file(predictions):
    """Update the summary.json file."""
    try:
        # Calculate statistics
        total = len(predictions)
        high_confidence = sum(1 for p in predictions if p.get('confidence', 0) >= 70)
        medium_confidence = sum(1 for p in predictions if 50 <= p.get('confidence', 0) < 70)
        low_confidence = sum(1 for p in predictions if p.get('confidence', 0) < 50)

        home_wins = sum(1 for p in predictions if p.get('prediction') == 'Home Win')
        draws = sum(1 for p in predictions if p.get('prediction') == 'Draw')
        away_wins = sum(1 for p in predictions if p.get('prediction') == 'Away Win')

        # Load existing summary to preserve historical data
        summary_path = Path("data/summary.json")
        if summary_path.exists():
            with open(summary_path, 'r') as f:
                summary = json.load(f)
        else:
            summary = {}

        # Update with current predictions data
        summary.update({
            "current_week_matches": total,
            "high_confidence": high_confidence,
            "medium_confidence": medium_confidence,
            "low_confidence": low_confidence,
            "home_wins_predicted": home_wins,
            "draws_predicted": draws,
            "away_wins_predicted": away_wins,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "current_week": datetime.now().isocalendar()[1]
        })

        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"Updated summary.json")
        return True
    except Exception as e:
        print(f"Error updating summary file: {e}")
        return False

def main():
    """Main function to rebuild predictions data."""
    print("=" * 60)
    print("Rebuilding Predictions Data from Tableau Format")
    print("=" * 60)

    # Load Tableau data
    tableau_df = load_tableau_match_predictions()
    if tableau_df is None:
        print("Failed to load Tableau data. Exiting.")
        return

    # Convert to predictions format
    print("Converting Tableau format to website predictions format...")
    predictions = convert_tableau_to_predictions_format(tableau_df)

    if not predictions:
        print("No predictions generated. Exiting.")
        return

    print(f"Generated {len(predictions)} predictions")

    # Update files
    print("Updating data files...")
    if update_predictions_file(predictions):
        print("Predictions file updated successfully")

    if update_summary_file(predictions):
        print("Summary file updated successfully")

    print("\n" + "=" * 60)
    print("Predictions Data Rebuild Complete!")
    print("=" * 60)
    print(f"Total predictions: {len(predictions)}")
    print(f"High confidence: {sum(1 for p in predictions if p.get('confidence', 0) >= 70)}")
    print(f"Medium confidence: {sum(1 for p in predictions if 50 <= p.get('confidence', 0) < 70)}")
    print(f"Low confidence: {sum(1 for p in predictions if p.get('confidence', 0) < 50)}")

if __name__ == "__main__":
    main()