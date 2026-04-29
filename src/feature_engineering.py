"""
Feature Engineering Module

This module provides comprehensive feature engineering for football match prediction,
including rolling statistics, ELO ratings, xG proxy, fatigue factors, and head-to-head history.
"""

import pandas as pd
import numpy as np
from typing import Optional


class FeatureEngineer:
    """
    Feature generation based on historical team statistics.

    Key principle: For each match we use ONLY data available BEFORE the match starts
    to prevent data leakage.
    """

    def __init__(self, window: int = 5):
        """
        Initialize the feature engineer.

        Args:
            window: Number of matches to use for rolling averages (default: 5)
        """
        self.window = window

    def compute_team_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute rolling averages for each team over the last N matches.

        Args:
            df: Match data DataFrame

        Returns:
            DataFrame with team-level rolling statistics
        """
        df = df.sort_values("Date").copy()

        # Create separate records for home and away teams
        home_records = df[["Date", "HomeTeam", "FTHG", "FTAG",
                           "HS", "AS", "HST", "AST",
                           "HC", "AC", "HF", "AF"]].copy()
        home_records.columns = ["Date", "Team", "GF", "GA",
                                "Shots", "ShotsAgainst",
                                "SoT", "SoTAgainst",
                                "Corners", "CornersAgainst",
                                "Fouls", "FoulsAgainst"]
        home_records["IsHome"] = 1

        away_records = df[["Date", "AwayTeam", "FTAG", "FTHG",
                           "AS", "HS", "AST", "HST",
                           "AC", "HC", "AF", "HF"]].copy()
        away_records.columns = ["Date", "Team", "GF", "GA",
                                "Shots", "ShotsAgainst",
                                "SoT", "SoTAgainst",
                                "Corners", "CornersAgainst",
                                "Fouls", "FoulsAgainst"]
        away_records["IsHome"] = 0

        all_records = pd.concat([home_records, away_records])
        all_records = all_records.sort_values("Date")

        # Calculate rolling averages per team
        stats_cols = ["GF", "GA", "Shots", "ShotsAgainst",
                      "SoT", "SoTAgainst", "Corners",
                      "CornersAgainst", "Fouls", "FoulsAgainst"]

        rolling_stats = {}
        for team in all_records["Team"].unique():
            team_data = all_records[all_records["Team"] == team].copy()
            for col in stats_cols:
                # shift(1) — to exclude the current match
                team_data[f"avg_{col}"] = (
                    team_data[col]
                    .shift(1)
                    .rolling(window=self.window, min_periods=3)
                    .mean()
                )
            # Form: average points over last N matches
            team_data["Points"] = team_data.apply(
                lambda r: 3 if r["GF"] > r["GA"]
                         else (1 if r["GF"] == r["GA"] else 0),
                axis=1,
            )
            team_data["Form"] = (
                team_data["Points"]
                .shift(1)
                .rolling(window=self.window, min_periods=3)
                .mean()
            )
            rolling_stats[team] = team_data

        return pd.concat(rolling_stats.values())

    def build_match_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Join home and away team statistics for each match.

        Args:
            df: Match data DataFrame

        Returns:
            DataFrame with match-level features
        """
        team_stats = self.compute_team_stats(df)

        stat_features = [c for c in team_stats.columns if c.startswith("avg_")]
        stat_features.append("Form")

        features_list = []

        for idx, match in df.iterrows():
            home = match["HomeTeam"]
            away = match["AwayTeam"]
            date = match["Date"]

            home_stats = team_stats[
                (team_stats["Team"] == home) &
                (team_stats["Date"] == date) &
                (team_stats["IsHome"] == 1)
            ]
            away_stats = team_stats[
                (team_stats["Team"] == away) &
                (team_stats["Date"] == date) &
                (team_stats["IsHome"] == 0)
            ]

            if home_stats.empty or away_stats.empty:
                continue

            row = {"match_idx": idx}
            for feat in stat_features:
                h_val = home_stats[feat].values[0]
                a_val = away_stats[feat].values[0]
                row[f"home_{feat}"] = h_val
                row[f"away_{feat}"] = a_val
                # Difference — one of the strongest features
                row[f"diff_{feat}"] = h_val - a_val

            features_list.append(row)

        features_df = pd.DataFrame(features_list).set_index("match_idx")
        result = df.join(features_df, how="inner")
        return result.dropna(subset=[c for c in features_df.columns])


class FootballELO:
    """
    ELO ratings for football teams.

    FIFA formula: R_new = R_old + K * M * (S - E)
    where:
      K — match significance coefficient
      M — goal difference multiplier
      S — actual result (1 / 0.5 / 0)
      E — expected result by ELO
    """

    def __init__(self, k: int = 32, home_advantage: int = 65):
        """
        Initialize the ELO system.

        Args:
            k: K-factor for rating updates (default: 32)
            home_advantage: ELO points added to home team (default: 65)
        """
        self.k = k
        self.home_advantage = home_advantage
        self.ratings: dict[str, float] = {}

    def get_rating(self, team: str) -> float:
        """Get the current ELO rating for a team."""
        return self.ratings.setdefault(team, 1500.0)

    def expected_score(self, rating_a: float, rating_b: float) -> float:
        """
        Calculate the expected score using the ELO formula.

        Args:
            rating_a: Rating of team A
            rating_b: Rating of team B

        Returns:
            Expected probability of A beating B
        """
        return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))

    def margin_multiplier(self, goal_diff: int) -> float:
        """
        Calculate the goal difference multiplier.

        A 5-0 win should have more impact than 1-0.

        Args:
            goal_diff: Goal difference in the match

        Returns:
            Multiplier based on goal difference
        """
        return np.log(abs(goal_diff) + 1) * (2.2 / 2.2)

    def update(self, home: str, away: str,
               home_goals: int, away_goals: int) -> tuple[float, float]:
        """
        Update ratings after a match.

        Args:
            home: Home team name
            away: Away team name
            home_goals: Goals scored by home team
            away_goals: Goals scored by away team

        Returns:
            Tuple of (new_home_elo, new_away_elo)
        """
        r_home = self.get_rating(home) + self.home_advantage
        r_away = self.get_rating(away)

        e_home = self.expected_score(r_home, r_away)
        e_away = 1.0 - e_home

        # Actual result
        if home_goals > away_goals:
            s_home, s_away = 1.0, 0.0
        elif home_goals < away_goals:
            s_home, s_away = 0.0, 1.0
        else:
            s_home, s_away = 0.5, 0.5

        # Goal difference multiplier
        m = self.margin_multiplier(home_goals - away_goals)

        # Update (without home_advantage in stored rating)
        self.ratings[home] += self.k * m * (s_home - e_home)
        self.ratings[away] += self.k * m * (s_away - e_away)

        return self.ratings[home], self.ratings[away]

    def compute_elo_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute ELO features for all matches.

        Iterates through all matches chronologically, updating ELO after each.
        For each match we save ratings BEFORE it starts (to prevent leakage).

        Args:
            df: Match data DataFrame

        Returns:
            DataFrame with ELO features added
        """
        df = df.sort_values("Date").copy()
        elo_features = []

        for _, row in df.iterrows():
            home = row["HomeTeam"]
            away = row["AwayTeam"]

            r_home = self.get_rating(home)
            r_away = self.get_rating(away)

            e_home = self.expected_score(
                r_home + self.home_advantage, r_away
            )

            elo_features.append({
                "elo_home": r_home,
                "elo_away": r_away,
                "elo_diff": r_home - r_away,
                "elo_expected_home": e_home,
                "elo_expected_away": 1 - e_home,
            })

            # Update AFTER saving pre-match ratings
            if pd.notna(row.get("FTHG")) and pd.notna(row.get("FTAG")):
                self.update(home, away,
                            int(row["FTHG"]), int(row["FTAG"]))

        return pd.concat(
            [df.reset_index(drop=True),
             pd.DataFrame(elo_features)],
            axis=1,
        )


def compute_xg_proxy(df: pd.DataFrame) -> pd.DataFrame:
    """
    xG proxy: expected goals approximation from basic statistics.

    Formula: xG ≈ SoT * conversion_rate + (Shots - SoT) * low_conversion
    where conversion_rate ~ 0.30 for shots on target,
          low_conversion ~ 0.03 for shots off target.

    This is a rough approximation, but it captures key information:
    attacking play quality.

    Args:
        df: Match data DataFrame

    Returns:
        DataFrame with xG proxy features added
    """
    df = df.copy()

    SOT_CONVERSION = 0.30   # ~30% shots on target = goal (EPL average)
    SHOT_CONVERSION = 0.03  # ~3% shots off target = goal

    if "HST" in df.columns and "HS" in df.columns:
        df["home_xG_proxy"] = (
            df["HST"] * SOT_CONVERSION
            + (df["HS"] - df["HST"]).clip(lower=0) * SHOT_CONVERSION
        )
        df["away_xG_proxy"] = (
            df["AST"] * SOT_CONVERSION
            + (df["AS"] - df["AST"]).clip(lower=0) * SHOT_CONVERSION
        )

        # xG overperformance: actual goals minus expected
        # Positive value = team scores more than it "should"
        # Usually regresses to mean → correction signal
        df["home_xG_overperf"] = df["FTHG"] - df["home_xG_proxy"]
        df["away_xG_overperf"] = df["FTAG"] - df["away_xG_proxy"]

    return df


def compute_fatigue_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fatigue features: rest days between matches.

    Less than 3 rest days → significant performance decline.
    Midweek matches (Tue/Wed) after weekends → fatigue.

    Args:
        df: Match data DataFrame

    Returns:
        DataFrame with fatigue features added
    """
    df = df.sort_values("Date").copy()

    rest_days_home = []
    rest_days_away = []
    last_match: dict[str, pd.Timestamp] = {}

    for _, row in df.iterrows():
        home = row["HomeTeam"]
        away = row["AwayTeam"]
        date = row["Date"]

        # Rest days for home team
        if home in last_match:
            delta = (date - last_match[home]).days
            rest_days_home.append(min(delta, 30))  # cap at 30
        else:
            rest_days_home.append(14)  # first match → default

        # Rest days for away team
        if away in last_match:
            delta = (date - last_match[away]).days
            rest_days_away.append(min(delta, 30))
        else:
            rest_days_away.append(14)

        last_match[home] = date
        last_match[away] = date

    df["home_rest_days"] = rest_days_home
    df["away_rest_days"] = rest_days_away
    df["rest_advantage"] = df["home_rest_days"] - df["away_rest_days"]

    # Binary flags
    df["home_fatigued"] = (df["home_rest_days"] <= 3).astype(int)
    df["away_fatigued"] = (df["away_rest_days"] <= 3).astype(int)

    # Day of week (Tuesday/Wednesday = midweek fixture)
    df["is_midweek"] = df["Date"].dt.dayofweek.isin([1, 2]).astype(int)

    return df


def compute_h2h_features(df: pd.DataFrame, n_last: int = 5) -> pd.DataFrame:
    """
    Head-to-head statistics between teams.

    Some pairs have persistent patterns (e.g., one team historically dominates).

    Args:
        df: Match data DataFrame
        n_last: Number of recent matches to consider (default: 5)

    Returns:
        DataFrame with head-to-head features added
    """
    df = df.sort_values("Date").copy()
    h2h_features = []

    for idx, row in df.iterrows():
        home = row["HomeTeam"]
        away = row["AwayTeam"]
        date = row["Date"]

        # All previous meetings between these teams
        prev = df[
            (df["Date"] < date)
            & (
                ((df["HomeTeam"] == home) & (df["AwayTeam"] == away))
                | ((df["HomeTeam"] == away) & (df["AwayTeam"] == home))
            )
        ].tail(n_last)

        if len(prev) < 2:
            h2h_features.append({
                "h2h_home_wins": np.nan,
                "h2h_draws": np.nan,
                "h2h_total_goals_avg": np.nan,
            })
            continue

        # Count results from home team's perspective
        home_wins = 0
        draws = 0
        total_goals = 0

        for _, p in prev.iterrows():
            if p["HomeTeam"] == home:
                if p["FTR"] == "H": home_wins += 1
                elif p["FTR"] == "D": draws += 1
                total_goals += p["FTHG"] + p["FTAG"]
            else:  # home team played away
                if p["FTR"] == "A": home_wins += 1
                elif p["FTR"] == "D": draws += 1
                total_goals += p["FTHG"] + p["FTAG"]

        n = len(prev)
        h2h_features.append({
            "h2h_home_wins": home_wins / n,
            "h2h_draws": draws / n,
            "h2h_total_goals_avg": total_goals / n,
        })

    h2h_df = pd.DataFrame(h2h_features, index=df.index)
    return pd.concat([df, h2h_df], axis=1)


def add_odds_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert bookmaker odds to probabilities and add as features.

    Args:
        df: Match data DataFrame

    Returns:
        DataFrame with odds probability features added
    """
    df = df.copy()

    if all(col in df.columns for col in ["B365H", "B365D", "B365A"]):
        # Raw implied probabilities
        df["odds_prob_H"] = 1 / df["B365H"]
        df["odds_prob_D"] = 1 / df["B365D"]
        df["odds_prob_A"] = 1 / df["B365A"]

        # Normalization (removing bookmaker margin)
        total = df["odds_prob_H"] + df["odds_prob_D"] + df["odds_prob_A"]
        df["norm_prob_H"] = df["odds_prob_H"] / total
        df["norm_prob_D"] = df["odds_prob_D"] / total
        df["norm_prob_A"] = df["odds_prob_A"] / total

        # Probability spread (favorite vs underdog)
        df["odds_spread"] = df["norm_prob_H"] - df["norm_prob_A"]

    return df


# Example usage
if __name__ == "__main__":
    from data_loader import FootballDataLoader, DataCleaner

    # Load data
    loader = FootballDataLoader(
        seasons=["2425", "2324", "2223"],
        leagues=["E0"]
    )
    raw_data = loader.load_all()
    clean_data = DataCleaner.clean(raw_data)

    # Feature engineering
    engineer = FeatureEngineer(window=5)
    featured_data = engineer.build_match_features(clean_data)

    # Add ELO features
    elo_system = FootballELO(k=32, home_advantage=65)
    featured_data = elo_system.compute_elo_features(featured_data)

    # Add xG proxy
    featured_data = compute_xg_proxy(featured_data)

    # Add fatigue features
    featured_data = compute_fatigue_features(featured_data)

    # Add H2H features
    featured_data = compute_h2h_features(featured_data)

    # Add odds features
    featured_data = add_odds_features(featured_data)

    print(f"Matches with features: {len(featured_data)}")
    print(f"Total features: {len([c for c in featured_data.columns if c not in ['Date', 'HomeTeam', 'AwayTeam', 'FTR', 'Result', 'League', 'Season']])}")
    print(f"Top 5 teams by ELO:")
    top_teams = sorted(elo_system.ratings.items(),
                       key=lambda x: -x[1])[:5]
    for team, rating in top_teams:
        print(f"  {team:25s} {rating:.0f}")
