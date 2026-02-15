"""Pydantic models for Oscar Markets Dashboard API."""

from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime


class Market(BaseModel):
    """Individual prediction market."""
    ticker: str
    title: str
    subtitle: Optional[str] = None
    category: str
    yes_price: int  # cents (0-100)
    yes_bid: Optional[int] = None
    no_price: Optional[int] = None
    volume: int
    volume_24h: Optional[int] = None
    open_interest: Optional[int] = None
    matched_keywords: List[str] = []


class MovieMetrics(BaseModel):
    """Aggregate metrics for a movie."""
    total_markets: int
    avg_yes_price: float
    total_volume: int
    total_open_interest: int
    categories: List[str]


class MovieComparison(BaseModel):
    """Complete movie data with markets and metrics."""
    name: str
    director: str
    year: int
    markets: List[Market]
    metrics: MovieMetrics
    best_picture_odds: Optional[int] = None
    best_director_odds: Optional[int] = None
    best_actor_odds: Optional[int] = None
    best_actress_odds: Optional[int] = None


class HeadToHeadMarket(BaseModel):
    """Market data for head-to-head comparison."""
    price: int
    volume: int
    ticker: str


class HeadToHead(BaseModel):
    """Head-to-head comparison for a category."""
    category: str
    leader: str
    markets: Dict[str, HeadToHeadMarket]


class ComparisonResponse(BaseModel):
    """Full comparison API response."""
    timestamp: datetime
    movies: List[MovieComparison]
    head_to_head: List[HeadToHead]
    summary: Dict


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
