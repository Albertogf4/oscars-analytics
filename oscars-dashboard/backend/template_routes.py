"""FastAPI routes for meme template processing and management."""

import asyncio
import os
import sys
import uuid
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# Add oscars-memes to path for imports
MEMES_DIR = Path(__file__).parent.parent.parent / "oscars-memes"
sys.path.insert(0, str(MEMES_DIR))

from llm_pipeline import MEME_TEMPLATES
from llm_pipeline.template_agents import (
    TemplateOrchestrator,
    TemplateProcessingResult,
)
from llm_pipeline.template_integrator import TemplateIntegrator

# Paths
TEMPLATE_IMAGE_DIR = Path(__file__).parent.parent.parent / "MemeTemplate"
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

router = APIRouter(prefix="/api/templates", tags=["templates"])

# In-memory storage for processing jobs (in production, use Redis or database)
processing_jobs: Dict[str, Dict[str, Any]] = {}


# === Request/Response Models ===

class TemplateInfo(BaseModel):
    """Template information for listing."""
    id: str
    name: str
    filename: str
    text_slots: int
    slot_names: list[str]
    irony_type: str
    description: str
    max_chars_per_slot: int
    thumbnail_url: Optional[str] = None


class TemplateListResponse(BaseModel):
    """Response for listing all templates."""
    templates: list[TemplateInfo]
    total: int


class ProcessingStatus(BaseModel):
    """Status of a template processing job."""
    job_id: str
    status: str  # "pending", "running", "completed", "failed"
    current_stage: Optional[str] = None
    progress_percent: int = 0
    stages_completed: list[str] = Field(default_factory=list)
    result: Optional[dict] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class FinalizeRequest(BaseModel):
    """Request to finalize and integrate a processed template."""
    job_id: str
    metadata_overrides: Optional[dict] = None  # User can override generated metadata


class FinalizeResponse(BaseModel):
    """Response from template finalization."""
    success: bool
    template_id: str
    integration_status: dict
    message: str


# === Endpoints ===

@router.get("", response_model=TemplateListResponse)
async def list_templates():
    """List all available meme templates."""
    templates = []
    for template_id, template_data in MEME_TEMPLATES.items():
        templates.append(TemplateInfo(
            id=template_data["id"],
            name=template_data["name"],
            filename=template_data["filename"],
            text_slots=template_data["text_slots"],
            slot_names=template_data["slot_names"],
            irony_type=template_data["irony_type"],
            description=template_data["description"],
            max_chars_per_slot=template_data["max_chars_per_slot"],
            thumbnail_url=f"/templates/{template_data['filename']}",
        ))

    return TemplateListResponse(
        templates=templates,
        total=len(templates),
    )


@router.post("/upload")
async def upload_template(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """Upload a new template image and start processing.

    Returns a job_id that can be used to track processing status.
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image (PNG, JPG, etc.)",
        )

    # Generate job ID
    job_id = str(uuid.uuid4())

    # Save uploaded file
    upload_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
    with open(upload_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Initialize job status
    now = datetime.now(timezone.utc)
    processing_jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "current_stage": None,
        "progress_percent": 0,
        "stages_completed": [],
        "result": None,
        "error": None,
        "created_at": now,
        "updated_at": now,
        "image_path": str(upload_path),
        "original_filename": file.filename,
    }

    # Start processing in background
    background_tasks.add_task(process_template_job, job_id, str(upload_path))

    return {
        "job_id": job_id,
        "status": "pending",
        "message": "Template upload successful. Processing started.",
    }


async def process_template_job(job_id: str, image_path: str):
    """Background task to process a template through all agents."""
    job = processing_jobs.get(job_id)
    if not job:
        return

    job["status"] = "running"
    job["updated_at"] = datetime.now(timezone.utc)

    try:
        # Check if OpenAI API key is available
        if not os.getenv("OPENAI_API_KEY"):
            job["status"] = "failed"
            job["error"] = "OpenAI API key not configured. Set OPENAI_API_KEY environment variable."
            job["updated_at"] = datetime.now(timezone.utc)
            return

        # Create orchestrator with progress callback
        def on_stage_complete(stage: str, result: Any):
            job["stages_completed"].append(stage)
            job["current_stage"] = stage
            stage_index = len(job["stages_completed"])
            job["progress_percent"] = int((stage_index / 7) * 100)
            job["updated_at"] = datetime.now(timezone.utc)

        orchestrator = TemplateOrchestrator(
            on_stage_complete=on_stage_complete,
        )

        # Run the processing pipeline
        result = await orchestrator.process(image_path)

        # Store result
        job["status"] = "completed"
        job["progress_percent"] = 100
        job["result"] = result.model_dump()
        job["updated_at"] = datetime.now(timezone.utc)

    except Exception as e:
        job["status"] = "failed"
        job["error"] = str(e)
        job["updated_at"] = datetime.now(timezone.utc)


@router.get("/process/{job_id}", response_model=ProcessingStatus)
async def get_processing_status(job_id: str):
    """Get the status of a template processing job."""
    job = processing_jobs.get(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found",
        )

    return ProcessingStatus(
        job_id=job["job_id"],
        status=job["status"],
        current_stage=job.get("current_stage"),
        progress_percent=job.get("progress_percent", 0),
        stages_completed=job.get("stages_completed", []),
        result=job.get("result"),
        error=job.get("error"),
        created_at=job["created_at"],
        updated_at=job["updated_at"],
    )


@router.post("/finalize", response_model=FinalizeResponse)
async def finalize_template(request: FinalizeRequest):
    """Finalize and integrate a processed template into the pipeline."""
    job = processing_jobs.get(request.job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job {request.job_id} not found",
        )

    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job is not completed. Current status: {job['status']}",
        )

    if not job.get("result"):
        raise HTTPException(
            status_code=400,
            detail="No processing result available",
        )

    try:
        # Reconstruct the result object
        result_data = job["result"]

        # Apply any user overrides to metadata
        if request.metadata_overrides:
            if "id" in request.metadata_overrides:
                result_data["metadata"]["id"] = request.metadata_overrides["id"]
            if "name" in request.metadata_overrides:
                result_data["metadata"]["name"] = request.metadata_overrides["name"]
            if "description" in request.metadata_overrides:
                result_data["metadata"]["description"] = request.metadata_overrides["description"]

        # Create result object
        result = TemplateProcessingResult(**result_data)

        # Copy template image to MemeTemplate directory
        source_path = Path(job["image_path"])
        dest_filename = result.metadata.filename
        dest_path = TEMPLATE_IMAGE_DIR / dest_filename

        if source_path.exists():
            shutil.copy2(source_path, dest_path)

        # Integrate into pipeline files
        integrator = TemplateIntegrator()
        integration_status = integrator.integrate(result)

        # Check if integration was successful
        integration_success = all(v is True for v in integration_status.values() if isinstance(v, bool))

        # Update in-memory MEME_TEMPLATES so template is immediately available
        if integration_success:
            registry_entry = result.build_registry_entry()
            MEME_TEMPLATES[result.metadata.id] = registry_entry

        # Clean up upload
        if source_path.exists():
            source_path.unlink()

        return FinalizeResponse(
            success=integration_success,
            template_id=result.metadata.id,
            integration_status=integration_status,
            message=f"Template '{result.metadata.name}' integrated successfully" if integration_success else f"Template integration failed",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to finalize template: {str(e)}",
        )


@router.delete("/{template_id}")
async def delete_template(template_id: str):
    """Delete a template from the system.

    Note: This only removes from in-memory registry.
    For full removal, manual file edits are needed.
    """
    if template_id not in MEME_TEMPLATES:
        raise HTTPException(
            status_code=404,
            detail=f"Template '{template_id}' not found",
        )

    # For safety, we don't actually delete files
    # Just return info about what would need to be manually deleted
    return {
        "message": f"Template '{template_id}' marked for deletion",
        "manual_steps": [
            f"Remove entry from templates.py MEME_TEMPLATES['{template_id}']",
            f"Remove entry from prompts.py TEMPLATE_SPECIFIC_PROMPTS['{template_id}']",
            f"Remove Pydantic model from models.py",
            f"Remove generator function from meme_generator.py",
            f"Remove entry from generator.py TEMPLATE_GENERATORS",
            f"Remove entry from pipeline.py TEMPLATE_OUTPUT_MODELS",
        ],
    }


@router.get("/{template_id}/preview")
async def preview_template(template_id: str):
    """Get detailed information about a template for preview."""
    if template_id not in MEME_TEMPLATES:
        raise HTTPException(
            status_code=404,
            detail=f"Template '{template_id}' not found",
        )

    template = MEME_TEMPLATES[template_id]

    return {
        "id": template["id"],
        "name": template["name"],
        "filename": template["filename"],
        "text_slots": template["text_slots"],
        "slot_names": template["slot_names"],
        "irony_type": template["irony_type"],
        "description": template["description"],
        "tone": template["tone"],
        "max_chars_per_slot": template["max_chars_per_slot"],
        "example": template["example"],
        "image_url": f"/templates/{template['filename']}",
    }
