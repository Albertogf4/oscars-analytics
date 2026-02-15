"""Pydantic models for structured LLM outputs and pipeline data."""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum


class MemeCategory(str, Enum):
    """Campaign category for meme generation."""
    PRO_OBAA = "pro_obaa"
    ANTI_SINNERS = "anti_sinners"


# === Per-Template Output Models ===

class DrakeOutput(BaseModel):
    """Output for Drake approves/disapproves meme."""
    reject_text: str = Field(..., max_length=40, description="Text for what Drake rejects (top panel)")
    approve_text: str = Field(..., max_length=40, description="Text for what Drake approves (bottom panel)")
    reasoning: str = Field(..., description="Why this contrast works for the meme")


class StrongDogeOutput(BaseModel):
    """Output for Strong vs Weak Doge meme."""
    strong_text: str = Field(..., max_length=45, description="Label for the strong/superior doge")
    weak_text: str = Field(..., max_length=45, description="Label for the weak/inferior doge")
    reasoning: str = Field(..., description="Why this comparison is effective")


class SpongebobOutput(BaseModel):
    """Output for Spongebob strength evolution meme."""
    weak_text: str = Field(..., max_length=35, description="First panel - weakest level")
    medium_text: str = Field(..., max_length=35, description="Second panel - medium level")
    strong_text: str = Field(..., max_length=35, description="Third panel - strongest/best level")
    reasoning: str = Field(..., description="Why this escalation works")


class ChadWojakOutput(BaseModel):
    """Output for Chad vs Crying Wojak meme."""
    wojak_text: str = Field(..., max_length=45, description="What the crying wojak says (cringe)")
    chad_text: str = Field(..., max_length=45, description="What the chad says (based)")
    reasoning: str = Field(..., description="Why this fan comparison works")


class RollSafeOutput(BaseModel):
    """Output for Roll Safe / Thinking Guy meme."""
    top_text: str = Field(..., max_length=50, description="Setup premise")
    bottom_text: str = Field(..., max_length=50, description="Ironic punchline")
    reasoning: str = Field(..., description="Why this sarcastic logic is funny")


class HappyConcernedOutput(BaseModel):
    """Output for Happy at First, Concerned Later meme."""
    happy_text: str = Field(..., max_length=45, description="Initial good news (top panel)")
    concerned_text: str = Field(..., max_length=45, description="The catch/bad realization (bottom)")
    reasoning: str = Field(..., description="Why this subversion works")


class SingleCaptionOutput(BaseModel):
    """Output for single-caption memes (monkey_puppet, disbelief, wojak_mask)."""
    caption: str = Field(..., max_length=60, description="The meme caption")
    reasoning: str = Field(..., description="Why this caption fits the template's irony")


class WantHoldingOutput(BaseModel):
    """Output for What I Want vs What's Holding Me Back meme."""
    want_text: str = Field(..., max_length=35, description="What you want (yellow ball)")
    holding_text: str = Field(..., max_length=35, description="What's holding you back (pink blob)")
    reasoning: str = Field(..., description="Why this desire/obstacle pairing is relatable")


class TwoButtonsOutput(BaseModel):
    """Output for Two Buttons Hard Choice meme."""
    button1: str = Field(..., max_length=35, description="First button option")
    button2: str = Field(..., max_length=35, description="Second button option")
    reasoning: str = Field(..., description="Why this is a difficult/ironic choice")


class MJCryingOutput(BaseModel):
    """Output for Michael Jordan Crying meme."""
    top_text: str = Field(..., max_length=40, description="Context/who (e.g., 'Sinners fans after')")
    bottom_text: str = Field(..., max_length=40, description="What caused the tears")
    reasoning: str = Field(..., description="Why this emotional moment works")



class IncognitoFaceChangeOutput(BaseModel):
    """Output for Incognito Face Change meme."""
    character_text: str = Field(..., max_length=50, description="Text for the character panel (top left)")
    shadow_text: str = Field(..., max_length=50, description="Text for the shadow panel (bottom right)")
    reasoning: str = Field(..., description="Explains the perceived reality shift in the meme")



class MrIncredibleUncannyOutput(BaseModel):
    """Output for Mr. Incredible Uncanny meme."""
    normal_text: str = Field(..., max_length=50, description="Text for the normal panel.")
    distorted_text: str = Field(..., max_length=50, description="Text for the distorted panel.")
    reasoning: str = Field(..., description="Why this contrast works for the meme")


# === Batch Generation Models ===

class GeneratedMeme(BaseModel):
    """A single generated meme with metadata."""
    template_id: str
    category: MemeCategory
    text_content: dict  # The actual text slots
    source_comments: List[str] = Field(default_factory=list, description="Comments that inspired this")
    confidence_score: float = Field(ge=0.0, le=1.0, description="How well this fits the template")
    reasoning: str = Field(default="", description="LLM's reasoning for this meme")


class BatchMemeOutput(BaseModel):
    """Output for generating multiple memes at once."""
    memes: List[GeneratedMeme]
    total_generated: int
    category_breakdown: dict  # {"pro_obaa": 10, "anti_sinners": 10}


# === Comment Analysis Models ===

class AnalyzedComment(BaseModel):
    """A comment analyzed for meme potential."""
    original_text: str
    sentiment: Literal["positive", "negative", "neutral"]
    compound_score: float
    meme_potential: float = Field(ge=0.0, le=1.0)
    suggested_templates: List[str] = Field(default_factory=list)
    extracted_keywords: List[str] = Field(default_factory=list)


class CommentBatchAnalysis(BaseModel):
    """Analysis of a batch of comments for meme generation."""
    best_positive_comments: List[AnalyzedComment]
    best_negative_comments: List[AnalyzedComment]
    theme_clusters: dict  # {"oscar_nominations": [...], "acting_quality": [...]}


# === User Request Model ===

class MemeGenerationRequest(BaseModel):
    """User request for meme generation."""

    # Required
    category: MemeCategory  # "pro_obaa" or "anti_sinners"

    # Optional - User can override
    target_movie: str = "One Battle After Another"  # or "Sinners"
    competitor_movie: str = "Sinners"  # or "One Battle After Another"

    # Template selection
    templates: Optional[List[str]] = None  # If None, use all templates
    num_memes: int = Field(default=10, ge=1, le=50)

    # Content guidance
    custom_themes: Optional[List[str]] = None  # e.g., ["oscar nominations", "acting"]
    tone_preference: Literal["savage", "playful", "sarcastic"] = "sarcastic"

    # Advanced
    use_specific_comments: Optional[List[str]] = None  # User can paste specific comments
    exclude_topics: Optional[List[str]] = None  # Topics to avoid


# === Context Models ===

class MemeContext(BaseModel):
    """Context automatically assembled for LLM."""

    # From database
    target_movie_positive_comments: List[str] = Field(default_factory=list)
    target_movie_negative_comments: List[str] = Field(default_factory=list)
    competitor_negative_comments: List[str] = Field(default_factory=list)
    competitor_positive_comments: List[str] = Field(default_factory=list)

    # Computed stats
    target_sentiment_score: float = 0.0
    competitor_sentiment_score: float = 0.0
    key_themes: List[str] = Field(default_factory=list)

    # Source tracking
    source_comments: List[str] = Field(default_factory=list)

    # Campaign info
    campaign_goal: str = ""  # "boost OBAA" or "undermine Sinners"
