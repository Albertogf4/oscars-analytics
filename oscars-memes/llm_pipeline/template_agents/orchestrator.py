"""Template Orchestrator - Chains all agents to process a new meme template."""

import os
from pathlib import Path
from typing import AsyncGenerator, Optional, Callable

from openai import OpenAI

from .models import (
    VisualAnalysis,
    SlotDetection,
    IronyAnalysis,
    TemplateMetadata,
    ExampleContent,
    PromptContent,
    GeneratedCode,
    TemplateProcessingResult,
    ProcessingUpdate,
)
from .visual_agent import VisualAnalysisAgent
from .slot_agent import SlotDetectionAgent
from .irony_agent import IronyAnalysisAgent
from .metadata_agent import MetadataGenerationAgent
from .example_agent import ExampleGenerationAgent
from .prompt_agent import PromptWritingAgent
from .code_agent import CodeGenerationAgent


class TemplateOrchestrator:
    """Orchestrates the 7-agent pipeline for processing new meme templates.

    The pipeline runs agents in sequence:
    1. Visual Analysis Agent - Understand the image structure
    2. Slot Detection Agent - Identify text placement areas
    3. Irony Analysis Agent (DEDICATED) - Deep humor/irony analysis
    4. Metadata Generation Agent - Create consistent naming
    5. Example Generation Agent - Generate example content
    6. Prompt Writing Agent - Write the template-specific prompt
    7. Code Generation Agent - Generate Python code
    """

    STAGES = [
        ("visual", "Visual Analysis"),
        ("slots", "Slot Detection"),
        ("irony", "Irony Analysis"),
        ("metadata", "Metadata Generation"),
        ("examples", "Example Generation"),
        ("prompt", "Prompt Writing"),
        ("code", "Code Generation"),
    ]

    def __init__(
        self,
        client: Optional[OpenAI] = None,
        model: str = "gpt-4o",
        on_stage_complete: Optional[Callable[[str, any], None]] = None,
    ):
        """Initialize the orchestrator with all agents.

        Args:
            client: OpenAI client instance. If None, creates one from env.
            model: Model to use for all agents.
            on_stage_complete: Optional callback when each stage completes.
        """
        self.client = client or OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.on_stage_complete = on_stage_complete

        # Initialize all agents
        self.visual_agent = VisualAnalysisAgent(client=self.client, model=model)
        self.slot_agent = SlotDetectionAgent(client=self.client, model=model)
        self.irony_agent = IronyAnalysisAgent(client=self.client, model=model)
        self.metadata_agent = MetadataGenerationAgent(client=self.client, model=model)
        self.example_agent = ExampleGenerationAgent(client=self.client, model=model)
        self.prompt_agent = PromptWritingAgent(client=self.client, model=model)
        self.code_agent = CodeGenerationAgent(client=self.client, model=model)

    async def process(
        self,
        image_path: str,
    ) -> TemplateProcessingResult:
        """Process a template image through all agents.

        Args:
            image_path: Path to the template image file.

        Returns:
            TemplateProcessingResult with all agent outputs.
        """
        # Validate image exists
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Template image not found: {image_path}")

        # Stage 1: Visual Analysis
        visual = await self.visual_agent.run(image_path)
        if self.on_stage_complete:
            self.on_stage_complete("visual", visual)

        # Stage 2: Slot Detection
        slots = await self.slot_agent.run(
            image_path,
            visual_analysis=visual,
        )
        if self.on_stage_complete:
            self.on_stage_complete("slots", slots)

        # Stage 3: Irony Analysis (CRITICAL)
        irony = await self.irony_agent.run(
            image_path,
            visual_analysis=visual,
        )
        if self.on_stage_complete:
            self.on_stage_complete("irony", irony)

        # Stage 4: Metadata Generation
        metadata = await self.metadata_agent.run(
            image_path,
            visual_analysis=visual,
            slot_detection=slots,
            irony_analysis=irony,
        )
        if self.on_stage_complete:
            self.on_stage_complete("metadata", metadata)

        # Stage 5: Example Generation
        examples = await self.example_agent.run(
            image_path,
            slot_detection=slots,
            irony_analysis=irony,
            metadata=metadata,
        )
        if self.on_stage_complete:
            self.on_stage_complete("examples", examples)

        # Stage 6: Prompt Writing
        prompt = await self.prompt_agent.run(
            image_path,
            visual_analysis=visual,
            slot_detection=slots,
            irony_analysis=irony,
            metadata=metadata,
            examples=examples,
        )
        if self.on_stage_complete:
            self.on_stage_complete("prompt", prompt)

        # Stage 7: Code Generation
        code = await self.code_agent.run(
            image_path,
            slot_detection=slots,
            irony_analysis=irony,
            metadata=metadata,
        )
        if self.on_stage_complete:
            self.on_stage_complete("code", code)

        # Build complete result
        result = TemplateProcessingResult(
            visual_analysis=visual,
            slot_detection=slots,
            irony_analysis=irony,
            metadata=metadata,
            examples=examples,
            prompt=prompt,
            code=code,
        )

        # Build the template registry entry
        result.template_registry_entry = result.build_registry_entry()

        return result

    async def process_with_updates(
        self,
        image_path: str,
    ) -> AsyncGenerator[ProcessingUpdate, None]:
        """Process template with streaming status updates.

        Args:
            image_path: Path to the template image file.

        Yields:
            ProcessingUpdate objects as each stage completes.
        """
        path = Path(image_path)
        if not path.exists():
            yield ProcessingUpdate(
                stage="validation",
                status="failed",
                error=f"Template image not found: {image_path}",
            )
            return

        total_stages = len(self.STAGES)
        results = {}

        for i, (stage_id, stage_name) in enumerate(self.STAGES):
            progress = int((i / total_stages) * 100)

            # Emit running status
            yield ProcessingUpdate(
                stage=stage_id,
                status="running",
                progress_percent=progress,
            )

            try:
                # Run the appropriate agent
                if stage_id == "visual":
                    result = await self.visual_agent.run(image_path)
                elif stage_id == "slots":
                    result = await self.slot_agent.run(
                        image_path,
                        visual_analysis=results.get("visual"),
                    )
                elif stage_id == "irony":
                    result = await self.irony_agent.run(
                        image_path,
                        visual_analysis=results.get("visual"),
                    )
                elif stage_id == "metadata":
                    result = await self.metadata_agent.run(
                        image_path,
                        visual_analysis=results.get("visual"),
                        slot_detection=results.get("slots"),
                        irony_analysis=results.get("irony"),
                    )
                elif stage_id == "examples":
                    result = await self.example_agent.run(
                        image_path,
                        slot_detection=results.get("slots"),
                        irony_analysis=results.get("irony"),
                        metadata=results.get("metadata"),
                    )
                elif stage_id == "prompt":
                    result = await self.prompt_agent.run(
                        image_path,
                        visual_analysis=results.get("visual"),
                        slot_detection=results.get("slots"),
                        irony_analysis=results.get("irony"),
                        metadata=results.get("metadata"),
                        examples=results.get("examples"),
                    )
                elif stage_id == "code":
                    result = await self.code_agent.run(
                        image_path,
                        slot_detection=results.get("slots"),
                        irony_analysis=results.get("irony"),
                        metadata=results.get("metadata"),
                    )
                else:
                    raise ValueError(f"Unknown stage: {stage_id}")

                results[stage_id] = result

                # Emit completed status with result
                yield ProcessingUpdate(
                    stage=stage_id,
                    status="completed",
                    result=result.model_dump(),
                    progress_percent=int(((i + 1) / total_stages) * 100),
                )

            except Exception as e:
                yield ProcessingUpdate(
                    stage=stage_id,
                    status="failed",
                    error=str(e),
                    progress_percent=progress,
                )
                return

        # Build final result
        final_result = TemplateProcessingResult(
            visual_analysis=results["visual"],
            slot_detection=results["slots"],
            irony_analysis=results["irony"],
            metadata=results["metadata"],
            examples=results["examples"],
            prompt=results["prompt"],
            code=results["code"],
        )
        final_result.template_registry_entry = final_result.build_registry_entry()

        yield ProcessingUpdate(
            stage="complete",
            status="completed",
            result=final_result.model_dump(),
            progress_percent=100,
        )

    def process_sync(self, image_path: str) -> TemplateProcessingResult:
        """Synchronous version of process for simpler usage.

        Args:
            image_path: Path to the template image file.

        Returns:
            TemplateProcessingResult with all agent outputs.
        """
        import asyncio
        return asyncio.run(self.process(image_path))
