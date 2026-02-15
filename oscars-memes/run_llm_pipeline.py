#!/usr/bin/env python3
"""
Example script demonstrating the LLM meme generation pipeline.

This script shows how to:
1. Set up the pipeline with your LLM client
2. Generate memes for a specific category
3. Generate a full campaign (both categories)
4. Render the generated memes to images

Usage:
    python run_llm_pipeline.py
"""

import asyncio
from pathlib import Path

# Import the pipeline components
from llm_pipeline import (
    MemeGenerationPipeline,
    CommentDatabase,
    MemeGenerationRequest,
    MemeCategory,
    MEME_TEMPLATES,
)
from llm_pipeline.generator import MemeRenderer, quick_render


# =============================================================================
# Example LLM Client (Replace with your actual implementation)
# =============================================================================

class MockLLMClient:
    """Mock LLM client for demonstration purposes.

    Replace this with your actual LLM wrapper that has the signature:
    async def _call_llm(self, model, system_prompt, user_prompt, response_format)
    """

    async def _call_llm(self, model, system_prompt, user_prompt, response_format):
        """Mock LLM call that returns example responses based on template."""

        # Get the field names from the response model
        fields = response_format.model_fields.keys()

        # Generate mock content based on field names
        mock_values = {}
        for field in fields:
            if field == "reasoning":
                mock_values[field] = "This meme effectively captures the campaign sentiment."
            elif "reject" in field:
                mock_values[field] = "Generic Oscar bait movies"
            elif "approve" in field:
                mock_values[field] = "One Battle After Another"
            elif "strong" in field:
                mock_values[field] = "OBAA cinematography"
            elif "weak" in field:
                mock_values[field] = "Sinners CGI"
            elif "medium" in field:
                mock_values[field] = "Average drama"
            elif "chad" in field:
                mock_values[field] = "OBAA enjoyer"
            elif "wojak" in field:
                mock_values[field] = "'Sinners is so deep bro'"
            elif "top" in field:
                mock_values[field] = "Can't be overrated"
            elif "bottom" in field:
                mock_values[field] = "If you get 16 nominations"
            elif "happy" in field:
                mock_values[field] = "New Oscar contender!"
            elif "concerned" in field:
                mock_values[field] = "It's 3 hours long"
            elif "want" in field:
                mock_values[field] = "Watching OBAA again"
            elif "holding" in field:
                mock_values[field] = "Responsibilities"
            elif "button1" in field:
                mock_values[field] = "Admit it's mid"
            elif "button2" in field:
                mock_values[field] = "Defend the hype"
            elif "caption" in field:
                mock_values[field] = "When Sinners gets 16 nominations"
            else:
                mock_values[field] = "Example meme text"

        return response_format(**mock_values)


# =============================================================================
# Integration with Your LLM Client
# =============================================================================

class YourLLMClient:
    """Template for integrating your actual LLM client.

    Modify this class to work with your LLM wrapper.
    The key requirement is the _call_llm method signature.
    """

    def __init__(self, api_key: str = None):
        # Initialize your LLM client here
        # e.g., self.client = OpenAI(api_key=api_key)
        pass

    async def _call_llm(self, model, system_prompt, user_prompt, response_format):
        """Call the LLM with structured output.

        Args:
            model: Model name (e.g., "gpt-4o-mini")
            system_prompt: System prompt string
            user_prompt: User prompt string
            response_format: Pydantic model class for structured output

        Returns:
            Instance of response_format with generated content
        """
        # Example implementation with OpenAI:
        #
        # response = await self.client.beta.chat.completions.parse(
        #     model=model,
        #     messages=[
        #         {"role": "system", "content": system_prompt},
        #         {"role": "user", "content": user_prompt},
        #     ],
        #     response_format=response_format,
        # )
        # return response.choices[0].message.parsed

        raise NotImplementedError("Replace with your LLM implementation")


# =============================================================================
# Example Usage
# =============================================================================

async def demo_pipeline():
    """Demonstrate the meme generation pipeline."""

    print("=" * 60)
    print("LLM Meme Generation Pipeline Demo")
    print("=" * 60)

    # 1. Initialize components
    print("\n1. Initializing components...")
    llm_client = MockLLMClient()  # Replace with YourLLMClient()
    comment_db = CommentDatabase()
    pipeline = MemeGenerationPipeline(llm_client, comment_db)

    # 2. Show available templates
    print("\n2. Available templates:")
    for tid, template in MEME_TEMPLATES.items():
        print(f"   - {tid}: {template['name']} ({template['text_slots']} slots)")

    # 3. Test comment database
    print("\n3. Testing comment database...")
    try:
        neg_comments = comment_db.get_negative_comments("sinners", limit=3)
        print(f"   Found {len(neg_comments)} negative comments about Sinners")
        if neg_comments:
            print(f"   Sample: \"{neg_comments[0][:60]}...\"")
    except FileNotFoundError as e:
        print(f"   Note: {e}")

    # 4. Generate single meme
    print("\n4. Generating single meme (Drake template)...")
    from llm_pipeline.models import MemeContext

    context = MemeContext(
        target_movie_positive_comments=["OBAA is incredible", "Best film of the year"],
        competitor_negative_comments=["Sinners was disappointing", "Overhyped"],
        key_themes=["oscar", "nominations", "quality"],
        campaign_goal="Boost OBAA",
    )

    meme = await pipeline.generate_meme(
        template_id="drake",
        category=MemeCategory.PRO_OBAA,
        context=context,
    )

    print(f"   Template: {meme.template_id}")
    print(f"   Category: {meme.category.value}")
    print(f"   Text content: {meme.text_content}")
    print(f"   Confidence: {meme.confidence_score:.2f}")

    # 5. Generate batch
    print("\n5. Generating batch of memes...")
    request = MemeGenerationRequest(
        category=MemeCategory.PRO_OBAA,
        templates=["drake", "strong_doge", "rollsafe"],
        num_memes=3,
    )

    batch = await pipeline.generate_batch(request)
    print(f"   Generated {batch.total_generated} memes")
    for m in batch.memes:
        print(f"   - {m.template_id}: {list(m.text_content.values())[:2]}")

    # 6. Render memes to images
    print("\n6. Rendering memes to images...")
    from llm_pipeline.generator import render_batch

    paths = render_batch(batch)
    print(f"   Rendered {len(paths)} memes:")
    for p in paths:
        print(f"   - {p}")

    # 7. Quick render example
    print("\n7. Quick render (manual meme creation)...")
    output = quick_render(
        template_id="disbelief",
        text_content={"caption": "When the LLM pipeline works perfectly"},
        category="pro_obaa",
        output_filename="test_quick_render.png",
    )
    print(f"   Created: {output}")

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


async def generate_full_campaign():
    """Generate a full campaign with both PRO_OBAA and ANTI_SINNERS memes."""

    print("Generating full meme campaign...")

    llm_client = MockLLMClient()  # Replace with your actual client
    pipeline = MemeGenerationPipeline(llm_client)
    renderer = MemeRenderer(pipeline)

    result = await renderer.generate_campaign(
        templates=None,  # Use all templates
        num_per_category=12,  # 12 memes per category
    )

    print(f"\nPro-OBAA memes: {len(result['pro_obaa'])}")
    print(f"Anti-Sinners memes: {len(result['anti_sinners'])}")

    return result


if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_pipeline())

    # Uncomment to generate full campaign:
    # asyncio.run(generate_full_campaign())
