"""Visual Analysis Agent - Understands the visual structure of meme templates."""

from typing import Type
from PIL import Image

from .base_agent import BaseTemplateAgent
from .models import VisualAnalysis, ImageDimensions


class VisualAnalysisAgent(BaseTemplateAgent[VisualAnalysis]):
    """Agent 1: Analyzes the visual structure of a meme template.

    This agent examines the template image and identifies:
    - Number of panels
    - Layout arrangement
    - Characters or visual elements
    - Visual contrasts between panels
    """

    @property
    def name(self) -> str:
        return "Visual Analysis Agent"

    @property
    def description(self) -> str:
        return """You are an expert at analyzing meme template images.
Your job is to objectively describe what you see in the image, panel by panel,
without interpreting the humor or meaning. Focus on visual elements only."""

    @property
    def output_model(self) -> Type[VisualAnalysis]:
        return VisualAnalysis

    def get_image_dimensions(self, image_path: str) -> tuple[int, int]:
        """Get the dimensions of an image.

        Args:
            image_path: Path to the image file.

        Returns:
            Tuple of (width, height).
        """
        with Image.open(image_path) as img:
            return img.size

    def build_prompt(self, image_path: str, **context) -> str:
        """Build the visual analysis prompt.

        Args:
            image_path: Path to the template image.
            **context: Not used for this agent.

        Returns:
            The prompt string.
        """
        # Get actual image dimensions
        width, height = self.get_image_dimensions(image_path)

        return f"""Analyze this meme template image and describe its visual structure.

IMAGE DIMENSIONS: {width}x{height} pixels

Your task:
1. Count the number of distinct panels or sections in this meme template
2. Identify the layout type:
   - "vertical": Panels stacked top to bottom
   - "horizontal": Panels arranged left to right
   - "grid": 2x2 or other grid arrangement
   - "single": Single panel with one scene

3. List the visual elements/characters you see in each panel
   - Be specific (e.g., "man with dismissive gesture", "same man pointing approvingly")
   - Note any recurring characters across panels

4. Describe the visual contrast between panels
   - What changes from one panel to the next?
   - Is it the same character with different expressions?
   - Are there different characters being compared?

5. Provide a detailed description of each panel
   - What's happening visually?
   - What emotions or actions are displayed?

IMPORTANT:
- Only describe what you SEE, not what the meme means
- Be objective and detailed
- Note the visual space available for text in each panel

The image dimensions are {width}x{height} pixels. Include this in your response."""

    async def run(self, image_path: str, **context) -> VisualAnalysis:
        """Execute visual analysis with image dimensions.

        Args:
            image_path: Path to the template image.
            **context: Additional context (not used).

        Returns:
            VisualAnalysis result.
        """
        # Get dimensions before LLM call
        width, height = self.get_image_dimensions(image_path)

        # Run the parent's run method
        result = await super().run(image_path, **context)

        # Ensure dimensions are set correctly (override LLM output with actual values)
        result.image_dimensions = ImageDimensions(width=width, height=height)

        return result
