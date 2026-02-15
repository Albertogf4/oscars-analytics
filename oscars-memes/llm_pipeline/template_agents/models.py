"""Pydantic models for template agent outputs."""

from pydantic import BaseModel, Field
from typing import Literal, Optional


class ImageDimensions(BaseModel):
    """Image width and height."""
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")


class TextPosition(BaseModel):
    """Position and dimensions for a text slot."""
    x: int = Field(..., description="X coordinate for text placement")
    y: int = Field(..., description="Y coordinate for text placement")
    width: int = Field(..., description="Maximum width for text wrapping")
    height: int = Field(..., description="Available height for text")
    alignment: Literal["left", "center", "right"] = Field(
        default="left", description="Text alignment"
    )


class VisualAnalysis(BaseModel):
    """Output from Visual Analysis Agent."""
    panel_count: int = Field(..., ge=1, le=4, description="Number of panels in the meme")
    layout_type: Literal["vertical", "horizontal", "grid", "single"] = Field(
        ..., description="How panels are arranged"
    )
    characters_or_elements: list[str] = Field(
        ..., description="Visual elements in each panel (e.g., 'drake pointing', 'drake disgusted')"
    )
    visual_contrast: str = Field(
        ..., description="Description of the visual contrast/change between panels"
    )
    panel_descriptions: list[str] = Field(
        ..., description="Detailed description of each panel"
    )
    image_dimensions: ImageDimensions = Field(
        ..., description="Width and height of the template image"
    )


class SlotDetection(BaseModel):
    """Output from Slot Detection Agent."""
    text_slots: int = Field(..., ge=1, le=4, description="Number of text areas")
    slot_names: list[str] = Field(
        ..., description="Variable names for each slot (e.g., ['reject_text', 'approve_text'])"
    )
    slot_descriptions: list[str] = Field(
        ..., description="What each slot represents semantically"
    )
    max_chars_per_slot: int = Field(
        ..., ge=20, le=80, description="Maximum characters per slot based on available space"
    )
    text_positions: list[TextPosition] = Field(
        ..., description="Position data for each text slot"
    )
    font_size_recommendation: int = Field(
        default=32, description="Recommended font size based on template"
    )


class IronyAnalysis(BaseModel):
    """Output from Irony Analysis Agent (DEDICATED for capturing humor)."""
    irony_type: str = Field(
        ..., description="Type of irony (e.g., 'preference_contrast', 'expectation_subversion')"
    )
    irony_explanation: str = Field(
        ..., description="Detailed explanation of how the irony works in this meme format"
    )
    humor_mechanics: str = Field(
        ..., description="Step-by-step breakdown of how humor is delivered"
    )
    emotional_journey: str = Field(
        ..., description="The viewer's emotional experience from start to finish"
    )
    meme_culture_context: str = Field(
        ..., description="Origin and cultural context of this meme format"
    )
    tone: str = Field(
        ..., description="The overall tone (e.g., 'Dismissive comparison', 'Escalating superiority')"
    )
    similar_templates: list[str] = Field(
        ..., description="IDs of existing similar templates (empty list if none match)"
    )
    key_contrast_elements: list[str] = Field(
        ..., description="The specific elements that create contrast/humor"
    )


class TemplateMetadata(BaseModel):
    """Output from Metadata Generation Agent."""
    id: str = Field(..., description="snake_case identifier for the template")
    name: str = Field(..., description="Human-readable name in Title Case")
    description: str = Field(
        ..., description="1-2 sentence description of how the meme works visually"
    )
    generator_function: str = Field(
        ..., description="Function name for meme_generator.py (create_{id}_meme)"
    )
    filename: str = Field(..., description="Original image filename")


class SlotExample(BaseModel):
    """Example text for a single slot."""
    slot_name: str = Field(..., description="Name of the slot (e.g., 'reject_text', 'approve_text')")
    text: str = Field(..., description="Example text content for this slot")


class ExampleContent(BaseModel):
    """Output from Example Generation Agent."""
    example: list[SlotExample] = Field(
        ..., description="Default example content for each slot as a list of {slot_name, text} objects"
    )
    pro_obaa_example: list[SlotExample] = Field(
        ..., description="Campaign-specific example for Pro-OBAA as a list of {slot_name, text} objects"
    )
    anti_sinners_example: list[SlotExample] = Field(
        ..., description="Campaign-specific example for Anti-Sinners as a list of {slot_name, text} objects"
    )


class PromptContent(BaseModel):
    """Output from Prompt Writing Agent."""
    template_prompt: str = Field(
        ..., description="The full TEMPLATE_SPECIFIC_PROMPT entry"
    )


class GeneratedCode(BaseModel):
    """Output from Code Generation Agent."""
    pydantic_model: str = Field(
        ..., description="Full Pydantic class definition for structured output"
    )
    generator_function: str = Field(
        ..., description="Full function definition for meme_generator.py"
    )
    template_generators_entry: str = Field(
        ..., description="Entry for TEMPLATE_GENERATORS dict in generator.py"
    )
    output_models_entry: str = Field(
        ..., description="Entry for TEMPLATE_OUTPUT_MODELS dict in pipeline.py"
    )


class TemplateProcessingResult(BaseModel):
    """Complete result from processing a template through all agents."""
    visual_analysis: VisualAnalysis
    slot_detection: SlotDetection
    irony_analysis: IronyAnalysis
    metadata: TemplateMetadata
    examples: ExampleContent
    prompt: PromptContent
    code: GeneratedCode

    # Template registry entry (combined from all agents)
    template_registry_entry: Optional[dict] = None

    def build_registry_entry(self) -> dict:
        """Build the complete template registry entry."""
        # Convert SlotExample list to dict for storage
        example_dict = {slot.slot_name: slot.text for slot in self.examples.example}

        return {
            "id": self.metadata.id,
            "name": self.metadata.name,
            "filename": self.metadata.filename,
            "text_slots": self.slot_detection.text_slots,
            "slot_names": self.slot_detection.slot_names,
            "irony_type": self.irony_analysis.irony_type,
            "description": self.metadata.description,
            "tone": self.irony_analysis.tone,
            "max_chars_per_slot": self.slot_detection.max_chars_per_slot,
            "example": example_dict,
            "generator_function": self.metadata.generator_function,
        }


class ProcessingUpdate(BaseModel):
    """Status update during template processing."""
    stage: str = Field(..., description="Current processing stage")
    status: Literal["running", "completed", "failed"] = Field(default="running")
    result: Optional[dict] = Field(default=None, description="Stage result if completed")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    progress_percent: int = Field(default=0, ge=0, le=100)
