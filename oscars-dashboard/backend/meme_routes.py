"""FastAPI routes for meme generation and listing."""

import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Literal

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query

# Load environment variables from .env file
load_dotenv()

from meme_models import (
    MemeTemplate,
    GeneratedMemeResponse,
    MemeListResponse,
    TemplateListResponse,
    GenerateMemeRequest,
    GenerateMemeResponse,
    CommentPreview,
    CommentListResponse,
)

# Add oscars-memes to path for imports
MEMES_DIR = Path(__file__).parent.parent.parent / "oscars-memes"
sys.path.insert(0, str(MEMES_DIR))

from llm_pipeline import MEME_TEMPLATES, CommentDatabase, MemeGenerationPipeline
from llm_pipeline.generator import render_memes_by_category

# Paths
GENERATED_DIR = MEMES_DIR / "generated"

router = APIRouter(prefix="/api/memes", tags=["memes"])


# Initialize comment database
comment_db = CommentDatabase(
    data_dir=Path(__file__).parent.parent.parent / "oscars-analytics" / "sentiment_analyzed"
)


# Mock LLM client for fallback when OpenAI is not available
class MockLLMClient:
    """Mock LLM client - used when OpenAI API key is not available."""

    async def _call_llm(self, model, system_prompt, user_prompt, response_format):
        """Generate mock meme content."""
        fields = response_format.model_fields.keys()
        mock_values = {}

        for field in fields:
            if field == "reasoning":
                mock_values[field] = "Generated for Oscar campaign"
            elif "reject" in field:
                mock_values[field] = "Generic Oscar bait"
            elif "approve" in field:
                mock_values[field] = "One Battle After Another"
            elif "strong" in field:
                mock_values[field] = "OBAA quality"
            elif "weak" in field:
                mock_values[field] = "Sinners hype"
            elif "medium" in field:
                mock_values[field] = "Average drama"
            elif "chad" in field:
                mock_values[field] = "Cinema enjoyer"
            elif "wojak" in field:
                mock_values[field] = "'It's so deep bro'"
            elif "top" in field:
                mock_values[field] = "Can't be overrated"
            elif "bottom" in field:
                mock_values[field] = "With 16 nominations"
            elif "happy" in field:
                mock_values[field] = "New Oscar film!"
            elif "concerned" in field:
                mock_values[field] = "It's 3 hours"
            elif "want" in field:
                mock_values[field] = "Watch OBAA again"
            elif "holding" in field:
                mock_values[field] = "Responsibilities"
            elif "button1" in field:
                mock_values[field] = "Admit it's mid"
            elif "button2" in field:
                mock_values[field] = "Defend the hype"
            elif "caption" in field:
                mock_values[field] = "16 Oscar nominations??"
            else:
                mock_values[field] = "Meme text"

        return response_format(**mock_values)


# Initialize LLM client - use OpenAI if available, otherwise fall back to mock
try:
    from llm_client import OpenAIClient
    llm_client = OpenAIClient()
    print("Using OpenAI LLM client for meme generation")
except (ImportError, ValueError) as e:
    print(f"Using mock LLM client: {e}")
    llm_client = MockLLMClient()

pipeline = MemeGenerationPipeline(llm_client, comment_db)


def scan_memes_directory(category: Optional[str] = None) -> list:
    """Scan the generated directory for memes."""
    memes = []

    categories = [category] if category else ["pro_obaa", "anti_sinners"]

    for cat in categories:
        cat_dir = GENERATED_DIR / cat
        if not cat_dir.exists():
            continue

        for file in sorted(cat_dir.glob("*.png")):
            # Parse filename to extract metadata
            parts = file.stem.split("_")
            template_id = parts[1] if len(parts) > 1 else "unknown"

            meme = GeneratedMemeResponse(
                id=file.stem,
                filename=file.name,
                url=f"/memes/{cat}/{file.name}",
                template_id=template_id,
                category=cat,
                text_content={},  # Text not stored in filename
                created_at=datetime.fromtimestamp(file.stat().st_mtime, tz=timezone.utc),
            )
            memes.append(meme)

    return memes


@router.get("", response_model=MemeListResponse)
async def list_memes(
    category: Optional[Literal["pro_obaa", "anti_sinners"]] = Query(None),
):
    """List all generated memes, optionally filtered by category."""
    try:
        memes = scan_memes_directory(category)

        # Count by category
        categories = {}
        for meme in memes:
            cat = meme.category
            categories[cat] = categories.get(cat, 0) + 1

        return MemeListResponse(
            memes=memes,
            total=len(memes),
            categories=categories,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates", response_model=TemplateListResponse)
async def list_templates():
    """List all available meme templates."""
    templates = [
        MemeTemplate(
            id=tid,
            name=t["name"],
            text_slots=t["text_slots"],
            slot_names=t["slot_names"],
            irony_type=t["irony_type"],
            description=t["description"],
            max_chars_per_slot=t["max_chars_per_slot"],
        )
        for tid, t in MEME_TEMPLATES.items()
    ]

    return TemplateListResponse(
        templates=templates,
        total=len(templates),
    )


@router.post("/generate", response_model=GenerateMemeResponse)
async def generate_memes(request: GenerateMemeRequest):
    """Generate new memes using the LLM pipeline."""
    try:
        start_time = time.time()

        # Import the request model
        from llm_pipeline import MemeGenerationRequest, MemeCategory

        # Convert API request to pipeline request
        pipeline_request = MemeGenerationRequest(
            category=MemeCategory(request.category),
            templates=request.templates,
            num_memes=request.num_memes,
            tone_preference=request.tone,
        )

        # Generate memes
        batch = await pipeline.generate_batch(pipeline_request)

        # Render to images - saves directly to category folders
        render_result = render_memes_by_category(batch)
        paths = render_result.get(request.category, [])

        # Build response
        memes = []
        for meme, path in zip(batch.memes, paths):
            memes.append(GeneratedMemeResponse(
                id=path.stem,
                filename=path.name,
                url=f"/memes/{request.category}/{path.name}",
                template_id=meme.template_id,
                category=request.category,
                text_content=meme.text_content,
                created_at=datetime.now(timezone.utc),
            ))

        generation_time = int((time.time() - start_time) * 1000)

        return GenerateMemeResponse(
            success=True,
            memes=memes,
            generation_time_ms=generation_time,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comments/{movie}", response_model=CommentListResponse)
async def get_comments(
    movie: str,
    sentiment: Literal["positive", "negative", "all"] = "all",
    limit: int = Query(default=20, ge=1, le=100),
):
    """Get sentiment comments for a movie."""
    try:
        if sentiment == "positive":
            comments_raw = comment_db.get_positive_comments(movie, limit=limit)
            compound_filter = lambda c: c.compound > 0.2
        elif sentiment == "negative":
            comments_raw = comment_db.get_negative_comments(movie, limit=limit)
            compound_filter = lambda c: c.compound < -0.2
        else:
            # Get both
            pos = comment_db.get_positive_comments(movie, limit=limit // 2)
            neg = comment_db.get_negative_comments(movie, limit=limit // 2)
            comments_raw = pos + neg

        # Get full comment objects for stats
        all_comments = comment_db.get_all_comments(movie)

        # Build response
        comments = []
        for text in comments_raw[:limit]:
            # Find the matching comment object
            matching = next((c for c in all_comments if c.full_text == text), None)
            if matching:
                comments.append(CommentPreview(
                    text=text[:200],  # Truncate for preview
                    sentiment=matching.sentiment,
                    compound_score=matching.compound,
                ))
            else:
                comments.append(CommentPreview(
                    text=text[:200],
                    sentiment="Unknown",
                    compound_score=0.0,
                ))

        stats = comment_db.get_comment_stats(movie)

        return CommentListResponse(
            movie=movie,
            comments=comments,
            total=stats.get("total", 0),
            avg_compound=stats.get("avg_compound", 0.0),
        )

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"No data found for movie: {movie}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
