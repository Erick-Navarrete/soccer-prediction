"""
Free Live Football Data API Integration

This module provides functionality to fetch live football data
from the Free API Live Football Data service on RapidAPI.

API: https://rapidapi.com/Creativesdev/api/free-api-live-football-data
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FreeLiveFootballData:
    """
    Fetch live football data from Free API Live Football Data.

    This is a free API that provides live match data, fixtures,
    and results for major football leagues.
    """

    def __init__(self, api_key: str):
        """
        Initialize the live data fetcher.

        Args:
            api_key: RapidAPI key for Free API Live Football Data
        """
        self.api_key = api_key
        self.base_url = "https://free-api-live-football-data.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "free-api-live-football-data.p.rapidapi.com"
        }

    def get_live_matches(self) -> List[Dict]:
        """
        Get currently live matches.

        Returns:
            List of live match data
        """
        try:
            url = f"{self.base_url}/football-live"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if data and isinstance(data, list):
                logger.info(f"Found {len(data)} live matches")
                return data
            elif data and isinstance(data, dict) and 'response' in data:
                logger.info(f"Found {len(data['response'])} live matches")
                return data['response']
            return []

        except Exception as e:
            logger.error(f"Error fetching live matches: {e}")
            return []

    def get_fixtures(self, league_id: Optional[int] = None, season: Optional[int] = None,
                    from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        """
        Get upcoming fixtures.

        Args:
            league_id: League ID (optional)
            season: Season year (optional)
            from_date: Start date in YYYY-MM-DD format (optional)
            to_date: End date in YYYY-MM-DD format (optional)

        Returns:
            List of fixture data
        """
        try:
            url = f"{self.base_url}/football-fixtures"

            params = {}
            if league_id:
                params['league'] = league_id
            if season:
                params['season'] = season
            if from_date:
                params['from'] = from_date
            if to_date:
                params['to'] = to_date

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            if data and isinstance(data, list):
                logger.info(f"Found {len(data)} fixtures")
                return data
            elif data and isinstance(data, dict) and 'response' in data:
                logger.info(f"Found {len(data['response'])} fixtures")
                return data['response']
            return []

        except Exception as e:
            logger.error(f"Error fetching fixtures: {e}")
            return []

    def get_match_results(self, league_id: Optional[int] = None, season: Optional[int] = None,
                         from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        """
        Get match results.

        Args:
            league_id: League ID (optional)
            season: Season year (optional)
            from_date: Start date in YYYY-MM-DD format (optional)
            to_date: End date in YYYY-MM-DD format (optional)

        Returns:
            List of match results
        """
        try:
            url = f"{self.base_url}/football-results"

            params = {}
            if league_id:
                params['league'] = league_id
            if season:
                params['season'] = season
            if from_date:
                params['from'] = from_date
            if to_date:
                params['to'] = to_date

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            if data and isinstance(data, list):
                logger.info(f"Found {len(data)} results")
                return data
            elif data and isinstance(data, dict) and 'response' in data:
                logger.info(f"Found {len(data['response'])} results")
                return data['response']
            return []

        except Exception as e:
            logger.error(f"Error fetching results: {e}")
            return []

    def get_league_standings(self, league_id: int, season: int) -> List[Dict]:
        """
        Get league standings.

        Args:
            league_id: League ID
            season: Season year

        Returns:
            List of team standings
        """
        try:
            url = f"{self.base_url}/football-standings"

            params = {
                'league': league_id,
                'season': season
            }

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            if data and isinstance(data, list):
                logger.info(f"Found standings for {len(data)} teams")
                return data
            elif data and isinstance(data, dict) and 'response' in data:
                logger.info(f"Found standings for {len(data['response'])} teams")
                return data['response']
            return []

        except Exception as e:
            logger.error(f"Error fetching standings: {e}")
            return []

    def get_head_to_head(self, team1_id: int, team2_id: int) -> List[Dict]:
        """
        Get head-to-head record between two teams.

        Args:
            team1_id: First team ID
            team2_id: Second team ID

        Returns:
            List of H2H matches
        """
        try:
            url = f"{self.base_url}/football-h2h"

            params = {
                'h2h': f"{team1_id}-{team2_id}"
            }

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            if data and isinstance(data, list):
                return data
            elif data and isinstance(data, dict) and 'response' in data:
                return data['response']
            return []

        except Exception as e:
            logger.error(f"Error fetching H2H: {e}")
            return []

    def format_live_match(self, match_data: Dict) -> Dict:
        """
        Format live match data for web display.

        Args:
            match_data: Raw match data from API

        Returns:
            Formatted match data
        """
        # Handle different API response formats
        teams = match_data.get('teams', match_data.get('Teams', {}))
        goals = match_data.get('goals', match_data.get('Goals', {}))
        fixture = match_data.get('fixture', match_data.get('Fixture', {}))
        league = match_data.get('league', match_data.get('League', {}))

        # Extract team names
        if isinstance(teams, dict):
            home_team = teams.get('home', teams.get('Home', {})).get('name', 'Unknown')
            away_team = teams.get('away', teams.get('Away', {})).get('name', 'Unknown')
        else:
            home_team = match_data.get('home', {}).get('name', 'Unknown')
            away_team = match_data.get('away', {}).get('name', 'Unknown')

        # Extract scores
        if isinstance(goals, dict):
            home_score = goals.get('home', goals.get('Home', 0))
            away_score = goals.get('away', goals.get('Away', 0))
        else:
            home_score = match_data.get('goals', {}).get('home', 0)
            away_score = match_data.get('goals', {}).get('away', 0)

        # Extract status
        if isinstance(fixture, dict):
            status = fixture.get('status', {}).get('long', fixture.get('status', {}).get('short', 'Unknown'))
            minute = fixture.get('status', {}).get('elapsed', 0)
        else:
            status = match_data.get('status', {}).get('long', 'Unknown')
            minute = match_data.get('status', {}).get('elapsed', 0)

        # Extract league
        if isinstance(league, dict):
            league_name = league.get('name', 'Unknown')
        else:
            league_name = match_data.get('league', {}).get('name', 'Unknown')

        return {
            "match_id": match_data.get('fixture', {}).get('id', match_data.get('id')),
            "home_team": home_team,
            "away_team": away_team,
            "home_score": home_score,
            "away_score": away_score,
            "status": status,
            "minute": minute,
            "league": league_name,
            "date": match_data.get('fixture', {}).get('date', match_data.get('date')),
            "time": match_data.get('fixture', {}).get('timestamp', match_data.get('timestamp')),
        }

    def format_fixture(self, fixture_data: Dict) -> Dict:
        """
        Format fixture data for web display.

        Args:
            fixture_data: Raw fixture data from API

        Returns:
            Formatted fixture data
        """
        teams = fixture_data.get('teams', fixture_data.get('Teams', {}))
        league = fixture_data.get('league', fixture_data.get('League', {}))

        if isinstance(teams, dict):
            home_team = teams.get('home', teams.get('Home', {})).get('name', 'Unknown')
            away_team = teams.get('away', teams.get('Away', {})).get('name', 'Unknown')
        else:
            home_team = fixture_data.get('home', {}).get('name', 'Unknown')
            away_team = fixture_data.get('away', {}).get('name', 'Unknown')

        if isinstance(league, dict):
            league_name = league.get('name', 'Unknown')
        else:
            league_name = fixture_data.get('league', {}).get('name', 'Unknown')

        return {
            "match_id": fixture_data.get('fixture', {}).get('id', fixture_data.get('id')),
            "home_team": home_team,
            "away_team": away_team,
            "league": league_name,
            "date": fixture_data.get('fixture', {}).get('date', fixture_data.get('date')),
            "time": fixture_data.get('fixture', {}).get('timestamp', fixture_data.get('timestamp')),
        }


def get_free_api_key() -> Optional[str]:
    """
    Get Free API Live Football Data key from environment.

    Returns:
        API key if found, None otherwise
    """
    import os
    return os.getenv("FREE_FOOTBALL_API_KEY")


# Example usage
if __name__ == "__main__":
    # Get API key from environment
    api_key = get_free_api_key()

    if not api_key:
        print("Error: FREE_FOOTBALL_API_KEY environment variable not set")
        print("Get your free API key from: https://rapidapi.com/Creativesdev/api/free-api-live-football-data")
        exit(1)

    # Initialize live data fetcher
    live_data = FreeLiveFootballData(api_key)

    # Get live matches
    print("\n=== Live Matches ===")
    live_matches = live_data.get_live_matches()
    for match in live_matches[:5]:  # Show first 5
        formatted = live_data.format_live_match(match)
        print(f"{formatted['home_team']} {formatted['home_score']} - "
              f"{formatted['away_score']} {formatted['away_team']} "
              f"({formatted['status']} - {formatted['minute']}')")

    # Get upcoming fixtures
    print("\n=== Upcoming Fixtures ===")
    from_date = datetime.now().strftime("%Y-%m-%d")
    to_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    fixtures = live_data.get_fixtures(from_date=from_date, to_date=to_date)
    for fixture in fixtures[:5]:  # Show first 5
        formatted = live_data.format_fixture(fixture)
        print(f"{formatted['home_team']} vs {formatted['away_team']} "
              f"on {formatted['date']}")

    # Get recent results
    print("\n=== Recent Results ===")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    results = live_data.get_match_results(from_date=week_ago)
    for result in results[:5]:  # Show first 5
        formatted = live_data.format_live_match(result)
        print(f"{formatted['home_team']} {formatted['home_score']} - "
              f"{formatted['away_score']} {formatted['away_team']} "
              f"on {formatted['date']}")
