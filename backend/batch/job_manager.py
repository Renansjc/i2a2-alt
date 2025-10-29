"""Job manager for batch processing operations"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import uuid

from utils.logger import get_logger
from utils.exceptions import BatchProcessingException, ErrorCode


logger = get_logger(__name__)


class JobStatus(Enum):
    """Batch job status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BatchJob:
    """Represents a batch processing job
    
    Tracks the state and progress of a batch import operation.
    """
    
    def __init__(
        self,
        job_id: str,
        folder_path: str,
        total_files: int = 0
    ):
        """Initialize batch job
        
        Args:
            job_id: Unique job identifier
            folder_path: Path to folder being processed
            total_files: Total number of files to process
        """
        self.job_id = job_id
        self.folder_path = folder_path
        self.status = JobStatus.PENDING
        self.total_files = total_files
        self.processed_files = 0
        self.successful_files = 0
        self.failed_files = 0
        self.errors: List[Dict[str, Any]] = []
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.metadata: Dict[str, Any] = {}
    
    def start(self):
        """Mark job as started"""
        self.status = JobStatus.RUNNING
        self.started_at = datetime.now()
        
        logger.info(
            "job_started",
            job_id=self.job_id,
            folder_path=self.folder_path,
            total_files=self.total_files
        )
    
    def complete(self):
        """Mark job as completed"""
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.now()
        
        logger.info(
            "job_completed",
            job_id=self.job_id,
            total_files=self.total_files,
            successful=self.successful_files,
            failed=self.failed_files,
            duration_seconds=self.duration_seconds
        )
    
    def fail(self, error: str):
        """Mark job as failed
        
        Args:
            error: Error message
        """
        self.status = JobStatus.FAILED
        self.completed_at = datetime.now()
        
        logger.error(
            "job_failed",
            job_id=self.job_id,
            error=error,
            duration_seconds=self.duration_seconds
        )
    
    def cancel(self):
        """Mark job as cancelled"""
        self.status = JobStatus.CANCELLED
        self.completed_at = datetime.now()
        
        logger.info(
            "job_cancelled",
            job_id=self.job_id
        )
    
    def update_progress(
        self,
        processed: int,
        successful: int,
        failed: int
    ):
        """Update job progress
        
        Args:
            processed: Number of files processed
            successful: Number of successful imports
            failed: Number of failed imports
        """
        self.processed_files = processed
        self.successful_files = successful
        self.failed_files = failed
    
    def add_error(
        self,
        file_name: str,
        error_message: str,
        error_type: Optional[str] = None
    ):
        """Add error to job
        
        Args:
            file_name: Name of file that failed
            error_message: Error message
            error_type: Type of error (optional)
        """
        error_detail = {
            "file": file_name,
            "error": error_message,
            "error_type": error_type,
            "timestamp": datetime.now().isoformat()
        }
        
        self.errors.append(error_detail)
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage
        
        Returns:
            Progress as percentage (0-100)
        """
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate job duration in seconds
        
        Returns:
            Duration in seconds or None if not started
        """
        if self.started_at is None:
            return None
        
        end_time = self.completed_at or datetime.now()
        return (end_time - self.started_at).total_seconds()
    
    @property
    def is_active(self) -> bool:
        """Check if job is currently active
        
        Returns:
            True if job is pending or running
        """
        return self.status in [JobStatus.PENDING, JobStatus.RUNNING]
    
    @property
    def is_finished(self) -> bool:
        """Check if job is finished
        
        Returns:
            True if job is completed, failed, or cancelled
        """
        return self.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary
        
        Returns:
            Dictionary representation of job
        """
        return {
            "job_id": self.job_id,
            "folder_path": self.folder_path,
            "status": self.status.value,
            "total_files": self.total_files,
            "processed_files": self.processed_files,
            "successful_files": self.successful_files,
            "failed_files": self.failed_files,
            "progress_percentage": round(self.progress_percentage, 2),
            "errors": self.errors,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "metadata": self.metadata
        }


class JobManager:
    """Manages batch processing jobs
    
    Provides centralized job tracking, status management, and cleanup.
    """
    
    def __init__(self):
        """Initialize job manager"""
        self.jobs: Dict[str, BatchJob] = {}
        logger.info("job_manager_initialized")
    
    def create_job(
        self,
        folder_path: str,
        total_files: int = 0,
        job_id: Optional[str] = None
    ) -> BatchJob:
        """Create a new batch job
        
        Args:
            folder_path: Path to folder being processed
            total_files: Total number of files to process
            job_id: Optional job ID (generated if not provided)
            
        Returns:
            Created BatchJob instance
        """
        if job_id is None:
            job_id = str(uuid.uuid4())
        
        job = BatchJob(
            job_id=job_id,
            folder_path=folder_path,
            total_files=total_files
        )
        
        self.jobs[job_id] = job
        
        logger.info(
            "job_created",
            job_id=job_id,
            folder_path=folder_path,
            total_files=total_files
        )
        
        return job
    
    def get_job(self, job_id: str) -> Optional[BatchJob]:
        """Get job by ID
        
        Args:
            job_id: Job identifier
            
        Returns:
            BatchJob instance or None if not found
        """
        return self.jobs.get(job_id)
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get job status as dictionary
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job status dictionary
            
        Raises:
            BatchProcessingException: If job not found
        """
        job = self.get_job(job_id)
        
        if job is None:
            raise BatchProcessingException(
                f"Job not found: {job_id}",
                details={"job_id": job_id}
            )
        
        return job.to_dict()
    
    def list_jobs(
        self,
        status_filter: Optional[JobStatus] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List all jobs with optional filtering
        
        Args:
            status_filter: Optional status to filter by
            limit: Optional limit on number of results
            
        Returns:
            List of job dictionaries
        """
        jobs = list(self.jobs.values())
        
        # Filter by status if specified
        if status_filter:
            jobs = [job for job in jobs if job.status == status_filter]
        
        # Sort by creation time (newest first)
        jobs.sort(key=lambda j: j.created_at, reverse=True)
        
        # Apply limit if specified
        if limit:
            jobs = jobs[:limit]
        
        return [job.to_dict() for job in jobs]
    
    def list_active_jobs(self) -> List[Dict[str, Any]]:
        """List all active jobs
        
        Returns:
            List of active job dictionaries
        """
        active_jobs = [
            job for job in self.jobs.values()
            if job.is_active
        ]
        
        return [job.to_dict() for job in active_jobs]
    
    def delete_job(self, job_id: str) -> bool:
        """Delete a job
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if job was deleted, False if not found
        """
        if job_id in self.jobs:
            del self.jobs[job_id]
            logger.info("job_deleted", job_id=job_id)
            return True
        
        return False
    
    def cleanup_old_jobs(
        self,
        max_age_seconds: int = 3600,
        keep_failed: bool = True
    ) -> int:
        """Clean up old completed jobs
        
        Args:
            max_age_seconds: Maximum age in seconds (default: 1 hour)
            keep_failed: Whether to keep failed jobs (default: True)
            
        Returns:
            Number of jobs cleaned up
        """
        current_time = datetime.now()
        jobs_to_remove = []
        
        for job_id, job in self.jobs.items():
            # Skip active jobs
            if job.is_active:
                continue
            
            # Skip failed jobs if keep_failed is True
            if keep_failed and job.status == JobStatus.FAILED:
                continue
            
            # Check age
            if job.completed_at:
                age_seconds = (current_time - job.completed_at).total_seconds()
                
                if age_seconds > max_age_seconds:
                    jobs_to_remove.append(job_id)
        
        # Remove old jobs
        for job_id in jobs_to_remove:
            del self.jobs[job_id]
        
        if jobs_to_remove:
            logger.info(
                "old_jobs_cleaned_up",
                count=len(jobs_to_remove)
            )
        
        return len(jobs_to_remove)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall job statistics
        
        Returns:
            Dictionary with job statistics
        """
        total_jobs = len(self.jobs)
        
        status_counts = {
            status.value: 0
            for status in JobStatus
        }
        
        total_files = 0
        total_successful = 0
        total_failed = 0
        
        for job in self.jobs.values():
            status_counts[job.status.value] += 1
            total_files += job.total_files
            total_successful += job.successful_files
            total_failed += job.failed_files
        
        return {
            "total_jobs": total_jobs,
            "status_counts": status_counts,
            "total_files_processed": total_files,
            "total_successful": total_successful,
            "total_failed": total_failed,
            "active_jobs": status_counts[JobStatus.RUNNING.value] + status_counts[JobStatus.PENDING.value]
        }


# Global job manager instance
_job_manager: Optional[JobManager] = None


def get_job_manager() -> JobManager:
    """Get global job manager instance
    
    Returns:
        JobManager singleton instance
    """
    global _job_manager
    
    if _job_manager is None:
        _job_manager = JobManager()
    
    return _job_manager
