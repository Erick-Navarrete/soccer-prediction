"""
Advanced Tableau Analysis Metrics

This script generates advanced analysis metrics specifically designed for Tableau visualization.
Includes trend analysis, predictive accuracy, confidence intervals, and more.

Author: Soccer Prediction System
Date: 2026-04-29
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import json
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('outputs/tableau_data/advanced_metrics.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AdvancedTableauMetrics:
    """Generate advanced metrics for Tableau analysis."""

    def __init__(self, base_dir="outputs"):
        """Initialize the metrics generator."""
        self.base_dir = Path(base_dir)
        self.tableau_dir = self.base_dir / "tableau_data"
        self.tableau_dir.mkdir(exist_ok=True)

        # Load existing data
        self.load_data()

        logger.info("Advanced Tableau Metrics initialized")
        logger.info(f"Base directory: {self.base_dir}")

    def load_data(self):
        """Load existing prediction data."""
        try:
            # Load predictions
            self.predictions = pd.read_csv(self.base_dir / "predictions.csv")
            self.predictions['date'] = pd.to_datetime(self.predictions['date'])

            logger.info(f"Loaded {len(self.predictions)} predictions")

        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.predictions = pd.DataFrame()

    def create_trend_analysis_file(self):
        """Create trend analysis data for time series visualization."""
        logger.info("Creating trend analysis file...")

        if self.predictions.empty:
            logger.warning("No predictions data available")
            return pd.DataFrame()

        # Create daily aggregates
        self.predictions['date_only'] = self.predictions['date'].dt.date
        daily_data = []

        for date in sorted(self.predictions['date_only'].unique()):
            date_mask = self.predictions['date_only'] == date
            date_predictions = self.predictions[date_mask]

            trend_data = {
                'date': str(date),
                'year': date.year,
                'month': date.month,
                'day': date.day,
                'day_of_week': date.strftime('%A'),
                'week_number': date.isocalendar()[1],
                'quarter': f"{date.year}Q{(date.month-1)//3 + 1}",

                # Match counts
                'total_matches': len(date_predictions),
                'home_wins_predicted': (date_predictions['prediction'] == 2).sum(),
                'draws_predicted': (date_predictions['prediction'] == 1).sum(),
                'away_wins_predicted': (date_predictions['prediction'] == 0).sum(),

                # Average probabilities
                'avg_home_win_prob': date_predictions['home_win_prob'].mean(),
                'avg_draw_prob': date_predictions['draw_prob'].mean(),
                'avg_away_win_prob': date_predictions['away_win_prob'].mean(),

                # Confidence distribution
                'high_confidence_count': 0,  # Will calculate below
                'medium_confidence_count': 0,
                'low_confidence_count': 0,

                # Accuracy metrics
                'correct_predictions': 0,
                'total_actual_results': 0,

                # Volatility metrics
                'probability_std': date_predictions['home_win_prob'].std(),
                'max_home_prob': date_predictions['home_win_prob'].max(),
                'min_home_prob': date_predictions['home_win_prob'].min(),

                # Unique teams
                'unique_teams': len(set(date_predictions['home_team'].tolist() + date_predictions['away_team'].tolist()))
            }

            # Calculate confidence levels
            for _, row in date_predictions.iterrows():
                max_prob = max(row['home_win_prob'], row['draw_prob'], row['away_win_prob'])
                if max_prob >= 0.7:
                    trend_data['high_confidence_count'] += 1
                elif max_prob >= 0.5:
                    trend_data['medium_confidence_count'] += 1
                else:
                    trend_data['low_confidence_count'] += 1

            # Calculate accuracy if actual results available
            if 'actual_result' in date_predictions.columns:
                valid_results = date_predictions[date_predictions['actual_result'] != -1]
                trend_data['correct_predictions'] = (valid_results['prediction'] == valid_results['actual_result']).sum()
                trend_data['total_actual_results'] = len(valid_results)

            daily_data.append(trend_data)

        trend_df = pd.DataFrame(daily_data)

        # Calculate moving averages
        trend_df['moving_avg_3day'] = trend_df['avg_home_win_prob'].rolling(window=3, min_periods=1).mean()
        trend_df['moving_avg_7day'] = trend_df['avg_home_win_prob'].rolling(window=7, min_periods=1).mean()

        # Calculate trend direction
        trend_df['trend_direction'] = np.where(
            trend_df['avg_home_win_prob'] > trend_df['moving_avg_3day'],
            'Increasing',
            'Decreasing'
        )

        # Save to CSV
        output_path = self.tableau_dir / "trend_analysis.csv"
        trend_df.to_csv(output_path, index=False)
        logger.info(f"Saved trend analysis to {output_path}")

        return trend_df

    def create_confidence_intervals_file(self):
        """Create confidence intervals for predictions."""
        logger.info("Creating confidence intervals file...")

        if self.predictions.empty:
            logger.warning("No predictions data available")
            return pd.DataFrame()

        confidence_data = []

        for _, row in self.predictions.iterrows():
            # Calculate confidence intervals for each outcome
            probs = [row['home_win_prob'], row['draw_prob'], row['away_win_prob']]
            max_prob = max(probs)
            predicted_outcome = probs.index(max_prob)

            # Calculate confidence interval (simple approach)
            std_dev = np.std(probs)
            confidence_level = max_prob

            # Determine confidence category
            if confidence_level >= 0.8:
                category = 'Very High'
            elif confidence_level >= 0.7:
                category = 'High'
            elif confidence_level >= 0.6:
                category = 'Medium-High'
            elif confidence_level >= 0.5:
                category = 'Medium'
            elif confidence_level >= 0.4:
                category = 'Medium-Low'
            else:
                category = 'Low'

            # Calculate margin of error
            margin_of_error = 1.96 * std_dev  # 95% confidence interval

            conf_data = {
                'date': str(row['date']),
                'home_team': row['home_team'],
                'away_team': row['away_team'],
                'league': row['league'],

                # Predicted outcome
                'predicted_outcome': ['Away Win', 'Draw', 'Home Win'][predicted_outcome],
                'predicted_probability': confidence_level,
                'confidence_category': category,

                # Home win interval
                'home_win_prob': row['home_win_prob'],
                'home_win_lower': max(0, row['home_win_prob'] - margin_of_error),
                'home_win_upper': min(1, row['home_win_prob'] + margin_of_error),

                # Draw interval
                'draw_prob': row['draw_prob'],
                'draw_lower': max(0, row['draw_prob'] - margin_of_error),
                'draw_upper': min(1, row['draw_prob'] + margin_of_error),

                # Away win interval
                'away_win_prob': row['away_win_prob'],
                'away_win_lower': max(0, row['away_win_prob'] - margin_of_error),
                'away_win_upper': min(1, row['away_win_prob'] + margin_of_error),

                # Uncertainty metrics
                'probability_std': std_dev,
                'margin_of_error': margin_of_error,
                'uncertainty_level': 'Low' if std_dev < 0.1 else 'Medium' if std_dev < 0.2 else 'High',

                # Actual result if available
                'actual_outcome': ['Away Win', 'Draw', 'Home Win'][row['actual_result']] if 'actual_result' in row and row['actual_result'] != -1 else 'Unknown',
                'prediction_correct': (row['prediction'] == row['actual_result']) if 'actual_result' in row and row['actual_result'] != -1 else None
            }

            confidence_data.append(conf_data)

        confidence_df = pd.DataFrame(confidence_data)

        # Save to CSV
        output_path = self.tableau_dir / "confidence_intervals.csv"
        confidence_df.to_csv(output_path, index=False)
        logger.info(f"Saved confidence intervals to {output_path}")

        return confidence_df

    def create_team_performance_trends_file(self):
        """Create team performance trends over time."""
        logger.info("Creating team performance trends file...")

        if self.predictions.empty:
            logger.warning("No predictions data available")
            return pd.DataFrame()

        team_trends = []

        # Get all unique teams
        all_teams = set(self.predictions['home_team'].tolist() + self.predictions['away_team'].tolist())

        for team in sorted(all_teams):
            # Get matches where this team played
            home_matches = self.predictions[self.predictions['home_team'] == team].copy()
            away_matches = self.predictions[self.predictions['away_team'] == team].copy()

            # Calculate home performance
            if not home_matches.empty:
                home_win_rate = (home_matches['prediction'] == 2).mean()
                avg_home_prob = home_matches['home_win_prob'].mean()
            else:
                home_win_rate = 0
                avg_home_prob = 0

            # Calculate away performance
            if not away_matches.empty:
                away_win_rate = (away_matches['prediction'] == 0).mean()
                avg_away_prob = away_matches['away_win_prob'].mean()
            else:
                away_win_rate = 0
                avg_away_prob = 0

            # Overall performance
            total_matches = len(home_matches) + len(away_matches)
            overall_win_prob = (avg_home_prob * len(home_matches) + avg_away_prob * len(away_matches)) / total_matches if total_matches > 0 else 0

            # Form trend (last 5 matches)
            recent_matches = pd.concat([home_matches, away_matches]).sort_values('date', ascending=False).head(5)
            if not recent_matches.empty:
                recent_form = []
                for _, match in recent_matches.iterrows():
                    if match['home_team'] == team:
                        result = 'W' if match['prediction'] == 2 else 'D' if match['prediction'] == 1 else 'L'
                    else:
                        result = 'W' if match['prediction'] == 0 else 'D' if match['prediction'] == 1 else 'L'
                    recent_form.append(result)
                form_string = ''.join(recent_form)
            else:
                form_string = ''

            trend_data = {
                'team': team,
                'league': home_matches['league'].iloc[0] if not home_matches.empty else away_matches['league'].iloc[0] if not away_matches.empty else 'Unknown',

                # Match counts
                'total_matches': total_matches,
                'home_matches': len(home_matches),
                'away_matches': len(away_matches),

                # Performance metrics
                'home_win_rate': home_win_rate,
                'away_win_rate': away_win_rate,
                'overall_win_probability': overall_win_prob,

                # Probability averages
                'avg_home_win_prob': avg_home_prob,
                'avg_away_win_prob': avg_away_prob,
                'avg_draw_prob': (home_matches['draw_prob'].mean() * len(home_matches) + away_matches['draw_prob'].mean() * len(away_matches)) / total_matches if total_matches > 0 else 0,

                # Recent form
                'recent_form': form_string,
                'form_points': sum([3 if f == 'W' else 1 if f == 'D' else 0 for f in recent_form]),

                # Strength indicators
                'home_strength': avg_home_prob,
                'away_strength': avg_away_prob,
                'overall_strength': overall_win_prob,

                # Consistency (std of probabilities)
                'home_consistency': home_matches['home_win_prob'].std() if not home_matches.empty else 0,
                'away_consistency': away_matches['away_win_prob'].std() if not away_matches.empty else 0,

                # Last match date
                'last_match_date': str(max(home_matches['date'].max() if not home_matches.empty else pd.Timestamp.min,
                                        away_matches['date'].max() if not away_matches.empty else pd.Timestamp.min))
            }

            team_trends.append(trend_data)

        team_trends_df = pd.DataFrame(team_trends)

        # Calculate rankings
        team_trends_df['strength_ranking'] = team_trends_df['overall_strength'].rank(ascending=False)
        team_trends_df['consistency_ranking'] = (1 - team_trends_df['home_consistency']).rank(ascending=False)

        # Save to CSV
        output_path = self.tableau_dir / "team_performance_trends.csv"
        team_trends_df.to_csv(output_path, index=False)
        logger.info(f"Saved team performance trends to {output_path}")

        return team_trends_df

    def create_predictive_accuracy_file(self):
        """Create predictive accuracy analysis."""
        logger.info("Creating predictive accuracy file...")

        if self.predictions.empty:
            logger.warning("No predictions data available")
            return pd.DataFrame()

        # Filter predictions with actual results
        valid_predictions = self.predictions[self.predictions['actual_result'] != -1].copy()

        if valid_predictions.empty:
            logger.warning("No predictions with actual results available")
            return pd.DataFrame()

        accuracy_data = []

        # Overall accuracy
        total_correct = (valid_predictions['prediction'] == valid_predictions['actual_result']).sum()
        total_predictions = len(valid_predictions)
        overall_accuracy = total_correct / total_predictions if total_predictions > 0 else 0

        # Accuracy by prediction type
        for pred_type in [0, 1, 2]:  # Away, Draw, Home
            type_predictions = valid_predictions[valid_predictions['prediction'] == pred_type]
            if not type_predictions.empty:
                type_correct = (type_predictions['prediction'] == type_predictions['actual_result']).sum()
                type_accuracy = type_correct / len(type_predictions)

                accuracy_data.append({
                    'prediction_type': ['Away Win', 'Draw', 'Home Win'][pred_type],
                    'total_predictions': len(type_predictions),
                    'correct_predictions': type_correct,
                    'accuracy': type_accuracy,
                    'error_rate': 1 - type_accuracy,
                    'category': 'By Prediction Type'
                })

        # Accuracy by confidence level
        for confidence in ['High', 'Medium', 'Low']:
            conf_predictions = valid_predictions[
                valid_predictions.apply(
                    lambda row: self._get_confidence_level(row),
                    axis=1
                ) == confidence
            ]
            if not conf_predictions.empty:
                conf_correct = (conf_predictions['prediction'] == conf_predictions['actual_result']).sum()
                conf_accuracy = conf_correct / len(conf_predictions)

                accuracy_data.append({
                    'prediction_type': confidence,
                    'total_predictions': len(conf_predictions),
                    'correct_predictions': conf_correct,
                    'accuracy': conf_accuracy,
                    'error_rate': 1 - conf_accuracy,
                    'category': 'By Confidence Level'
                })

        # Accuracy by league
        for league in valid_predictions['league'].unique():
            league_predictions = valid_predictions[valid_predictions['league'] == league]
            if not league_predictions.empty:
                league_correct = (league_predictions['prediction'] == league_predictions['actual_result']).sum()
                league_accuracy = league_correct / len(league_predictions)

                accuracy_data.append({
                    'prediction_type': league,
                    'total_predictions': len(league_predictions),
                    'correct_predictions': league_correct,
                    'accuracy': league_accuracy,
                    'error_rate': 1 - league_accuracy,
                    'category': 'By League'
                })

        # Add overall metrics
        accuracy_data.append({
            'prediction_type': 'Overall',
            'total_predictions': total_predictions,
            'correct_predictions': total_correct,
            'accuracy': overall_accuracy,
            'error_rate': 1 - overall_accuracy,
            'category': 'Overall'
        })

        accuracy_df = pd.DataFrame(accuracy_data)

        # Save to CSV
        output_path = self.tableau_dir / "predictive_accuracy.csv"
        accuracy_df.to_csv(output_path, index=False)
        logger.info(f"Saved predictive accuracy to {output_path}")

        return accuracy_df

    def create_probability_distribution_file(self):
        """Create probability distribution analysis."""
        logger.info("Creating probability distribution file...")

        if self.predictions.empty:
            logger.warning("No predictions data available")
            return pd.DataFrame()

        distribution_data = []

        # Create probability bins
        bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        bin_labels = ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50-60%', '60-70%', '70-80%', '80-90%', '90-100%']

        for outcome in ['home_win_prob', 'draw_prob', 'away_win_prob']:
            outcome_name = outcome.replace('_prob', '').replace('_', ' ').title()

            # Calculate distribution
            hist, _ = np.histogram(self.predictions[outcome], bins=bins)

            for i, (count, bin_label) in enumerate(zip(hist, bin_labels)):
                distribution_data.append({
                    'outcome_type': outcome_name,
                    'probability_range': bin_label,
                    'range_lower': bins[i],
                    'range_upper': bins[i+1],
                    'count': int(count),
                    'percentage': (count / len(self.predictions)) * 100,
                    'cumulative_percentage': (hist[:i+1].sum() / len(self.predictions)) * 100
                })

        distribution_df = pd.DataFrame(distribution_data)

        # Save to CSV
        output_path = self.tableau_dir / "probability_distribution.csv"
        distribution_df.to_csv(output_path, index=False)
        logger.info(f"Saved probability distribution to {output_path}")

        return distribution_df

    def create_head_to_head_analysis_file(self):
        """Create head-to-head matchup analysis."""
        logger.info("Creating head-to-head analysis file...")

        if self.predictions.empty:
            logger.warning("No predictions data available")
            return pd.DataFrame()

        h2h_data = []

        # Get all unique matchups
        matchups = set()
        for _, row in self.predictions.iterrows():
            # Create sorted tuple to avoid duplicates
            matchup = tuple(sorted([row['home_team'], row['away_team']]))
            matchups.add(matchup)

        for team1, team2 in sorted(matchups):
            # Get all matches between these teams
            team1_home = self.predictions[
                (self.predictions['home_team'] == team1) &
                (self.predictions['away_team'] == team2)
            ]

            team2_home = self.predictions[
                (self.predictions['home_team'] == team2) &
                (self.predictions['away_team'] == team1)
            ]

            all_matches = pd.concat([team1_home, team2_home])

            if all_matches.empty:
                continue

            # Calculate head-to-head stats
            team1_wins = len(team1_home[team1_home['prediction'] == 2]) + len(team2_home[team2_home['prediction'] == 0])
            team2_wins = len(team2_home[team2_home['prediction'] == 2]) + len(team1_home[team1_home['prediction'] == 0])
            draws = len(all_matches[all_matches['prediction'] == 1])

            # Average probabilities when team1 is home
            if not team1_home.empty:
                team1_home_avg = team1_home['home_win_prob'].mean()
                team2_away_avg = team1_home['away_win_prob'].mean()
            else:
                team1_home_avg = 0
                team2_away_avg = 0

            # Average probabilities when team2 is home
            if not team2_home.empty:
                team2_home_avg = team2_home['home_win_prob'].mean()
                team1_away_avg = team2_home['away_win_prob'].mean()
            else:
                team2_home_avg = 0
                team1_away_avg = 0

            h2h_stats = {
                'team1': team1,
                'team2': team2,
                'total_matches': len(all_matches),
                'team1_wins': team1_wins,
                'team2_wins': team2_wins,
                'draws': draws,
                'team1_win_rate': team1_wins / len(all_matches) if len(all_matches) > 0 else 0,
                'team2_win_rate': team2_wins / len(all_matches) if len(all_matches) > 0 else 0,
                'draw_rate': draws / len(all_matches) if len(all_matches) > 0 else 0,

                # Home advantage analysis
                'team1_home_advantage': team1_home_avg - team1_away_avg,
                'team2_home_advantage': team2_home_avg - team2_away_avg,

                # Average probabilities
                'team1_avg_win_prob': (team1_home_avg + team1_away_avg) / 2,
                'team2_avg_win_prob': (team2_home_avg + team2_away_avg) / 2,

                # Last meeting
                'last_meeting_date': str(all_matches['date'].max()),
                'last_result': self._get_match_result(all_matches.iloc[-1], team1, team2),

                # Historical dominance
                'dominant_team': team1 if team1_wins > team2_wins else team2 if team2_wins > team1_wins else 'Balanced',
                'dominance_margin': abs(team1_wins - team2_wins)
            }

            h2h_data.append(h2h_stats)

        h2h_df = pd.DataFrame(h2h_data)

        # Save to CSV
        output_path = self.tableau_dir / "head_to_head_analysis.csv"
        h2h_df.to_csv(output_path, index=False)
        logger.info(f"Saved head-to-head analysis to {output_path}")

        return h2h_df

    def _get_confidence_level(self, row):
        """Get confidence level for a prediction."""
        max_prob = max(row['home_win_prob'], row['draw_prob'], row['away_win_prob'])
        if max_prob >= 0.7:
            return 'High'
        elif max_prob >= 0.5:
            return 'Medium'
        else:
            return 'Low'

    def _get_match_result(self, match_row, team1, team2):
        """Get match result from perspective of team1."""
        if match_row['home_team'] == team1:
            if match_row['prediction'] == 2:
                return f'{team1} Win'
            elif match_row['prediction'] == 1:
                return 'Draw'
            else:
                return f'{team2} Win'
        else:
            if match_row['prediction'] == 2:
                return f'{team2} Win'
            elif match_row['prediction'] == 1:
                return 'Draw'
            else:
                return f'{team1} Win'

    def create_advanced_summary(self):
        """Create a summary of all advanced metrics."""
        logger.info("Creating advanced metrics summary...")

        summary = {
            "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "total_predictions": len(self.predictions),
            "metrics_created": [
                "trend_analysis.csv",
                "confidence_intervals.csv",
                "team_performance_trends.csv",
                "predictive_accuracy.csv",
                "probability_distribution.csv",
                "head_to_head_analysis.csv"
            ],
            "visualization_recommendations": [
                "Use trend_analysis.csv for time series charts",
                "Use confidence_intervals.csv for error bar charts",
                "Use team_performance_trends.csv for team comparison dashboards",
                "Use predictive_accuracy.csv for accuracy KPIs",
                "Use probability_distribution.csv for histogram analysis",
                "Use head_to_head_analysis.csv for matchup matrices"
            ],
            "tableau_tips": [
                "Create calculated fields for rolling averages",
                "Use parameters for interactive confidence level filtering",
                "Build story points for narrative analysis",
                "Use color coding for confidence levels",
                "Create tooltips with detailed probability breakdowns"
            ]
        }

        summary_path = self.tableau_dir / "advanced_metrics_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Advanced metrics summary saved to {summary_path}")
        return summary

    def generate_all_advanced_metrics(self):
        """Generate all advanced metrics for Tableau."""
        logger.info("="*60)
        logger.info("ADVANCED TABLEAU METRICS GENERATION")
        logger.info("="*60)

        try:
            # Generate all metric files
            self.create_trend_analysis_file()
            self.create_confidence_intervals_file()
            self.create_team_performance_trends_file()
            self.create_predictive_accuracy_file()
            self.create_probability_distribution_file()
            self.create_head_to_head_analysis_file()

            # Create summary
            summary = self.create_advanced_summary()

            logger.info("="*60)
            logger.info("ADVANCED METRICS GENERATION COMPLETE")
            logger.info("="*60)
            logger.info(f"Total metrics files created: {len(summary['metrics_created'])}")
            logger.info(f"Total predictions analyzed: {summary['total_predictions']}")
            logger.info()
            logger.info("Advanced metrics ready for Tableau visualization!")

            return True

        except Exception as e:
            logger.error(f"Error generating advanced metrics: {e}")
            return False


def main():
    """Main function to generate advanced metrics."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate Advanced Tableau Metrics'
    )
    parser.add_argument(
        '--base-dir',
        type=str,
        default='outputs',
        help='Base directory for data files'
    )

    args = parser.parse_args()

    # Create metrics generator
    generator = AdvancedTableauMetrics(base_dir=args.base_dir)

    # Generate all advanced metrics
    success = generator.generate_all_advanced_metrics()

    # Exit with appropriate code
    exit(0 if success else 1)


if __name__ == "__main__":
    main()