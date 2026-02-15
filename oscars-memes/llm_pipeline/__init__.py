"""LLM-powered meme generation pipeline.

This module provides an automated meme generation system that uses LLMs
to generate text content for meme templates based on sentiment analysis data.

Example usage:

    from llm_pipeline import MemeGenerationPipeline, CommentDatabase, MemeCategory

    # Initialize with your LLM client
    pipeline = MemeGenerationPipeline(your_llm_client)

    # Generate memes
    batch = await pipeline.generate_batch(MemeGenerationRequest(
        category=MemeCategory.PRO_OBAA,
        num_memes=10,
    ))

    # Render to images
    from llm_pipeline.generator import render_batch
    paths = render_batch(batch)
"""

from .models import (
    MemeCategory,
    DrakeOutput,
    StrongDogeOutput,
    SpongebobOutput,
    ChadWojakOutput,
    RollSafeOutput,
    HappyConcernedOutput,
    SingleCaptionOutput,
    WantHoldingOutput,
    TwoButtonsOutput,
    MJCryingOutput,
    GeneratedMeme,
    BatchMemeOutput,
    MemeGenerationRequest,
    MemeContext,
)
from .templates import MEME_TEMPLATES, get_template, get_all_template_ids
from .pipeline import MemeGenerationPipeline
from .comment_db import CommentDatabase
from .generator import MemeRenderer, render_batch, render_meme, quick_render

__all__ = [
    # Models
    "MemeCategory",
    "DrakeOutput",
    "StrongDogeOutput",
    "SpongebobOutput",
    "ChadWojakOutput",
    "RollSafeOutput",
    "HappyConcernedOutput",
    "SingleCaptionOutput",
    "WantHoldingOutput",
    "TwoButtonsOutput",
    "MJCryingOutput",
    "GeneratedMeme",
    "BatchMemeOutput",
    "MemeGenerationRequest",
    "MemeContext",
    # Templates
    "MEME_TEMPLATES",
    "get_template",
    "get_all_template_ids",
    # Pipeline
    "MemeGenerationPipeline",
    "CommentDatabase",
    # Generator
    "MemeRenderer",
    "render_batch",
    "render_meme",
    "quick_render",
]
