"""Base class for template processing agents."""

import base64
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypeVar, Generic, Type, Optional

from openai import OpenAI
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseTemplateAgent(ABC, Generic[T]):
    """Base class for all template processing agents.

    Each agent:
    - Has a single focused responsibility
    - Uses vision capabilities to analyze template images
    - Returns structured Pydantic output
    """

    def __init__(
        self,
        client: Optional[OpenAI] = None,
        model: str = "gpt-4o",
    ):
        """Initialize the agent.

        Args:
            client: OpenAI client instance. If None, creates one from env.
            model: Model to use for LLM calls (must support vision).
        """
        self.client = client or OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for this agent."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what this agent does."""
        pass

    @property
    @abstractmethod
    def output_model(self) -> Type[T]:
        """Pydantic model class for structured output."""
        pass

    @abstractmethod
    def build_prompt(self, image_path: str, **context) -> str:
        """Build the prompt for this agent.

        Args:
            image_path: Path to the template image.
            **context: Additional context from previous agents.

        Returns:
            The prompt string to send to the LLM.
        """
        pass

    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 for vision API.

        Args:
            image_path: Path to the image file.

        Returns:
            Base64 encoded image string.
        """
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def get_image_media_type(self, image_path: str) -> str:
        """Get the media type for an image file.

        Args:
            image_path: Path to the image file.

        Returns:
            Media type string (e.g., 'image/png').
        """
        ext = Path(image_path).suffix.lower()
        media_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        return media_types.get(ext, "image/png")

    async def run(self, image_path: str, **context) -> T:
        """Execute this agent.

        Args:
            image_path: Path to the template image.
            **context: Additional context from previous agents.

        Returns:
            Structured output as the agent's output_model type.
        """
        prompt = self.build_prompt(image_path, **context)

        # Encode image for vision
        image_data = self.encode_image(image_path)
        media_type = self.get_image_media_type(image_path)

        # Build messages with image
        messages = [
            {
                "role": "system",
                "content": f"You are {self.name}. {self.description}"
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{image_data}"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]

        # Call LLM with structured output
        response = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=messages,
            response_format=self.output_model,
        )

        return response.choices[0].message.parsed

    def run_sync(self, image_path: str, **context) -> T:
        """Synchronous version of run for simpler usage.

        Args:
            image_path: Path to the template image.
            **context: Additional context from previous agents.

        Returns:
            Structured output as the agent's output_model type.
        """
        import asyncio
        return asyncio.run(self.run(image_path, **context))


class MockTemplateAgent(BaseTemplateAgent[T]):
    """Mock agent for testing without LLM calls."""

    def __init__(self, mock_response: T, **kwargs):
        """Initialize with a mock response.

        Args:
            mock_response: The response to return from run().
        """
        self._mock_response = mock_response
        self._name = "Mock Agent"
        self._description = "A mock agent for testing"
        self._output_model = type(mock_response)

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def output_model(self) -> Type[T]:
        return self._output_model

    def build_prompt(self, image_path: str, **context) -> str:
        return "mock prompt"

    async def run(self, image_path: str, **context) -> T:
        return self._mock_response
