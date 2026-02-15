"""Main meme generation pipeline using LLM."""

import asyncio
from typing import List, Optional, Type, Any
from pydantic import BaseModel

from .models import (
    MemeCategory,
    MemeGenerationRequest,
    MemeContext,
    GeneratedMeme,
    BatchMemeOutput,
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
)
from .templates import MEME_TEMPLATES, get_template
from .prompts import get_full_system_prompt, build_user_prompt
from .comment_db import CommentDatabase


# Mapping of template IDs to their Pydantic output models
TEMPLATE_OUTPUT_MODELS = {
    "drake": DrakeOutput,
    "strong_doge": StrongDogeOutput,
    "spongebob_evolution": SpongebobOutput,
    "chad_wojak": ChadWojakOutput,
    "rollsafe": RollSafeOutput,
    "happy_concerned": HappyConcernedOutput,
    "monkey_puppet": SingleCaptionOutput,
    "want_holding": WantHoldingOutput,
    "two_buttons": TwoButtonsOutput,
    "disbelief": SingleCaptionOutput,
    "mj_crying": MJCryingOutput,
    "wojak_mask": SingleCaptionOutput,
}


class MemeGenerationPipeline:
    """Main pipeline for LLM-powered meme generation."""

    def __init__(self, llm_client: Any, comment_db: Optional[CommentDatabase] = None):
        """Initialize the pipeline.

        Args:
            llm_client: An object with an async _call_llm method matching the signature:
                       async def _call_llm(self, model, system_prompt, user_prompt, response_format)
            comment_db: CommentDatabase instance. Creates default if not provided.
        """
        self.llm = llm_client
        self.comments = comment_db or CommentDatabase()

    def _get_output_model(self, template_id: str) -> Type[BaseModel]:
        """Get the appropriate Pydantic model for a template."""
        if template_id not in TEMPLATE_OUTPUT_MODELS:
            raise ValueError(f"No output model for template: {template_id}")
        return TEMPLATE_OUTPUT_MODELS[template_id]

    def _extract_text_content(self, result: BaseModel, template_id: str) -> dict:
        """Extract the text content from an LLM result, excluding reasoning."""
        template = get_template(template_id)
        slot_names = template["slot_names"]

        content = {}
        for slot in slot_names:
            if hasattr(result, slot):
                content[slot] = getattr(result, slot)

        return content

    def _calculate_confidence(self, result: BaseModel, template_id: str) -> float:
        """Calculate a confidence score for the generated meme.

        Higher score = better fit for the template.
        """
        template = get_template(template_id)
        max_chars = template["max_chars_per_slot"]

        # Check if all text fits within limits
        score = 1.0
        for slot in template["slot_names"]:
            if hasattr(result, slot):
                text = getattr(result, slot)
                if len(text) > max_chars:
                    # Penalize for going over limit
                    score -= 0.2
                if len(text) < 5:
                    # Penalize for being too short
                    score -= 0.1

        return max(0.0, min(1.0, score))

    async def _build_context(
        self,
        request: MemeGenerationRequest
    ) -> MemeContext:
        """Build the context for meme generation from request."""

        # Fetch comments from database
        target_positive = self.comments.get_positive_comments(
            request.target_movie, limit=10
        )
        target_negative = self.comments.get_negative_comments(
            request.target_movie, limit=10
        )
        competitor_positive = self.comments.get_positive_comments(
            request.competitor_movie, limit=10
        )
        competitor_negative = self.comments.get_negative_comments(
            request.competitor_movie, limit=10
        )

        # Get sentiment stats
        target_stats = self.comments.get_comment_stats(request.target_movie)
        competitor_stats = self.comments.get_comment_stats(request.competitor_movie)

        # Extract key themes
        themes = self.comments.extract_key_themes(request.competitor_movie)
        if request.custom_themes:
            themes = request.custom_themes + themes

        # Determine campaign goal
        if request.category == MemeCategory.PRO_OBAA:
            goal = f"Boost {request.target_movie} - celebrate its qualities, make it look superior"
        else:
            goal = f"Undermine {request.competitor_movie} - mock the hype, question the quality"

        # Build source comments for tracking
        source_comments = []
        if request.category == MemeCategory.PRO_OBAA:
            source_comments = target_positive[:3] + competitor_negative[:2]
        else:
            source_comments = competitor_negative[:3] + target_positive[:2]

        return MemeContext(
            target_movie_positive_comments=target_positive,
            target_movie_negative_comments=target_negative,
            competitor_negative_comments=competitor_negative,
            competitor_positive_comments=competitor_positive,
            target_sentiment_score=target_stats.get("avg_compound", 0),
            competitor_sentiment_score=competitor_stats.get("avg_compound", 0),
            key_themes=themes,
            source_comments=source_comments,
            campaign_goal=goal,
        )

    async def generate_meme(
        self,
        template_id: str,
        category: MemeCategory,
        context: MemeContext,
        target_movie: str = "One Battle After Another",
        competitor_movie: str = "Sinners",
    ) -> GeneratedMeme:
        """Generate a single meme using the LLM.

        Args:
            template_id: ID of the meme template to use
            category: PRO_OBAA or ANTI_SINNERS
            context: MemeContext with comments and themes
            target_movie: Movie to promote
            competitor_movie: Movie to contrast against

        Returns:
            GeneratedMeme with text content and metadata
        """
        template = get_template(template_id)
        response_model = self._get_output_model(template_id)

        # Build prompts
        system_prompt = get_full_system_prompt(template_id)

        # Select comments based on category
        if category == MemeCategory.PRO_OBAA:
            positive_comments = context.target_movie_positive_comments
            negative_comments = context.competitor_negative_comments
        else:
            positive_comments = context.target_movie_positive_comments
            negative_comments = context.competitor_negative_comments

        user_prompt = build_user_prompt(
            template=template,
            category=category.value,
            target_movie=target_movie,
            competitor_movie=competitor_movie,
            positive_comments=positive_comments,
            negative_comments=negative_comments,
            key_themes=context.key_themes,
        )

        # Call the LLM
        result = await self.llm._call_llm(
            model="gpt-4o-mini",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_format=response_model,
        )

        # Extract text content and calculate confidence
        text_content = self._extract_text_content(result, template_id)
        confidence = self._calculate_confidence(result, template_id)

        # Get reasoning if available
        reasoning = getattr(result, "reasoning", "")

        return GeneratedMeme(
            template_id=template_id,
            category=category,
            text_content=text_content,
            source_comments=context.source_comments[:3],
            confidence_score=confidence,
            reasoning=reasoning,
        )

    async def generate_batch(
        self,
        request: MemeGenerationRequest
    ) -> BatchMemeOutput:
        """Generate a batch of memes based on user request.

        Args:
            request: MemeGenerationRequest with category and options

        Returns:
            BatchMemeOutput with all generated memes
        """
        # Build context from database
        context = await self._build_context(request)

        # Select templates
        templates = request.templates or list(MEME_TEMPLATES.keys())

        # Limit to requested number
        if len(templates) > request.num_memes:
            templates = templates[:request.num_memes]

        # Generate memes concurrently
        tasks = [
            self.generate_meme(
                template_id=template_id,
                category=request.category,
                context=context,
                target_movie=request.target_movie,
                competitor_movie=request.competitor_movie,
            )
            for template_id in templates
        ]

        memes = await asyncio.gather(*tasks)

        return BatchMemeOutput(
            memes=list(memes),
            total_generated=len(memes),
            category_breakdown={request.category.value: len(memes)},
        )

    async def generate_for_both_categories(
        self,
        templates: Optional[List[str]] = None,
        num_per_category: int = 10,
    ) -> BatchMemeOutput:
        """Generate memes for both PRO_OBAA and ANTI_SINNERS categories.

        Useful for generating a balanced set of campaign memes.

        Args:
            templates: List of template IDs to use. Uses all if None.
            num_per_category: Number of memes to generate per category.

        Returns:
            BatchMemeOutput with memes from both categories.
        """
        pro_request = MemeGenerationRequest(
            category=MemeCategory.PRO_OBAA,
            templates=templates,
            num_memes=num_per_category,
        )

        anti_request = MemeGenerationRequest(
            category=MemeCategory.ANTI_SINNERS,
            templates=templates,
            num_memes=num_per_category,
        )

        # Generate both batches concurrently
        pro_batch, anti_batch = await asyncio.gather(
            self.generate_batch(pro_request),
            self.generate_batch(anti_request),
        )

        # Combine results
        all_memes = pro_batch.memes + anti_batch.memes

        return BatchMemeOutput(
            memes=all_memes,
            total_generated=len(all_memes),
            category_breakdown={
                MemeCategory.PRO_OBAA.value: len(pro_batch.memes),
                MemeCategory.ANTI_SINNERS.value: len(anti_batch.memes),
            },
        )
