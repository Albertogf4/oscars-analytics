#!/usr/bin/env python3
"""
Kalshi Oscar Markets Analyzer for "One Battle After Another"

This script searches Kalshi prediction markets for Oscar-related series,
identifies markets related to the movie "One Battle After Another" (2025),
and outputs a JSON file with matched markets, prices, and volumes.
"""

import requests
import json
import re
import time
from datetime import datetime, timezone

# Kalshi API Configuration
BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"

# Enriched keywords for "One Battle After Another" (2025)
# Based on web research about the film
KEYWORDS = [
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
    """Main pipeline to fetch and filter Oscar markets for OBAA."""
    print("=" * 60)
    print("Kalshi Oscar Markets Analyzer")
    print("Movie: One Battle After Another (2025)")
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

    # Step 3: Filter markets matching OBAA keywords
    print("Step 3: Filtering markets for 'One Battle After Another'...")
    matched_markets = filter_markets_by_keywords(all_markets, KEYWORDS)

    print(f"Found {len(matched_markets)} markets matching OBAA keywords")
    print()

    # Step 4: Prepare output
    output = {
        "movie": "One Battle After Another",
        "year": 2025,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "keywords_used": KEYWORDS,
        "markets": matched_markets,
        "summary": {
            "total_oscar_series": len(oscar_series),
            "total_markets_scanned": len(all_markets),
            "total_markets_matched": len(matched_markets),
            "oscar_series": [s["ticker"] for s in oscar_series],
        }
    }

    # Step 5: Save to JSON
    output_file = "oscars_obaa_markets.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Results saved to: {output_file}")
    print()

    # Step 6: Print summary
    print("=" * 60)
    print("MATCHED MARKETS SUMMARY")
    print("=" * 60)

    if matched_markets:
        for market in matched_markets:
            print(f"\nMarket: {market['ticker']}")
            print(f"  Title: {market['title']}")
            if market.get('subtitle'):
                print(f"  Subtitle: {market['subtitle']}")
            print(f"  Yes Price: {market['yes_price_cents']}¢")
            print(f"  Volume: {market['volume']:,}")
            print(f"  Status: {market['status']}")
            print(f"  Matched Keywords: {', '.join(market['matched_keywords'])}")
    else:
        print("\nNo markets found matching 'One Battle After Another' keywords.")
        print("This could mean:")
        print("  - The movie is listed under a different name")
        print("  - Markets haven't been created yet")
        print("  - Keywords need adjustment")

    print()
    print("=" * 60)
    print("DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()
