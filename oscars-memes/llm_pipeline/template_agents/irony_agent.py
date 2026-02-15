"""Irony Analysis Agent (DEDICATED) - Deeply analyzes humor and irony mechanics."""

from typing import Type

from .base_agent import BaseTemplateAgent
from .models import IronyAnalysis, VisualAnalysis


class IronyAnalysisAgent(BaseTemplateAgent[IronyAnalysis]):
    """Agent 3: DEDICATED agent for capturing irony and humor mechanics.

    This is THE critical agent for understanding how a meme works.
    It deeply analyzes:
    - The type of irony employed
    - Step-by-step humor mechanics
    - Emotional journey of the viewer
    - Meme culture context and origins
    - The specific elements that create contrast/humor
    """

    # Known irony types from existing templates
    KNOWN_IRONY_TYPES = {
        "preference_contrast": "Drake - Shows rejection vs approval of options",
        "superiority_comparison": "Strong Doge - One thing is clearly superior to another",
        "escalating_quality": "Spongebob - Progression from weak to powerful",
        "fan_comparison": "Chad Wojak - Comparing cringe fans vs based fans",
        "sarcastic_logic": "Roll Safe - Galaxy brain logic that's actually flawed",
        "expectation_subversion": "Happy Concerned - Good news revealed to have a catch",
        "awkward_situation": "Monkey Puppet - Uncomfortable truth you avoid",
        "desire_blocked": "Want/Holding - Something stopping you from what you want",
        "impossible_choice": "Two Buttons - Difficult decision between options",
        "shocked_disappointment": "Disbelief - Expressing shock at an outrageous fact",
        "emotional_aftermath": "MJ Crying - Showing what caused emotional reaction",
        "hidden_pain": "Wojak Mask - Pretending to be okay while suffering",
    }

    @property
    def name(self) -> str:
        return "Irony Analysis Agent"

    @property
    def description(self) -> str:
        return """You are a meme culture expert and humor analyst.
Your specialty is deeply understanding HOW memes create humor through irony,
contrast, subversion, and other comedic techniques. You understand internet
culture, meme formats, and the psychology of why memes are funny."""

    @property
    def output_model(self) -> Type[IronyAnalysis]:
        return IronyAnalysis

    def build_prompt(self, image_path: str, **context) -> str:
        """Build the irony analysis prompt.

        Args:
            image_path: Path to the template image.
            **context: Should include 'visual_analysis'.

        Returns:
            The prompt string for deep irony analysis.
        """
        visual: VisualAnalysis = context.get("visual_analysis")

        visual_context = ""
        if visual:
            visual_context = f"""
VISUAL ANALYSIS:
- Panels: {visual.panel_count} ({visual.layout_type} layout)
- Visual elements: {', '.join(visual.characters_or_elements)}
- Visual contrast: {visual.visual_contrast}
- Panel descriptions: {'; '.join(visual.panel_descriptions)}
"""

        known_types_str = "\n".join(
            f"  - {k}: {v}" for k, v in self.KNOWN_IRONY_TYPES.items()
        )

        return f"""Perform a DEEP ANALYSIS of the irony and humor mechanics in this meme template.
{visual_context}

This is THE most important analysis. You must capture exactly HOW this meme creates humor.

## TASK 1: IDENTIFY THE IRONY TYPE

KNOWN IRONY TYPES (use one of these if applicable, or create a new descriptive type):
{known_types_str}

If this meme doesn't fit existing types, create a new descriptive snake_case type
that captures its essence (e.g., "temporal_decline", "false_equivalence", "dramatic_reveal").

## TASK 2: EXPLAIN THE IRONY IN DETAIL

Write a comprehensive explanation of HOW the irony works:
- What is being contrasted, subverted, or exaggerated?
- Why does this contrast create humor?
- What expectations are set up and how are they violated?
- What makes this format effective for comedy?

## TASK 3: BREAK DOWN THE HUMOR MECHANICS

Provide a step-by-step breakdown:
1. What does the viewer see first?
2. How does each panel/element build on the previous?
3. Where is the comedic "turn" or punchline?
4. Why is the final element funny in context?

## TASK 4: DESCRIBE THE EMOTIONAL JOURNEY

Map the viewer's emotional experience:
- Initial reaction (expectation, curiosity, etc.)
- Middle state (recognition, anticipation, etc.)
- Final reaction (laughter, recognition, satisfaction, etc.)

## TASK 5: PROVIDE MEME CULTURE CONTEXT

Explain:
- Origin of this meme format (if known/recognizable)
- How it's typically used on social media
- What communities use it most
- What topics it's commonly applied to

## TASK 6: DEFINE THE TONE

Describe the overall emotional tone:
- Is it dismissive? Celebratory? Mocking? Sympathetic?
- Is it aggressive or gentle in its humor?
- Does it punch up or punch down?

Example tones: "Dismissive comparison", "Escalating superiority", "Sympathetic frustration",
"Sarcastic endorsement", "Reluctant admission"

## TASK 7: IDENTIFY SIMILAR TEMPLATES

List template IDs that use similar humor mechanics:
- drake, strong_doge, spongebob_evolution, chad_wojak, rollsafe,
- happy_concerned, monkey_puppet, want_holding, two_buttons,
- disbelief, mj_crying, wojak_mask

## TASK 8: KEY CONTRAST ELEMENTS

List the specific visual/conceptual elements that create the contrast:
- What two things are being compared?
- What quality makes one "better" or different from the other?
- What's the implicit value judgment?

CRITICAL: Your analysis will be used to generate prompts for an LLM to create
content for this meme format. The better you understand the humor, the funnier
the generated memes will be."""

    async def run(self, image_path: str, **context) -> IronyAnalysis:
        """Execute irony analysis.

        Args:
            image_path: Path to the template image.
            **context: Should include 'visual_analysis'.

        Returns:
            IronyAnalysis with deep understanding of the meme's humor.
        """
        return await super().run(image_path, **context)
