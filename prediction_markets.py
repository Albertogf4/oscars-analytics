#!/usr/bin/env python3
"""
Kalshi Oscar Markets Analyzer - Multi-Movie Comparison

This script searches Kalshi prediction markets for Oscar-related series,
identifies markets related to top Oscar contenders (2025),
and outputs a JSON file with matched markets, prices, and volumes for comparison.
"""

import requests
import json
import re
import time
from datetime import datetime, timezone

# Kalshi API Configuration
BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"

# =============================================================================
# MOVIE KEYWORD CONFIGURATIONS
# =============================================================================

# Keywords for "One Battle After Another" (2025)
OBAA_KEYWORDS = [
    # Movie Title Variations
    "One Battle After Another",
    "Battle After Another",
    "OBAA",

    # Director & Screenplay
    "Paul Thomas Anderson",
    "PTA",

    # Lead Cast (Oscar-nominated)
    "Leonardo DiCaprio",
    "Leo DiCaprio",
    "DiCaprio",
    "Sean Penn",
    "Benicio Del Toro",
    "Benicio del Toro",
    "Del Toro",

    # Supporting Cast
    "Regina Hall",
    "Teyana Taylor",
    "Chase Infiniti",
    "Alana Haim",
    "Wood Harris",

    # Key Crew (potential Oscar categories)
    "Jonny Greenwood",      # Composer - Original Score
    "Michael Bauman",       # Cinematographer
    "Florencia Martin",     # Production Designer
    "Andy Jurgensen",       # Editor
    "Colleen Atwood",       # Costume Designer
    "Chris Scarabosio",     # Sound

    # Source Material
    "Vineland",
    "Thomas Pynchon",
]

# Keywords for "Sinners" (2025) - Ryan Coogler vampire film
SINNERS_KEYWORDS = [
    # Movie Title Variations
    "Sinners",

    # Director & Screenplay
    "Ryan Coogler",
    "Coogler",

    # Lead Cast
    "Michael B. Jordan",
    "Michael B Jordan",
    "Michael Jordan",

    # Supporting Cast
    "Hailee Steinfeld",
    "Jack O'Connell",
    "Wunmi Mosaku",
    "Delroy Lindo",
    "Omar Benson Miller",
    "Jayme Lawson",

    # Key Crew (potential Oscar categories)
    "Ludwig Göransson",    # Composer - Original Score
    "Ludwig Goransson",
    "Autumn Durald",       # Cinematographer
    "Hannah Beachler",     # Production Designer
    "Ruth E. Carter",      # Costume Designer
]

# Keywords for "Hamnet" (2025) - Chloé Zhao Shakespeare drama
HAMNET_KEYWORDS = [
    # Movie Title Variations
    "Hamnet",

    # Director & Screenplay
    "Chloé Zhao",
    "Chloe Zhao",
    "Zhao",

    # Lead Cast
    "Paul Mescal",
    "Mescal",
    "Jessie Buckley",
    "Buckley",

    # Supporting Cast
    "Emily Watson",
    "Joe Alwyn",

    # Key Crew (potential Oscar categories)
    "Joshua James Richards",  # Cinematographer (frequent Zhao collaborator)

    # Source Material
    "Maggie O'Farrell",       # Novel author
    "O'Farrell",
]

# All movies to analyze
MOVIES = {
    "One Battle After Another": {
        "keywords": OBAA_KEYWORDS,
        "year": 2025,
        "director": "Paul Thomas Anderson",
    },
    "Sinners": {
        "keywords": SINNERS_KEYWORDS,
        "year": 2025,
        "director": "Ryan Coogler",
    },
    "Hamnet": {
        "keywords": HAMNET_KEYWORDS,
        "year": 2025,
        "director": "Chloé Zhao",
    },
}


def fetch_all_series():
    """Fetch all series from Kalshi and filter Oscar-related ones."""
    url = f"{BASE_URL}/series"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        all_series = data.get("series", [])
        oscar_series = []

        for series in all_series:
            title = series.get("title", "")
            if "oscar" in title.lower():
                oscar_series.append({
                    "ticker": series.get("ticker"),
                    "title": series.get("title"),
                    "frequency": series.get("frequency"),
                    "category": series.get("category"),
                })

        return oscar_series

    except requests.exceptions.RequestException as e:
        print(f"Error fetching series: {e}")
        return []


def fetch_markets_for_series(series_ticker, max_retries=3):
    """Fetch all markets for a given series ticker with pagination."""
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

                # Check for pagination cursor
                cursor = data.get("cursor")
                if not cursor:
                    return markets

                break  # Successful, move to next page

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"  Retry {attempt + 1}/{max_retries} after {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"  Error fetching markets for {series_ticker}: {e}")
                    return markets

    return markets


def match_keywords(text, keywords):
    """Check if text matches any keywords. Returns list of matched keywords."""
    if not text:
        return []

    matched = []
    text_lower = text.lower()

    for keyword in keywords:
        # Use word boundary matching for short keywords to avoid false positives
        if len(keyword) <= 4:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text_lower):
                matched.append(keyword)
        else:
            if keyword.lower() in text_lower:
                matched.append(keyword)

    return matched


def filter_markets_by_keywords(markets, keywords):
    """Filter markets that match any of the keywords."""
    matched_markets = []

    for market in markets:
        title = market.get("title", "")
        subtitle = market.get("subtitle", "")
        yes_sub_title = market.get("yes_sub_title", "")
        no_sub_title = market.get("no_sub_title", "")

        # Combine all text fields for matching
        combined_text = f"{title} {subtitle} {yes_sub_title} {no_sub_title}"

        matched_keywords = match_keywords(combined_text, keywords)

        if matched_keywords:
            matched_markets.append({
                "ticker": market.get("ticker"),
                "title": title,
                "subtitle": subtitle,
                "event_ticker": market.get("event_ticker"),
                "yes_price_cents": market.get("yes_ask"),
                "yes_bid_cents": market.get("yes_bid"),
                "no_price_cents": market.get("no_ask"),
                "volume": market.get("volume"),
                "volume_24h": market.get("volume_24h"),
                "open_interest": market.get("open_interest"),
                "status": market.get("status"),
                "matched_keywords": matched_keywords,
            })

    return matched_markets


def main():
    """Main pipeline to fetch and filter Oscar markets for multiple movies."""
    print("=" * 60)
    print("Kalshi Oscar Markets Analyzer - Multi-Movie Comparison")
    print("Comparing: One Battle After Another, Sinners, Hamnet")
    print("=" * 60)
    print()

    # Step 1: Fetch all Oscar-related series
    print("Step 1: Fetching all series from Kalshi...")
    oscar_series = fetch_all_series()

    if not oscar_series:
        print("No Oscar-related series found.")
        return

    print(f"Found {len(oscar_series)} Oscar-related series:")
    for series in oscar_series:
        print(f"  - {series['ticker']}: {series['title']}")
    print()

    # Step 2: Fetch markets for each Oscar series
    print("Step 2: Fetching markets for each series...")
    all_markets = []

    for series in oscar_series:
        ticker = series["ticker"]
        print(f"  Fetching markets for {ticker}...")
        markets = fetch_markets_for_series(ticker)
        print(f"    Found {len(markets)} markets")

        # Add series info to each market
        for market in markets:
            market["_series_ticker"] = ticker
            market["_series_title"] = series["title"]

        all_markets.extend(markets)
        time.sleep(0.5)  # Rate limiting

    print(f"\nTotal markets across all Oscar series: {len(all_markets)}")
    print()

    # Step 3: Filter markets for each movie
    print("Step 3: Filtering markets for each movie...")
    movies_results = {}

    for movie_name, movie_info in MOVIES.items():
        matched = filter_markets_by_keywords(all_markets, movie_info["keywords"])
        movies_results[movie_name] = {
            "markets": matched,
            "director": movie_info["director"],
            "year": movie_info["year"],
            "keywords": movie_info["keywords"],
        }
        print(f"  {movie_name}: {len(matched)} markets found")

    print()

    # Step 4: Build comparison data
    comparison = []
    for movie_name, result in movies_results.items():
        movie_data = {
            "movie": movie_name,
            "director": result["director"],
            "year": result["year"],
            "total_markets": len(result["markets"]),
            "markets": result["markets"],
            "aggregate_metrics": calculate_aggregate_metrics(result["markets"]),
        }
        comparison.append(movie_data)

    # Step 5: Prepare output
    output = {
        "analysis_type": "Oscar Contenders Comparison",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "movies_analyzed": list(MOVIES.keys()),
        "comparison": comparison,
        "summary": {
            "total_oscar_series": len(oscar_series),
            "total_markets_scanned": len(all_markets),
            "oscar_series": [s["ticker"] for s in oscar_series],
        }
    }

    # Step 6: Save to JSON
    output_file = "oscars_comparison_markets.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Results saved to: {output_file}")
    print()

    # Step 7: Print comparison summary
    print("=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)

    for movie_data in comparison:
        print(f"\n{'─' * 50}")
        print(f"📽️  {movie_data['movie']} ({movie_data['year']})")
        print(f"    Director: {movie_data['director']}")
        print(f"    Markets Found: {movie_data['total_markets']}")

        metrics = movie_data["aggregate_metrics"]
        if metrics["total_markets"] > 0:
            print(f"    Avg Yes Price: {metrics['avg_yes_price']:.1f}¢")
            print(f"    Total Volume: {metrics['total_volume']:,}")
            print(f"    Total Open Interest: {metrics['total_open_interest']:,}")
            print(f"    Categories: {', '.join(metrics['categories'])}")

        if movie_data["markets"]:
            print(f"\n    Top Markets:")
            # Sort by volume and show top 3
            sorted_markets = sorted(
                movie_data["markets"],
                key=lambda x: x.get("volume", 0) or 0,
                reverse=True
            )[:3]
            for market in sorted_markets:
                price = market.get('yes_price_cents') or 'N/A'
                volume = market.get('volume') or 0
                print(f"      • {market['title']}")
                print(f"        Price: {price}¢ | Volume: {volume:,}")

    # Step 8: Print head-to-head comparison
    print()
    print("=" * 60)
    print("HEAD-TO-HEAD METRICS")
    print("=" * 60)
    print()
    print(f"{'Movie':<30} {'Markets':<10} {'Avg Price':<12} {'Total Vol':<15}")
    print("-" * 67)

    for movie_data in sorted(comparison, key=lambda x: x["aggregate_metrics"]["avg_yes_price"], reverse=True):
        metrics = movie_data["aggregate_metrics"]
        name = movie_data["movie"][:28]
        markets = movie_data["total_markets"]
        avg_price = f"{metrics['avg_yes_price']:.1f}¢" if metrics["total_markets"] > 0 else "N/A"
        total_vol = f"{metrics['total_volume']:,}" if metrics["total_markets"] > 0 else "N/A"
        print(f"{name:<30} {markets:<10} {avg_price:<12} {total_vol:<15}")

    print()
    print("=" * 60)
    print("DONE")
    print("=" * 60)


def calculate_aggregate_metrics(markets):
    """Calculate aggregate metrics for a movie's markets."""
    if not markets:
        return {
            "total_markets": 0,
            "avg_yes_price": 0,
            "total_volume": 0,
            "total_open_interest": 0,
            "categories": [],
        }

    yes_prices = [m.get("yes_price_cents") for m in markets if m.get("yes_price_cents")]
    volumes = [m.get("volume", 0) or 0 for m in markets]
    open_interests = [m.get("open_interest", 0) or 0 for m in markets]

    # Extract category from market titles (e.g., "Best Picture", "Best Director")
    categories = set()
    for m in markets:
        title = m.get("title", "")
        if "Best Picture" in title:
            categories.add("Best Picture")
        elif "Best Director" in title:
            categories.add("Best Director")
        elif "Best Actor" in title:
            categories.add("Best Actor")
        elif "Best Actress" in title:
            categories.add("Best Actress")
        elif "Supporting Actor" in title:
            categories.add("Supporting Actor")
        elif "Supporting Actress" in title:
            categories.add("Supporting Actress")
        elif "Screenplay" in title:
            categories.add("Screenplay")
        elif "Score" in title or "Music" in title:
            categories.add("Score/Music")
        elif "Cinematography" in title:
            categories.add("Cinematography")
        else:
            categories.add("Other")

    return {
        "total_markets": len(markets),
        "avg_yes_price": sum(yes_prices) / len(yes_prices) if yes_prices else 0,
        "total_volume": sum(volumes),
        "total_open_interest": sum(open_interests),
        "categories": list(categories),
    }


if __name__ == "__main__":
    main()
