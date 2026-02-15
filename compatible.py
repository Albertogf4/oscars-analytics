"""
Campaign validation on top of VADER results (YouTube/Reddit comments)
- Works with your JSON schema: { query, commentsByVideo{title:[comments...]}, ... }
- Produces: per-video and per-movie indices for campaign hypotheses + basic significance checks

Install (if missing):
pip install pandas scipy vaderSentiment
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Optional: significance tests
try:
    from scipy.stats import ttest_ind, mannwhitneyu
    SCIPY_OK = True
except Exception:
    SCIPY_OK = False


# -----------------------------
# 1) Keyword dictionaries (tweak freely)
# -----------------------------
KEYWORDS = {
    # Watch/Buy intent: supports campaign "accessible/event/heart"
    "intent_watch": [
        "i'm in", "im in", "i am in", "must watch", "need to watch", "can't wait", "cant wait",
        "so hyped", "hyped", "i will watch", "going to watch", "see it", "watch this",
        "opening night", "buy tickets", "ticket", "cinema", "theater", "theatre", "imax", "70mm"
    ],
    # Craft / spectacle: supports "Craft as Spectacle"
    "craft": [
        "cinematography", "shot", "shots", "camera", "lens", "lighting", "framing", "composition",
        "vfx", "visuals", "color grading", "sound design", "mix", "editing", "cut", "montage",
        "production design", "set design", "vistas", "format", "film", "35mm", "70mm", "imax", "vistavision"
    ],
    # Music / score: supports "Greenwood listening experience"
    "music": [
        "score", "soundtrack", "music", "theme", "jonny greenwood", "greenwood", "composition",
        "orchestra", "strings", "sound"
    ],
    # Performance: supports "Performance spotlight"
    "performance": [
        "acting", "performance", "cast", "actor", "actress",
        "dicaprio", "leonardo", "leo", "sean penn", "penn",
        "teyana", "taylor", "benicio", "del toro"
    ],
    # Heart / father-daughter / family: supports "Heart of the chase"
    "family": [
        "father", "dad", "daughter", "family", "parent", "kid", "child", "protect", "relationship",
        "emotional", "heart", "cry", "tears", "made me cry"
    ],
    # Confusion / friction: supports "PTA but entertaining" (reduce confusion)
    "confusion": [
        "confusing", "what is this", "i don't get it", "dont get it", "don't get it", "no idea",
        "makes no sense", "lost", "weird", "wtf", "huh", "hard to follow", "complicated"
    ],
    # Toxicity / risk (helps decide moderation + messaging)
    "toxicity": [
        "trash", "garbage", "woke", "propaganda", "boycott", "stupid", "idiot", "hate", "ruined",
        "worst", "cringe"
    ],
}

# Simple regex normalizer for keyword search
_WORD_RE = re.compile(r"[^a-z0-9\s']+")


def normalize_text(s: str) -> str:
    s = s.lower()
    s = _WORD_RE.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def contains_any(text: str, phrases: List[str]) -> int:
    """
    Returns 1 if any phrase appears as substring in normalized text, else 0.
    (Substring is OK because many phrases contain spaces.)
    """
    t = normalize_text(text)
    return int(any(p in t for p in phrases))


# -----------------------------
# 2) Load JSON to DataFrame
# -----------------------------
def load_comments_json(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def json_to_df(data: dict, source: str = "youtube") -> pd.DataFrame:
    """
    Creates one row per comment with fields:
    movie, video_title, source, comment
    """
    movie = data.get("query", "UNKNOWN_MOVIE")
    rows = []
    for video_title, comments in data.get("commentsByVideo", {}).items():
        for c in comments:
            if not isinstance(c, str):
                continue
            rows.append(
                {
                    "movie": movie,
                    "video_title": video_title,
                    "source": source,
                    "comment": c,
                }
            )
    return pd.DataFrame(rows)


# -----------------------------
# 3) VADER + campaign indices
# -----------------------------
def add_vader(df: pd.DataFrame, analyzer: Optional[SentimentIntensityAnalyzer] = None) -> pd.DataFrame:
    analyzer = analyzer or SentimentIntensityAnalyzer()
    scores = df["comment"].apply(analyzer.polarity_scores)
    df = df.copy()
    df["neg"] = scores.apply(lambda d: d["neg"])
    df["neu"] = scores.apply(lambda d: d["neu"])
    df["pos"] = scores.apply(lambda d: d["pos"])
    df["compound"] = scores.apply(lambda d: d["compound"])
    df["sentiment"] = pd.cut(
        df["compound"],
        bins=[-1.0001, -0.05, 0.05, 1.0001],
        labels=["Negative", "Neutral", "Positive"],
    )
    return df


def add_campaign_flags(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for k, phrases in KEYWORDS.items():
        df[f"kw_{k}"] = df["comment"].apply(lambda x: contains_any(x, phrases))
    return df


# -----------------------------
# 4) Aggregations and tests
# -----------------------------
@dataclass
class CampaignScoreConfig:
    """
    Weights to produce a prioritization score per campaign.
    You can tune weights for your deck narrative.
    """
    w_sentiment: float = 0.35
    w_intent: float = 0.25
    w_signal: float = 0.25
    w_friction: float = 0.15  # subtract confusion/toxicity


def agg_metrics(df: pd.DataFrame, level: str = "video") -> pd.DataFrame:
    """
    level: "video" => group by movie + video_title (+source)
           "movie" => group by movie (+source)
    Returns rates and averages.
    """
    group_cols = ["movie", "source"]
    if level == "video":
        group_cols = ["movie", "video_title", "source"]

    agg = df.groupby(group_cols).agg(
        n=("comment", "size"),
        avg_compound=("compound", "mean"),
        pos_rate=("sentiment", lambda s: (s == "Positive").mean()),
        neg_rate=("sentiment", lambda s: (s == "Negative").mean()),
        neu_rate=("sentiment", lambda s: (s == "Neutral").mean()),
        intent_rate=("kw_intent_watch", "mean"),
        craft_rate=("kw_craft", "mean"),
        music_rate=("kw_music", "mean"),
        perf_rate=("kw_performance", "mean"),
        family_rate=("kw_family", "mean"),
        confusion_rate=("kw_confusion", "mean"),
        toxicity_rate=("kw_toxicity", "mean"),
    ).reset_index()

    # Make nicer percent columns
    for c in [
        "pos_rate", "neg_rate", "neu_rate",
        "intent_rate", "craft_rate", "music_rate",
        "perf_rate", "family_rate", "confusion_rate", "toxicity_rate"
    ]:
        agg[c] = (agg[c] * 100).round(2)

    agg["avg_compound"] = agg["avg_compound"].round(3)
    return agg


def significance_compare(
    df: pd.DataFrame,
    movie_a: str,
    movie_b: str,
    metric: str = "compound",
    source: Optional[str] = None,
) -> Dict[str, float]:
    """
    Compare two movies on a metric using t-test and Mann-Whitney U (if scipy available).
    Returns p-values and effect size (Cohen's d) where possible.
    """
    sub = df
    if source is not None:
        sub = sub[sub["source"] == source]

    a = sub[sub["movie"] == movie_a][metric].dropna().values
    b = sub[sub["movie"] == movie_b][metric].dropna().values

    out = {"n_a": len(a), "n_b": len(b)}
    if len(a) < 20 or len(b) < 20:
        out["warning"] = "Sample too small for reliable inference (<20 per group)."
        return out

    # Effect size: Cohen's d
    import numpy as np
    pooled = np.sqrt(((a.var(ddof=1) + b.var(ddof=1)) / 2))
    out["cohens_d"] = float((a.mean() - b.mean()) / pooled) if pooled > 0 else 0.0

    if SCIPY_OK:
        out["p_ttest"] = float(ttest_ind(a, b, equal_var=False).pvalue)
        out["p_mannwhitneyu"] = float(mannwhitneyu(a, b, alternative="two-sided").pvalue)
    else:
        out["warning"] = "scipy not installed; no p-values computed."

    return out


def campaign_prioritization(movie_metrics: pd.DataFrame, cfg: CampaignScoreConfig = CampaignScoreConfig()) -> pd.DataFrame:
    """
    Produces one row per movie with scores for each campaign hypothesis.
    Scores are 0-100-ish (not strict), higher = better fit.
    """
    m = movie_metrics.copy()

    # normalize some columns roughly to 0-1 in a stable way
    # avg_compound in [-1,1] => map to [0,1]
    m["sent_norm"] = (m["avg_compound"] + 1) / 2

    # rates are in percent already
    for col in ["intent_rate", "craft_rate", "music_rate", "perf_rate", "family_rate", "confusion_rate", "toxicity_rate"]:
        m[col + "_n"] = (m[col] / 100.0).clip(0, 1)

    # Campaign scores: sentiment + intent + signal - friction
    def score(signal_col, friction_cols=("confusion_rate_n", "toxicity_rate_n")):
        friction = sum(m[c] for c in friction_cols) / len(friction_cols)
        return (
            cfg.w_sentiment * m["sent_norm"]
            + cfg.w_intent * m["intent_rate_n"]
            + cfg.w_signal * m[signal_col]
            - cfg.w_friction * friction
        )

    # Define campaigns
    m["score_heart_family"] = (score("family_rate_n") * 100).round(2)
    m["score_craft_event"] = (score("craft_rate_n") * 100).round(2)
    m["score_music_listening"] = (score("music_rate_n") * 100).round(2)
    m["score_performance_spotlight"] = (score("perf_rate_n") * 100).round(2)

    # Confusion reduction campaign: we want high sentiment & intent but ALSO high confusion to justify this angle
    m["score_reduce_confusion"] = (
        (
            0.45 * m["sent_norm"]
            + 0.25 * m["intent_rate_n"]
            + 0.30 * m["confusion_rate_n"]  # high confusion => more need
            - 0.10 * m["toxicity_rate_n"]
        ) * 100
    ).round(2)

    # Keep only relevant columns
    keep = ["movie", "source", "n", "avg_compound",
            "pos_rate", "neg_rate", "intent_rate",
            "family_rate", "craft_rate", "music_rate", "perf_rate",
            "confusion_rate", "toxicity_rate",
            "score_heart_family", "score_craft_event", "score_music_listening",
            "score_performance_spotlight", "score_reduce_confusion"]
    return m[keep].sort_values(["source", "score_craft_event"], ascending=[True, False])


# -----------------------------
# 5) End-to-end runner
# -----------------------------
def run_validation(
    youtube_json_dir: str,
    reddit_json_dir: Optional[str] = None,
    out_dir: str = "campaign_validation_out"
):
    """
    Reads all comments_*.json and reddit_*.json files from dirs, computes metrics and exports CSVs.
    - If reddit_json_dir is provided, assumes same JSON schema.
    """
    analyzer = SentimentIntensityAnalyzer()

    def load_dir(dir_path: str, source_name: str, pattern: str = "comments_*.json") -> pd.DataFrame:
        p = Path(dir_path)
        files = sorted(p.glob(pattern))
        if not files:
            print(f"⚠️ No files found in {dir_path} with pattern {pattern}")
            return pd.DataFrame(columns=["movie","video_title","source","comment"])
        dfs = []
        for f in files:
            print(f"📂 Loading {f.name}...")
            data = load_comments_json(str(f))
            dfs.append(json_to_df(data, source=source_name))
        return pd.concat(dfs, ignore_index=True)

    df_y = load_dir(youtube_json_dir, "youtube", pattern="comments_*.json")
    df_all = df_y

    if reddit_json_dir:
        df_r = load_dir(reddit_json_dir, "reddit", pattern="reddit_*.json")
        df_all = pd.concat([df_y, df_r], ignore_index=True)

    if df_all.empty:
        print("❌ No comments loaded. Exiting.")
        return

    print(f"\n✅ Loaded comments: {len(df_all):,} rows (sources: {df_all['source'].unique().tolist()})")
    print(f"   Movies: {df_all['movie'].unique().tolist()}")

    df_all = add_vader(df_all, analyzer=analyzer)
    df_all = add_campaign_flags(df_all)

    # Aggregations
    video_metrics = agg_metrics(df_all, level="video")
    movie_metrics = agg_metrics(df_all, level="movie")

    # Campaign prioritization
    prio = campaign_prioritization(movie_metrics)

    # Export
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    df_all.to_csv(out / "comments_scored_all.csv", index=False, encoding="utf-8")
    video_metrics.to_csv(out / "video_metrics.csv", index=False, encoding="utf-8")
    movie_metrics.to_csv(out / "movie_metrics.csv", index=False, encoding="utf-8")
    prio.to_csv(out / "campaign_prioritization.csv", index=False, encoding="utf-8")

    print(f"\n💾 Exported:\n- {out/'comments_scored_all.csv'}\n- {out/'video_metrics.csv'}\n- {out/'movie_metrics.csv'}\n- {out/'campaign_prioritization.csv'}")

    # Quick console view: Top campaigns per source
    for src in prio["source"].unique():
        sub = prio[prio["source"] == src].copy()
        print("\n" + "="*80)
        print(f"🏁 Top campaigns (source={src})")
        print("="*80)

        # For each movie, show its best campaign
        campaigns = [
            "score_heart_family",
            "score_craft_event",
            "score_music_listening",
            "score_performance_spotlight",
            "score_reduce_confusion",
        ]
        sub["best_campaign"] = sub[campaigns].idxmax(axis=1)
        sub["best_score"] = sub[campaigns].max(axis=1)
        show = sub.sort_values("best_score", ascending=False)[["movie","n","avg_compound","intent_rate","confusion_rate","best_campaign","best_score"]]
        print(show.to_string(index=False))

    return {
        "df_all": df_all,
        "video_metrics": video_metrics,
        "movie_metrics": movie_metrics,
        "prioritization": prio
    }


# -----------------------------
# 6) Optional: pairwise comparison helper
# -----------------------------
def compare_one_movie_vs_rest(df_all: pd.DataFrame, target_movie: str, metric: str = "compound", source: Optional[str] = None) -> pd.DataFrame:
    """
    Compare target movie vs each other movie on a metric.
    Returns p-values/effect sizes (if scipy installed) or warnings.
    """
    others = sorted([m for m in df_all["movie"].unique() if m != target_movie])
    rows = []
    for m in others:
        rows.append({
            "target": target_movie,
            "other": m,
            **significance_compare(df_all, target_movie, m, metric=metric, source=source)
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    # Example usage:
    # 1) Only YouTube:
    # run_validation(youtube_json_dir="raw_data_youtube")
    #
    # 2) YouTube + Reddit:
    # run_validation(youtube_json_dir="raw_data_youtube", reddit_json_dir="raw_data_reddit")

    # EDIT THESE PATHS:
    run_validation(
        youtube_json_dir="raw_data/results/youtube",      # your current folder name for youtube JSONs
        reddit_json_dir="raw_data/results/reddit",             # put your reddit folder path here if you have it
        out_dir="campaign_validation_out"
    )
