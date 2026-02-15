"""OpenAI LLM client for structured meme generation."""

import os
from typing import Type
from pydantic import BaseModel

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAIClient:
    """Real OpenAI client with structured outputs for meme generation."""

    def __init__(self, api_key: str = None):
        """Initialize the OpenAI client.

        Args:
            api_key: OpenAI API key. Falls back to OPENAI_API_KEY env var.

        Raises:
            ValueError: If no API key is found.
            ImportError: If openai package is not installed.
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package not installed. Run: pip install openai")

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        self.client = AsyncOpenAI(api_key=self.api_key)

    async def _call_llm(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        response_format: Type[BaseModel]
    ) -> BaseModel:
        """Call OpenAI with structured output parsing.

        Args:
            model: Model name (e.g., "gpt-4o-mini")
            system_prompt: System prompt string
            user_prompt: User prompt string
            response_format: Pydantic model class for structured output

        Returns:
            Instance of response_format with generated content
        """
        response = await self.client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=response_format,
        )
        return response.choices[0].message.parsed


def get_llm_client():
    """Get the appropriate LLM client based on environment.

    Returns OpenAIClient if API key is available, otherwise returns None.
    The caller should handle the fallback to MockLLMClient.
    """
    try:
        return OpenAIClient()
    except (ImportError, ValueError) as e:
        print(f"OpenAI client not available: {e}")
        return None
