"""Kalshi API client for fetching Oscar prediction markets."""

import requests
import re
import time
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from functools import lru_cache

BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"

# Cache configuration
CACHE_TTL_MINUTES = int(os.getenv("CACHE_TTL_MINUTES", "5"))
CACHE_TTL = timedelta(minutes=CACHE_TTL_MINUTES)

# In-memory cache
_cache: Dict[str, Any] = {}
_cache_timestamps: Dict[str, datetime] = {}

# File-based persistent cache
CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)


# Movie configurations
MOVIES = {
    "One Battle After Another": {
        "keywords": [
            "One Battle After Another", "Battle After Another", "OBAA",
            "Paul Thomas Anderson", "PTA",
            "Leonardo DiCaprio", "Leo DiCaprio", "DiCaprio",
            "Sean Penn", "Benicio Del Toro", "Benicio del Toro", "Del Toro",
            "Regina Hall", "Teyana Taylor", "Chase Infiniti", "Alana Haim", "Wood Harris",
            "Jonny Greenwood", "Michael Bauman", "Florencia Martin",
            "Andy Jurgensen", "Colleen Atwood", "Chris Scarabosio",
            "Vineland", "Thomas Pynchon",
        ],
        "year": 2025,
        "director": "Paul Thomas Anderson",
    },
    "Sinners": {
        "keywords": [
            "Sinners",
            "Ryan Coogler", "Coogler",
            "Michael B. Jordan", "Michael B Jordan", "Michael Jordan",
            "Hailee Steinfeld", "Jack O'Connell", "Wunmi Mosaku",
            "Delroy Lindo", "Omar Benson Miller", "Jayme Lawson",
            "Ludwig Goransson", "Autumn Durald", "Hannah Beachler", "Ruth E. Carter",
        ],
        "year": 2025,
        "director": "Ryan Coogler",
    },
    "Hamnet": {
        "keywords": [
            "Hamnet",
            "Chloe Zhao", "Zhao",
            "Paul Mescal", "Mescal", "Jessie Buckley", "Buckley",
            "Emily Watson", "Joe Alwyn",
            "Joshua James Richards",
            "Maggie O'Farrell", "O'Farrell",
        ],
        "year": 2025,
        "director": "Chloe Zhao",
    },
}


def _get_file_cache(key: str) -> Optional[Any]:
    """Load from file cache if valid."""
    cache_file = CACHE_DIR / f"{key}.json"
    meta_file = CACHE_DIR / "cache_metadata.json"

    if not cache_file.exists():
        return None

    try:
        meta = json.loads(meta_file.read_text()) if meta_file.exists() else {}
        timestamp_str = meta.get(key)
        if timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str)
            if datetime.now(timezone.utc) - timestamp < CACHE_TTL:
                return json.loads(cache_file.read_text())
    except (json.JSONDecodeError, ValueError):
        pass

    return None


def _set_file_cache(key: str, value: Any) -> None:
    """Save to file cache."""
    cache_file = CACHE_DIR / f"{key}.json"
    meta_file = CACHE_DIR / "cache_metadata.json"

    try:
        cache_file.write_text(json.dumps(value, default=str))

        meta = json.loads(meta_file.read_text()) if meta_file.exists() else {}
        meta[key] = datetime.now(timezone.utc).isoformat()
        meta_file.write_text(json.dumps(meta))
    except (OSError, TypeError):
        pass  # Silently fail file cache writes


def _get_cached(key: str) -> Optional[Any]:
    """Get cached value from memory or file."""
    # Try memory first
    if key in _cache and key in _cache_timestamps:
        if datetime.now(timezone.utc) - _cache_timestamps[key] < CACHE_TTL:
            return _cache[key]

    # Try file cache
    file_data = _get_file_cache(key)
    if file_data:
        # Warm memory cache
        _cache[key] = file_data
        _cache_timestamps[key] = datetime.now(timezone.utc)
        return file_data

    return None


def _set_cache(key: str, value: Any) -> None:
    """Set cache in memory and file."""
    _cache[key] = value
    _cache_timestamps[key] = datetime.now(timezone.utc)
    _set_file_cache(key, value)


def fetch_oscar_series() -> List[Dict]:
    """Fetch all Oscar-related series from Kalshi."""
    cached = _get_cached("oscar_series")
    if cached:
        return cached

    url = f"{BASE_URL}/series"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        all_series = data.get("series", [])
        oscar_series = [
            {
                "ticker": s.get("ticker"),
                "title": s.get("title"),
                "category": s.get("category"),
            }
            for s in all_series
            if "oscar" in s.get("title", "").lower()
        ]

        _set_cache("oscar_series", oscar_series)
        return oscar_series

    except requests.exceptions.RequestException:
        return []


def fetch_markets_for_series(series_ticker: str, max_retries: int = 3) -> List[Dict]:
    """Fetch all open markets for a series ticker."""
    cache_key = f"markets_{series_ticker}"
    cached = _get_cached(cache_key)
    if cached:
        return cached

    markets = []
    cursor = None

    while True:
        url = f"{BASE_URL}/markets?series_ticker={series_ticker}&status=open"
        if cursor:
            url += f"&cursor={cursor}"

        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                data = response.json()

                batch_markets = data.get("markets", [])
                markets.extend(batch_markets)

                cursor = data.get("cursor")
                if not cursor:
                    _set_cache(cache_key, markets)
                    return markets
                break

            except requests.exceptions.RequestException:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return markets

    return markets


def match_keywords(text: str, keywords: List[str]) -> List[str]:
    """Check if text matches any keywords."""
    if not text:
        return []

    matched = []
    text_lower = text.lower()

    for keyword in keywords:
        if len(keyword) <= 4:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text_lower):
                matched.append(keyword)
        else:
            if keyword.lower() in text_lower:
                matched.append(keyword)

    return matched


def extract_category(title: str) -> str:
    """Extract Oscar category from market title."""
    if "Best Picture" in title:
        return "Best Picture"
    elif "Best Director" in title:
        return "Best Director"
    elif "Best Actor" in title and "Supporting" not in title:
        return "Best Actor"
    elif "Best Actress" in title and "Supporting" not in title:
        return "Best Actress"
    elif "Supporting Actor" in title:
        return "Supporting Actor"
    elif "Supporting Actress" in title:
        return "Supporting Actress"
    elif "Original Screenplay" in title:
        return "Original Screenplay"
    elif "Adapted Screenplay" in title:
        return "Adapted Screenplay"
    elif "Screenplay" in title:
        return "Screenplay"
    elif "Score" in title or "Music" in title:
        return "Original Score"
    elif "Cinematography" in title:
        return "Cinematography"
    elif "Editing" in title:
        return "Film Editing"
    elif "Visual Effects" in title:
        return "Visual Effects"
    elif "Production Design" in title:
        return "Production Design"
    elif "Costume" in title:
        return "Costume Design"
    elif "Makeup" in title:
        return "Makeup"
    elif "Sound" in title:
        return "Sound"
    elif "Song" in title:
        return "Original Song"
    elif "How many" in title:
        return "Total Wins"
    else:
        return "Other"


def fetch_all_oscar_markets() -> Dict[str, Any]:
    """Fetch all Oscar markets and organize by movie."""
    cached = _get_cached("all_markets")
    if cached:
        return cached

    oscar_series = fetch_oscar_series()
    all_markets = []

    for series in oscar_series:
        ticker = series["ticker"]
        markets = fetch_markets_for_series(ticker)
        for market in markets:
            market["_series_ticker"] = ticker
        all_markets.extend(markets)
        time.sleep(0.3)  # Rate limiting

    # Filter markets for each movie
    movies_data = {}
    for movie_name, movie_info in MOVIES.items():
        matched_markets = []
        for market in all_markets:
            title = market.get("title", "")
            subtitle = market.get("subtitle", "")
            combined = f"{title} {subtitle}"

            matched_keywords = match_keywords(combined, movie_info["keywords"])
            if matched_keywords:
                matched_markets.append({
                    "ticker": market.get("ticker"),
                    "title": title,
                    "subtitle": subtitle,
                    "category": extract_category(title),
                    "yes_price": market.get("yes_ask"),
                    "yes_bid": market.get("yes_bid"),
                    "no_price": market.get("no_ask"),
                    "volume": market.get("volume", 0) or 0,
                    "volume_24h": market.get("volume_24h", 0) or 0,
                    "open_interest": market.get("open_interest", 0) or 0,
                    "matched_keywords": matched_keywords,
                })

        movies_data[movie_name] = {
            "markets": matched_markets,
            "director": movie_info["director"],
            "year": movie_info["year"],
        }

    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_markets_scanned": len(all_markets),
        "movies": movies_data,
    }

    _set_cache("all_markets", result)
    return result


def calculate_metrics(markets: List[Dict]) -> Dict:
    """Calculate aggregate metrics for a list of markets."""
    if not markets:
        return {
            "total_markets": 0,
            "avg_yes_price": 0,
            "total_volume": 0,
            "total_open_interest": 0,
            "categories": [],
        }

    yes_prices = [m.get("yes_price") for m in markets if m.get("yes_price")]
    volumes = [m.get("volume", 0) or 0 for m in markets]
    open_interests = [m.get("open_interest", 0) or 0 for m in markets]
    categories = list(set(m.get("category", "Other") for m in markets))

    return {
        "total_markets": len(markets),
        "avg_yes_price": sum(yes_prices) / len(yes_prices) if yes_prices else 0,
        "total_volume": sum(volumes),
        "total_open_interest": sum(open_interests),
        "categories": categories,
    }


def get_key_odds(markets: List[Dict], category: str) -> Optional[int]:
    """Get odds for a specific category."""
    for m in markets:
        if m.get("category") == category:
            return m.get("yes_price")
    return None


def build_head_to_head(movies_data: Dict) -> List[Dict]:
    """Build head-to-head comparison by category."""
    # Collect all categories across all movies
    all_categories = set()
    for movie_name, data in movies_data.items():
        for market in data["markets"]:
            cat = market.get("category", "Other")
            if cat not in ["Other", "Total Wins"]:
                all_categories.add(cat)

    head_to_head = []
    for category in sorted(all_categories):
        category_data = {"category": category, "markets": {}}
        max_price = 0
        leader = None

        for movie_name, data in movies_data.items():
            for market in data["markets"]:
                if market.get("category") == category:
                    price = market.get("yes_price") or 0
                    category_data["markets"][movie_name] = {
                        "price": price,
                        "volume": market.get("volume", 0),
                        "ticker": market.get("ticker"),
                    }
                    if price > max_price:
                        max_price = price
                        leader = movie_name
                    break

        if category_data["markets"]:
            category_data["leader"] = leader
            head_to_head.append(category_data)

    # Sort by importance
    category_order = [
        "Best Picture", "Best Director", "Best Actor", "Best Actress",
        "Supporting Actor", "Supporting Actress", "Original Screenplay",
        "Adapted Screenplay", "Cinematography", "Original Score", "Film Editing",
    ]

    def sort_key(item):
        try:
            return category_order.index(item["category"])
        except ValueError:
            return len(category_order)

    return sorted(head_to_head, key=sort_key)


def clear_cache():
    """Clear all cached data (memory and files)."""
    global _cache, _cache_timestamps
    _cache = {}
    _cache_timestamps = {}

    # Clear file cache
    for f in CACHE_DIR.glob("*.json"):
        try:
            f.unlink()
        except OSError:
            pass
