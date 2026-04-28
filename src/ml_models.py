"""
ML Models Module

This module provides machine learning model training, evaluation, and ensemble methods
for football match prediction.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, classification_report,
    confusion_matrix, log_loss,
)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier, GradientBoostingClassifier,
    VotingClassifier,
)
from xgboost import XGBClassifier
from typing import Dict, Tuple, Optional


def prepare_model_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, list]:
    """
    Prepare data for model training.

    Extracts features and target variable, using ONLY features available
    before match start to prevent data leakage.

    Args:
        df: Feature-engineered match data DataFrame

    Returns:
        Tuple of (X, y, feature_names)
    """
    feature_cols = [c for c in df.columns
                    if c.startswith(("home_", "away_", "diff_",
                                     "norm_prob_", "odds_spread", "elo_",
                                     "h2h_", "xG_", "rest_", "fatigue"))]

    X = df[feature_cols].copy()
    y = df["Result"].copy()

    # Fill missing values with median
    X = X.fillna(X.median())

    print(f"Features: {X.shape[1]}")
    print(f"Matches: {X.shape[0]}")
    print(f"Class balance: {y.value_counts().to_dict()}")

    return X, y, feature_cols


def train_and_evaluate(
    X: pd.DataFrame,
    y: pd.Series,
    n_splits: int = 5
) -> Tuple[Dict, Dict]:
    """
    Train multiple models with time series validation.

    Uses TimeSeriesSplit to prevent data leakage from future matches.

    Args:
        X: Feature matrix
        y: Target variable
        n_splits: Number of time series splits

    Returns:
        Tuple of (results_dict, models_dict)
    """
    # TimeSeriesSplit — correct validation for time series data
    tscv = TimeSeriesSplit(n_splits=n_splits)
    scaler = StandardScaler()

    models = {
        "Logistic Regression": LogisticRegression(
            max_iter=1000, multi_class="multinomial", C=0.5,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200, max_depth=8,
            min_samples_leaf=10, random_state=42,
        ),
        "XGBoost": XGBClassifier(
            n_estimators=200, max_depth=5,
            learning_rate=0.05, subsample=0.8,
            colsample_bytree=0.8, random_state=42,
            eval_metric="mlogloss",
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=150, max_depth=4,
            learning_rate=0.08, random_state=42,
        ),
    }

    results = {}

    for name, model in models.items():
        fold_accuracies = []
        fold_log_losses = []

        for train_idx, test_idx in tscv.split(X):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            model.fit(X_train_scaled, y_train)

            preds = model.predict(X_test_scaled)
            proba = model.predict_proba(X_test_scaled)

            fold_accuracies.append(accuracy_score(y_test, preds))
            fold_log_losses.append(log_loss(y_test, proba))

        results[name] = {
            "accuracy_mean": np.mean(fold_accuracies),
            "accuracy_std": np.std(fold_accuracies),
            "log_loss_mean": np.mean(fold_log_losses),
            "log_loss_std": np.std(fold_log_losses),
        }

        print(f"\n{'='*50}")
        print(f"  {name}")
        print(f"  Accuracy:  {results[name]['accuracy_mean']:.4f} "
              f"± {results[name]['accuracy_std']:.4f}")
        print(f"  Log Loss:  {results[name]['log_loss_mean']:.4f} "
              f"± {results[name]['log_loss_std']:.4f}")

    return results, models


def build_ensemble(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.2
) -> Tuple[VotingClassifier, StandardScaler]:
    """
    Build an ensemble model with soft voting.

    Ensembles usually outperform individual models by combining
    their strengths.

    Args:
        X: Feature matrix
        y: Target variable
        test_size: Proportion of data to use for testing

    Returns:
        Tuple of (ensemble_model, scaler)
    """
    scaler = StandardScaler()

    ensemble = VotingClassifier(
        estimators=[
            ("lr", LogisticRegression(
                max_iter=1000, multi_class="multinomial", C=0.5)),
            ("rf", RandomForestClassifier(
                n_estimators=200, max_depth=8, random_state=42)),
            ("xgb", XGBClassifier(
                n_estimators=200, max_depth=5, learning_rate=0.05,
                random_state=42, eval_metric="mlogloss")),
        ],
        voting="soft",  # use probabilities, not votes
        weights=[1, 1, 2],  # higher weight for XGBoost
    )

    # Final training on all data (for production)
    # In practice, keep a holdout set
    split_idx = int(len(X) * (1 - test_size))
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    ensemble.fit(X_train_scaled, y_train)

    preds = ensemble.predict(X_test_scaled)
    proba = ensemble.predict_proba(X_test_scaled)

    print(f"\n{'='*60}")
    print(f"  ENSEMBLE (Soft Voting)")
    print(f"  Accuracy:  {accuracy_score(y_test, preds):.4f}")
    print(f"  Log Loss:  {log_loss(y_test, proba):.4f}")
    print(f"\n{classification_report(y_test, preds, "
          f"target_names=['Away Win', 'Draw', 'Home Win'])}")

    return ensemble, scaler


def predict_match(
    model: VotingClassifier,
    scaler: StandardScaler,
    features: pd.DataFrame
) -> Tuple[int, np.ndarray]:
    """
    Make predictions for a single match.

    Args:
        model: Trained ensemble model
        scaler: Fitted scaler
        features: Feature DataFrame for the match

    Returns:
        Tuple of (prediction, probabilities)
    """
    features_scaled = scaler.transform(features)
    prediction = model.predict(features_scaled)[0]
    probabilities = model.predict_proba(features_scaled)[0]

    return prediction, probabilities


def get_feature_importance(
    model: object,
    feature_names: list
) -> pd.DataFrame:
    """
    Get feature importance from a model.

    Args:
        model: Trained model with feature_importances_ attribute
        feature_names: List of feature names

    Returns:
        DataFrame with feature importance sorted by importance
    """
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    else:
        raise ValueError("Model does not have feature_importances_ attribute")

    importance_df = pd.DataFrame({
        "feature": feature_names,
        "importance": importances
    }).sort_values("importance", ascending=False)

    return importance_df


# Example usage
if __name__ == "__main__":
    from data_loader import FootballDataLoader, DataCleaner
    from feature_engineering import (
        FeatureEngineer, FootballELO, compute_xg_proxy,
        compute_fatigue_features, compute_h2h_features, add_odds_features
    )

    # Load and prepare data
    loader = FootballDataLoader(
        seasons=["2425", "2324", "2223", "2122"],
        leagues=["E0"]
    )
    raw_data = loader.load_all()
    clean_data = DataCleaner.clean(raw_data)

    # Feature engineering
    engineer = FeatureEngineer(window=5)
    featured_data = engineer.build_match_features(clean_data)

    # Add advanced features
    elo_system = FootballELO(k=32, home_advantage=65)
    featured_data = elo_system.compute_elo_features(featured_data)
    featured_data = compute_xg_proxy(featured_data)
    featured_data = compute_fatigue_features(featured_data)
    featured_data = compute_h2h_features(featured_data)
    featured_data = add_odds_features(featured_data)

    # Prepare model data
    X, y, feature_names = prepare_model_data(featured_data)

    # Train and evaluate models
    results, models = train_and_evaluate(X, y)

    # Build ensemble
    ensemble, scaler = build_ensemble(X, y)

    # Get feature importance from Random Forest
    rf_model = models["Random Forest"]
    importance_df = get_feature_importance(rf_model, feature_names)
    print(f"\nTop 10 Most Important Features:")
    print(importance_df.head(10))
