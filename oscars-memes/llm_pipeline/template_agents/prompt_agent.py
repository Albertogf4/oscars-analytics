"""Prompt Writing Agent - Generates TEMPLATE_SPECIFIC_PROMPT entries."""

from typing import Type

from .base_agent import BaseTemplateAgent
from .models import (
    PromptContent,
    VisualAnalysis,
    SlotDetection,
    IronyAnalysis,
    TemplateMetadata,
    ExampleContent,
)


class PromptWritingAgent(BaseTemplateAgent[PromptContent]):
    """Agent 6: Writes the template-specific prompt for the LLM pipeline.

    This agent creates the TEMPLATE_SPECIFIC_PROMPTS entry that guides
    the meme generation LLM on how to create content for this template.
    """

    # Reference prompt from existing templates
    EXAMPLE_PROMPT = '''For Drake Approves/Disapproves memes:
- Top panel (reject_text): Something clearly worse/cringe/overrated
- Bottom panel (approve_text): Something clearly better/based/underrated
- The contrast should be immediately obvious
- Use "X vs Y" thinking - what would someone REJECT in favor of the APPROVED thing?
- Keep it relatable to film fans

STRUCTURE:
- reject_text = "What Drake says no to" (dismissive gesture)
- approve_text = "What Drake approves" (satisfied pointing)'''

    @property
    def name(self) -> str:
        return "Prompt Writing Agent"

    @property
    def description(self) -> str:
        return """You are an expert at writing prompts for LLMs that generate meme content.
You create clear, structured prompts that guide the model to produce funny,
format-appropriate content. You follow the exact format used in existing templates."""

    @property
    def output_model(self) -> Type[PromptContent]:
        return PromptContent

    def build_prompt(self, image_path: str, **context) -> str:
        """Build the prompt writing prompt.

        Args:
            image_path: Path to the template image.
            **context: Should include all previous agent outputs.

        Returns:
            The prompt string.
        """
        visual: VisualAnalysis = context.get("visual_analysis")
        slots: SlotDetection = context.get("slot_detection")
        irony: IronyAnalysis = context.get("irony_analysis")
        metadata: TemplateMetadata = context.get("metadata")
        examples: ExampleContent = context.get("examples")

        context_str = ""

        if metadata:
            context_str += f"""
TEMPLATE INFO:
- ID: {metadata.id}
- Name: {metadata.name}
- Description: {metadata.description}
"""

        if slots:
            context_str += f"""
SLOT INFORMATION:
- Slots: {slots.text_slots}
- Names: {', '.join(slots.slot_names)}
- Descriptions: {'; '.join(slots.slot_descriptions)}
- Max chars: {slots.max_chars_per_slot}
"""

        if irony:
            context_str += f"""
IRONY ANALYSIS:
- Type: {irony.irony_type}
- Mechanics: {irony.humor_mechanics}
- Emotional journey: {irony.emotional_journey}
- Tone: {irony.tone}
- Key contrasts: {', '.join(irony.key_contrast_elements)}
"""

        if examples:
            context_str += f"""
EXAMPLES:
- Default: {examples.example}
- Pro-OBAA: {examples.pro_obaa_example}
- Anti-Sinners: {examples.anti_sinners_example}
"""

        return f"""Write a TEMPLATE_SPECIFIC_PROMPT entry for this meme template.
{context_str}

REFERENCE FORMAT (from existing prompts):
```
{self.EXAMPLE_PROMPT}
```

Your task:
Write a prompt following this EXACT format:

1. HEADER LINE
   Format: "For [Template Name] memes:"

2. BULLET POINTS (3-5 bullets)
   - Each bullet explains ONE aspect of the format
   - Describe what goes in each panel/slot
   - Explain the type of contrast or humor
   - Give guidance on what makes it work
   - Keep bullets concise but informative

3. STRUCTURE SECTION
   Format exactly:
   ```
   STRUCTURE:
   - slot_name = "what this slot represents"
   - slot_name2 = "what this slot represents"
   ```

REQUIREMENTS:
- Follow the exact format of existing prompts
- Be specific about what each slot should contain
- Reference the irony type and how to use it
- Keep it concise but complete
- Use quotation marks for example descriptions in STRUCTURE

OUTPUT:
Return ONLY the template_prompt string. Do not include ```python or any code formatting.
Just the raw prompt text that will go into TEMPLATE_SPECIFIC_PROMPTS["template_id"]."""

    async def run(self, image_path: str, **context) -> PromptContent:
        """Execute prompt writing.

        Args:
            image_path: Path to the template image.
            **context: Should include all previous agent outputs.

        Returns:
            PromptContent with the template-specific prompt string.
        """
        return await super().run(image_path, **context)
