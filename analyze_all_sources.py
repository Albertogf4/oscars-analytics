"""
Unified Sentiment Analysis for YouTube and Reddit Comments
Analyzes comments from both sources using VADER and generates dashboard data.
"""

import json
import re
from pathlib import Path
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def extract_movie_name(filename: str, source: str) -> str:
    """Extract movie name from filename."""
    if source == "youtube":
        # Format: comments_MovieName_YYYY-MM-DD.json or comments_YYYY-MM-DD.json
        match = re.match(r'comments_([A-Za-z0-9]+)_\d{4}', filename)
        if match:
            name = match.group(1)
            # Convert camelCase to spaces (e.g., OneBattleAfterAnother -> One Battle After Another)
            name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
            return name
        # Fallback for comments_YYYY-MM-DD.json format (no movie name)
        return "One Battle After Another"
    else:
        # Format: reddit_Movie_Name_movie_YYYY-MM-DD.json or reddit_Movie_Name_YYYY-MM-DD.json
        match = re.match(r'reddit_(.+?)_\d{4}', filename)
        if match:
            name = match.group(1).replace('_', ' ')
            # Remove trailing "movie" if present
            name = re.sub(r'\s+movie$', '', name, flags=re.IGNORECASE)
            return name
    return "Unknown"


def normalize_movie_name(name: str) -> str:
    """Normalize movie names for consistent matching."""
    name = name.lower().strip()
    name = re.sub(r'\s+', ' ', name)
    
    # Handle common variations
    if 'one battle' in name or 'obaa' in name:
        return "One Battle After Another"
    if 'marty' in name:
        return "Marty Supreme"
    if 'sinner' in name:
        return "Sinners"
    if 'f1' in name or name == 'f 1':
        return "F1"
    return name.title()


def classify_sentiment(compound: float) -> str:
    """Classify sentiment based on VADER compound score."""
    if compound >= 0.05:
        return "positive"
    elif compound <= -0.05:
        return "negative"
    return "neutral"


def analyze_comments(comments: list, analyzer: SentimentIntensityAnalyzer) -> list:
    """Analyze sentiment for a list of comments."""
    results = []
    for comment in comments:
        if not comment or comment == "[deleted]" or comment == "[removed]":
            continue
        scores = analyzer.polarity_scores(comment)
        results.append({
            "text": comment[:150] + "..." if len(comment) > 150 else comment,
            "compound": scores["compound"],
            "sentiment": classify_sentiment(scores["compound"])
        })
    return results


def process_source(source_dir: Path, source_name: str, analyzer: SentimentIntensityAnalyzer) -> dict:
    """Process all JSON files from a source directory."""
    results = {}
    
    for json_file in source_dir.glob("*.json"):
        movie = extract_movie_name(json_file.name, source_name)
        movie = normalize_movie_name(movie)
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        all_comments = []
        
        # Handle commentsByVideo structure (most files)
        if "commentsByVideo" in data:
            for video_title, comments in data.get("commentsByVideo", {}).items():
                all_comments.extend(comments)
        
        # Handle posts structure (some Reddit files)
        elif "posts" in data:
            posts = data.get("posts", {})
            # posts can be a dict with post titles as keys
            if isinstance(posts, dict):
                for post_title, post_data in posts.items():
                    if isinstance(post_data, dict) and "comments" in post_data:
                        all_comments.extend(post_data["comments"])
            # or a list of post objects
            elif isinstance(posts, list):
                for post in posts:
                    if "comments" in post:
                        all_comments.extend(post["comments"])
        
        analyzed = analyze_comments(all_comments, analyzer)
        
        if movie not in results:
            results[movie] = []
        results[movie].extend(analyzed)
    
    return results


def calculate_stats(comments: list) -> dict:
    """Calculate sentiment statistics from analyzed comments."""
    if not comments:
        return {"total": 0, "positive": 0, "negative": 0, "neutral": 0, 
                "positive_pct": 0, "negative_pct": 0, "neutral_pct": 0, "avg_compound": 0}
    
    total = len(comments)
    positive = sum(1 for c in comments if c["sentiment"] == "positive")
    negative = sum(1 for c in comments if c["sentiment"] == "negative")
    neutral = sum(1 for c in comments if c["sentiment"] == "neutral")
    avg_compound = sum(c["compound"] for c in comments) / total
    
    return {
        "total": total,
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "positive_pct": round(positive / total * 100, 1),
        "negative_pct": round(negative / total * 100, 1),
        "neutral_pct": round(neutral / total * 100, 1),
        "avg_compound": round(avg_compound, 3)
    }


def get_top_comments(comments: list, n: int = 5) -> dict:
    """Get top positive and negative comments."""
    if not comments:
        return {"positive": [], "negative": []}
    
    sorted_by_score = sorted(comments, key=lambda x: x["compound"], reverse=True)
    return {
        "positive": sorted_by_score[:n],
        "negative": sorted_by_score[-n:][::-1]
    }


def main():
    print("🎬 Sentiment Analysis - All Sources")
    print("=" * 50)
    
    script_dir = Path(__file__).parent
    youtube_dir = script_dir / "raw_data" / "results" / "youtube"
    reddit_dir = script_dir / "raw_data" / "results" / "reddit"
    
    analyzer = SentimentIntensityAnalyzer()
    
    # Process each source
    print("\n📺 Processing YouTube comments...")
    youtube_results = process_source(youtube_dir, "youtube", analyzer)
    
    print("🤖 Processing Reddit comments...")
    reddit_results = process_source(reddit_dir, "reddit", analyzer)
    
    # Build dashboard data
    dashboard_data = {
        "generated_at": __import__("datetime").datetime.now().isoformat(),
        "sources": {
            "youtube": {"stats": {}, "by_movie": {}},
            "reddit": {"stats": {}, "by_movie": {}}
        },
        "global": {"stats": {}, "by_movie": {}},
        "movies": []
    }
    
    # Get all unique movies
    all_movies = set(youtube_results.keys()) | set(reddit_results.keys())
    
    # Calculate per-movie stats
    all_global_comments = []
    all_youtube_comments = []
    all_reddit_comments = []
    
    for movie in sorted(all_movies):
        yt_comments = youtube_results.get(movie, [])
        rd_comments = reddit_results.get(movie, [])
        combined = yt_comments + rd_comments
        
        all_global_comments.extend(combined)
        all_youtube_comments.extend(yt_comments)
        all_reddit_comments.extend(rd_comments)
        
        movie_data = {
            "name": movie,
            "youtube": {
                "stats": calculate_stats(yt_comments),
                "top_comments": get_top_comments(yt_comments, 3)
            },
            "reddit": {
                "stats": calculate_stats(rd_comments),
                "top_comments": get_top_comments(rd_comments, 3)
            },
            "combined": {
                "stats": calculate_stats(combined),
                "top_comments": get_top_comments(combined, 5)
            }
        }
        dashboard_data["movies"].append(movie_data)
        
        print(f"  ✅ {movie}: {len(yt_comments)} YT + {len(rd_comments)} Reddit = {len(combined)} total")
    
    # Global stats
    dashboard_data["global"]["stats"] = calculate_stats(all_global_comments)
    dashboard_data["sources"]["youtube"]["stats"] = calculate_stats(all_youtube_comments)
    dashboard_data["sources"]["reddit"]["stats"] = calculate_stats(all_reddit_comments)
    
    # Save dashboard data
    output_file = script_dir / "sentiment_dashboard_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Dashboard data saved to: {output_file}")
    print(f"\n📊 GLOBAL SUMMARY")
    print(f"   Total comments: {dashboard_data['global']['stats']['total']}")
    print(f"   ✅ Positive: {dashboard_data['global']['stats']['positive_pct']}%")
    print(f"   ❌ Negative: {dashboard_data['global']['stats']['negative_pct']}%")
    print(f"   ➖ Neutral:  {dashboard_data['global']['stats']['neutral_pct']}%")
    print(f"   📈 Avg score: {dashboard_data['global']['stats']['avg_compound']}")


if __name__ == "__main__":
    main()
