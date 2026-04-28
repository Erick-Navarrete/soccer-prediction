"""
Claude Integration Module

This module provides optional Claude API integration for contextual match analysis,
divergence interpretation, and natural language prediction reports.

Note: Claude API requires an Anthropic API key. This module is optional and
the system works without it.
"""

import anthropic
import json
from typing import Dict, Optional
from dotenv import load_dotenv
import os

load_dotenv()


def get_claude_client() -> Optional[anthropic.Anthropic]:
    """
    Get Claude API client if API key is available.

    Returns:
        Anthropic client or None if no API key
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("⚠ Claude API key not found. Skipping Claude integration.")
        print("  To enable: Set ANTHROPIC_API_KEY in .env file")
        return None
    return anthropic.Anthropic(api_key=api_key)


def claude_analyze_matchup(
    home_team: str,
    away_team: str,
    home_form: Dict,
    away_form: Dict,
    league: str,
    client: Optional[anthropic.Anthropic] = None
) -> Dict:
    """
    Ask Claude to evaluate contextual match factors that are difficult
    to extract from numerical data.

    Returns JSON with scores on a 0-1 scale.

    Args:
        home_team: Home team name
        away_team: Away team name
        home_form: Dictionary with home team statistics
        away_form: Dictionary with away team statistics
        league: League name
        client: Anthropic client (optional, will create if not provided)

    Returns:
        Dictionary with analysis scores
    """
    if client is None:
        client = get_claude_client()
        if client is None:
            return {}

    prompt = f"""You are an expert football match analyst. Analyze the upcoming match
and return ONLY JSON (no markdown, no comments) with the following scores
on a scale from 0.0 to 1.0:

Match: {home_team} (home) vs {away_team} (away)
League: {league}

{home_team} stats over last 5 matches:
- Avg goals scored: {home_form.get('avg_GF', 'N/A'):.2f}
- Avg goals conceded: {home_form.get('avg_GA', 'N/A'):.2f}
- Avg shots: {home_form.get('avg_Shots', 'N/A'):.2f}
- Avg shots on target: {home_form.get('avg_SoT', 'N/A'):.2f}
- Form (avg points): {home_form.get('Form', 'N/A'):.2f}

{away_team} stats over last 5 matches:
- Avg goals scored: {away_form.get('avg_GF', 'N/A'):.2f}
- Avg goals conceded: {away_form.get('avg_GA', 'N/A'):.2f}
- Avg shots: {away_form.get('avg_Shots', 'N/A'):.2f}
- Avg shots on target: {away_form.get('avg_SoT', 'N/A'):.2f}
- Form (avg points): {away_form.get('Form', 'N/A'):.2f}

Return JSON strictly in the format:
{{
    "home_attack_strength": <float>,
    "home_defense_strength": <float>,
    "away_attack_strength": <float>,
    "away_defense_strength": <float>,
    "home_momentum": <float>,
    "away_momentum": <float>,
    "match_intensity_prediction": <float>,
    "upset_probability": <float>,
    "home_win_confidence": <float>,
    "draw_likelihood": <float>,
    "reasoning": "<brief 1-2 sentence explanation>"
}}"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text.strip()

        # Extract JSON from response
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to find JSON in the response
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(response_text[start:end])
            return {}
    except Exception as e:
        print(f"⚠ Claude API error: {e}")
        return {}


def claude_analyze_divergence(
    match: str,
    bookmaker: Dict,
    polymarket: Dict,
    ml_model: Dict,
    poly_liquidity: float,
    poly_volume_24h: float,
    client: Optional[anthropic.Anthropic] = None
) -> str:
    """
    Claude analyzes divergences between three sources and proposes an interpretation.

    Args:
        match: Match name
        bookmaker: Dictionary with bookmaker probabilities
        polymarket: Dictionary with Polymarket probabilities
        ml_model: Dictionary with ML model probabilities
        poly_liquidity: Polymarket liquidity
        poly_volume_24h: Polymarket 24h volume
        client: Anthropic client (optional)

    Returns:
        String with analysis
    """
    if client is None:
        client = get_claude_client()
        if client is None:
            return "Claude API not available"

    prompt = f"""You are a senior sports analyst. You have three probability
sources for a football match. Analyze the divergences.

**Match:** {match}

| Source | Home | Draw | Away |
|---|---|---|---|
| Bookmaker (Bet365) | {bookmaker['home']:.1%} | {bookmaker['draw']:.1%} | {bookmaker['away']:.1%} |
| Polymarket | {polymarket['home']:.1%} | {polymarket['draw']:.1%} | {polymarket['away']:.1%} |
| ML Model | {ml_model['home']:.1%} | {ml_model['draw']:.1%} | {ml_model['away']:.1%} |

**Polymarket metadata:**
- Liquidity: ${poly_liquidity:,.0f}
- 24h volume: ${poly_volume_24h:,.0f}

**Task:**
1. Where are the main divergences and what might they mean?
2. Which source should be trusted more in this case and why?
3. Are there signs of insider activity on Polymarket?
   (unusual volume, sharp probability shift)
4. What final prediction would you give and with what confidence?

Be specific, no filler. 5-8 sentences."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )

        return message.content[0].text
    except Exception as e:
        print(f"⚠ Claude API error: {e}")
        return f"Error: {e}"


def generate_prediction_report(
    home_team: str,
    away_team: str,
    model_proba: Dict,
    stats: Dict,
    league: str,
    client: Optional[anthropic.Anthropic] = None
) -> str:
    """
    Generate a detailed analytical report using Claude based on model
    probabilities and team statistics.

    Args:
        home_team: Home team name
        away_team: Away team name
        model_proba: Dictionary with model probabilities
        stats: Dictionary with team statistics
        league: League name
        client: Anthropic client (optional)

    Returns:
        String with prediction report
    """
    if client is None:
        client = get_claude_client()
        if client is None:
            return "Claude API not available"

    prompt = f"""You are a professional football analyst. Based on the machine
learning model data and team statistics, write a concise but
insightful analytical report on the upcoming match.

## Model Data

Match: **{home_team}** vs **{away_team}** ({league})

Model probabilities (ML Ensemble):
- {home_team} win: {model_proba['home_win']:.1%}
- Draw: {model_proba['draw']:.1%}
- {away_team} win: {model_proba['away_win']:.1%}

{home_team} stats (last 5 matches):
- Goals scored (avg): {stats['home_avg_GF']:.2f}
- Goals conceded (avg): {stats['home_avg_GA']:.2f}
- Shots on target (avg): {stats['home_avg_SoT']:.1f}
- Form (avg points): {stats['home_Form']:.2f}

{away_team} stats (last 5 matches):
- Goals scored (avg): {stats['away_avg_GF']:.2f}
- Goals conceded (avg): {stats['away_avg_GA']:.2f}
- Shots on target (avg): {stats['away_avg_SoT']:.1f}
- Form (avg points): {stats['away_Form']:.2f}

## Task

Write an analytical report that includes:
1. Key factors affecting the prediction
2. Strengths and weaknesses of each team
3. Most likely outcome prediction
4. Confidence level (high / medium / low)
5. Potential risks and upset scenarios

Write concisely, professionally, no filler."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )

        return message.content[0].text
    except Exception as e:
        print(f"⚠ Claude API error: {e}")
        return f"Error: {e}"


def analyze_matchday(
    matches: list,
    client: Optional[anthropic.Anthropic] = None
) -> str:
    """
    Analyze an entire matchday with a single Claude call.
    More efficient than separate requests for each match.

    Args:
        matches: List of match dictionaries
        client: Anthropic client (optional)

    Returns:
        String with matchday analysis
    """
    if client is None:
        client = get_claude_client()
        if client is None:
            return "Claude API not available"

    matches_text = ""
    for i, m in enumerate(matches, 1):
        matches_text += f"""
{i}. {m['home']} vs {m['away']}
   ML prediction: H={m['prob_H']:.0%} | D={m['prob_D']:.0%} | A={m['prob_A']:.0%}
   Home form: {m['home_form']:.2f} | Away form: {m['away_form']:.2f}
"""

    prompt = f"""Analyze the upcoming matchday. For each match, provide:
- Prediction (1X2)
- Confidence (⭐ low, ⭐⭐ medium, ⭐⭐⭐ high)
- Brief comment (1 sentence)

Matches:
{matches_text}

Return in table format. At the end, add the 1-2 best picks of the matchday (highest confidence)."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )

        return message.content[0].text
    except Exception as e:
        print(f"⚠ Claude API error: {e}")
        return f"Error: {e}"


# Example usage
if __name__ == "__main__":
    # Check if Claude API is available
    client = get_claude_client()

    if client:
        # Example: Analyze a matchup
        home_form_example = {
            "avg_GF": 1.8, "avg_GA": 0.6,
            "avg_Shots": 14.2, "avg_SoT": 5.8,
            "Form": 2.4,
        }
        away_form_example = {
            "avg_GF": 1.2, "avg_GA": 1.4,
            "avg_Shots": 10.6, "avg_SoT": 3.2,
            "Form": 1.2,
        }

        analysis = claude_analyze_matchup(
            home_team="Arsenal",
            away_team="Brighton",
            home_form=home_form_example,
            away_form=away_form_example,
            league="Premier League",
            client=client,
        )
        print("Matchup Analysis:")
        print(json.dumps(analysis, indent=2, ensure_ascii=False))

        # Example: Generate prediction report
        report = generate_prediction_report(
            home_team="Arsenal",
            away_team="Brighton",
            model_proba={"home_win": 0.58, "draw": 0.22, "away_win": 0.20},
            stats={
                "home_avg_GF": 1.8, "home_avg_GA": 0.6,
                "home_avg_SoT": 5.8, "home_Form": 2.4,
                "away_avg_GF": 1.2, "away_avg_GA": 1.4,
                "away_avg_SoT": 3.2, "away_Form": 1.2,
            },
            league="Premier League",
            client=client,
        )
        print("\nPrediction Report:")
        print(report)
    else:
        print("Claude API not configured. Skipping examples.")
