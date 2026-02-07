"""
Movie Sentiment Comparison
Aggregates and compares sentiment analysis results across multiple movies for visualization.
"""

import pandas as pd
from pathlib import Path
import json


def load_all_results(sentiment_dir: Path) -> dict[str, pd.DataFrame]:
    """Load all sentiment result CSVs from sentiment_analyzed directory."""
    results = {}
    for csv_file in sentiment_dir.glob("sentiment_results_*.csv"):
        # Extract movie name from filename
        movie_name = csv_file.stem.replace("sentiment_results_", "")
        results[movie_name] = pd.read_csv(csv_file)
    return results


def calculate_movie_stats(df: pd.DataFrame) -> dict:
    """Calculate key statistics for a movie's comments."""
    total = len(df)
    
    positive = len(df[df['sentiment'] == 'Positive'])
    negative = len(df[df['sentiment'] == 'Negative'])
    neutral = len(df[df['sentiment'] == 'Neutral'])
    
    return {
        'total_comments': total,
        'positive_count': positive,
        'negative_count': negative,
        'neutral_count': neutral,
        'positive_pct': round(positive / total * 100, 1) if total > 0 else 0,
        'negative_pct': round(negative / total * 100, 1) if total > 0 else 0,
        'neutral_pct': round(neutral / total * 100, 1) if total > 0 else 0,
        'avg_compound': round(df['compound'].mean(), 3),
        'median_compound': round(df['compound'].median(), 3),
        'std_compound': round(df['compound'].std(), 3),
        'min_compound': round(df['compound'].min(), 3),
        'max_compound': round(df['compound'].max(), 3),
    }


def create_comparison_dataframe(all_results: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Create a comparison DataFrame with stats for each movie."""
    comparison_data = []
    
    for movie_name, df in all_results.items():
        stats = calculate_movie_stats(df)
        stats['movie'] = movie_name
        comparison_data.append(stats)
    
    # Create DataFrame and reorder columns
    comparison_df = pd.DataFrame(comparison_data)
    cols = ['movie', 'total_comments', 
            'positive_count', 'negative_count', 'neutral_count',
            'positive_pct', 'negative_pct', 'neutral_pct',
            'avg_compound', 'median_compound', 'std_compound',
            'min_compound', 'max_compound']
    
    return comparison_df[cols].sort_values('avg_compound', ascending=False)


def create_visualization_data(comparison_df: pd.DataFrame) -> dict:
    """Create a JSON structure optimized for visualization libraries."""
    return {
        'movies': comparison_df['movie'].tolist(),
        'metrics': {
            'total_comments': comparison_df['total_comments'].tolist(),
            'positive_pct': comparison_df['positive_pct'].tolist(),
            'negative_pct': comparison_df['negative_pct'].tolist(),
            'neutral_pct': comparison_df['neutral_pct'].tolist(),
            'avg_compound': comparison_df['avg_compound'].tolist(),
        },
        'sentiment_distribution': [
            {
                'movie': row['movie'],
                'Positive': row['positive_pct'],
                'Negative': row['negative_pct'],
                'Neutral': row['neutral_pct']
            }
            for _, row in comparison_df.iterrows()
        ],
        'rankings': {
            'by_positivity': comparison_df.sort_values('positive_pct', ascending=False)['movie'].tolist(),
            'by_avg_compound': comparison_df.sort_values('avg_compound', ascending=False)['movie'].tolist(),
            'by_engagement': comparison_df.sort_values('total_comments', ascending=False)['movie'].tolist(),
        }
    }


def print_comparison_report(comparison_df: pd.DataFrame):
    """Print a formatted comparison report."""
    print("\n" + "="*80)
    print("📊 MOVIE SENTIMENT COMPARISON")
    print("="*80)
    
    print("\n🎬 Overall Rankings (by Average Compound Score):\n")
    for i, (_, row) in enumerate(comparison_df.iterrows(), 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        print(f"  {emoji} {i}. {row['movie']}")
        print(f"       Avg Score: {row['avg_compound']:.3f} | "
              f"✅ {row['positive_pct']}% | ❌ {row['negative_pct']}% | ➖ {row['neutral_pct']}%")
        print(f"       Total Comments: {row['total_comments']}")
        print()
    
    # Quick insights
    print("\n" + "-"*80)
    print("💡 KEY INSIGHTS")
    print("-"*80)
    
    most_positive = comparison_df.loc[comparison_df['positive_pct'].idxmax()]
    most_negative = comparison_df.loc[comparison_df['negative_pct'].idxmax()]
    most_engagement = comparison_df.loc[comparison_df['total_comments'].idxmax()]
    
    print(f"\n  🌟 Most Positive Reception: {most_positive['movie']} ({most_positive['positive_pct']}% positive)")
    print(f"  💔 Most Controversial: {most_negative['movie']} ({most_negative['negative_pct']}% negative)")
    print(f"  🔥 Most Engagement: {most_engagement['movie']} ({most_engagement['total_comments']} comments)")


def main():
    # Get directory where this script is located
    script_dir = Path(__file__).parent
    sentiment_dir = script_dir / "sentiment_analyzed"
    
    print("📂 Loading sentiment results...")
    all_results = load_all_results(sentiment_dir)
    
    if not all_results:
        print("❌ No sentiment result files found in sentiment_analyzed/!")
        return
    
    print(f"✅ Found {len(all_results)} movie(s) to compare:")
    for movie in all_results.keys():
        print(f"   - {movie}")
    
    # Create comparison DataFrame
    comparison_df = create_comparison_dataframe(all_results)
    
    # Print report
    print_comparison_report(comparison_df)
    
    # Export comparison CSV to sentiment_analyzed
    csv_path = sentiment_dir / "movie_comparison.csv"
    comparison_df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"\n💾 Comparison CSV exported to: {csv_path}")
    
    # Export visualization-ready JSON to sentiment_analyzed
    viz_data = create_visualization_data(comparison_df)
    json_path = sentiment_dir / "movie_comparison.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(viz_data, f, indent=2, ensure_ascii=False)
    print(f"💾 Visualization JSON exported to: {json_path}")


if __name__ == "__main__":
    main()
