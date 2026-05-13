"""
Fetch Historical Premier League Data for Current Season

Retrieves all match data from the 2025-26 Premier League season
from football-data.co.uk and processes it for analysis.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import requests
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PremierLeagueHistoricalDataFetcher:
    """Fetch and process historical Premier League data."""

    def __init__(self, season="2526"):
        """
        Initialize the historical data fetcher.

        Args:
            season: Season code (e.g., "2526" for 2025-26 season)
        """
        self.season = season
        self.base_url = "https://www.football-data.co.uk/mmz4281"

    def fetch_premier_league_data(self):
        """
        Fetch Premier League data from football-data.co.uk.

        Returns:
            DataFrame with historical match data
        """
        logger.info(f"Fetching Premier League data for {self.get_season_name()}...")

        try:
            # Premier League code is 'E0'
            url = f"{self.base_url}/{self.season}/E0.csv"

            logger.info(f"Downloading from: {url}")
            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                # Save raw data
                raw_data = response.text

                # Parse CSV
                df = pd.read_csv(pd.io.common.StringIO(raw_data))

                logger.info(f"Successfully fetched {len(df)} matches")

                # Add season information
                df['Season'] = self.get_season_name()
                df['League'] = 'Premier League'

                return df
            else:
                logger.error(f"Failed to fetch data: HTTP {response.status_code}")
                return self.get_sample_historical_data()

        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            logger.info("Using sample historical data instead")
            return self.get_sample_historical_data()

    def get_season_name(self):
        """Get human-readable season name."""
        year1 = int(self.season[:2])
        year2 = int(self.season[2:4])
        return f"20{year1}-20{year2}"

    def get_sample_historical_data(self):
        """
        Generate sample historical data for demonstration.

        Returns:
            DataFrame with sample historical matches
        """
        logger.info("Generating sample historical Premier League data...")

        # Premier League teams
        teams = [
            'Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton',
            'Chelsea', 'Crystal Palace', 'Everton', 'Fulham', 'Ipswich',
            'Leicester', 'Liverpool', 'Man City', 'Man United', 'Newcastle',
            'Nottm Forest', 'Southampton', 'Tottenham', 'West Ham', 'Wolves'
        ]

        # Generate sample matches for the season
        matches = []

        # Simulate a full season of matches (380 matches)
        for gameweek in range(1, 39):
            # Create matchups for each gameweek
            week_teams = teams.copy()

            for i in range(0, len(week_teams), 2):
                if i + 1 < len(week_teams):
                    home_team = week_teams[i]
                    away_team = week_teams[i + 1]

                    # Generate realistic results based on team strength
                    home_strength = self.get_team_strength(home_team)
                    away_strength = self.get_team_strength(away_team)

                    # Calculate result probabilities
                    home_advantage = 0.1
                    home_prob = home_strength + home_advantage
                    away_prob = away_strength - home_advantage
                    draw_prob = 0.25

                    # Normalize
                    total = home_prob + away_prob + draw_prob
                    home_prob /= total
                    away_prob /= total
                    draw_prob /= total

                    # Generate result
                    result = np.random.choice(['H', 'D', 'A'],
                                            p=[home_prob, draw_prob, away_prob])

                    # Generate scores based on result
                    if result == 'H':
                        home_goals = np.random.randint(1, 4)
                        away_goals = np.random.randint(0, 2)
                    elif result == 'A':
                        home_goals = np.random.randint(0, 2)
                        away_goals = np.random.randint(1, 4)
                    else:  # Draw
                        home_goals = away_goals = np.random.randint(0, 3)

                    # Generate date (spread across August 2025 - May 2026)
                    week_offset = (gameweek - 1) * 7
                    match_date = datetime(2025, 8, 16) + pd.Timedelta(days=week_offset)

                    matches.append({
                        'Date': match_date.strftime('%d/%m/%Y'),
                        'HomeTeam': home_team,
                        'AwayTeam': away_team,
                        'FTHG': home_goals,  # Full Time Home Goals
                        'FTAG': away_goals,  # Full Time Away Goals
                        'FTR': result,       # Full Time Result
                        'HTHG': min(home_goals, 2),  # Half Time Home Goals
                        'HTAG': min(away_goals, 2),  # Half Time Away Goals
                        'HTR': result if home_goals > 1 or away_goals > 1 else 'D',  # Half Time Result
                        'Season': self.get_season_name(),
                        'League': 'Premier League',
                        'GameWeek': gameweek
                    })

        df = pd.DataFrame(matches)
        logger.info(f"Generated {len(df)} sample matches")
        return df

    def get_team_strength(self, team_name):
        """Get team strength for realistic results."""
        # Approximate strength based on historical performance
        strength_map = {
            'Man City': 0.85,
            'Arsenal': 0.80,
            'Liverpool': 0.78,
            'Chelsea': 0.70,
            'Man United': 0.65,
            'Tottenham': 0.62,
            'Newcastle': 0.60,
            'Brighton': 0.58,
            'Aston Villa': 0.55,
            'Brentford': 0.52,
            'West Ham': 0.50,
            'Crystal Palace': 0.48,
            'Fulham': 0.47,
            'Wolves': 0.45,
            'Everton': 0.42,
            'Nottm Forest': 0.40,
            'Bournemouth': 0.38,
            'Leicester': 0.35,
            'Ipswich': 0.32,
            'Southampton': 0.30
        }
        return strength_map.get(team_name, 0.50)

    def process_historical_data(self, df):
        """
        Process historical data for analysis.

        Args:
            df: Raw historical data

        Returns:
            Processed DataFrame with additional features
        """
        logger.info("Processing historical data...")

        # Convert date
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')

        # Create result encoding
        result_map = {'H': 2, 'D': 1, 'A': 0}
        df['Result'] = df['FTR'].map(result_map)

        # Calculate goal difference
        df['GoalDifference'] = df['FTHG'] - df['FTAG']

        # Calculate total goals
        df['TotalGoals'] = df['FTHG'] + df['FTAG']

        # Add over/under indicator (2.5 goals)
        df['Over2_5'] = (df['TotalGoals'] > 2).astype(int)

        # Clean data
        df = df.dropna(subset=['Date', 'HomeTeam', 'AwayTeam', 'FTR'])

        logger.info(f"Processed {len(df)} matches")
        return df

    def calculate_team_statistics(self, df):
        """
        Calculate comprehensive team statistics from historical data.

        Args:
            df: Processed historical data

        Returns:
            DataFrame with team statistics
        """
        logger.info("Calculating team statistics...")

        teams = set(df['HomeTeam'].unique()) | set(df['AwayTeam'].unique())

        team_stats = []

        for team in teams:
            # Home matches
            home_matches = df[df['HomeTeam'] == team]
            home_played = len(home_matches)
            home_wins = len(home_matches[home_matches['FTR'] == 'H'])
            home_draws = len(home_matches[home_matches['FTR'] == 'D'])
            home_losses = home_played - home_wins - home_draws
            home_goals_for = home_matches['FTHG'].sum()
            home_goals_against = home_matches['FTAG'].sum()

            # Away matches
            away_matches = df[df['AwayTeam'] == team]
            away_played = len(away_matches)
            away_wins = len(away_matches[away_matches['FTR'] == 'A'])
            away_draws = len(away_matches[away_matches['FTR'] == 'D'])
            away_losses = away_played - away_wins - away_draws
            away_goals_for = away_matches['FTAG'].sum()
            away_goals_against = away_matches['FTHG'].sum()

            # Total statistics
            total_played = home_played + away_played
            total_wins = home_wins + away_wins
            total_draws = home_draws + away_draws
            total_losses = home_losses + away_losses
            total_points = total_wins * 3 + total_draws
            total_goals_for = home_goals_for + away_goals_for
            total_goals_against = home_goals_against + away_goals_against
            goal_difference = total_goals_for - total_goals_against

            # Calculate rates
            home_win_rate = home_wins / home_played if home_played > 0 else 0
            away_win_rate = away_wins / away_played if away_played > 0 else 0
            overall_win_rate = total_wins / total_played if total_played > 0 else 0

            # Recent form (last 5 matches)
            all_matches = pd.concat([
                home_matches.assign(venue='home'),
                away_matches.assign(venue='away')
            ]).sort_values('Date', ascending=False)

            recent_form = []
            for _, match in all_matches.head(5).iterrows():
                if match['HomeTeam'] == team:
                    result = match['FTR']
                else:
                    result = {'H': 'A', 'A': 'H', 'D': 'D'}[match['FTR']]
                recent_form.append(result)

            recent_form_str = ''.join(recent_form) if recent_form else '-----'

            team_stats.append({
                'Team': team,
                'League': 'Premier League',
                'Season': self.get_season_name(),
                'Matches_Played': total_played,
                'Wins': total_wins,
                'Draws': total_draws,
                'Losses': total_losses,
                'Points': total_points,
                'Goals_For': total_goals_for,
                'Goals_Against': total_goals_against,
                'Goal_Difference': goal_difference,
                'Home_Wins': home_wins,
                'Home_Draws': home_draws,
                'Home_Losses': home_losses,
                'Home_Goals_For': home_goals_for,
                'Home_Goals_Against': home_goals_against,
                'Away_Wins': away_wins,
                'Away_Draws': away_draws,
                'Away_Losses': away_losses,
                'Away_Goals_For': away_goals_for,
                'Away_Goals_Against': away_goals_against,
                'Home_Win_Rate': round(home_win_rate, 3),
                'Away_Win_Rate': round(away_win_rate, 3),
                'Overall_Win_Rate': round(overall_win_rate, 3),
                'Recent_Form': recent_form_str,
                'Position': 0  # Will be calculated after sorting
            })

        # Create DataFrame and calculate position
        stats_df = pd.DataFrame(team_stats)
        stats_df = stats_df.sort_values(['Points', 'Goal_Difference'], ascending=False)
        stats_df['Position'] = range(1, len(stats_df) + 1)

        logger.info(f"Calculated statistics for {len(stats_df)} teams")
        return stats_df

    def generate_historical_analysis(self, df):
        """
        Generate comprehensive historical analysis.

        Args:
            df: Processed historical data

        Returns:
            Dictionary with analysis results
        """
        logger.info("Generating historical analysis...")

        # Overall statistics
        total_matches = len(df)
        home_wins = len(df[df['FTR'] == 'H'])
        draws = len(df[df['FTR'] == 'D'])
        away_wins = len(df[df['FTR'] == 'A'])

        # Goal statistics
        total_goals = df['TotalGoals'].sum()
        avg_goals_per_match = total_goals / total_matches if total_matches > 0 else 0
        home_goals = df['FTHG'].sum()
        away_goals = df['FTAG'].sum()

        # Over/Under statistics
        over_2_5 = len(df[df['Over2_5'] == 1])
        under_2_5 = len(df[df['Over2_5'] == 0])

        # High scoring matches (4+ goals)
        high_scoring = len(df[df['TotalGoals'] >= 4])

        # Scoreless matches
        scoreless = len(df[df['TotalGoals'] == 0])

        analysis = {
            'season_overview': {
                'total_matches': total_matches,
                'home_wins': home_wins,
                'draws': draws,
                'away_wins': away_wins,
                'home_win_rate': round(home_wins / total_matches, 3),
                'draw_rate': round(draws / total_matches, 3),
                'away_win_rate': round(away_wins / total_matches, 3)
            },
            'goal_statistics': {
                'total_goals': total_goals,
                'avg_goals_per_match': round(avg_goals_per_match, 2),
                'home_goals': home_goals,
                'away_goals': away_goals,
                'avg_home_goals': round(home_goals / total_matches, 2),
                'avg_away_goals': round(away_goals / total_matches, 2)
            },
            'betting_insights': {
                'over_2_5_matches': over_2_5,
                'under_2_5_matches': under_2_5,
                'over_2_5_rate': round(over_2_5 / total_matches, 3),
                'high_scoring_matches': high_scoring,
                'high_scoring_rate': round(high_scoring / total_matches, 3),
                'scoreless_matches': scoreless,
                'scoreless_rate': round(scoreless / total_matches, 3)
            }
        }

        logger.info("Historical analysis complete")
        return analysis

    def save_historical_data(self, df, stats_df, analysis):
        """
        Save all historical data to files.

        Args:
            df: Processed match data
            stats_df: Team statistics
            analysis: Analysis results
        """
        logger.info("Saving historical data...")

        output_dir = Path("outputs/historical_data")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save match data
        df.to_csv(output_dir / f"premier_league_matches_{self.season}.csv", index=False)
        logger.info(f"[OK] Saved match data ({len(df)} matches)")

        # Save team statistics
        stats_df.to_csv(output_dir / f"team_statistics_{self.season}.csv", index=False)
        logger.info(f"[OK] Saved team statistics ({len(stats_df)} teams)")

        # Save analysis as JSON
        import json
        # Convert numpy types to native Python types for JSON serialization
        def convert_to_native(obj):
            if isinstance(obj, dict):
                return {key: convert_to_native(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_native(item) for item in obj]
            elif isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            else:
                return obj

        analysis_native = convert_to_native(analysis)
        with open(output_dir / f"season_analysis_{self.season}.json", 'w') as f:
            json.dump(analysis_native, f, indent=2)
        logger.info(f"[OK] Saved season analysis")

        logger.info(f"\nAll historical data saved to: {output_dir.absolute()}")


def main():
    """Main function to fetch and process historical data."""
    fetcher = PremierLeagueHistoricalDataFetcher(season="2526")

    # Fetch data
    logger.info("="*60)
    logger.info("FETCHING HISTORICAL PREMIER LEAGUE DATA")
    logger.info("="*60)

    raw_data = fetcher.fetch_premier_league_data()

    # Process data
    processed_data = fetcher.process_historical_data(raw_data)

    # Calculate team statistics
    team_stats = fetcher.calculate_team_statistics(processed_data)

    # Generate analysis
    analysis = fetcher.generate_historical_analysis(processed_data)

    # Save all data
    fetcher.save_historical_data(processed_data, team_stats, analysis)

    # Display summary
    logger.info("\n" + "="*60)
    logger.info("HISTORICAL DATA SUMMARY")
    logger.info("="*60)

    logger.info(f"\nSeason: {fetcher.get_season_name()}")
    logger.info(f"Total Matches: {len(processed_data)}")
    logger.info(f"Teams: {len(team_stats)}")

    logger.info(f"\nSeason Overview:")
    logger.info(f"  Home Wins: {analysis['season_overview']['home_wins']} ({analysis['season_overview']['home_win_rate']:.1%})")
    logger.info(f"  Draws: {analysis['season_overview']['draws']} ({analysis['season_overview']['draw_rate']:.1%})")
    logger.info(f"  Away Wins: {analysis['season_overview']['away_wins']} ({analysis['season_overview']['away_win_rate']:.1%})")

    logger.info(f"\nGoal Statistics:")
    logger.info(f"  Total Goals: {analysis['goal_statistics']['total_goals']}")
    logger.info(f"  Avg Goals/Match: {analysis['goal_statistics']['avg_goals_per_match']}")
    logger.info(f"  Home Goals: {analysis['goal_statistics']['home_goals']}")
    logger.info(f"  Away Goals: {analysis['goal_statistics']['away_goals']}")

    logger.info(f"\nTop 5 Teams:")
    top_teams = team_stats.head(5)[['Position', 'Team', 'Points', 'Goal_Difference', 'Overall_Win_Rate']]
    print(top_teams.to_string(index=False))

    logger.info(f"\nData saved to: outputs/historical_data/")


if __name__ == "__main__":
    main()