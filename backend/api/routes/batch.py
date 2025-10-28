"""Batch processing endpoints for Multi-Agent NF-e System

This module implements the batch processing API endpoints that allow users
to upload and process multiple NF-e XML files in batch mode.

Requirements satisfied:
- 7.5: REST API endpoint for batch upload
- 1.1: Process multiple XML files from xml_nf folder
- 1.2: Process files using existing db.py logic
- 1.3: Record successful imports
- 1.4: Record errors and continue processing
- 1.5: Generate report with successes and failures
"""

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from datetime import datetime
from typing import Optional
import asyncio

from api.models.requests import BatchUploadRequest
from api.models.responses import (
    BatchUploadResponse,
    BatchStatusResponse,
    BatchJobStatus
)
from batch.processor import BatchProcessor
from batch.job_manager import get_job_manager, JobManager
from utils.exceptions import (
    AppException,
    BatchProcessingException,
    ValidationException
)
from utils.logger import get_logger

logger = get_logger(__name__)

# Initialize router
router = APIRouter(prefix="/api/batch", tags=["batch"])

# Global instances
batch_processor: Optional[BatchProcessor] = None
job_manager: Optional[JobManager] = None


def initialize_batch_services(processor: BatchProcessor, manager: JobManager):
    """Initialize batch services with processor and job manager instances
    
    This function should be called during application startup to inject
    the BatchProcessor and JobManager dependencies.
    
    Args:
        processor: Initialized BatchProcessor instance
        manager: Initialized JobManager instance
    """
    global batch_processor, job_manager
    batch_processor = processor
    job_manager = manager
    
    logger.info(
        "batch_services_initialized",
        processor_initialized=batch_processor is not None,
        manager_initialized=job_manager is not None
    )


async def _run_batch_processing(
    job_id: str,
    folder_path: str,
    max_concurrent: Optional[int] = None
):
    """Background task to run batch processing
    
    This function runs the actual batch processing in the background,
    allowing the API to return immediately with the job ID.
    
    Args:
        job_id: Unique job identifier
        folder_path: Path to folder containing XML files
        max_concurrent: Optional max concurrent uploads
    """
    try:
        logger.info(
            "background_batch_processing_started",
            job_id=job_id,
            folder_path=folder_path
        )
        
        # Create processor with custom concurrency if specified
        processor = batch_processor
        if max_concurrent is not None:
            processor = BatchProcessor(max_concurrent=max_concurrent)
        
        # Run batch processing
        result = await processor.process_folder(
            folder_path=folder_path,
            job_id=job_id
        )
        
        logger.info(
            "background_batch_processing_completed",
            job_id=job_id,
            successful=result.get("successful", 0),
            failed=result.get("failed", 0)
        )
        
    except Exception as e:
        logger.exception(
            "background_batch_processing_failed",
            e,
            job_id=job_id
        )


@router.post(
    "/upload",
    response_model=BatchUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start batch XML processing",
    description="""
    Start processing multiple NF-e XML files from a specified folder.
    
    The system will:
    1. Locate all XML files in the specified folder
    2. Process each file using the existing import logic from db.py
    3. Track successes and failures
    4. Continue processing even if individual files fail
    5. Generate a comprehensive report
    
    Processing happens asynchronously in the background. Use the returned
    job_id to check the status via GET /api/batch/status/{job_id}.
    
    Requirements:
    - 7.5: REST API endpoint for batch upload
    - 1.1: Process multiple XML files from folder
    - 1.2: Uses existing SupabaseNFeImporter logic
    - 1.3: Records successful imports
    - 1.4: Records errors and continues processing
    - 1.5: Generates report with successes and failures
    """,
    responses={
        202: {
            "description": "Batch processing started successfully",
            "content": {
                "application/json": {
                    "example": {
                        "job_id": "batch-20251027-103000-abc123",
                        "status": "running",
                        "total_files": 10,
                        "successful": 0,
                        "failed": 0,
                        "errors": [],
                        "duration_seconds": None,
                        "started_at": "2025-10-27T10:30:00",
                        "completed_at": None
                    }
                }
            }
        },
        400: {"description": "Invalid request data or folder not found"},
        500: {"description": "Internal server error"}
    }
)
async def start_batch_upload(
    request: BatchUploadRequest,
    background_tasks: BackgroundTasks
) -> BatchUploadResponse:
    """Start batch processing of XML files
    
    Requirements:
    - 7.5: REST API endpoint for batch upload
    - 1.1: Process multiple XML files from xml_nf folder
    
    Args:
        request: BatchUploadRequest with folder path and options
        background_tasks: FastAPI background tasks manager
        
    Returns:
        BatchUploadResponse with job details and initial status
        
    Raises:
        HTTPException: If services not initialized or validation fails
    """
    # Validate services are initialized
    if batch_processor is None or job_manager is None:
        logger.error("batch_services_not_initialized")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch services not initialized"
        )
    
    logger.info(
        "batch_upload_request_received",
        folder_path=request.xml_folder,
        max_concurrent=request.max_concurrent
    )
    
    try:
        # Create processor with custom concurrency if specified
        processor = batch_processor
        if request.max_concurrent is not None:
            processor = BatchProcessor(max_concurrent=request.max_concurrent)
            logger.debug(
                "custom_processor_created",
                max_concurrent=request.max_concurrent
            )
        
        # Validate folder exists and count files (synchronous check)
        from pathlib import Path
        folder = Path(request.xml_folder)
        
        if not folder.exists():
            logger.warning(
                "batch_folder_not_found",
                folder_path=request.xml_folder
            )
            raise ValidationException(
                message=f"Folder not found: {request.xml_folder}",
                details={"folder_path": request.xml_folder}
            )
        
        # Count XML files
        xml_files = list(folder.glob("*.xml")) + list(folder.glob("*.XML"))
        total_files = len(xml_files)
        
        if total_files == 0:
            logger.warning(
                "batch_no_files_found",
                folder_path=request.xml_folder
            )
            raise ValidationException(
                message=f"No XML files found in folder: {request.xml_folder}",
                details={"folder_path": request.xml_folder}
            )
        
        logger.info(
            "batch_files_counted",
            folder_path=request.xml_folder,
            total_files=total_files
        )
        
        # Create job in job manager
        import uuid
        job_id = f"batch-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}"
        
        job = job_manager.create_job(
            job_id=job_id,
            folder_path=request.xml_folder,
            total_files=total_files
        )
        
        # Start job
        job.start()
        
        logger.info(
            "batch_job_created",
            job_id=job_id,
            total_files=total_files
        )
        
        # Schedule background processing
        background_tasks.add_task(
            _run_batch_processing,
            job_id=job_id,
            folder_path=request.xml_folder,
            max_concurrent=request.max_concurrent
        )
        
        # Return initial response
        response = BatchUploadResponse(
            job_id=job_id,
            status=BatchJobStatus.RUNNING,
            total_files=total_files,
            successful=0,
            failed=0,
            errors=[],
            duration_seconds=None,
            started_at=datetime.now(),
            completed_at=None
        )
        
        logger.info(
            "batch_upload_started",
            job_id=job_id,
            total_files=total_files
        )
        
        return response
        
    except ValidationException:
        # Re-raise validation exceptions
        raise
        
    except BatchProcessingException as e:
        logger.error(
            "batch_processing_exception",
            error=str(e),
            details=e.details
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    except Exception as e:
        logger.exception(
            "unexpected_error_in_batch_upload",
            e
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get(
    "/status/{job_id}",
    response_model=BatchStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get batch job status",
    description="""
    Retrieve the current status of a batch processing job.
    
    Returns detailed information including:
    - Current status (pending, running, completed, failed)
    - Progress percentage
    - Number of files processed, successful, and failed
    - List of errors encountered
    - Timing information
    
    Requirements:
    - 7.5: REST API endpoint for status checking
    - 1.1: Track batch processing progress
    """,
    responses={
        200: {
            "description": "Job status retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "job_id": "batch-20251027-103000-abc123",
                        "status": "running",
                        "progress": 60,
                        "total": 10,
                        "processed": 6,
                        "successful": 5,
                        "failed": 1,
                        "current_file": None,
                        "errors": [
                            {
                                "file": "nota_003.xml",
                                "error": "XML malformado"
                            }
                        ],
                        "started_at": "2025-10-27T10:30:00",
                        "estimated_completion": None
                    }
                }
            }
        },
        404: {"description": "Job not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_batch_status(job_id: str) -> BatchStatusResponse:
    """Get status of a batch processing job
    
    Requirements:
    - 7.5: REST API endpoint for status checking
    - 1.1: Track batch processing progress
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        BatchStatusResponse with current job status
        
    Raises:
        HTTPException: If services not initialized or job not found
    """
    # Validate services are initialized
    if batch_processor is None or job_manager is None:
        logger.error("batch_services_not_initialized")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch services not initialized"
        )
    
    logger.debug(
        "batch_status_request",
        job_id=job_id
    )
    
    try:
        # Try to get status from batch processor first (has more real-time data)
        processor_status = batch_processor.get_job_status(job_id)
        
        if processor_status:
            # Convert processor status to response format
            total = processor_status.get("total", 0)
            processed = processor_status.get("processed", 0)
            progress = int((processed / total * 100) if total > 0 else 0)
            
            # Parse status
            status_str = processor_status.get("status", "unknown")
            try:
                job_status = BatchJobStatus(status_str)
            except ValueError:
                job_status = BatchJobStatus.RUNNING
            
            # Parse timestamps
            started_at = None
            if processor_status.get("start_time"):
                try:
                    started_at = datetime.fromisoformat(processor_status["start_time"])
                except (ValueError, TypeError):
                    pass
            
            response = BatchStatusResponse(
                job_id=job_id,
                status=job_status,
                progress=progress,
                total=total,
                processed=processed,
                successful=processor_status.get("successful", 0),
                failed=processor_status.get("failed", 0),
                current_file=None,  # Processor doesn't track current file
                errors=processor_status.get("errors", []),
                started_at=started_at,
                estimated_completion=None  # Could be calculated based on progress
            )
            
            logger.debug(
                "batch_status_retrieved_from_processor",
                job_id=job_id,
                status=status_str,
                progress=progress
            )
            
            return response
        
        # Fallback to job manager
        try:
            job_data = job_manager.get_job_status(job_id)
            
            # Convert job manager data to response format
            total = job_data.get("total_files", 0)
            processed = job_data.get("processed_files", 0)
            progress = int(job_data.get("progress_percentage", 0))
            
            # Parse status
            status_str = job_data.get("status", "unknown")
            try:
                job_status = BatchJobStatus(status_str)
            except ValueError:
                job_status = BatchJobStatus.RUNNING
            
            # Parse timestamps
            started_at = None
            if job_data.get("started_at"):
                try:
                    started_at = datetime.fromisoformat(job_data["started_at"])
                except (ValueError, TypeError):
                    pass
            
            response = BatchStatusResponse(
                job_id=job_id,
                status=job_status,
                progress=progress,
                total=total,
                processed=processed,
                successful=job_data.get("successful_files", 0),
                failed=job_data.get("failed_files", 0),
                current_file=None,
                errors=job_data.get("errors", []),
                started_at=started_at,
                estimated_completion=None
            )
            
            logger.debug(
                "batch_status_retrieved_from_manager",
                job_id=job_id,
                status=status_str,
                progress=progress
            )
            
            return response
            
        except BatchProcessingException:
            # Job not found in either system
            logger.warning(
                "batch_job_not_found",
                job_id=job_id
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job '{job_id}' not found"
            )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.exception(
            "unexpected_error_in_batch_status",
            e,
            job_id=job_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get(
    "/jobs",
    summary="List all batch jobs",
    description="""
    List all batch processing jobs with optional filtering.
    
    Useful for monitoring and management of batch operations.
    """,
    responses={
        200: {
            "description": "Jobs list retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "jobs": [
                            {
                                "job_id": "batch-20251027-103000-abc123",
                                "status": "completed",
                                "total_files": 10,
                                "successful": 8,
                                "failed": 2,
                                "started_at": "2025-10-27T10:30:00",
                                "completed_at": "2025-10-27T10:31:00"
                            }
                        ],
                        "total_count": 1
                    }
                }
            }
        },
        500: {"description": "Internal server error"}
    }
)
async def list_batch_jobs(
    status_filter: Optional[str] = None,
    limit: Optional[int] = 50
):
    """List all batch jobs with optional filtering
    
    Args:
        status_filter: Optional status to filter by (pending, running, completed, failed)
        limit: Maximum number of jobs to return (default: 50)
        
    Returns:
        Dictionary with jobs list and count
        
    Raises:
        HTTPException: If services not initialized
    """
    # Validate services are initialized
    if batch_processor is None or job_manager is None:
        logger.error("batch_services_not_initialized")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch services not initialized"
        )
    
    try:
        # Get jobs from processor (has most up-to-date data)
        jobs = batch_processor.list_jobs()
        
        # Apply status filter if provided
        if status_filter:
            jobs = [
                job for job in jobs
                if job.get("status") == status_filter
            ]
        
        # Apply limit
        if limit:
            jobs = jobs[:limit]
        
        logger.debug(
            "batch_jobs_listed",
            total_count=len(jobs),
            status_filter=status_filter
        )
        
        return {
            "jobs": jobs,
            "total_count": len(jobs)
        }
        
    except Exception as e:
        logger.exception(
            "unexpected_error_in_list_jobs",
            e
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.delete(
    "/jobs/{job_id}",
    summary="Delete a batch job",
    description="""
    Delete a batch job from the system.
    
    Note: This only removes the job record. It does not undo any
    database imports that were completed.
    """,
    responses={
        200: {
            "description": "Job deleted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "job_id": "batch-20251027-103000-abc123",
                        "deleted": True,
                        "message": "Job deleted successfully"
                    }
                }
            }
        },
        404: {"description": "Job not found"},
        500: {"description": "Internal server error"}
    }
)
async def delete_batch_job(job_id: str):
    """Delete a batch job
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        Dictionary with operation result
        
    Raises:
        HTTPException: If services not initialized or job not found
    """
    # Validate services are initialized
    if job_manager is None:
        logger.error("batch_services_not_initialized")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch services not initialized"
        )
    
    try:
        # Delete from job manager
        deleted = job_manager.delete_job(job_id)
        
        if not deleted:
            logger.warning(
                "batch_job_not_found_for_deletion",
                job_id=job_id
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job '{job_id}' not found"
            )
        
        logger.info(
            "batch_job_deleted",
            job_id=job_id
        )
        
        return {
            "job_id": job_id,
            "deleted": True,
            "message": "Job deleted successfully"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.exception(
            "unexpected_error_in_delete_job",
            e,
            job_id=job_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.post(
    "/cleanup",
    summary="Cleanup old batch jobs",
    description="""
    Clean up old completed batch jobs to free memory.
    
    By default, keeps failed jobs for debugging purposes.
    """,
    responses={
        200: {
            "description": "Cleanup completed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "cleaned_up": 5,
                        "message": "5 old jobs cleaned up successfully"
                    }
                }
            }
        },
        500: {"description": "Internal server error"}
    }
)
async def cleanup_old_jobs(
    max_age_seconds: int = 3600,
    keep_failed: bool = True
):
    """Clean up old completed batch jobs
    
    Args:
        max_age_seconds: Maximum age in seconds (default: 3600 = 1 hour)
        keep_failed: Whether to keep failed jobs (default: True)
        
    Returns:
        Dictionary with cleanup results
        
    Raises:
        HTTPException: If services not initialized
    """
    # Validate services are initialized
    if job_manager is None:
        logger.error("batch_services_not_initialized")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch services not initialized"
        )
    
    try:
        # Cleanup from job manager
        cleaned_count = job_manager.cleanup_old_jobs(
            max_age_seconds=max_age_seconds,
            keep_failed=keep_failed
        )
        
        logger.info(
            "batch_jobs_cleaned_up",
            count=cleaned_count,
            max_age_seconds=max_age_seconds,
            keep_failed=keep_failed
        )
        
        return {
            "cleaned_up": cleaned_count,
            "message": f"{cleaned_count} old jobs cleaned up successfully"
        }
        
    except Exception as e:
        logger.exception(
            "unexpected_error_in_cleanup",
            e
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )
