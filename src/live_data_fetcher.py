"""
Live Data Fetcher Module

This module provides functionality to fetch live football data
from API-Football for real-time updates.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LiveFootballData:
    """
    Fetch live football data from API-Football.

    Free tier: 100 requests/day
    Paid tiers: More frequent updates available
    """

    def __init__(self, api_key: str):
        """
        Initialize the live data fetcher.

        Args:
            api_key: API-Football API key from RapidAPI
        """
        self.api_key = api_key
        self.base_url = "https://api-football-v1.p.rapidapi.com/v3"
        self.headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }

    def get_live_matches(self, league_id: int = 39) -> List[Dict]:
        """
        Get currently live matches.

        Args:
            league_id: League ID (39 = Premier League)

        Returns:
            List of live match data
        """
        try:
            url = f"{self.base_url}/fixtures?live=league-{league_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if data.get("response"):
                logger.info(f"Found {len(data['response'])} live matches")
                return data["response"]
            return []

        except Exception as e:
            logger.error(f"Error fetching live matches: {e}")
            return []

    def get_upcoming_matches(self, league_id: int = 39, days: int = 7) -> List[Dict]:
        """
        Get upcoming matches.

        Args:
            league_id: League ID (39 = Premier League)
            days: Number of days ahead to look

        Returns:
            List of upcoming match data
        """
        try:
            from_date = datetime.now().strftime("%Y-%m-%d")
            to_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

            url = f"{self.base_url}/fixtures?league={league_id}&from={from_date}&to={to_date}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if data.get("response"):
                logger.info(f"Found {len(data['response'])} upcoming matches")
                return data["response"]
            return []

        except Exception as e:
            logger.error(f"Error fetching upcoming matches: {e}")
            return []

    def get_match_events(self, match_id: int) -> List[Dict]:
        """
        Get live events for a match (goals, cards, substitutions).

        Args:
            match_id: Fixture ID

        Returns:
            List of match events
        """
        try:
            url = f"{self.base_url}/fixtures/events?fixture={match_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if data.get("response"):
                return data["response"]
            return []

        except Exception as e:
            logger.error(f"Error fetching match events: {e}")
            return []

    def get_match_odds(self, match_id: int) -> Optional[Dict]:
        """
        Get current odds for a match.

        Args:
            match_id: Fixture ID

        Returns:
            Dictionary with odds data
        """
        try:
            url = f"{self.base_url}/odds?fixture={match_id}&bookmaker=8"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if data.get("response"):
                return data["response"][0]
            return None

        except Exception as e:
            logger.error(f"Error fetching match odds: {e}")
            return None

    def get_league_standings(self, league_id: int = 39, season: int = 2024) -> List[Dict]:
        """
        Get current league standings.

        Args:
            league_id: League ID (39 = Premier League)
            season: Season year

        Returns:
            List of team standings
        """
        try:
            url = f"{self.base_url}/standings?league={league_id}&season={season}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if data.get("response"):
                return data["response"][0]["league"]["standings"][0]
            return []

        except Exception as e:
            logger.error(f"Error fetching league standings: {e}")
            return []

    def format_live_match(self, match_data: Dict) -> Dict:
        """
        Format live match data for web display.

        Args:
            match_data: Raw match data from API

        Returns:
            Formatted match data
        """
        return {
            "match_id": match_data.get("fixture", {}).get("id"),
            "home_team": match_data.get("teams", {}).get("home", {}).get("name"),
            "away_team": match_data.get("teams", {}).get("away", {}).get("name"),
            "home_score": match_data.get("goals", {}).get("home"),
            "away_score": match_data.get("goals", {}).get("away"),
            "status": match_data.get("fixture", {}).get("status", {}).get("long"),
            "minute": match_data.get("fixture", {}).get("status", {}).get("elapsed"),
            "league": match_data.get("league", {}).get("name"),
            "date": match_data.get("fixture", {}).get("date"),
            "time": match_data.get("fixture", {}).get("timestamp"),
        }


def get_api_football_key() -> Optional[str]:
    """
    Get API-Football key from environment.

    Returns:
        API key if found, None otherwise
    """
    import os
    return os.getenv("API_FOOTBALL_KEY")


# Example usage
if __name__ == "__main__":
    # Get API key from environment
    api_key = get_api_football_key()

    if not api_key:
        print("Error: API_FOOTBALL_KEY environment variable not set")
        print("Get your free API key from: https://rapidapi.com/api-sports/api/api-football")
        exit(1)

    # Initialize live data fetcher
    live_data = LiveFootballData(api_key)

    # Get live matches
    print("\n=== Live Matches ===")
    live_matches = live_data.get_live_matches()
    for match in live_matches:
        formatted = live_data.format_live_match(match)
        print(f"{formatted['home_team']} {formatted['home_score']} - "
              f"{formatted['away_score']} {formatted['away_team']} "
              f"({formatted['status']} - {formatted['minute']}')")

    # Get upcoming matches
    print("\n=== Upcoming Matches ===")
    upcoming_matches = live_data.get_upcoming_matches(days=3)
    for match in upcoming_matches[:5]:  # Show first 5
        formatted = live_data.format_live_match(match)
        print(f"{formatted['home_team']} vs {formatted['away_team']} "
              f"on {formatted['date']}")

    # Get league standings
    print("\n=== League Standings (Top 5) ===")
    standings = live_data.get_league_standings()
    for team in standings[:5]:
        print(f"{team['rank']}. {team['team']['name']} - "
              f"{team['points']} pts ({team['all']['win']}-{team['all']['draw']}-{team['all']['lose']})")
