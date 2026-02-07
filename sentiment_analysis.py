"""
VADER Sentiment Analysis for Movie Trailer Comments
Analyzes comments from "One Battle After Another" trailer using NLTK's VADER engine.
"""

import json
from pathlib import Path
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd


def load_comments(file_path: str) -> dict:
    """Load comments from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_sentiment(comments: list[str], analyzer: SentimentIntensityAnalyzer) -> list[dict]:
    """
    Analyze sentiment of each comment using VADER.
    
    Returns a list of dictionaries with comment text and sentiment scores.
    """
    results = []
    for comment in comments:
        scores = analyzer.polarity_scores(comment)
        sentiment_label = classify_sentiment(scores['compound'])
        results.append({
            'comment': comment[:100] + '...' if len(comment) > 100 else comment,
            'full_comment': comment,
            'negative': scores['neg'],
            'neutral': scores['neu'],
            'positive': scores['pos'],
            'compound': scores['compound'],
            'sentiment': sentiment_label
        })
    return results


def classify_sentiment(compound_score: float) -> str:
    """
    Classify sentiment based on compound score.
    
    VADER compound score thresholds:
    - Positive: compound >= 0.05
    - Negative: compound <= -0.05
    - Neutral: -0.05 < compound < 0.05
    """
    if compound_score >= 0.05:
        return 'Positive'
    elif compound_score <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'


def generate_summary(results: list[dict]) -> dict:
    """Generate summary statistics for sentiment analysis results."""
    total = len(results)
    if total == 0:
        return {'total': 0, 'positive': 0, 'negative': 0, 'neutral': 0}
    
    positive = sum(1 for r in results if r['sentiment'] == 'Positive')
    negative = sum(1 for r in results if r['sentiment'] == 'Negative')
    neutral = sum(1 for r in results if r['sentiment'] == 'Neutral')
    
    avg_compound = sum(r['compound'] for r in results) / total
    
    return {
        'total': total,
        'positive': positive,
        'negative': negative,
        'neutral': neutral,
        'positive_pct': round(positive / total * 100, 1),
        'negative_pct': round(negative / total * 100, 1),
        'neutral_pct': round(neutral / total * 100, 1),
        'avg_compound': round(avg_compound, 3)
    }


def print_summary(video_title: str, summary: dict):
    """Print a formatted summary for a video's comments."""
    print(f"\n{'='*80}")
    print(f"Video: {video_title[:70]}...")
    print(f"{'='*80}")
    print(f"Total Comments: {summary['total']}")
    print(f"  ✅ Positive: {summary['positive']} ({summary['positive_pct']}%)")
    print(f"  ❌ Negative: {summary['negative']} ({summary['negative_pct']}%)")
    print(f"  ➖ Neutral:  {summary['neutral']} ({summary['neutral_pct']}%)")
    print(f"  📊 Average Compound Score: {summary['avg_compound']}")


def print_top_comments(results: list[dict], n: int = 5):
    """Print top positive and negative comments."""
    sorted_results = sorted(results, key=lambda x: x['compound'], reverse=True)
    
    print(f"\n  🌟 Top {n} Most Positive Comments:")
    for i, r in enumerate(sorted_results[:n], 1):
        print(f"    {i}. [{r['compound']:.3f}] {r['comment']}")
    
    print(f"\n  💔 Top {n} Most Negative Comments:")
    for i, r in enumerate(sorted_results[-n:][::-1], 1):
        print(f"    {i}. [{r['compound']:.3f}] {r['comment']}")

def sanitize_filename(name: str) -> str:
    """Remove or replace characters that are invalid in filenames."""
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name.strip()


def main(comments_file: str):
    """
    Analyze sentiment for comments in a JSON file.
    
    Args:
        comments_file: Path to the JSON file containing comments.
    """
    # Initialize VADER analyzer
    analyzer = SentimentIntensityAnalyzer()
    
    # Load comments
    print("📂 Loading comments...")
    data = load_comments(comments_file)
    
    # Extract movie name from query for file naming
    movie_name = sanitize_filename(data['query'])
    
    print(f"\n🎬 Analyzing comments for: {data['query']}")
    print(f"📅 Fetched at: {data['fetchedAt']}")
    print(f"📊 Total comments: {data['totalComments']}")
    print(f"🎥 Number of videos: {data['videoCount']}")
    
    # Analyze comments for each video
    all_results = []
    video_summaries = {}
    
    for video_title, comments in data['commentsByVideo'].items():
        results = analyze_sentiment(comments, analyzer)
        all_results.extend(results)
        summary = generate_summary(results)
        video_summaries[video_title] = summary
        
        print_summary(video_title, summary)
        print_top_comments(results)
    
    # Overall summary
    print("\n" + "="*80)
    print("📈 OVERALL SENTIMENT ANALYSIS")
    print("="*80)
    
    overall_summary = generate_summary(all_results)
    print(f"Total Comments Analyzed: {overall_summary['total']}")
    print(f"  ✅ Positive: {overall_summary['positive']} ({overall_summary['positive_pct']}%)")
    print(f"  ❌ Negative: {overall_summary['negative']} ({overall_summary['negative_pct']}%)")
    print(f"  ➖ Neutral:  {overall_summary['neutral']} ({overall_summary['neutral_pct']}%)")
    print(f"  📊 Average Compound Score: {overall_summary['avg_compound']}")
    
    # Export to CSV with movie name
    output_dir = Path(__file__).parent / "sentiment_analyzed"
    output_dir.mkdir(exist_ok=True)
    df = pd.DataFrame(all_results)
    csv_path = output_dir / f"sentiment_results_{movie_name}.csv"
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"\n💾 Results exported to: {csv_path}")
    
    # Create summary DataFrame
    summary_data = []
    for video, summary in video_summaries.items():
        summary_data.append({
            'video': video[:50] + '...' if len(video) > 50 else video,
            **summary
        })
    summary_df = pd.DataFrame(summary_data)
    summary_csv_path = output_dir / f"sentiment_summary_{movie_name}.csv"
    summary_df.to_csv(summary_csv_path, index=False, encoding='utf-8')
    print(f"💾 Summary exported to: {summary_csv_path}")


if __name__ == "__main__":
    import glob
    
    # Get directory where this script is located
    script_dir = Path(__file__).parent
    raw_data_dir = script_dir / "raw_data"
    
    # Find all JSON files in the raw_data directory
    json_files = list(raw_data_dir.glob("comments_*.json"))
    
    if not json_files:
        print("❌ No JSON files found matching 'comments_*.json' pattern")
    else:
        print(f"🔍 Found {len(json_files)} JSON file(s) to process:\n")
        for json_file in json_files:
            print(f"  - {json_file.name}")
        
        print("\n" + "="*80)
        
        # Process each JSON file
        for json_file in json_files:
            print(f"\n\n{'#'*80}")
            print(f"# Processing: {json_file.name}")
            print(f"{'#'*80}")
            main(str(json_file))
