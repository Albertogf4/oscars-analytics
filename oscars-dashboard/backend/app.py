"""FastAPI server for Oscar Markets Dashboard."""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timezone
from typing import List

from models import (
    ComparisonResponse,
    MovieComparison,
    MovieMetrics,
    Market,
    HeadToHead,
    HeadToHeadMarket,
    HealthResponse,
)

# Load meme and template routes first (before Kalshi)
from meme_routes import router as meme_router
from template_routes import router as template_router

# Kalshi client loaded after memes/templates
from kalshi_client import (
    fetch_all_oscar_markets,
    calculate_metrics,
    get_key_odds,
    build_head_to_head,
    clear_cache,
)

app = FastAPI(
    title="Oscar Markets Dashboard API",
    description="Real-time Oscar prediction market data from Kalshi",
    version="1.0.0",
)

# Include routers
app.include_router(meme_router)
app.include_router(template_router)

# Mount static files for generated memes
MEMES_DIR = Path(__file__).parent.parent.parent / "oscars-memes" / "generated"
if MEMES_DIR.exists():
    app.mount("/memes", StaticFiles(directory=str(MEMES_DIR)), name="memes")

# Mount static files for template images
TEMPLATES_DIR = Path(__file__).parent.parent.parent / "MemeTemplate"
if TEMPLATES_DIR.exists():
    app.mount("/templates", StaticFiles(directory=str(TEMPLATES_DIR)), name="templates")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
    )


@app.get("/api/comparison", response_model=ComparisonResponse)
async def get_comparison():
    """Get full comparison data for all movies."""
    try:
        data = fetch_all_oscar_markets()
        movies_data = data["movies"]

        movies = []
        for movie_name, movie_info in movies_data.items():
            markets = movie_info["markets"]
            metrics = calculate_metrics(markets)

            movie = MovieComparison(
                name=movie_name,
                director=movie_info["director"],
                year=movie_info["year"],
                markets=[
                    Market(
                        ticker=m["ticker"],
                        title=m["title"],
                        subtitle=m.get("subtitle"),
                        category=m["category"],
                        yes_price=m.get("yes_price") or 0,
                        yes_bid=m.get("yes_bid"),
                        no_price=m.get("no_price"),
                        volume=m.get("volume", 0),
                        volume_24h=m.get("volume_24h"),
                        open_interest=m.get("open_interest"),
                        matched_keywords=m.get("matched_keywords", []),
                    )
                    for m in markets
                ],
                metrics=MovieMetrics(**metrics),
                best_picture_odds=get_key_odds(markets, "Best Picture"),
                best_director_odds=get_key_odds(markets, "Best Director"),
                best_actor_odds=get_key_odds(markets, "Best Actor"),
                best_actress_odds=get_key_odds(markets, "Best Actress"),
            )
            movies.append(movie)

        # Sort by average price (overall odds)
        movies.sort(key=lambda x: x.metrics.avg_yes_price, reverse=True)

        # Build head-to-head comparisons
        h2h_data = build_head_to_head(movies_data)
        head_to_head = [
            HeadToHead(
                category=h["category"],
                leader=h["leader"],
                markets={
                    name: HeadToHeadMarket(**market_data)
                    for name, market_data in h["markets"].items()
                },
            )
            for h in h2h_data
        ]

        return ComparisonResponse(
            timestamp=datetime.now(timezone.utc),
            movies=movies,
            head_to_head=head_to_head,
            summary={
                "total_markets_scanned": data["total_markets_scanned"],
                "movies_analyzed": len(movies),
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/movie/{movie_name}")
async def get_movie(movie_name: str):
    """Get detailed data for a specific movie."""
    try:
        data = fetch_all_oscar_markets()
        movies_data = data["movies"]

        if movie_name not in movies_data:
            raise HTTPException(status_code=404, detail=f"Movie '{movie_name}' not found")

        movie_info = movies_data[movie_name]
        markets = movie_info["markets"]
        metrics = calculate_metrics(markets)

        return {
            "name": movie_name,
            "director": movie_info["director"],
            "year": movie_info["year"],
            "markets": markets,
            "metrics": metrics,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/refresh")
async def refresh_data():
    """Force refresh of cached data."""
    clear_cache()
    return {"status": "cache cleared", "timestamp": datetime.now(timezone.utc).isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
