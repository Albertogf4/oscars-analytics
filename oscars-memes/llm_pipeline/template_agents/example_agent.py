"""Example Generation Agent - Creates compelling example content for templates."""

from typing import Type

from .base_agent import BaseTemplateAgent
from .models import ExampleContent, SlotDetection, IronyAnalysis, TemplateMetadata


class ExampleGenerationAgent(BaseTemplateAgent[ExampleContent]):
    """Agent 5: Generates example content for the template.

    This agent creates:
    - Default example content demonstrating the format
    - Pro-OBAA campaign example
    - Anti-Sinners campaign example
    """

    @property
    def name(self) -> str:
        return "Example Generation Agent"

    @property
    def description(self) -> str:
        return """You are a meme content creator who understands both internet humor
and the Oscar campaign context. You create punchy, funny examples that perfectly
demonstrate how a meme format works while staying within character limits."""

    @property
    def output_model(self) -> Type[ExampleContent]:
        return ExampleContent

    def build_prompt(self, image_path: str, **context) -> str:
        """Build the example generation prompt.

        Args:
            image_path: Path to the template image.
            **context: Should include previous agent outputs.

        Returns:
            The prompt string.
        """
        slots: SlotDetection = context.get("slot_detection")
        irony: IronyAnalysis = context.get("irony_analysis")
        metadata: TemplateMetadata = context.get("metadata")

        slots_str = ""
        if slots:
            slots_str = f"""
SLOT INFORMATION:
- Number of slots: {slots.text_slots}
- Slot names: {', '.join(slots.slot_names)}
- Max characters per slot: {slots.max_chars_per_slot}
- Slot descriptions: {'; '.join(slots.slot_descriptions)}
"""

        irony_str = ""
        if irony:
            irony_str = f"""
IRONY/HUMOR MECHANICS:
- Irony type: {irony.irony_type}
- How it works: {irony.humor_mechanics}
- Tone: {irony.tone}
- Key contrast elements: {', '.join(irony.key_contrast_elements)}
"""

        template_name = metadata.name if metadata else "Unknown Template"

        return f"""Generate example content for the "{template_name}" meme template.
{slots_str}
{irony_str}

CAMPAIGN CONTEXT:
- PRO_OBAA: Boost "One Battle After Another" (OBAA) - a critically acclaimed film
- ANTI_SINNERS: Mock "Sinners" - an overhyped vampire movie with 16 Oscar nominations

Your task:

1. CREATE DEFAULT EXAMPLE
   - Generate example text for each slot
   - Should be generic enough to work without campaign context
   - Must demonstrate the meme's humor format perfectly
   - Stay within character limits!

2. CREATE PRO_OBAA EXAMPLE
   - Boost/celebrate One Battle After Another
   - Make OBAA look superior, amazing, must-watch
   - Use the meme's irony type to elevate OBAA

3. CREATE ANTI_SINNERS EXAMPLE
   - Mock/undermine Sinners
   - Question its Oscar nominations, quality, hype
   - Use the meme's irony type to satirize Sinners

REQUIREMENTS:
- Each slot's text MUST be under {slots.max_chars_per_slot if slots else 40} characters
- Text should be punchy and immediately funny
- Use internet meme language naturally: "fr fr", "no cap", "based", "mid", "kino"
- The irony/humor should be immediately obvious
- Make examples that are actually shareable on social media

EXISTING EXAMPLES FOR REFERENCE (as slot_name + text pairs):
- Drake: [{{"slot_name": "reject_text", "text": "Generic Oscar bait"}}, {{"slot_name": "approve_text", "text": "One Battle After Another"}}]
- Strong Doge: [{{"slot_name": "strong_text", "text": "Classic vampire movies"}}, {{"slot_name": "weak_text", "text": "Sinners"}}]
- Roll Safe: [{{"slot_name": "top_text", "text": "Can't be called overrated"}}, {{"slot_name": "bottom_text", "text": "If you nominate it 16 times"}}]

FORMAT YOUR OUTPUT AS THREE LISTS OF SLOT EXAMPLES:
Each example should be a list of objects with "slot_name" and "text" fields:
- example: [{{"slot_name": "...", "text": "..."}}, ...]  - Default example for any context
- pro_obaa_example: [{{"slot_name": "...", "text": "..."}}, ...] - Campaign-specific for boosting OBAA
- anti_sinners_example: [{{"slot_name": "...", "text": "..."}}, ...] - Campaign-specific for mocking Sinners

IMPORTANT: Return lists of objects, NOT dictionaries. Each object must have both "slot_name" and "text" fields."""

    async def run(self, image_path: str, **context) -> ExampleContent:
        """Execute example generation.

        Args:
            image_path: Path to the template image.
            **context: Should include previous agent outputs.

        Returns:
            ExampleContent with examples for each campaign context.
        """
        return await super().run(image_path, **context)
