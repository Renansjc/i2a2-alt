"""Batch processor for importing multiple NF-e XML files"""

import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from db import SupabaseNFeImporter
from utils.logger import get_logger
from utils.exceptions import BatchProcessingException, XMLProcessingException
from config import settings


logger = get_logger(__name__)


class BatchProcessor:
    """Processes multiple XML files in batch with concurrency control
    
    This processor reuses the existing SupabaseNFeImporter from db.py
    to import XML files, adding batch management, error handling, and
    asynchronous processing capabilities.
    """
    
    def __init__(self, max_concurrent: Optional[int] = None):
        """Initialize batch processor
        
        Args:
            max_concurrent: Maximum number of concurrent file processing
                          (defaults to settings.max_concurrent_uploads)
        """
        self.importer = SupabaseNFeImporter()
        self.max_concurrent = max_concurrent or settings.max_concurrent_uploads
        self.jobs: Dict[str, Dict[str, Any]] = {}
        
        logger.info(
            "batch_processor_initialized",
            max_concurrent=self.max_concurrent
        )
    
    async def process_folder(
        self,
        folder_path: str,
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process all XML files in a folder
        
        Args:
            folder_path: Path to folder containing XML files
            job_id: Optional job ID (generated if not provided)
            
        Returns:
            Dictionary with processing results including:
            - job_id: Unique job identifier
            - status: Job status (running, completed, failed)
            - total: Total number of files found
            - processed: Number of files processed
            - successful: Number of successful imports
            - failed: Number of failed imports
            - errors: List of error details
            - duration_seconds: Total processing time
            
        Raises:
            BatchProcessingException: If folder doesn't exist or is empty
        """
        # Generate job ID if not provided
        if job_id is None:
            job_id = str(uuid.uuid4())
        
        start_time = datetime.now()
        
        logger.info(
            "batch_processing_started",
            job_id=job_id,
            folder_path=folder_path
        )
        
        # Validate folder exists
        folder = Path(folder_path)
        if not folder.exists():
            raise BatchProcessingException(
                f"Folder not found: {folder_path}",
                details={"folder_path": folder_path}
            )
        
        # Find all XML files
        xml_files = list(folder.glob("*.xml")) + list(folder.glob("*.XML"))
        
        if not xml_files:
            raise BatchProcessingException(
                f"No XML files found in folder: {folder_path}",
                details={"folder_path": folder_path}
            )
        
        # Initialize job status
        self.jobs[job_id] = {
            "job_id": job_id,
            "status": "running",
            "folder_path": folder_path,
            "total": len(xml_files),
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "errors": [],
            "start_time": start_time.isoformat(),
            "end_time": None,
            "duration_seconds": None
        }
        
        logger.info(
            "batch_files_found",
            job_id=job_id,
            total_files=len(xml_files)
        )
        
        # Process files with concurrency control
        try:
            await self._process_files_concurrent(job_id, xml_files)
            self.jobs[job_id]["status"] = "completed"
        except Exception as e:
            self.jobs[job_id]["status"] = "failed"
            logger.exception(
                "batch_processing_failed",
                e,
                job_id=job_id
            )
            raise BatchProcessingException(
                f"Batch processing failed: {str(e)}",
                details={"job_id": job_id, "error": str(e)}
            )
        finally:
            # Calculate duration
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            self.jobs[job_id]["end_time"] = end_time.isoformat()
            self.jobs[job_id]["duration_seconds"] = duration
            
            logger.log_batch_processing(
                job_id=job_id,
                status=self.jobs[job_id]["status"],
                total_files=self.jobs[job_id]["total"],
                processed=self.jobs[job_id]["processed"],
                successful=self.jobs[job_id]["successful"],
                failed=self.jobs[job_id]["failed"],
                duration_seconds=duration
            )
        
        return self.jobs[job_id]
    
    async def _process_files_concurrent(
        self,
        job_id: str,
        xml_files: List[Path]
    ):
        """Process files with concurrency control using semaphore
        
        Args:
            job_id: Job identifier
            xml_files: List of XML file paths to process
        """
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        # Create tasks for all files
        tasks = [
            self._process_file_with_semaphore(
                job_id,
                xml_file,
                semaphore
            )
            for xml_file in xml_files
        ]
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _process_file_with_semaphore(
        self,
        job_id: str,
        xml_file: Path,
        semaphore: asyncio.Semaphore
    ):
        """Process a single file with semaphore control
        
        Args:
            job_id: Job identifier
            xml_file: Path to XML file
            semaphore: Semaphore for concurrency control
        """
        async with semaphore:
            await self._process_single_file(job_id, xml_file)
    
    async def _process_single_file(
        self,
        job_id: str,
        xml_file: Path
    ):
        """Process a single XML file
        
        Args:
            job_id: Job identifier
            xml_file: Path to XML file
        """
        file_start_time = datetime.now()
        
        logger.debug(
            "processing_file",
            job_id=job_id,
            file_name=xml_file.name
        )
        
        try:
            # Run import in thread pool to avoid blocking
            await asyncio.to_thread(
                self.importer.import_nfe,
                str(xml_file)
            )
            
            # Update success count
            self.jobs[job_id]["successful"] += 1
            
            duration_ms = (datetime.now() - file_start_time).total_seconds() * 1000
            
            logger.info(
                "file_processed_successfully",
                job_id=job_id,
                file_name=xml_file.name,
                duration_ms=duration_ms
            )
            
        except Exception as e:
            # Update failure count and record error
            self.jobs[job_id]["failed"] += 1
            
            error_detail = {
                "file": xml_file.name,
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": datetime.now().isoformat()
            }
            
            self.jobs[job_id]["errors"].append(error_detail)
            
            logger.error(
                "file_processing_failed",
                job_id=job_id,
                file_name=xml_file.name,
                error=str(e),
                error_type=type(e).__name__
            )
        
        finally:
            # Always increment processed count
            self.jobs[job_id]["processed"] += 1
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a batch job
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job status dictionary or None if job not found
        """
        return self.jobs.get(job_id)
    
    def list_jobs(self) -> List[Dict[str, Any]]:
        """List all batch jobs
        
        Returns:
            List of job status dictionaries
        """
        return list(self.jobs.values())
    
    def clear_completed_jobs(self, max_age_seconds: int = 3600):
        """Clear completed jobs older than specified age
        
        Args:
            max_age_seconds: Maximum age in seconds (default: 1 hour)
        """
        current_time = datetime.now()
        jobs_to_remove = []
        
        for job_id, job_data in self.jobs.items():
            if job_data["status"] in ["completed", "failed"]:
                if job_data["end_time"]:
                    end_time = datetime.fromisoformat(job_data["end_time"])
                    age_seconds = (current_time - end_time).total_seconds()
                    
                    if age_seconds > max_age_seconds:
                        jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            del self.jobs[job_id]
            logger.debug(
                "job_cleared",
                job_id=job_id
            )
        
        if jobs_to_remove:
            logger.info(
                "completed_jobs_cleared",
                count=len(jobs_to_remove)
            )
