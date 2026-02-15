"""Integration with meme_generator.py for rendering LLM-generated meme text."""

import sys
from pathlib import Path
from typing import List, Optional
import asyncio
from datetime import datetime

# Add parent directory to path for importing meme_generator
sys.path.insert(0, str(Path(__file__).parent.parent))

from meme_generator import (
    create_drake_meme,
    create_doge_meme,
    create_spongebob_meme,
    create_chad_wojak_meme,
    create_rollsafe_meme,
    create_happy_concerned_meme,
    create_monkey_puppet_meme,
    create_want_holding_meme,
    create_two_buttons_meme,
    create_disbelief_meme,
    create_mj_crying_meme,
    create_wojak_mask_meme,
        create_incognito_face_change_meme,
    OUTPUT_DIR,
)

from .models import GeneratedMeme, BatchMemeOutput, MemeCategory


# Mapping of template IDs to generator functions and argument names
TEMPLATE_GENERATORS = {
    "drake": {
        "function": create_drake_meme,
        "args_map": ["reject_text", "approve_text"],
    },
    "strong_doge": {
        "function": create_doge_meme,
        "args_map": ["strong_text", "weak_text"],
    },
    "spongebob_evolution": {
        "function": create_spongebob_meme,
        "args_map": ["weak_text", "medium_text", "strong_text"],
    },
    "chad_wojak": {
        "function": create_chad_wojak_meme,
        "args_map": ["chad_text", "wojak_text"],  # Note: function signature has chad first
    },
    "rollsafe": {
        "function": create_rollsafe_meme,
        "args_map": ["top_text", "bottom_text"],
    },
    "happy_concerned": {
        "function": create_happy_concerned_meme,
        "args_map": ["happy_text", "concerned_text"],
    },
    "monkey_puppet": {
        "function": create_monkey_puppet_meme,
        "args_map": ["caption"],  # Single arg maps to top_text parameter
    },
    "want_holding": {
        "function": create_want_holding_meme,
        "args_map": ["want_text", "holding_text"],
    },
    "two_buttons": {
        "function": create_two_buttons_meme,
        "args_map": ["button1", "button2"],
    },
    "disbelief": {
        "function": create_disbelief_meme,
        "args_map": ["caption"],  # Single arg maps to text parameter
    },
    "mj_crying": {
        "function": create_mj_crying_meme,
        "args_map": ["top_text", "bottom_text"],
    },
    "wojak_mask": {
        "function": create_wojak_mask_meme,
        "args_map": ["caption"],  # Single arg maps to text parameter
    },
    "incognito_face_change": {
    "function": create_incognito_face_change_meme,
    "slots": ['character_text', 'shadow_text'],
},
}


def ensure_output_dirs():
    """Ensure output directories exist."""
    (OUTPUT_DIR / "pro_obaa").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "anti_sinners").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "llm_generated").mkdir(parents=True, exist_ok=True)


def generate_filename(meme: GeneratedMeme, index: int) -> str:
    """Generate a unique filename for a meme."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{index:02d}_{meme.template_id}_{meme.category.value}_{timestamp}.png"


def render_meme(meme: GeneratedMeme, output_path: Path) -> bool:
    """Render a single meme using the appropriate generator function.

    Args:
        meme: GeneratedMeme with template_id and text_content
        output_path: Path to save the rendered image

    Returns:
        True if successful, False otherwise
    """
    if meme.template_id not in TEMPLATE_GENERATORS:
        print(f"Unknown template: {meme.template_id}")
        return False

    config = TEMPLATE_GENERATORS[meme.template_id]
    func = config["function"]
    args_map = config["args_map"]

    # Extract arguments in order
    args = []
    for arg_name in args_map:
        value = meme.text_content.get(arg_name, "")
        args.append(value)

    try:
        # Call the generator function
        func(*args, output_path, meme.category.value)
        return True
    except Exception as e:
        print(f"Error rendering {meme.template_id}: {e}")
        return False


def render_batch(
    batch: BatchMemeOutput,
    output_subdir: Optional[str] = None
) -> List[Path]:
    """Render all memes in a batch.

    Args:
        batch: BatchMemeOutput with list of GeneratedMeme
        output_subdir: Optional subdirectory name. If None, uses "llm_generated"

    Returns:
        List of paths to successfully rendered memes
    """
    ensure_output_dirs()

    if output_subdir:
        base_dir = OUTPUT_DIR / output_subdir
        base_dir.mkdir(parents=True, exist_ok=True)
    else:
        base_dir = OUTPUT_DIR / "llm_generated"

    rendered_paths = []

    for idx, meme in enumerate(batch.memes, start=1):
        # Determine output directory based on category
        if output_subdir:
            category_dir = base_dir
        else:
            category_dir = base_dir / meme.category.value

        category_dir.mkdir(parents=True, exist_ok=True)

        filename = generate_filename(meme, idx)
        output_path = category_dir / filename

        if render_meme(meme, output_path):
            rendered_paths.append(output_path)

    return rendered_paths


def render_memes_by_category(
    batch: BatchMemeOutput,
) -> dict:
    """Render memes into category-specific folders.

    Args:
        batch: BatchMemeOutput with list of GeneratedMeme

    Returns:
        Dict mapping category to list of rendered paths
    """
    ensure_output_dirs()

    result = {
        "pro_obaa": [],
        "anti_sinners": [],
    }

    pro_idx = 1
    anti_idx = 1

    for meme in batch.memes:
        if meme.category == MemeCategory.PRO_OBAA:
            output_dir = OUTPUT_DIR / "pro_obaa"
            idx = pro_idx
            pro_idx += 1
        else:
            output_dir = OUTPUT_DIR / "anti_sinners"
            idx = anti_idx
            anti_idx += 1

        filename = generate_filename(meme, idx)
        output_path = output_dir / filename

        if render_meme(meme, output_path):
            result[meme.category.value].append(output_path)

    return result


class MemeRenderer:
    """High-level meme rendering interface."""

    def __init__(self, pipeline, output_dir: Optional[Path] = None):
        """Initialize the renderer.

        Args:
            pipeline: MemeGenerationPipeline instance
            output_dir: Custom output directory. Defaults to standard OUTPUT_DIR.
        """
        self.pipeline = pipeline
        self.output_dir = output_dir or OUTPUT_DIR
        ensure_output_dirs()

    async def generate_and_render(
        self,
        category: MemeCategory,
        templates: Optional[List[str]] = None,
        num_memes: int = 10,
    ) -> dict:
        """Generate memes with LLM and render them.

        Args:
            category: PRO_OBAA or ANTI_SINNERS
            templates: List of template IDs to use
            num_memes: Number of memes to generate

        Returns:
            Dict with 'memes' (GeneratedMeme list) and 'paths' (rendered file paths)
        """
        from .models import MemeGenerationRequest

        request = MemeGenerationRequest(
            category=category,
            templates=templates,
            num_memes=num_memes,
        )

        batch = await self.pipeline.generate_batch(request)
        paths = render_batch(batch)

        return {
            "memes": batch.memes,
            "paths": paths,
            "total": batch.total_generated,
        }

    async def generate_campaign(
        self,
        templates: Optional[List[str]] = None,
        num_per_category: int = 10,
    ) -> dict:
        """Generate a full campaign with memes for both categories.

        Args:
            templates: List of template IDs to use
            num_per_category: Number of memes per category

        Returns:
            Dict with rendered paths organized by category
        """
        batch = await self.pipeline.generate_for_both_categories(
            templates=templates,
            num_per_category=num_per_category,
        )

        return render_memes_by_category(batch)


# Utility function for quick rendering
def quick_render(
    template_id: str,
    text_content: dict,
    category: str = "pro_obaa",
    output_filename: Optional[str] = None,
) -> Path:
    """Quick render a single meme without using the full pipeline.

    Useful for testing or manual meme creation.

    Args:
        template_id: ID of the template to use
        text_content: Dict of text slot values
        category: "pro_obaa" or "anti_sinners"
        output_filename: Optional custom filename

    Returns:
        Path to the rendered meme
    """
    ensure_output_dirs()

    meme = GeneratedMeme(
        template_id=template_id,
        category=MemeCategory(category),
        text_content=text_content,
        confidence_score=1.0,
    )

    if output_filename:
        output_path = OUTPUT_DIR / category / output_filename
    else:
        output_path = OUTPUT_DIR / category / generate_filename(meme, 1)

    render_meme(meme, output_path)
    return output_path
