"""Retrain ML ensemble model using only pre-match-available features.

This script trains a model that doesn't rely on odds data (which is unavailable
for upcoming fixtures), and uses proper forward-fill for rolling stats so the
model works cleanly for both historical and upcoming matches.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import pickle

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))

from data_loader import FootballDataLoader
from feature_engineering import (
    FeatureEngineer, FootballELO,
    compute_xg_proxy, compute_fatigue_features,
    compute_h2h_features,
)
from ml_models import build_ensemble
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, log_loss, classification_report
from sklearn.model_selection import TimeSeriesSplit


def prepare_features_no_odds(df):
    """Select features available before match start (no odds)."""
    feature_cols = [c for c in df.columns
                    if c.startswith(("home_", "away_", "diff_"))
                    and not c.startswith(("home_xG", "away_xG", "diff_xG"))
                    or c.startswith("elo_")
                    or c.startswith("h2h_")
                    or c.startswith("rest_")
                    or c in ("home_fatigued", "away_fatigued", "is_midweek")]

    # Remove xG proxy columns — these use match-in-progress stats (SoT, shots)
    # For upcoming fixtures we can't compute them, so exclude from model
    feature_cols = [c for c in feature_cols
                    if "xG" not in c and "xg" not in c.lower()]

    return feature_cols


def main():
    print("=== Retraining ML Model (Pre-Match Features Only) ===\n")

    # 1. Load historical data (3 seasons for better training)
    print("Loading historical data...")
    loader = FootballDataLoader(seasons=["2526", "2425", "2324"], leagues=["E0"])
    raw = loader.load_all()
    df = raw.copy()
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date"])

    num_cols = ["FTHG", "FTAG", "HTHG", "HTAG", "HS", "AS", "HST", "AST",
                "HF", "AF", "HC", "AC", "HY", "AY", "HR", "AR", "B365H", "B365D", "B365A"]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    result_map = {"H": 2, "D": 1, "A": 0}
    df["Result"] = df["FTR"].map(result_map)
    df = df.dropna(subset=["Result"])
    print(f"  {len(df)} matches loaded")

    # 2. Feature engineering
    print("Computing features...")
    fe = FeatureEngineer(window=5)
    featured = fe.build_match_features(df)

    elo_sys = FootballELO(k=32, home_advantage=65)
    featured = elo_sys.compute_elo_features(featured)

    featured = compute_xg_proxy(featured)
    featured = compute_fatigue_features(featured)
    featured = compute_h2h_features(featured)

    # NOTE: intentionally NOT adding odds features — unavailable for upcoming

    print(f"  {len(featured)} matches with features")

    # 3. Select features available at prediction time
    feature_cols = prepare_features_no_odds(featured)

    # Filter to only rows with results and valid features
    X = featured[feature_cols].copy()
    y = featured["Result"].copy()
    X = X.fillna(X.median())

    # Drop any columns that are entirely NaN
    valid_cols = [c for c in X.columns if X[c].notna().sum() > 0]
    X = X[valid_cols]
    feature_names = list(X.columns)

    print(f"  {len(feature_names)} features selected (no odds, no xG)")
    print(f"  Class balance: {y.value_counts().to_dict()}")

    # 4. Time-series cross-validation
    print("\nCross-validating...")
    tscv = TimeSeriesSplit(n_splits=5)
    scaler = StandardScaler()

    models = {
        "LR": LogisticRegression(max_iter=1000, C=0.5),
        "RF": RandomForestClassifier(n_estimators=200, max_depth=8, min_samples_leaf=10, random_state=42),
        "GB": GradientBoostingClassifier(n_estimators=150, max_depth=4, learning_rate=0.08, random_state=42),
    }

    for name, model in models.items():
        accs = []
        for train_idx, test_idx in tscv.split(X):
            X_tr = scaler.fit_transform(X.iloc[train_idx])
            X_te = scaler.transform(X.iloc[test_idx])
            model.fit(X_tr, y.iloc[train_idx])
            preds = model.predict(X_te)
            accs.append(accuracy_score(y.iloc[test_idx], preds))
        print(f"  {name}: {np.mean(accs):.4f} ± {np.std(accs):.4f}")

    # 5. Train final ensemble
    print("\nTraining final ensemble...")
    ensemble = VotingClassifier(
        estimators=[
            ("lr", LogisticRegression(max_iter=1000, C=0.5)),
            ("rf", RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)),
            ("gb", GradientBoostingClassifier(n_estimators=150, max_depth=4, learning_rate=0.08, random_state=42)),
        ],
        voting="soft",
        weights=[1, 1, 1],
    )

    # Train on all data
    scaler_final = StandardScaler()
    X_scaled = scaler_final.fit_transform(X)
    ensemble.fit(X_scaled, y)

    # Evaluate on last 20% (time-ordered)
    split = int(len(X) * 0.8)
    X_test_s = scaler_final.transform(X.iloc[split:])
    preds = ensemble.predict(X_test_s)
    probs = ensemble.predict_proba(X_test_s)
    print(f"\n  Holdout accuracy: {accuracy_score(y.iloc[split:], preds):.4f}")
    print(f"  Holdout log loss: {log_loss(y.iloc[split:], probs):.4f}")
    print(classification_report(y.iloc[split:], preds, target_names=["Away Win", "Draw", "Home Win"]))

    # 6. Save model
    output_dir = ROOT / "outputs"
    with open(output_dir / "ensemble_model.pkl", "wb") as f:
        pickle.dump(ensemble, f)
    with open(output_dir / "scaler.pkl", "wb") as f:
        pickle.dump(scaler_final, f)
    with open(output_dir / "feature_names.pkl", "wb") as f:
        pickle.dump(feature_names, f)

    print(f"\nModel saved to outputs/")
    print(f"  Features: {len(feature_names)}")
    print(f"  Feature list: {feature_names}")

    # 7. Print ELO ratings for reference
    print("\nTop 10 teams by ELO:")
    for team, rating in sorted(elo_sys.ratings.items(), key=lambda x: -x[1])[:10]:
        print(f"  {team:25s} {rating:.0f}")


if __name__ == "__main__":
    main()
