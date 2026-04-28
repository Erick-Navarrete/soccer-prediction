"""
Polymarket Integration Module

This module provides integration with Polymarket's prediction market API,
including fetching current odds, historical prices, and computing divergence
features between different probability sources.
"""

import requests
import json
import time
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Optional, Dict, List


GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"


@dataclass
class PolymarketOdds:
    """Structure for storing Polymarket probabilities."""
    home_win: float
    draw: Optional[float]  # Some markets are binary (no draw)
    away_win: float
    liquidity: float
    volume_24h: float
    market_slug: str
    last_updated: str


class PolymarketClient:
    """
    Client for fetching sports markets from Polymarket.

    Polymarket Gamma API — public REST API requiring
    no authorization. Limits: ~50 results per request,
    recommended rate limit ~1 req/sec.
    """

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/118.0.0.0 Safari/537.36"
        )
    }

    # Keywords for filtering football markets
    FOOTBALL_KEYWORDS = [
        "soccer", "premier league", "la liga", "bundesliga",
        "serie a", "ligue 1", "champions league", "uefa",
        "manchester", "liverpool", "arsenal", "chelsea",
        "barcelona", "real madrid", "bayern", "psg",
        "epl", "football match",
    ]

    def search_football_markets(
        self, limit: int = 100
    ) -> List[Dict]:
        """
        Find all active football markets on Polymarket.
        Filter by keywords in the market question.

        Args:
            limit: Maximum number of markets to fetch

        Returns:
            List of market dictionaries
        """
        all_markets = []
        offset = 0

        while offset < limit:
            try:
                resp = requests.get(
                    f"{GAMMA_API}/markets",
                    params={
                        "active": "true",
                        "closed": "false",
                        "limit": 50,
                        "offset": offset,
                    },
                    headers=self.HEADERS,
                    timeout=15,
                )
                resp.raise_for_status()
                markets = resp.json()

                if not markets:
                    break

                # Filter by football keywords
                for market in markets:
                    question = market.get("question", "").lower()
                    description = market.get("description", "").lower()
                    text = question + " " + description

                    if any(kw in text for kw in self.FOOTBALL_KEYWORDS):
                        all_markets.append(market)

                offset += 50
                time.sleep(0.5)  # Polite rate limiting

            except requests.RequestException as e:
                print(f"  ⚠ Request error: {e}")
                break

        print(f"  ✓ Found {len(all_markets)} football markets")
        return all_markets

    def get_event_markets(self, event_slug: str) -> List[Dict]:
        """
        Get all markets for a specific event (e.g., a match).

        Polymarket organizes data hierarchically:
        Event → Markets → Outcomes

        Args:
            event_slug: Event identifier

        Returns:
            List of market dictionaries
        """
        try:
            resp = requests.get(
                f"{GAMMA_API}/events",
                params={
                    "slug": event_slug,
                    "closed": "false",
                },
                headers=self.HEADERS,
                timeout=15,
            )
            resp.raise_for_status()
            events = resp.json()

            if events:
                return events[0].get("markets", [])
            return []

        except requests.RequestException as e:
            print(f"  ⚠ Error: {e}")
            return []

    def extract_match_odds(self, market: Dict) -> Optional[PolymarketOdds]:
        """
        Extract probabilities from market data.

        On Polymarket, contract price = implied probability.
        "Yes" price = $0.65 → 65% probability.

        Args:
            market: Market dictionary from API

        Returns:
            PolymarketOdds object or None if extraction fails
        """
        try:
            outcomes = market.get("outcomes", [])
            prices_raw = market.get("outcomePrices", "[]")

            if isinstance(prices_raw, str):
                prices = json.loads(prices_raw)
            else:
                prices = prices_raw

            if len(prices) < 2:
                return None

            prices = [float(p) for p in prices]
            outcomes_lower = [o.lower() for o in outcomes]

            # Determine market type
            # Option 1: binary market "Team A wins?"
            if len(prices) == 2:
                return PolymarketOdds(
                    home_win=prices[0],
                    draw=None,
                    away_win=prices[1],
                    liquidity=float(market.get("liquidity", 0) or 0),
                    volume_24h=float(market.get("volume24hr", 0) or 0),
                    market_slug=market.get("slug", ""),
                    last_updated=market.get("updatedAt", ""),
                )

            # Option 2: 3-way market (Home / Draw / Away)
            if len(prices) >= 3:
                home_idx = next(
                    (i for i, o in enumerate(outcomes_lower)
                     if "home" in o or "win" in o),
                    0,
                )
                draw_idx = next(
                    (i for i, o in enumerate(outcomes_lower)
                     if "draw" in o or "tie" in o),
                    1,
                )
                away_idx = next(
                    (i for i, o in enumerate(outcomes_lower)
                     if "away" in o or "lose" in o),
                    2,
                )

                return PolymarketOdds(
                    home_win=prices[home_idx],
                    draw=prices[draw_idx],
                    away_win=prices[away_idx],
                    liquidity=float(market.get("liquidity", 0) or 0),
                    volume_24h=float(market.get("volume24hr", 0) or 0),
                    market_slug=market.get("slug", ""),
                    last_updated=market.get("updatedAt", ""),
                )

        except (ValueError, IndexError, KeyError) as e:
            print(f"  ⚠ Failed to extract prices: {e}")

        return None


class PolymarketHistorical:
    """
    Fetching historical prices from Polymarket CLOB API
    for use in backtesting.
    """

    def get_price_history(
        self, token_id: str, interval: str = "1d",
        fidelity: int = 60,
    ) -> pd.DataFrame:
        """
        Get price history for a specific outcome token.

        Args:
            token_id: Token ID from market data
            interval: time interval ('1d', '1w', '1m', 'all')
            fidelity: granularity in minutes

        Returns:
            DataFrame with price history
        """
        try:
            resp = requests.get(
                f"{CLOB_API}/prices-history",
                params={
                    "market": token_id,
                    "interval": interval,
                    "fidelity": fidelity,
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

            if not data or "history" not in data:
                return pd.DataFrame()

            df = pd.DataFrame(data["history"])
            df["timestamp"] = pd.to_datetime(df["t"], unit="s")
            df["price"] = df["p"].astype(float)
            df = df[["timestamp", "price"]].sort_values("timestamp")

            return df

        except requests.RequestException as e:
            print(f"  ⚠ Error fetching history: {e}")
            return pd.DataFrame()

    def get_orderbook_snapshot(self, token_id: str) -> Dict:
        """
        Order book snapshot — shows liquidity depth.

        Thin order book = unreliable signal.
        Deep order book = strong market consensus.

        Args:
            token_id: Token ID from market data

        Returns:
            Dictionary with order book metrics
        """
        try:
            resp = requests.get(
                f"{CLOB_API}/book",
                params={"token_id": token_id},
                timeout=15,
            )
            resp.raise_for_status()
            book = resp.json()

            bids = book.get("bids", [])
            asks = book.get("asks", [])

            total_bid_depth = sum(
                float(b.get("size", 0)) for b in bids
            )
            total_ask_depth = sum(
                float(a.get("size", 0)) for a in asks
            )

            best_bid = float(bids[0]["price"]) if bids else 0
            best_ask = float(asks[0]["price"]) if asks else 1
            spread = best_ask - best_bid
            midpoint = (best_bid + best_ask) / 2

            return {
                "midpoint": midpoint,
                "spread": spread,
                "spread_pct": spread / midpoint if midpoint > 0 else 0,
                "bid_depth_usd": total_bid_depth,
                "ask_depth_usd": total_ask_depth,
                "total_depth": total_bid_depth + total_ask_depth,
                "imbalance": (
                    (total_bid_depth - total_ask_depth)
                    / (total_bid_depth + total_ask_depth)
                    if (total_bid_depth + total_ask_depth) > 0
                    else 0
                ),
            }

        except (requests.RequestException, IndexError, ValueError):
            return {}


class TripleLayerFeatures:
    """
    Combining three probability layers:
    1. Bookmaker (Bet365) — margined odds
    2. Polymarket — blockchain crowd intelligence
    3. ML model — our own estimate

    Divergences between layers are among the most valuable features.
    """

    @staticmethod
    def compute_divergence_features(
        bookmaker_probs: Dict,
        polymarket_probs: Dict,
        ml_probs: Optional[Dict] = None,
    ) -> Dict:
        """
        Compute features based on divergences between probability sources.

        High divergence may indicate:
        - Insider information on one of the markets
        - One source lagging behind
        - Value bet opportunity

        Args:
            bookmaker_probs: Dictionary with 'home', 'draw', 'away' probabilities
            polymarket_probs: Dictionary with 'home', 'draw', 'away' probabilities
            ml_probs: Optional dictionary with ML model probabilities

        Returns:
            Dictionary of divergence features
        """
        features = {}

        # === Raw probabilities from each source ===
        for prefix, probs in [("bk", bookmaker_probs),
                               ("poly", polymarket_probs)]:
            features[f"{prefix}_prob_H"] = probs.get("home", 0)
            features[f"{prefix}_prob_D"] = probs.get("draw", 0)
            features[f"{prefix}_prob_A"] = probs.get("away", 0)

        # === KL-divergence between bookmaker and Polymarket ===
        # Higher KL-divergence = stronger disagreement
        epsilon = 1e-6
        kl_div = 0
        for key in ["home", "draw", "away"]:
            p = bookmaker_probs.get(key, epsilon)
            q = polymarket_probs.get(key, epsilon)
            p = max(p, epsilon)
            q = max(q, epsilon)
            kl_div += p * np.log(p / q)
        features["kl_div_bk_poly"] = kl_div

        # === Absolute divergences ===
        for key, label in [("home", "H"), ("draw", "D"), ("away", "A")]:
            bk = bookmaker_probs.get(key, 0)
            poly = polymarket_probs.get(key, 0)
            features[f"divergence_{label}"] = bk - poly
            features[f"abs_divergence_{label}"] = abs(bk - poly)

        # === Maximum divergence (across any outcome) ===
        features["max_divergence"] = max(
            features["abs_divergence_H"],
            features["abs_divergence_D"],
            features["abs_divergence_A"],
        )

        # === Who is favorite by each source ===
        bk_favorite = max(bookmaker_probs, key=bookmaker_probs.get)
        poly_favorite = max(polymarket_probs, key=polymarket_probs.get)
        features["sources_agree"] = int(bk_favorite == poly_favorite)

        # === Weighted average probabilities ===
        # Polymarket with higher liquidity → higher weight
        for key, label in [("home", "H"), ("draw", "D"), ("away", "A")]:
            bk = bookmaker_probs.get(key, 0)
            poly = polymarket_probs.get(key, 0)
            # 50/50 by default, adjustable
            features[f"blended_prob_{label}"] = 0.5 * bk + 0.5 * poly

        # === If ML probabilities available — triple system ===
        if ml_probs:
            for key, label in [("home", "H"), ("draw", "D"),
                                ("away", "A")]:
                ml = ml_probs.get(key, 0)
                bk = bookmaker_probs.get(key, 0)
                poly = polymarket_probs.get(key, 0)

                features[f"ml_prob_{label}"] = ml
                features[f"ml_vs_bk_{label}"] = ml - bk
                features[f"ml_vs_poly_{label}"] = ml - poly

                # Triple blend: ML=40%, Polymarket=35%, Bookmaker=25%
                features[f"triple_blend_{label}"] = (
                    0.40 * ml + 0.35 * poly + 0.25 * bk
                )

            # All three sources agree?
            ml_favorite = max(ml_probs, key=ml_probs.get)
            features["all_three_agree"] = int(
                bk_favorite == poly_favorite == ml_favorite
            )

        return features

    @staticmethod
    def compute_liquidity_features(orderbook: Dict) -> Dict:
        """
        Features based on Polymarket liquidity.

        Liquidity depth is a market confidence indicator.
        Narrow spread + deep order book = strong consensus.

        Args:
            orderbook: Dictionary from get_orderbook_snapshot

        Returns:
            Dictionary of liquidity features
        """
        return {
            "poly_spread": orderbook.get("spread", 0),
            "poly_spread_pct": orderbook.get("spread_pct", 0),
            "poly_depth_total": orderbook.get("total_depth", 0),
            "poly_depth_log": np.log1p(
                orderbook.get("total_depth", 0)
            ),
            "poly_imbalance": orderbook.get("imbalance", 0),
            # Binary: liquidity above threshold?
            "poly_liquid_market": int(
                orderbook.get("total_depth", 0) > 5000
            ),
        }


# Example usage
if __name__ == "__main__":
    # Example: Search for football markets
    poly_client = PolymarketClient()
    football_markets = poly_client.search_football_markets(limit=200)

    for market in football_markets[:5]:
        odds = poly_client.extract_match_odds(market)
        if odds:
            print(f"\n  📊 {market['question']}")
            if odds.draw:
                print(f"     Home: {odds.home_win:.1%} | "
                      f"Draw: {odds.draw:.1%} | "
                      f"Away: {odds.away_win:.1%}")
            else:
                print(f"     Yes: {odds.home_win:.1%} | "
                      f"No: {odds.away_win:.1%}")
            print(f"     Liquidity: ${odds.liquidity:,.0f} | "
                  f"24h Vol: ${odds.volume_24h:,.0f}")

    # Example: Compute divergence features
    bookmaker = {"home": 0.55, "draw": 0.25, "away": 0.20}
    polymarket = {"home": 0.48, "draw": 0.22, "away": 0.30}
    ml_model_probs = {"home": 0.52, "draw": 0.23, "away": 0.25}

    triple_features = TripleLayerFeatures.compute_divergence_features(
        bookmaker_probs=bookmaker,
        polymarket_probs=polymarket,
        ml_probs=ml_model_probs,
    )

    print("\n=== Triple Layer Features ===")
    for k, v in triple_features.items():
        print(f"  {k:30s} = {v:.4f}")
