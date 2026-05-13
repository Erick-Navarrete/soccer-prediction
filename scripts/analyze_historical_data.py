import pandas as pd
import numpy as np
import json
from datetime import datetime
from collections import defaultdict

def analyze_historical_data():
    """Analyze the historical Premier League data and generate insights."""
    try:
        # Load the historical data
        df = pd.read_csv('D:/Project_App/soccer-prediction/outputs/historical_data/premier_league_matches_2526_improved.csv')

        # Filter for completed matches
        completed_matches = df[df['FullTimeResult'].notna()].copy()

        insights = {
            "overview": {},
            "team_performance": {},
            "match_statistics": {},
            "betting_insights": {},
            "season_progress": {},
            "key_findings": []
        }

        # Overview statistics
        total_matches = len(completed_matches)
        total_goals = completed_matches['FullTimeHomeGoals'].sum() + completed_matches['FullTimeAwayGoals'].sum()
        avg_goals_per_match = total_goals / total_matches if total_matches > 0 else 0

        home_wins = len(completed_matches[completed_matches['FullTimeResult'] == 'H'])
        away_wins = len(completed_matches[completed_matches['FullTimeResult'] == 'A'])
        draws = len(completed_matches[completed_matches['FullTimeResult'] == 'D'])

        insights["overview"] = {
            "total_matches": total_matches,
            "total_goals": int(total_goals),
            "avg_goals_per_match": round(avg_goals_per_match, 2),
            "home_wins": home_wins,
            "away_wins": away_wins,
            "draws": draws,
            "home_win_rate": round((home_wins / total_matches) * 100, 2) if total_matches > 0 else 0,
            "away_win_rate": round((away_wins / total_matches) * 100, 2) if total_matches > 0 else 0,
            "draw_rate": round((draws / total_matches) * 100, 2) if total_matches > 0 else 0
        }

        # Team performance analysis
        team_stats = defaultdict(lambda: {
            'matches': 0,
            'wins': 0,
            'draws': 0,
            'losses': 0,
            'goals_for': 0,
            'goals_against': 0,
            'points': 0
        })

        for _, match in completed_matches.iterrows():
            home_team = match['HomeTeam']
            away_team = match['AwayTeam']
            home_goals = match['FullTimeHomeGoals']
            away_goals = match['FullTimeAwayGoals']
            result = match['FullTimeResult']

            # Home team stats
            team_stats[home_team]['matches'] += 1
            team_stats[home_team]['goals_for'] += home_goals
            team_stats[home_team]['goals_against'] += away_goals

            if result == 'H':
                team_stats[home_team]['wins'] += 1
                team_stats[home_team]['points'] += 3
            elif result == 'D':
                team_stats[home_team]['draws'] += 1
                team_stats[home_team]['points'] += 1
            else:
                team_stats[home_team]['losses'] += 1

            # Away team stats
            team_stats[away_team]['matches'] += 1
            team_stats[away_team]['goals_for'] += away_goals
            team_stats[away_team]['goals_against'] += home_goals

            if result == 'A':
                team_stats[away_team]['wins'] += 1
                team_stats[away_team]['points'] += 3
            elif result == 'D':
                team_stats[away_team]['draws'] += 1
                team_stats[away_team]['points'] += 1
            else:
                team_stats[away_team]['losses'] += 1

        # Convert to list and sort by points
        team_performance = []
        for team, stats in team_stats.items():
            stats['goal_difference'] = stats['goals_for'] - stats['goals_against']
            stats['win_rate'] = round((stats['wins'] / stats['matches']) * 100, 2) if stats['matches'] > 0 else 0
            team_performance.append({
                'team': team,
                **stats
            })

        team_performance.sort(key=lambda x: x['points'], reverse=True)

        insights["team_performance"] = {
            "top_teams": team_performance[:5],
            "bottom_teams": team_performance[-5:],
            "highest_scoring": sorted(team_performance, key=lambda x: x['goals_for'], reverse=True)[:5],
            "best_defense": sorted(team_performance, key=lambda x: x['goals_against'])[:5]
        }

        # Match statistics
        insights["match_statistics"] = {
            "avg_home_goals": round(completed_matches['FullTimeHomeGoals'].mean(), 2),
            "avg_away_goals": round(completed_matches['FullTimeAwayGoals'].mean(), 2),
            "high_scoring_matches": len(completed_matches[completed_matches['TotalGoals'] >= 4]),
            "low_scoring_matches": len(completed_matches[completed_matches['TotalGoals'] <= 1]),
            "over_2_5_percentage": round((len(completed_matches[completed_matches['Over25Goals'] == 1]) / total_matches) * 100, 2) if total_matches > 0 else 0
        }

        # Betting insights
        if 'AverageHomeOdds' in completed_matches.columns:
            insights["betting_insights"] = {
                "avg_home_odds": round(completed_matches['AverageHomeOdds'].mean(), 2),
                "avg_draw_odds": round(completed_matches['AverageDrawOdds'].mean(), 2),
                "avg_away_odds": round(completed_matches['AverageAwayOdds'].mean(), 2),
                "favorite_win_rate": calculate_favorite_win_rate(completed_matches)
            }

        # Season progress
        if 'SeasonProgress' in completed_matches.columns:
            progress_str = completed_matches['SeasonProgress'].iloc[0] if len(completed_matches) > 0 else "0/0"
            insights["season_progress"] = {
                "progress": progress_str,
                "completion_percentage": extract_completion_percentage(progress_str)
            }

        # Key findings
        insights["key_findings"] = generate_key_findings(insights)

        return insights

    except Exception as e:
        print(f"Error analyzing historical data: {e}")
        return {}

def calculate_favorite_win_rate(matches):
    """Calculate win rate for favorites (lowest odds)."""
    try:
        favorites_won = 0
        total_with_odds = 0

        for _, match in matches.iterrows():
            if pd.notna(match['AverageHomeOdds']) and pd.notna(match['AverageDrawOdds']) and pd.notna(match['AverageAwayOdds']):
                odds = {
                    'H': match['AverageHomeOdds'],
                    'D': match['AverageDrawOdds'],
                    'A': match['AverageAwayOdds']
                }
                favorite = min(odds, key=odds.get)
                if favorite == match['FullTimeResult']:
                    favorites_won += 1
                total_with_odds += 1

        return round((favorites_won / total_with_odds) * 100, 2) if total_with_odds > 0 else 0
    except:
        return 0

def extract_completion_percentage(progress_str):
    """Extract completion percentage from progress string."""
    try:
        if '(' in progress_str and '%' in progress_str:
            start = progress_str.index('(') + 1
            end = progress_str.index('%')
            return float(progress_str[start:end])
        return 0
    except:
        return 0

def generate_key_findings(insights):
    """Generate key findings from the insights."""
    findings = []

    overview = insights.get('overview', {})
    team_perf = insights.get('team_performance', {})
    match_stats = insights.get('match_statistics', {})

    # Home advantage
    if overview.get('home_win_rate', 0) > 45:
        findings.append(f"Strong home advantage: {overview['home_win_rate']}% of matches won by home teams")

    # Scoring trends
    if match_stats.get('avg_goals_per_match', 0) > 2.5:
        findings.append(f"High-scoring season: Average of {match_stats['avg_goals_per_match']} goals per match")

    # Top team dominance
    if team_perf.get('top_teams'):
        top_team = team_perf['top_teams'][0]
        findings.append(f"{top_team['team']} leading with {top_team['points']} points ({top_team['win_rate']}% win rate)")

    # Over/under trends
    if match_stats.get('over_2_5_percentage', 0) > 50:
        findings.append(f"Betting trend: {match_stats['over_2_5_percentage']}% of matches go over 2.5 goals")

    # Defensive strength
    if team_perf.get('best_defense'):
        best_defense = team_perf['best_defense'][0]
        findings.append(f"Best defense: {best_defense['team']} with only {best_defense['goals_against']} goals conceded")

    return findings

def main():
    """Main function to analyze and save insights."""
    print("Analyzing historical Premier League data...")

    insights = analyze_historical_data()

    if insights:
        # Save insights to JSON
        output_path = 'data/historical_insights.json'
        with open(output_path, 'w') as f:
            json.dump(insights, f, indent=2)

        print(f"Saved insights to {output_path}")
        print(f"\nKey Findings:")
        for finding in insights.get('key_findings', []):
            print(f"  • {finding}")

        print(f"\nOverview:")
        print(f"  • Total matches: {insights['overview']['total_matches']}")
        print(f"  • Total goals: {insights['overview']['total_goals']}")
        print(f"  • Average goals per match: {insights['overview']['avg_goals_per_match']}")
        print(f"  • Home win rate: {insights['overview']['home_win_rate']}%")
        print(f"  • Away win rate: {insights['overview']['away_win_rate']}%")
        print(f"  • Draw rate: {insights['overview']['draw_rate']}%")

        print(f"\nTop 5 Teams:")
        for i, team in enumerate(insights['team_performance']['top_teams'], 1):
            print(f"  {i}. {team['team']}: {team['points']} pts ({team['wins']}W-{team['draws']}D-{team['losses']}L)")

    else:
        print("Failed to generate insights")

if __name__ == "__main__":
    main()
