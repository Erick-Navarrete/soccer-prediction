"""
Visualization Module

This module provides comprehensive visualization functions for model evaluation,
feature importance, probability distributions, and divergence analysis.
"""

import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import numpy as np
import pandas as pd
from typing import Dict, List, Optional

# Style settings
matplotlib.rcParams["figure.dpi"] = 120
matplotlib.rcParams["font.size"] = 11
sns.set_style("whitegrid")


def plot_model_comparison(results: Dict, figsize: tuple = (14, 5)):
    """
    Visualization of model accuracy comparison.

    Args:
        results: Dictionary with model results from train_and_evaluate
        figsize: Figure size tuple
    """
    fig, axes = plt.subplots(1, 2, figsize=figsize)

    names = list(results.keys())
    accuracies = [results[n]["accuracy_mean"] for n in names]
    acc_stds = [results[n]["accuracy_std"] for n in names]
    log_losses = [results[n]["log_loss_mean"] for n in names]
    ll_stds = [results[n]["log_loss_std"] for n in names]

    colors = ["#2ecc71", "#3498db", "#e74c3c", "#f39c12"]

    # Accuracy
    bars = axes[0].barh(names, accuracies, xerr=acc_stds,
                         color=colors, edgecolor="white", linewidth=1.5)
    axes[0].set_xlabel("Accuracy")
    axes[0].set_title("Model Accuracy (TimeSeriesSplit CV)")
    axes[0].set_xlim(0.3, 0.65)
    for bar, val in zip(bars, accuracies):
        axes[0].text(val + 0.005, bar.get_y() + bar.get_height()/2,
                     f"{val:.3f}", va="center", fontweight="bold")

    # Log Loss
    bars = axes[1].barh(names, log_losses, xerr=ll_stds,
                         color=colors, edgecolor="white", linewidth=1.5)
    axes[1].set_xlabel("Log Loss")
    axes[1].set_title("Model Log Loss (lower = better)")
    for bar, val in zip(bars, log_losses):
        axes[1].text(val + 0.005, bar.get_y() + bar.get_height()/2,
                     f"{val:.3f}", va="center", fontweight="bold")

    plt.tight_layout()
    plt.savefig("outputs/model_comparison.png", bbox_inches="tight")
    plt.show()


def plot_confusion_matrix(y_true, y_pred, figsize: tuple = (8, 6)):
    """
    Confusion matrix visualization.

    Args:
        y_true: True labels
        y_pred: Predicted labels
        figsize: Figure size tuple
    """
    from sklearn.metrics import confusion_matrix

    cm = confusion_matrix(y_true, y_pred)
    labels = ["Away Win", "Draw", "Home Win"]

    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=labels, yticklabels=labels,
        ax=ax, linewidths=0.5, linecolor="white",
        annot_kws={"size": 14, "weight": "bold"},
    )
    ax.set_xlabel("Predicted Result", fontsize=12)
    ax.set_ylabel("Actual Result", fontsize=12)
    ax.set_title("Confusion Matrix — Ensemble Model", fontsize=14)

    # Add percentages
    cm_pct = cm / cm.sum(axis=1, keepdims=True)
    for i in range(3):
        for j in range(3):
            ax.text(j + 0.5, i + 0.75,
                    f"({cm_pct[i, j]:.0%})",
                    ha="center", va="center",
                    fontsize=9, color="gray")

    plt.tight_layout()
    plt.savefig("outputs/confusion_matrix.png", bbox_inches="tight")
    plt.show()


def plot_feature_importance(model, feature_names: List[str], top_n: int = 15,
                           figsize: tuple = (10, 8)):
    """
    Feature importance visualization for XGBoost / Random Forest.

    Args:
        model: Trained model with feature_importances_ attribute
        feature_names: List of feature names
        top_n: Number of top features to display
        figsize: Figure size tuple
    """
    if not hasattr(model, "feature_importances_"):
        print("Model does not have feature_importances_ attribute")
        return

    importances = model.feature_importances_
    indices = np.argsort(importances)[-top_n:]

    fig, ax = plt.subplots(figsize=figsize)

    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, top_n))
    ax.barh(
        range(top_n),
        importances[indices],
        color=colors,
        edgecolor="white",
        linewidth=0.8,
    )
    ax.set_yticks(range(top_n))
    ax.set_yticklabels([feature_names[i] for i in indices])
    ax.set_xlabel("Feature Importance")
    ax.set_title(f"Top {top_n} Important Features", fontsize=14)

    plt.tight_layout()
    plt.savefig("outputs/feature_importance.png", bbox_inches="tight")
    plt.show()


def plot_probability_distribution(proba, y_true, figsize: tuple = (16, 5)):
    """
    Visualization of predicted probability distributions for each class.

    Args:
        proba: Predicted probabilities array
        y_true: True labels
        figsize: Figure size tuple
    """
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    labels = ["Away Win (0)", "Draw (1)", "Home Win (2)"]
    colors = ["#e74c3c", "#f1c40f", "#2ecc71"]

    for i, (ax, label, color) in enumerate(zip(axes, labels, colors)):
        # Correct predictions
        correct_mask = y_true == i
        ax.hist(proba[correct_mask, i], bins=30, alpha=0.7,
                color=color, label="Correct", density=True)
        ax.hist(proba[~correct_mask, i], bins=30, alpha=0.3,
                color="gray", label="Incorrect", density=True)

        ax.set_xlabel(f"P({label})")
        ax.set_ylabel("Density")
        ax.set_title(label)
        ax.legend()

    plt.suptitle("Predicted Probability Distributions",
                 fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig("outputs/probability_distribution.png", bbox_inches="tight")
    plt.show()


def plot_probability_divergence(
    matches: List[Dict],
    figsize: tuple = (14, 8),
):
    """
    Scatter plot: bookmaker probabilities vs Polymarket.
    Points far from the diagonal = divergences = potential edge.

    Args:
        matches: List of match dictionaries with probability data
        figsize: Figure size tuple
    """
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    outcomes = [("home", "Home Win"), ("draw", "Draw"), ("away", "Away Win")]
    colors = ["#2ecc71", "#f1c40f", "#e74c3c"]

    for ax, (key, title), color in zip(axes, outcomes, colors):
        bk_probs = [m[f"bk_{key}"] for m in matches]
        poly_probs = [m[f"poly_{key}"] for m in matches]

        ax.scatter(bk_probs, poly_probs, alpha=0.6, color=color,
                   edgecolors="white", s=60)

        # Diagonal (full agreement)
        ax.plot([0, 1], [0, 1], "k--", alpha=0.3, linewidth=1)

        # Divergence zones
        ax.fill_between([0, 1], [0.05, 1.05], [0, 1],
                        alpha=0.05, color="blue",
                        label="Polymarket higher")
        ax.fill_between([0, 1], [0, 1], [-0.05, 0.95],
                        alpha=0.05, color="red",
                        label="Bookmaker higher")

        ax.set_xlabel("Bookmaker P", fontsize=11)
        ax.set_ylabel("Polymarket P", fontsize=11)
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal")
        ax.legend(fontsize=8, loc="upper left")

    plt.suptitle(
        "Probability Divergence: Bookmaker vs Polymarket\n"
        "Points far from diagonal → potential value",
        fontsize=14, y=1.04,
    )
    plt.tight_layout()
    plt.savefig("outputs/divergence_scatter.png", bbox_inches="tight")
    plt.show()


def plot_triple_layer_radar(
    match_name: str,
    bookmaker: Dict,
    polymarket: Dict,
    ml_model: Dict,
    figsize: tuple = (8, 8),
):
    """
    Radar chart: comparing three probability sources for a single match.

    Args:
        match_name: Name of the match
        bookmaker: Dictionary with bookmaker probabilities
        polymarket: Dictionary with Polymarket probabilities
        ml_model: Dictionary with ML model probabilities
        figsize: Figure size tuple
    """
    categories = ["Home Win", "Draw", "Away Win"]
    keys = ["home", "draw", "away"]

    fig, ax = plt.subplots(figsize=figsize,
                            subplot_kw=dict(polar=True))

    angles = np.linspace(0, 2 * np.pi, len(categories),
                          endpoint=False).tolist()
    angles += angles[:1]

    sources = [
        ("Bookmaker", bookmaker, "#3498db"),
        ("Polymarket", polymarket, "#e74c3c"),
        ("ML Model", ml_model, "#2ecc71"),
    ]

    for label, probs, color in sources:
        values = [probs[k] for k in keys]
        values += values[:1]
        ax.plot(angles, values, "o-", linewidth=2,
                label=label, color=color)
        ax.fill(angles, values, alpha=0.1, color=color)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=12)
    ax.set_ylim(0, 0.8)
    ax.set_title(f"Triple Layer: {match_name}",
                 fontsize=14, pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))

    plt.tight_layout()
    plt.savefig("outputs/triple_radar.png", bbox_inches="tight")
    plt.show()


def plot_calibration_curve(y_true, y_proba, class_idx: int = 2,
                          class_name: str = "Home Win",
                          figsize: tuple = (8, 8)):
    """
    Calibration plot: shows how well predicted probabilities match actual outcomes.
    Ideal model — diagonal line.

    Args:
        y_true: True labels
        y_proba: Predicted probabilities
        class_idx: Index of the class to plot
        class_name: Name of the class
        figsize: Figure size tuple
    """
    from sklearn.calibration import calibration_curve

    prob_true, prob_pred = calibration_curve(
        (y_true == class_idx).astype(int),
        y_proba[:, class_idx],
        n_bins=10,
        strategy="uniform",
    )

    fig, ax = plt.subplots(figsize=figsize)
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


def plot_elo_timeline(team_names: List[str], elo_data: Dict[str, List[tuple]],
                     figsize: tuple = (14, 8)):
    """
    Plot ELO rating timeline for specified teams.

    Args:
        team_names: List of team names to plot
        elo_data: Dictionary mapping team names to list of (date, rating) tuples
        figsize: Figure size tuple
    """
    fig, ax = plt.subplots(figsize=figsize)

    colors = plt.cm.tab10(np.linspace(0, 1, len(team_names)))

    for team, color in zip(team_names, colors):
        if team in elo_data:
            dates, ratings = zip(*elo_data[team])
            ax.plot(dates, ratings, "o-", linewidth=2,
                    markersize=4, label=team, color=color)

    ax.set_xlabel("Date")
    ax.set_ylabel("ELO Rating")
    ax.set_title("ELO Rating Timeline")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("outputs/elo_timeline.png", bbox_inches="tight")
    plt.show()


# Example usage
if __name__ == "__main__":
    # Example: Model comparison
    results = {
        "Logistic Regression": {
            "accuracy_mean": 0.52,
            "accuracy_std": 0.03,
            "log_loss_mean": 0.98,
            "log_loss_std": 0.05,
        },
        "Random Forest": {
            "accuracy_mean": 0.54,
            "accuracy_std": 0.04,
            "log_loss_mean": 0.92,
            "log_loss_std": 0.06,
        },
        "XGBoost": {
            "accuracy_mean": 0.56,
            "accuracy_std": 0.03,
            "log_loss_mean": 0.88,
            "log_loss_std": 0.04,
        },
    }
    plot_model_comparison(results)

    # Example: Triple layer radar
    plot_triple_layer_radar(
        "Arsenal vs Manchester City",
        bookmaker={"home": 0.42, "draw": 0.28, "away": 0.30},
        polymarket={"home": 0.38, "draw": 0.24, "away": 0.38},
        ml_model={"home": 0.45, "draw": 0.26, "away": 0.29},
    )
