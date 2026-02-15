"""Template agents for extracting meme template information."""

from .models import (
    ImageDimensions,
    VisualAnalysis,
    SlotDetection,
    IronyAnalysis,
    TemplateMetadata,
    SlotExample,
    ExampleContent,
    PromptContent,
    GeneratedCode,
    TemplateProcessingResult,
)
from .base_agent import BaseTemplateAgent
from .visual_agent import VisualAnalysisAgent
from .slot_agent import SlotDetectionAgent
from .irony_agent import IronyAnalysisAgent
from .metadata_agent import MetadataGenerationAgent
from .example_agent import ExampleGenerationAgent
from .prompt_agent import PromptWritingAgent
from .code_agent import CodeGenerationAgent
from .orchestrator import TemplateOrchestrator

__all__ = [
    # Models
    "ImageDimensions",
    "VisualAnalysis",
    "SlotDetection",
    "IronyAnalysis",
    "TemplateMetadata",
    "SlotExample",
    "ExampleContent",
    "PromptContent",
    "GeneratedCode",
    "TemplateProcessingResult",
    # Agents
    "BaseTemplateAgent",
    "VisualAnalysisAgent",
    "SlotDetectionAgent",
    "IronyAnalysisAgent",
    "MetadataGenerationAgent",
    "ExampleGenerationAgent",
    "PromptWritingAgent",
    "CodeGenerationAgent",
    # Orchestrator
    "TemplateOrchestrator",
]
