"""Pydantic models for Meme API endpoints."""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from datetime import datetime


class MemeTemplate(BaseModel):
    """Meme template metadata."""
    id: str
    name: str
    text_slots: int
    slot_names: List[str]
    irony_type: str
    description: str
    max_chars_per_slot: int


class GeneratedMemeResponse(BaseModel):
    """A generated meme with metadata."""
    id: str
    filename: str
    url: str
    template_id: str
    category: Literal["pro_obaa", "anti_sinners"]
    text_content: Dict[str, str]
    created_at: datetime


class MemeListResponse(BaseModel):
    """Response for listing memes."""
    memes: List[GeneratedMemeResponse]
    total: int
    categories: Dict[str, int]


class TemplateListResponse(BaseModel):
    """Response for listing templates."""
    templates: List[MemeTemplate]
    total: int


class GenerateMemeRequest(BaseModel):
    """Request to generate new memes."""
    category: Literal["pro_obaa", "anti_sinners"]
    templates: Optional[List[str]] = None  # None = use all templates
    num_memes: int = Field(default=5, ge=1, le=12)
    tone: Literal["savage", "playful", "sarcastic"] = "sarcastic"


class GenerateMemeResponse(BaseModel):
    """Response after generating memes."""
    success: bool
    memes: List[GeneratedMemeResponse]
    generation_time_ms: int
    errors: List[str] = Field(default_factory=list)


class CommentPreview(BaseModel):
    """Preview of a sentiment comment."""
    text: str
    sentiment: str
    compound_score: float


class CommentListResponse(BaseModel):
    """Response for listing comments."""
    movie: str
    comments: List[CommentPreview]
    total: int
    avg_compound: float
