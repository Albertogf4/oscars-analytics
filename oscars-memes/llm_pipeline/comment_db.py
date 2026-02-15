"""Database for fetching comments from sentiment analysis CSV files."""

import csv
import os
from pathlib import Path
from typing import List, Optional, Literal
from dataclasses import dataclass


@dataclass
class Comment:
    """A comment with sentiment data."""
    text: str
    full_text: str
    negative: float
    neutral: float
    positive: float
    compound: float
    sentiment: str  # "Positive", "Negative", "Neutral"


# Movie name mapping for CSV files
MOVIE_FILE_MAPPING = {
    "obaa": "One Battle After Another trailer",
    "one battle after another": "One Battle After Another trailer",
    "sinners": "Sinners movie trailer",
    "f1": "F1 movie trailer",
    "marty supreme": "Marty Supreme movie trailer",
}


class CommentDatabase:
    """Handles fetching comments from sentiment CSV files."""

    def __init__(self, data_dir: Optional[str] = None):
        """Initialize the comment database.

        Args:
            data_dir: Path to the sentiment_analyzed directory.
                     Defaults to ../oscars-analytics/sentiment_analyzed
        """
        if data_dir is None:
            # Default path relative to this file
            this_dir = Path(__file__).parent
            data_dir = this_dir.parent.parent / "oscars-analytics" / "sentiment_analyzed"
        self.data_dir = Path(data_dir)

    def _get_csv_path(self, movie: str) -> Path:
        """Get the CSV file path for a movie."""
        # Normalize movie name
        movie_lower = movie.lower().strip()

        # Check if we have a mapping
        if movie_lower in MOVIE_FILE_MAPPING:
            movie_name = MOVIE_FILE_MAPPING[movie_lower]
        else:
            movie_name = movie

        csv_path = self.data_dir / f"sentiment_results_{movie_name}.csv"

        if not csv_path.exists():
            # Try to find a matching file
            for f in self.data_dir.glob("sentiment_results_*.csv"):
                if movie_lower in f.stem.lower():
                    return f
            raise FileNotFoundError(f"No sentiment CSV found for movie: {movie}")

        return csv_path

    def _load_comments(self, movie: str) -> List[Comment]:
        """Load all comments for a movie from CSV."""
        csv_path = self._get_csv_path(movie)
        comments = []

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    comment = Comment(
                        text=row.get('comment', ''),
                        full_text=row.get('full_comment', row.get('comment', '')),
                        negative=float(row.get('negative', 0)),
                        neutral=float(row.get('neutral', 0)),
                        positive=float(row.get('positive', 0)),
                        compound=float(row.get('compound', 0)),
                        sentiment=row.get('sentiment', 'Neutral'),
                    )
                    comments.append(comment)
                except (ValueError, KeyError) as e:
                    continue  # Skip malformed rows

        return comments

    def get_negative_comments(
        self,
        movie: str,
        limit: int = 20,
        min_compound: float = -1.0,
        max_compound: float = -0.2
    ) -> List[str]:
        """Fetch most negative comments for anti-movie memes.

        Args:
            movie: Movie name
            limit: Max comments to return
            min_compound: Minimum compound score (more negative = more intense)
            max_compound: Maximum compound score (threshold for "negative")

        Returns:
            List of comment texts
        """
        comments = self._load_comments(movie)

        # Filter by compound score range
        negative = [
            c for c in comments
            if min_compound <= c.compound <= max_compound
        ]

        # Sort by most negative first (lowest compound)
        negative.sort(key=lambda c: c.compound)

        # Return text only
        return [c.full_text for c in negative[:limit]]

    def get_positive_comments(
        self,
        movie: str,
        limit: int = 20,
        min_compound: float = 0.3,
        max_compound: float = 1.0
    ) -> List[str]:
        """Fetch most positive comments for pro-movie memes.

        Args:
            movie: Movie name
            limit: Max comments to return
            min_compound: Minimum compound score (threshold for "positive")
            max_compound: Maximum compound score

        Returns:
            List of comment texts
        """
        comments = self._load_comments(movie)

        # Filter by compound score range
        positive = [
            c for c in comments
            if min_compound <= c.compound <= max_compound
        ]

        # Sort by most positive first (highest compound)
        positive.sort(key=lambda c: c.compound, reverse=True)

        # Return text only
        return [c.full_text for c in positive[:limit]]

    def get_controversial_comments(
        self,
        movie: str,
        limit: int = 10
    ) -> List[str]:
        """Fetch comments with strong opinions (high positive or high negative).

        These are comments with extreme sentiment scores in either direction.
        """
        comments = self._load_comments(movie)

        # Sort by absolute compound value (most extreme opinions)
        comments.sort(key=lambda c: abs(c.compound), reverse=True)

        return [c.full_text for c in comments[:limit]]

    def get_theme_comments(
        self,
        movie: str,
        theme: str,
        sentiment: Literal["positive", "negative", "any"] = "any",
        limit: int = 10
    ) -> List[str]:
        """Fetch comments mentioning specific themes.

        Args:
            movie: Movie name
            theme: Keyword to search for (e.g., "oscar", "acting", "boring")
            sentiment: Filter by sentiment type
            limit: Max comments to return
        """
        comments = self._load_comments(movie)

        # Filter by theme keyword
        theme_lower = theme.lower()
        themed = [c for c in comments if theme_lower in c.full_text.lower()]

        # Filter by sentiment if specified
        if sentiment == "positive":
            themed = [c for c in themed if c.compound > 0.2]
        elif sentiment == "negative":
            themed = [c for c in themed if c.compound < -0.2]

        return [c.full_text for c in themed[:limit]]

    def get_comment_stats(self, movie: str) -> dict:
        """Get sentiment statistics for a movie."""
        comments = self._load_comments(movie)

        if not comments:
            return {"total": 0}

        compounds = [c.compound for c in comments]

        return {
            "total": len(comments),
            "avg_compound": sum(compounds) / len(compounds),
            "positive_count": sum(1 for c in comments if c.sentiment == "Positive"),
            "negative_count": sum(1 for c in comments if c.sentiment == "Negative"),
            "neutral_count": sum(1 for c in comments if c.sentiment == "Neutral"),
            "most_positive": max(compounds),
            "most_negative": min(compounds),
        }

    def get_all_comments(
        self,
        movie: str,
        sentiment: Optional[Literal["positive", "negative", "neutral"]] = None
    ) -> List[Comment]:
        """Get all comments for a movie, optionally filtered by sentiment."""
        comments = self._load_comments(movie)

        if sentiment:
            sentiment_map = {
                "positive": "Positive",
                "negative": "Negative",
                "neutral": "Neutral"
            }
            target = sentiment_map.get(sentiment.lower(), sentiment)
            comments = [c for c in comments if c.sentiment == target]

        return comments

    def extract_key_themes(self, movie: str, top_n: int = 5) -> List[str]:
        """Extract key themes from comments using simple keyword frequency.

        Returns common themes found in the comments.
        """
        # Common film-related keywords to look for
        theme_keywords = [
            "oscar", "acting", "boring", "amazing", "overrated", "underrated",
            "cinematography", "directing", "script", "story", "plot", "music",
            "score", "hype", "expectations", "trailer", "masterpiece", "mid",
            "peak", "kino", "cinema", "nominated", "award", "performance",
            "visual", "effects", "slow", "fast", "emotional", "predictable"
        ]

        comments = self._load_comments(movie)
        all_text = " ".join(c.full_text.lower() for c in comments)

        # Count occurrences
        theme_counts = {}
        for theme in theme_keywords:
            count = all_text.count(theme)
            if count > 0:
                theme_counts[theme] = count

        # Sort by frequency
        sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)

        return [theme for theme, _ in sorted_themes[:top_n]]
