"""
Backtesting Module

This module provides walk-forward backtesting and probability calibration
for realistic model evaluation on time-series sports data.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, log_loss, classification_report
from sklearn.preprocessing import StandardScaler
from typing import Dict, Optional


class WalkForwardBacktest:
    """
    Walk-forward backtesting: train model on past data,
    predict the next round, shift the window.

    This is the only correct way to test a predictive model on sports data -
    simulating real-time trading over time.
    """

    def __init__(self, model, scaler: StandardScaler,
                 initial_train_size: int = 500, step_size: int = 50):
        """
        Initialize the walk-forward backtester.

        Args:
            model: Machine learning model to test
            scaler: Fitted StandardScaler
            initial_train_size: Minimum number of samples for initial training
            step_size: Number of samples to advance in each step
        """
        self.model = model
        self.scaler = scaler
        self.initial_train_size = initial_train_size
        self.step_size = step_size

    def run(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """
        Run the walk-forward backtest.

        Args:
            X: Feature matrix
            y: Target variable

        Returns:
            Dictionary with backtest results
        """
        all_preds = []
        all_proba = []
        all_true = []

        for start in range(self.initial_train_size,
                           len(X) - self.step_size,
                           self.step_size):
            end = start + self.step_size

            X_train = X.iloc[:start]
            y_train = y.iloc[:start]
            X_test = X.iloc[start:end]
            y_test = y.iloc[start:end]

            X_train_s = self.scaler.fit_transform(X_train)
            X_test_s = self.scaler.transform(X_test)

            self.model.fit(X_train_s, y_train)

            preds = self.model.predict(X_test_s)
            proba = self.model.predict_proba(X_test_s)

            all_preds.extend(preds)
            all_proba.extend(proba)
            all_true.extend(y_test.values)

        all_preds = np.array(all_preds)
        all_proba = np.array(all_proba)
        all_true = np.array(all_true)

        accuracy = accuracy_score(all_true, all_preds)
        logloss = log_loss(all_true, all_proba)

        print(f"Walk-Forward Backtest Results:")
        print(f"  Total predictions: {len(all_preds)}")
        print(f"  Accuracy: {accuracy:.4f}")
        print(f"  Log Loss: {logloss:.4f}")
        report = classification_report(all_true, all_preds, target_names=['Away', 'Draw', 'Home'])
        print(f"\n{report}")

        return {
            "predictions": all_preds,
            "probabilities": all_proba,
            "actuals": all_true,
            "accuracy": accuracy,
            "log_loss": logloss,
        }


def plot_calibration_curve(y_true, y_proba, class_idx: int = 2,
                          class_name: str = "Home Win",
                          n_bins: int = 10):
    """
    Calibration plot: shows how well predicted probabilities match actual outcomes.
    Ideal model — diagonal line.

    Args:
        y_true: True labels
        y_proba: Predicted probabilities
        class_idx: Index of the class to plot
        class_name: Name of the class
        n_bins: Number of bins for calibration
    """
    from sklearn.calibration import calibration_curve
    import matplotlib.pyplot as plt

    prob_true, prob_pred = calibration_curve(
        (y_true == class_idx).astype(int),
        y_proba[:, class_idx],
        n_bins=n_bins,
        strategy="uniform",
    )

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.plot([0, 1], [0, 1], "k--", label="Perfectly calibrated")
    ax.plot(prob_pred, prob_true, "s-", color="#e74c3c",
            label=f"Model ({class_name})", linewidth=2, markersize=8)

    ax.fill_between(prob_pred, prob_true,
                     [p for p in prob_pred],
                     alpha=0.1, color="#e74c3c")

    ax.set_xlabel("Mean predicted probability")
    ax.set_ylabel("Actual fraction of positives")
    ax.set_title("Calibration Curve")
    ax.legend(loc="lower right")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig("outputs/calibration_curve.png", bbox_inches="tight")
    plt.show()


def calculate_brier_score(y_true, y_proba) -> float:
    """
    Calculate Brier score for probability calibration.

    Lower is better. 0 = perfect calibration.

    Args:
        y_true: True labels (one-hot encoded)
        y_proba: Predicted probabilities

    Returns:
        Brier score
    """
    return np.mean((y_proba - y_true) ** 2)


def calculate_reliability_diagram(y_true, y_proba, n_bins: int = 10) -> Dict:
    """
    Calculate reliability diagram data for calibration analysis.

    Args:
        y_true: True labels
        y_proba: Predicted probabilities
        n_bins: Number of bins

    Returns:
        Dictionary with bin statistics
    """
    bin_edges = np.linspace(0, 1, n_bins + 1)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    bin_true = []
    bin_pred = []
    bin_count = []

    for i in range(n_bins):
        mask = (y_proba >= bin_edges[i]) & (y_proba < bin_edges[i + 1])
        if i == n_bins - 1:  # Include the upper edge for the last bin
            mask = (y_proba >= bin_edges[i]) & (y_proba <= bin_edges[i + 1])

        if np.sum(mask) > 0:
            bin_true.append(np.mean(y_true[mask]))
            bin_pred.append(np.mean(y_proba[mask]))
            bin_count.append(np.sum(mask))
        else:
            bin_true.append(np.nan)
            bin_pred.append(np.nan)
            bin_count.append(0)

    return {
        "bin_centers": bin_centers,
        "bin_true": bin_true,
        "bin_pred": bin_pred,
        "bin_count": bin_count,
    }


def calculate_expected_calibration_error(y_true, y_proba, n_bins: int = 10) -> float:
    """
    Calculate Expected Calibration Error (ECE).

    ECE measures the weighted average difference between
    predicted probabilities and actual outcomes.

    Args:
        y_true: True labels
        y_proba: Predicted probabilities
        n_bins: Number of bins

    Returns:
        ECE score
    """
    reliability = calculate_reliability_diagram(y_true, y_proba, n_bins)

    ece = 0.0
    total_samples = len(y_true)

    for i in range(n_bins):
        if reliability["bin_count"][i] > 0:
            weight = reliability["bin_count"][i] / total_samples
            ece += weight * abs(reliability["bin_true"][i] - reliability["bin_pred"][i])

    return ece


def backtest_with_rolling_window(
    model, X: pd.DataFrame, y: pd.Series,
    window_size: int = 100,
    test_size: int = 10
) -> Dict:
    """
    Backtest using a rolling window approach.

    Args:
        model: Machine learning model
        X: Feature matrix
        y: Target variable
        window_size: Size of training window
        test_size: Size of test window

    Returns:
        Dictionary with backtest results
    """
    scaler = StandardScaler()
    all_preds = []
    all_proba = []
    all_true = []

    for i in range(window_size, len(X) - test_size, test_size):
        X_train = X.iloc[i-window_size:i]
        y_train = y.iloc[i-window_size:i]
        X_test = X.iloc[i:i+test_size]
        y_test = y.iloc[i:i+test_size]

        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)

        model.fit(X_train_s, y_train)

        preds = model.predict(X_test_s)
        proba = model.predict_proba(X_test_s)

        all_preds.extend(preds)
        all_proba.extend(proba)
        all_true.extend(y_test.values)

    all_preds = np.array(all_preds)
    all_proba = np.array(all_proba)
    all_true = np.array(all_true)

    accuracy = accuracy_score(all_true, all_preds)
    logloss = log_loss(all_true, all_proba)

    return {
        "predictions": all_preds,
        "probabilities": all_proba,
        "actuals": all_true,
        "accuracy": accuracy,
        "log_loss": logloss,
    }


# Example usage
if __name__ == "__main__":
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import make_classification

    # Generate sample data
    X, y = make_classification(
        n_samples=1000, n_features=20, n_classes=3,
        n_informative=10, random_state=42
    )
    X = pd.DataFrame(X)
    y = pd.Series(y)

    # Run walk-forward backtest
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    scaler = StandardScaler()

    backtester = WalkForwardBacktest(
        model=model,
        scaler=scaler,
        initial_train_size=500,
        step_size=50
    )

    results = backtester.run(X, y)

    # Plot calibration curve
    plot_calibration_curve(
        results["actuals"],
        results["probabilities"],
        class_idx=2,
        class_name="Class 2"
    )

    # Calculate calibration metrics
    y_true_onehot = np.zeros_like(results["probabilities"])
    for i in range(len(results["actuals"])):
        y_true_onehot[i, results["actuals"][i]] = 1

    brier_score = calculate_brier_score(y_true_onehot, results["probabilities"])
    print(f"\nBrier Score: {brier_score:.4f}")

    ece = calculate_expected_calibration_error(
        (results["actuals"] == 2).astype(int),
        results["probabilities"][:, 2]
    )
    print(f"Expected Calibration Error: {ece:.4f}")
