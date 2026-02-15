"""Metadata Generation Agent - Creates clean, consistent template metadata."""

from pathlib import Path
from typing import Type

from .base_agent import BaseTemplateAgent
from .models import TemplateMetadata, VisualAnalysis, SlotDetection, IronyAnalysis


class MetadataGenerationAgent(BaseTemplateAgent[TemplateMetadata]):
    """Agent 4: Generates clean, consistent metadata for the template.

    This agent creates:
    - Unique snake_case ID
    - Human-readable name
    - Concise description
    - Generator function name
    """

    @property
    def name(self) -> str:
        return "Metadata Generation Agent"

    @property
    def description(self) -> str:
        return """You are an expert at creating clean, consistent metadata for meme templates.
You follow established naming conventions exactly and create concise, accurate descriptions."""

    @property
    def output_model(self) -> Type[TemplateMetadata]:
        return TemplateMetadata

    def build_prompt(self, image_path: str, **context) -> str:
        """Build the metadata generation prompt.

        Args:
            image_path: Path to the template image.
            **context: Should include previous agent outputs.

        Returns:
            The prompt string.
        """
        visual: VisualAnalysis = context.get("visual_analysis")
        slots: SlotDetection = context.get("slot_detection")
        irony: IronyAnalysis = context.get("irony_analysis")

        filename = Path(image_path).name

        context_str = ""
        if visual:
            context_str += f"""
VISUAL ANALYSIS:
- {visual.panel_count} panels, {visual.layout_type} layout
- Elements: {', '.join(visual.characters_or_elements)}
"""

        if slots:
            context_str += f"""
SLOT DETECTION:
- {slots.text_slots} text slots
- Slot names: {', '.join(slots.slot_names)}
"""

        if irony:
            context_str += f"""
IRONY ANALYSIS:
- Irony type: {irony.irony_type}
- Tone: {irony.tone}
- Culture context: {irony.meme_culture_context[:200]}...
"""

        return f"""Generate clean metadata for this meme template.

FILENAME: {filename}
{context_str}

Your task:

1. CREATE THE ID
   - snake_case format
   - Short but descriptive (1-3 words)
   - Must be unique and memorable
   - Examples: "drake", "strong_doge", "rollsafe", "chad_wojak"

2. CREATE THE NAME
   - Title Case format
   - Human-readable, can be longer
   - Should describe the meme format
   - Examples: "Drake Approves/Disapproves", "Strong vs Weak Doge", "Roll Safe / Thinking Guy"

3. WRITE THE DESCRIPTION
   - 1-2 sentences maximum
   - Describe the VISUAL format, not the humor
   - Explain what each panel shows
   - Example: "Top panel: thing being rejected with dismissive gesture. Bottom panel: thing being approved with satisfied expression."

4. SET GENERATOR FUNCTION NAME
   - Format: "create_{{id}}_meme"
   - Example: if id is "drake", function is "create_drake_meme"

5. RECORD THE FILENAME
   - Use the exact filename provided: {filename}

NAMING CONVENTIONS (follow these exactly):
- ID: snake_case, short, memorable
- Name: Title Case, descriptive
- Description: Visual format description, not humor explanation
- Generator function: create_{{id}}_meme

EXISTING TEMPLATE IDs (don't duplicate):
- drake, strong_doge, spongebob_evolution, chad_wojak
- rollsafe, happy_concerned, monkey_puppet, want_holding
- two_buttons, disbelief, mj_crying, wojak_mask"""

    async def run(self, image_path: str, **context) -> TemplateMetadata:
        """Execute metadata generation.

        Args:
            image_path: Path to the template image.
            **context: Should include previous agent outputs.

        Returns:
            TemplateMetadata with clean, consistent naming.
        """
        return await super().run(image_path, **context)
