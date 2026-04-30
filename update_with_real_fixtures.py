"""
Update All Soccer Data with Real Fixtures

Uses actual real match data provided by user to update all files.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, date
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealSoccerDataUpdater:
    """Update all soccer data files with real fixtures."""

    def __init__(self):
        """Initialize the updater with real match data."""
        self.real_fixtures = self.get_real_fixtures()

    def get_real_fixtures(self):
        """
        Get real fixtures from user-provided data.

        Returns:
            List of real fixture dictionaries
        """
        # Actual real fixtures for May 1-4, 2026
        fixtures = [
            {
                'date': '2026-05-01',
                'time': '14:00',
                'home_team': 'Leeds United',
                'away_team': 'Burnley',
                'venue': 'Elland Road, Leeds, England',
                'tv': 'USA Network, Universo',
                'odds_home': -230,
                'odds_away': +190,
                'over_under': 2.5
            },
            {
                'date': '2026-05-02',
                'time': '09:00',
                'home_team': 'Brentford',
                'away_team': 'West Ham United',
                'venue': 'Gtech Community Stadium, London, England',
                'tv': 'USA Network, Universo',
                'odds_home': +100,
                'odds_away': -120,
                'over_under': 2.5
            },
            {
                'date': '2026-05-02',
                'time': '09:00',
                'home_team': 'Newcastle United',
                'away_team': 'Brighton & Hove Albion',
                'venue': 'St. James Park, Newcastle-upon-Tyne, England',
                'tv': 'Peacock',
                'odds_home': +150,
                'odds_away': -175,
                'over_under': 2.5
            },
            {
                'date': '2026-05-02',
                'time': '09:00',
                'home_team': 'Wolverhampton Wanderers',
                'away_team': 'Sunderland',
                'venue': 'Molineux Stadium, Wolverhampton, England',
                'tv': 'Peacock',
                'odds_home': -110,
                'odds_away': +130,
                'over_under': 2.5
            },
            {
                'date': '2026-05-02',
                'time': '11:30',
                'home_team': 'Arsenal',
                'away_team': 'Fulham',
                'venue': 'Emirates Stadium, London, England',
                'tv': 'NBC, Telemundo',
                'odds_home': -225,
                'odds_away': +185,
                'over_under': 2.5
            },
            {
                'date': '2026-05-03',
                'time': '08:00',
                'home_team': 'AFC Bournemouth',
                'away_team': 'Crystal Palace',
                'venue': 'Vitality Stadium, Bournemouth, England',
                'tv': 'Peacock',
                'odds_home': -155,
                'odds_away': +135,
                'over_under': 2.5
            },
            {
                'date': '2026-05-03',
                'time': '09:30',
                'home_team': 'Manchester United',
                'away_team': 'Liverpool',
                'venue': 'Old Trafford, Manchester, England',
                'tv': 'Telemundo, Peacock',
                'odds_home': +130,
                'odds_away': -150,
                'over_under': 3.5
            },
            {
                'date': '2026-05-03',
                'time': '13:00',
                'home_team': 'Aston Villa',
                'away_team': 'Tottenham Hotspur',
                'venue': 'Villa Park, Birmingham, England',
                'tv': 'USA Network, Telemundo',
                'odds_home': +120,
                'odds_away': -140,
                'over_under': 2.5
            },
            {
                'date': '2026-05-04',
                'time': '09:00',
                'home_team': 'Chelsea',
                'away_team': 'Nottingham Forest',
                'venue': 'Stamford Bridge, London, England',
                'tv': 'USA Network, Universo',
                'odds_home': -145,
                'odds_away': +125,
                'over_under': 2.5
            },
            {
                'date': '2026-05-04',
                'time': '14:00',
                'home_team': 'Everton',
                'away_team': 'Manchester City',
                'venue': 'Hill Dickinson Stadium, Liverpool, England',
                'tv': 'USA Network, Universo',
                'odds_home': +180,
                'odds_away': -220,
                'over_under': 2.5
            }
        ]

        logger.info(f"Loaded {len(fixtures)} real fixtures")
        return fixtures

    def odds_to_probability(self, odds):
        """
        Convert American odds to probability.

        Args:
            odds: American odds (e.g., -230, +150)

        Returns:
            Probability as decimal (0-1)
        """
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)

    def calculate_real_probabilities(self, fixture):
        """
        Calculate realistic probabilities based on actual betting odds.

        Args:
            fixture: Fixture dictionary with odds

        Returns:
            Dictionary with home_win_prob, draw_prob, away_win_prob
        """
        # Convert odds to probabilities
        home_prob = self.odds_to_probability(fixture['odds_home'])
        away_prob = self.odds_to_probability(fixture['odds_away'])

        # For soccer, we need to account for the draw
        # Typical draw probability is around 25-30%
        # We'll estimate it based on how close the teams are

        # Calculate the implied probability from odds (without draw)
        total_implied = home_prob + away_prob

        # If the total is too high, we need to make room for draw
        # If it's too low, we can add more draw probability
        if total_implied > 0.75:
            # Teams are heavily favored, draw is less likely
            draw_prob = 1.0 - total_implied
            draw_prob = max(0.20, min(0.30, draw_prob))  # Keep between 20-30%
        elif total_implied < 0.65:
            # Teams are closely matched, draw is more likely
            draw_prob = 0.28  # Higher draw probability for close matches
        else:
            # Standard case
            draw_prob = 0.25

        # Adjust home and away probabilities to accommodate draw
        scaling_factor = (1.0 - draw_prob) / total_implied
        home_prob = home_prob * scaling_factor
        away_prob = away_prob * scaling_factor

        # Ensure all probabilities are positive
        home_prob = max(0.01, home_prob)
        away_prob = max(0.01, away_prob)
        draw_prob = max(0.01, draw_prob)

        # Normalize to ensure they sum to 1
        total = home_prob + away_prob + draw_prob

        return {
            'home_win_prob': round(home_prob / total, 6),
            'away_win_prob': round(away_prob / total, 6),
            'draw_prob': round(draw_prob / total, 6)
        }

    def generate_predictions(self):
        """
        Generate predictions for all real fixtures.

        Returns:
            DataFrame with predictions
        """
        logger.info("Generating predictions for real fixtures...")

        predictions = []

        for fixture in self.real_fixtures:
            # Calculate probabilities based on real odds
            probs = self.calculate_real_probabilities(fixture)

            # Make prediction based on probabilities
            prob_array = [probs['away_win_prob'], probs['draw_prob'], probs['home_win_prob']]
            prediction = int(np.argmax(prob_array))  # 0=Away, 1=Draw, 2=Home

            # Determine confidence level based on max probability
            max_prob = max(prob_array)
            if max_prob > 0.60:
                confidence = 'High'
            elif max_prob > 0.45:
                confidence = 'Medium'
            else:
                confidence = 'Low'

            predictions.append({
                'date': fixture['date'],
                'time': fixture['time'],
                'home_team': fixture['home_team'],
                'away_team': fixture['away_team'],
                'venue': fixture['venue'],
                'tv': fixture['tv'],
                'home_win_prob': probs['home_win_prob'],
                'draw_prob': probs['draw_prob'],
                'away_win_prob': probs['away_win_prob'],
                'prediction': prediction,
                'actual_result': -1,  # Not played yet
                'league': 'Premier League',
                'confidence_level': confidence,
                'odds_home': fixture['odds_home'],
                'odds_away': fixture['odds_away'],
                'over_under': fixture['over_under']
            })

        return pd.DataFrame(predictions)

    def create_tableau_ready_data(self, predictions_df):
        """
        Create Tableau-ready data with enhanced fields.

        Args:
            predictions_df: DataFrame with predictions

        Returns:
            Enhanced DataFrame for Tableau
        """
        logger.info("Creating Tableau-ready data...")

        # Add text fields
        predictions_df['prediction_text'] = predictions_df['prediction'].map({
            2: 'Home Win',
            1: 'Draw',
            0: 'Away Win'
        })

        predictions_df['actual_result_text'] = 'Not Played'

        # Add percentage fields
        predictions_df['home_win_pct'] = (predictions_df['home_win_prob'] * 100).round(2)
        predictions_df['draw_pct'] = (predictions_df['draw_prob'] * 100).round(2)
        predictions_df['away_win_pct'] = (predictions_df['away_win_prob'] * 100).round(2)

        # Add date fields
        predictions_df['date'] = pd.to_datetime(predictions_df['date'])
        predictions_df['year'] = predictions_df['date'].dt.year
        predictions_df['month'] = predictions_df['date'].dt.month
        predictions_df['day_of_week'] = predictions_df['date'].dt.day_name()

        # Add accuracy field
        predictions_df['prediction_correct'] = False

        return predictions_df

    def create_team_performance_data(self, predictions_df):
        """Create team performance data based on real fixtures."""
        all_teams = set(predictions_df['home_team'].unique()) | set(predictions_df['away_team'].unique())

        team_data = []

        for team in all_teams:
            # Get team's fixtures
            home_games = predictions_df[predictions_df['home_team'] == team]
            away_games = predictions_df[predictions_df['away_team'] == team]

            total_games = len(home_games) + len(away_games)

            # Calculate average probabilities
            avg_home_prob = home_games['home_win_prob'].mean() if len(home_games) > 0 else 0
            avg_away_prob = away_games['away_win_prob'].mean() if len(away_games) > 0 else 0

            # Overall strength (average of home and away probabilities)
            overall_strength = (avg_home_prob + avg_away_prob) / 2 if total_games > 0 else 0.5

            team_data.append({
                'team': team,
                'league': 'Premier League',
                'home_win_rate': round(avg_home_prob, 3),
                'away_win_rate': round(avg_away_prob, 3),
                'overall_strength': round(overall_strength, 3),
                'recent_form': '----',  # Will be updated after matches
                'total_matches': total_games
            })

        df = pd.DataFrame(team_data)
        df['strength_ranking'] = df['overall_strength'].rank(ascending=False)

        return df

    def create_model_performance_data(self, predictions_df):
        """Create model performance summary."""
        return pd.DataFrame([{
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total_predictions': len(predictions_df),
            'high_confidence_matches': len(predictions_df[predictions_df['confidence_level'] == 'High']),
            'medium_confidence_matches': len(predictions_df[predictions_df['confidence_level'] == 'Medium']),
            'low_confidence_matches': len(predictions_df[predictions_df['confidence_level'] == 'Low']),
            'avg_home_win_prob': round(predictions_df['home_win_prob'].mean(), 3),
            'avg_draw_prob': round(predictions_df['draw_prob'].mean(), 3),
            'avg_away_win_prob': round(predictions_df['away_win_prob'].mean(), 3)
        }])

    def create_confidence_data(self, predictions_df):
        """Create confidence interval analysis."""
        return predictions_df.groupby('confidence_level').agg({
            'home_win_pct': 'mean',
            'draw_pct': 'mean',
            'away_win_pct': 'mean'
        }).round(2).reset_index()

    def update_all_files(self):
        """Update all data files with real fixture data."""
        logger.info("="*60)
        logger.info("UPDATING ALL FILES WITH REAL FIXTURE DATA")
        logger.info("="*60)

        # Step 1: Generate predictions
        logger.info("\nStep 1: Generating predictions from real fixtures...")
        predictions_df = self.generate_predictions()

        # Step 2: Create Tableau-ready data
        logger.info("\nStep 2: Creating Tableau-ready data...")
        tableau_df = self.create_tableau_ready_data(predictions_df)

        # Step 3: Create additional files
        logger.info("\nStep 3: Creating additional analysis files...")

        team_performance = self.create_team_performance_data(tableau_df)
        model_performance = self.create_model_performance_data(tableau_df)
        confidence_data = self.create_confidence_data(tableau_df)

        # Step 4: Save all files
        logger.info("\nStep 4: Saving updated files...")

        output_dir = Path("outputs/tableau_data")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save main predictions file
        tableau_df.to_csv(output_dir / "match_predictions.csv", index=False)
        logger.info(f"[OK] Updated match_predictions.csv ({len(tableau_df)} real matches)")

        # Save team performance
        team_performance.to_csv(output_dir / "team_performance_trends.csv", index=False)
        logger.info(f"[OK] Updated team_performance_trends.csv ({len(team_performance)} teams)")

        # Save model performance
        model_performance.to_csv(output_dir / "model_performance.csv", index=False)
        logger.info(f"[OK] Updated model_performance.csv")

        # Save confidence intervals
        confidence_data.to_csv(output_dir / "confidence_intervals.csv", index=False)
        logger.info(f"[OK] Updated confidence_intervals.csv")

        logger.info("\n" + "="*60)
        logger.info("ALL FILES UPDATED WITH REAL DATA!")
        logger.info("="*60)

        return {
            'match_predictions': tableau_df,
            'team_performance': team_performance,
            'model_performance': model_performance,
            'confidence_intervals': confidence_data
        }


def main():
    """Main function to update all files with real data."""
    updater = RealSoccerDataUpdater()

    # Update all files
    data = updater.update_all_files()

    if data:
        # Show sample of real data
        logger.info("\n" + "="*60)
        logger.info("REAL FIXTURE DATA SAMPLE")
        logger.info("="*60)

        sample_cols = ['date', 'time', 'home_team', 'away_team', 'prediction_text',
                      'confidence_level', 'home_win_pct', 'odds_home', 'odds_away']

        print("\nReal Premier League Fixtures (May 1-4, 2026):")
        print(data['match_predictions'][sample_cols].to_string(index=False))

        logger.info(f"\nAll data files updated with real fixture information!")
        logger.info(f"Data location: {Path('outputs/tableau_data').absolute()}")


if __name__ == "__main__":
    main()