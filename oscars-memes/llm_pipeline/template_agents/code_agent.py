"""Code Generation Agent - Generates Python code for new templates."""

from typing import Type

from .base_agent import BaseTemplateAgent
from .models import (
    GeneratedCode,
    SlotDetection,
    IronyAnalysis,
    TemplateMetadata,
)


class CodeGenerationAgent(BaseTemplateAgent[GeneratedCode]):
    """Agent 7: Generates the Python code needed for the template.

    This agent creates:
    - Pydantic output model for structured LLM responses
    - Generator function for meme_generator.py
    - Mapping entries for generator.py and pipeline.py
    """

    # Reference code from existing templates
    EXAMPLE_PYDANTIC = '''class DrakeOutput(BaseModel):
    """Output for Drake approves/disapproves meme."""
    reject_text: str = Field(..., max_length=40, description="Text for what Drake rejects (top panel)")
    approve_text: str = Field(..., max_length=40, description="Text for what Drake approves (bottom panel)")
    reasoning: str = Field(..., description="Why this contrast works for the meme")'''

    EXAMPLE_GENERATOR = '''def create_drake_meme(reject_text, approve_text, output_path, category):
    """Create Drake approves/disapproves meme."""
    template = Image.open(TEMPLATE_DIR / "What drake likes, what drake doesn't like.png")
    draw = ImageDraw.Draw(template)

    width, height = template.size
    font = get_font(36)

    # Text area is on the right side
    text_x = width // 2 + 30
    text_width = width // 2 - 60

    # Reject text (top right)
    wrapped_reject = wrap_text(reject_text, font, text_width, draw)
    draw_outlined_text(draw, (text_x, height // 4 - 30), wrapped_reject, font)

    # Approve text (bottom right)
    wrapped_approve = wrap_text(approve_text, font, text_width, draw)
    draw_outlined_text(draw, (text_x, height * 3 // 4 - 30), wrapped_approve, font)

    template.save(output_path)
    print(f"Created: {output_path}")'''

    @property
    def name(self) -> str:
        return "Code Generation Agent"

    @property
    def description(self) -> str:
        return """You are an expert Python developer who generates clean, consistent code.
You match the exact style of existing code and ensure all generated code is syntactically
correct and follows the established patterns."""

    @property
    def output_model(self) -> Type[GeneratedCode]:
        return GeneratedCode

    def build_prompt(self, image_path: str, **context) -> str:
        """Build the code generation prompt.

        Args:
            image_path: Path to the template image.
            **context: Should include previous agent outputs.

        Returns:
            The prompt string.
        """
        slots: SlotDetection = context.get("slot_detection")
        irony: IronyAnalysis = context.get("irony_analysis")
        metadata: TemplateMetadata = context.get("metadata")

        context_str = ""

        if metadata:
            context_str += f"""
TEMPLATE METADATA:
- ID: {metadata.id}
- Name: {metadata.name}
- Filename: {metadata.filename}
- Generator function: {metadata.generator_function}
"""

        if slots:
            positions_str = ""
            for i, pos in enumerate(slots.text_positions):
                positions_str += f"  Slot {i+1} ({slots.slot_names[i]}): x={pos.x}, y={pos.y}, width={pos.width}, align={pos.alignment}\n"

            context_str += f"""
SLOT INFORMATION:
- Number of slots: {slots.text_slots}
- Slot names: {slots.slot_names}
- Max chars: {slots.max_chars_per_slot}
- Font size: {slots.font_size_recommendation}
- Positions:
{positions_str}
"""

        if irony:
            context_str += f"""
IRONY TYPE: {irony.irony_type}
"""

        return f"""Generate Python code for this meme template.
{context_str}

## TASK 1: PYDANTIC OUTPUT MODEL

Generate a Pydantic model class matching this format:
```python
{self.EXAMPLE_PYDANTIC}
```

Requirements:
- Class name: {metadata.id.title().replace('_', '')}Output (e.g., DrakeOutput, StrongDogeOutput)
- One field per slot with max_length set to {slots.max_chars_per_slot if slots else 40}
- Always include a 'reasoning' field at the end
- Include descriptive docstring and field descriptions

## TASK 2: GENERATOR FUNCTION

Generate a meme generator function matching this format:
```python
{self.EXAMPLE_GENERATOR}
```

Requirements:
- Function name: {metadata.generator_function if metadata else 'create_template_meme'}
- Parameters: one for each slot, plus output_path and category
- Load template from TEMPLATE_DIR / "{metadata.filename if metadata else 'template.png'}"
- Use font size {slots.font_size_recommendation if slots else 32}
- Position text according to the slot positions provided
- Use wrap_text() and draw_outlined_text() helpers
- Save to output_path and print creation message

## TASK 3: TEMPLATE_GENERATORS ENTRY

Generate the dict entry for generator.py:
```python
"{metadata.id if metadata else 'template'}": {{
    "function": {metadata.generator_function if metadata else 'create_template_meme'},
    "slots": {slots.slot_names if slots else ['slot1', 'slot2']},
}},
```

## TASK 4: TEMPLATE_OUTPUT_MODELS ENTRY

Generate the dict entry for pipeline.py:
```python
"{metadata.id if metadata else 'template'}": {metadata.id.title().replace('_', '') if metadata else 'Template'}Output,
```

OUTPUT FORMAT:
Return each piece of code as a separate string field.
Do NOT include ```python code blocks - just the raw code.
Ensure all code is syntactically valid Python."""

    async def run(self, image_path: str, **context) -> GeneratedCode:
        """Execute code generation.

        Args:
            image_path: Path to the template image.
            **context: Should include previous agent outputs.

        Returns:
            GeneratedCode with all necessary Python code.
        """
        return await super().run(image_path, **context)
