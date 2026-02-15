"""Slot Detection Agent - Identifies text placement areas in meme templates."""

from typing import Type

from .base_agent import BaseTemplateAgent
from .models import SlotDetection, VisualAnalysis


class SlotDetectionAgent(BaseTemplateAgent[SlotDetection]):
    """Agent 2: Detects text slots and their properties.

    This agent identifies:
    - Number of text areas in the template
    - Semantic names for each slot
    - Character limits based on visual space
    - Precise positioning for text rendering
    """

    @property
    def name(self) -> str:
        return "Slot Detection Agent"

    @property
    def description(self) -> str:
        return """You are an expert at identifying text placement areas in meme templates.
You analyze where text naturally fits in meme images and determine appropriate
naming conventions and character limits based on the available visual space."""

    @property
    def output_model(self) -> Type[SlotDetection]:
        return SlotDetection

    def build_prompt(self, image_path: str, **context) -> str:
        """Build the slot detection prompt.

        Args:
            image_path: Path to the template image.
            **context: Should include 'visual_analysis' from previous agent.

        Returns:
            The prompt string.
        """
        visual: VisualAnalysis = context.get("visual_analysis")

        visual_context = ""
        if visual:
            visual_context = f"""
VISUAL ANALYSIS CONTEXT:
- Panel count: {visual.panel_count}
- Layout: {visual.layout_type}
- Image dimensions: {visual.image_dimensions.width}x{visual.image_dimensions.height}
- Elements: {', '.join(visual.characters_or_elements)}
- Panel descriptions: {'; '.join(visual.panel_descriptions)}
"""

        return f"""Analyze this meme template to identify text placement areas (slots).
{visual_context}

Your task:
1. IDENTIFY TEXT SLOTS
   - Count how many distinct text areas this meme format typically has
   - Common patterns: 1 slot (single caption), 2 slots (top/bottom or comparison), 3 slots (progression)

2. NAME EACH SLOT
   - Use descriptive snake_case names that reflect their PURPOSE
   - Examples: "reject_text", "approve_text", "top_text", "bottom_text", "caption"
   - Names should match what the slot represents in the meme's format

3. DESCRIBE EACH SLOT
   - What does this slot represent semantically?
   - "The text the character is rejecting" or "The superior option"

4. ESTIMATE CHARACTER LIMITS
   - Based on the available visual space
   - Consider typical meme font sizes (24-40px)
   - Most slots: 30-50 characters
   - Shorter for small areas, longer for wider spaces

5. DETERMINE TEXT POSITIONS
   For each slot, provide:
   - x: Horizontal position (pixels from left)
   - y: Vertical position (pixels from top)
   - width: Maximum text width before wrapping
   - height: Available vertical space
   - alignment: "left", "center", or "right"

6. RECOMMEND FONT SIZE
   - Based on image dimensions and typical meme aesthetics
   - Usually 24-40 for standard memes

NAMING CONVENTIONS TO FOLLOW:
- For comparison memes: use terms like "strong_text", "weak_text", "good_text", "bad_text"
- For reaction memes: use "caption" or "top_text", "bottom_text"
- For multi-panel: use positional names or semantic names based on meaning

EXISTING SLOT NAME PATTERNS (for consistency):
- drake: ["reject_text", "approve_text"]
- strong_doge: ["strong_text", "weak_text"]
- spongebob_evolution: ["weak_text", "medium_text", "strong_text"]
- chad_wojak: ["wojak_text", "chad_text"]
- rollsafe: ["top_text", "bottom_text"]
- Single caption memes: ["caption"]"""

    async def run(self, image_path: str, **context) -> SlotDetection:
        """Execute slot detection.

        Args:
            image_path: Path to the template image.
            **context: Should include 'visual_analysis'.

        Returns:
            SlotDetection result with text slot information.
        """
        return await super().run(image_path, **context)
