"""
Data Loading and Cleaning Module

This module provides classes for loading football match data from football-data.co.uk
and cleaning/standardizing the data for analysis.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional


class FootballDataLoader:
    """
    Historical football match data loader.
    Source: football-data.co.uk

    Supports multiple European leagues and seasons with comprehensive
    match statistics including goals, shots, corners, fouls, cards, and bookmaker odds.
    """

    BASE_URL = "https://www.football-data.co.uk/mmz4281"

    LEAGUES = {
        "E0": "Premier League",
        "SP1": "La Liga",
        "D1": "Bundesliga",
        "I1": "Serie A",
        "F1": "Ligue 1",
    }

    COLUMNS_TO_KEEP = [
        "Date", "HomeTeam", "AwayTeam",
        "FTHG", "FTAG", "FTR",       # Final score and result
        "HTHG", "HTAG", "HTR",       # Half-time score
        "HS", "AS",                   # Shots
        "HST", "AST",                 # Shots on target
        "HF", "AF",                   # Fouls
        "HC", "AC",                   # Corners
        "HY", "AY",                   # Yellow cards
        "HR", "AR",                   # Red cards
        "B365H", "B365D", "B365A",   # Bet365 odds
    ]

    def __init__(self, seasons: list[str], leagues: Optional[list[str]] = None):
        """
        Initialize the data loader.

        Args:
            seasons: List of seasons in format ["2425", "2324", "2223"]
            leagues: List of league codes (default: all available leagues)
        """
        self.seasons = seasons
        self.leagues = leagues or list(self.LEAGUES.keys())

    def load_season(self, league: str, season: str) -> pd.DataFrame:
        """
        Load data for a single season and league.

        Args:
            league: League code (e.g., "E0" for Premier League)
            season: Season code (e.g., "2425" for 2024-25)

        Returns:
            DataFrame with match data for the specified season/league
        """
        url = f"{self.BASE_URL}/{season}/{league}.csv"
        try:
            df = pd.read_csv(url, encoding="utf-8", on_bad_lines="skip")
            available_cols = [c for c in self.COLUMNS_TO_KEEP if c in df.columns]
            df = df[available_cols].dropna(subset=["HomeTeam", "AwayTeam", "FTR"])
            df["League"] = self.LEAGUES.get(league, league)
            df["Season"] = season
            return df
        except Exception as e:
            print(f"Error loading {league}/{season}: {e}")
            return pd.DataFrame()

    def load_all(self) -> pd.DataFrame:
        """
        Load all data for specified leagues and seasons.

        Returns:
            Combined DataFrame with all matches
        """
        frames = []
        for league in self.leagues:
            for season in self.seasons:
                df = self.load_season(league, season)
                if not df.empty:
                    frames.append(df)
                    print(f"  OK {self.LEAGUES.get(league)}, season {season}: "
                          f"{len(df)} matches")
        result = pd.concat(frames, ignore_index=True)
        print(f"\nTotal loaded: {len(result)} matches")
        return result


class DataCleaner:
    """Data cleaning and standardization utilities."""

    @staticmethod
    def clean(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize the match data.

        Args:
            df: Raw match data DataFrame

        Returns:
            Cleaned DataFrame with standardized formats
        """
        df = df.copy()

        # Standardize date format
        df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["Date"])
        df = df.sort_values("Date").reset_index(drop=True)

        # Numeric columns
        numeric_cols = [
            "FTHG", "FTAG", "HTHG", "HTAG",
            "HS", "AS", "HST", "AST",
            "HF", "AF", "HC", "AC",
            "HY", "AY", "HR", "AR",
            "B365H", "B365D", "B365A",
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Encoding result: H=2, D=1, A=0
        result_map = {"H": 2, "D": 1, "A": 0}
        df["Result"] = df["FTR"].map(result_map)
        df = df.dropna(subset=["Result"])
        df["Result"] = df["Result"].astype(int)

        return df


# Example usage
if __name__ == "__main__":
    loader = FootballDataLoader(
        seasons=["2425", "2324", "2223", "2122", "2021"],
        leagues=["E0", "SP1", "D1"]  # EPL, La Liga, Bundesliga
    )
    raw_data = loader.load_all()

    cleaner = DataCleaner()
    clean_data = cleaner.clean(raw_data)

    print(f"After cleaning: {len(clean_data)} matches")
    print(f"Result distribution:\n{clean_data['FTR'].value_counts()}")
