# Batch Processing Module

This module provides batch processing capabilities for importing multiple NF-e XML files into the Supabase database.

## Overview

The batch processing module consists of two main components:

1. **BatchProcessor**: Handles the actual processing of XML files with concurrency control
2. **JobManager**: Manages job tracking, status, and lifecycle

## Features

- ✅ Asynchronous processing with configurable concurrency
- ✅ Reuses existing `SupabaseNFeImporter` from `db.py`
- ✅ Robust error handling - continues processing even if individual files fail
- ✅ Detailed job tracking and status reporting
- ✅ Structured logging for all operations
- ✅ Automatic cleanup of old completed jobs

## Usage

### Basic Usage

```python
import asyncio
from batch.processor import BatchProcessor

async def process_xmls():
    # Initialize processor with max 5 concurrent imports
    processor = BatchProcessor(max_concurrent=5)
    
    # Process all XMLs in folder
    result = await processor.process_folder("xml_nf")
    
    print(f"Processed: {result['successful']} successful, {result['failed']} failed")
    print(f"Duration: {result['duration_seconds']} seconds")

# Run
asyncio.run(process_xmls())
```

### Using Job Manager

```python
from batch.job_manager import get_job_manager

# Get global job manager instance
job_manager = get_job_manager()

# Create a job
job = job_manager.create_job(
    folder_path="xml_nf",
    total_files=10
)

# Start the job
job.start()

# Update progress
job.update_progress(processed=5, successful=4, failed=1)

# Add error details
job.add_error("file.xml", "Parse error", "XMLParseError")

# Complete the job
job.complete()

# Get job status
status = job_manager.get_job_status(job.job_id)
print(f"Status: {status['status']}")
print(f"Progress: {status['progress_percentage']}%")

# List all jobs
jobs = job_manager.list_jobs()

# Get statistics
stats = job_manager.get_statistics()
print(f"Total jobs: {stats['total_jobs']}")
print(f"Active jobs: {stats['active_jobs']}")
```

### Integration with API

```python
from fastapi import APIRouter, BackgroundTasks
from batch.processor import BatchProcessor
from batch.job_manager import get_job_manager

router = APIRouter()
processor = BatchProcessor()

@router.post("/batch/upload")
async def start_batch_upload(
    folder_path: str,
    background_tasks: BackgroundTasks
):
    # Start processing in background
    job_id = str(uuid.uuid4())
    
    background_tasks.add_task(
        processor.process_folder,
        folder_path,
        job_id
    )
    
    return {"job_id": job_id, "status": "started"}

@router.get("/batch/status/{job_id}")
async def get_batch_status(job_id: str):
    status = processor.get_job_status(job_id)
    
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return status
```

## Configuration

The batch processor uses settings from `config.py`:

```python
# Maximum concurrent file processing
max_concurrent_uploads: int = 5

# Default XML folder
xml_folder: str = "xml_nf"

# Batch processing timeout
batch_timeout_seconds: int = 300
```

## Error Handling

The batch processor implements robust error handling:

1. **File-level errors**: If a single file fails, the error is logged and processing continues
2. **Job-level errors**: Critical errors (folder not found, etc.) stop the job
3. **All errors are tracked**: Each error includes file name, error message, and timestamp

Example error structure:

```python
{
    "file": "example.xml",
    "error": "Invalid XML structure",
    "error_type": "XMLParseError",
    "timestamp": "2025-10-27T10:30:00"
}
```

## Job Status

Jobs can have the following statuses:

- `pending`: Job created but not started
- `running`: Job is currently processing files
- `completed`: Job finished successfully
- `failed`: Job failed with critical error
- `cancelled`: Job was cancelled

## Job Lifecycle

```
pending → running → completed
                 ↘ failed
                 ↘ cancelled
```

## Testing

Run the test script to verify functionality:

```bash
cd backend
python test_batch_processor.py
```

The test script will:
1. Test job manager functionality
2. Process all XML files in the `xml_nf` folder
3. Display detailed results and statistics

## Logging

All operations are logged using structured logging:

```json
{
  "timestamp": "2025-10-27T10:30:00",
  "logger": "batch.processor",
  "event": "batch_processing_started",
  "context": {
    "job_id": "abc-123",
    "folder_path": "xml_nf"
  }
}
```

Key log events:
- `batch_processing_started`: Job started
- `batch_files_found`: XML files discovered
- `file_processed_successfully`: Individual file imported
- `file_processing_failed`: Individual file failed
- `batch_processing_completed`: Job completed

## Performance

The batch processor uses:
- **Asyncio semaphores** for concurrency control
- **Thread pool** for blocking I/O operations
- **Efficient error handling** to avoid blocking on failures

Typical performance:
- ~2-5 seconds per XML file (depending on complexity)
- 5 concurrent imports = ~1 file/second throughput
- Memory usage: ~50-100MB for typical workloads

## Cleanup

Old completed jobs can be cleaned up automatically:

```python
# Clean up jobs older than 1 hour
processor.clear_completed_jobs(max_age_seconds=3600)

# Or using job manager
job_manager.cleanup_old_jobs(
    max_age_seconds=3600,
    keep_failed=True  # Keep failed jobs for debugging
)
```

## Requirements

This module requires:
- Python 3.12+
- `asyncio` for async processing
- `db.py` with `SupabaseNFeImporter`
- `utils.logger` for structured logging
- `utils.exceptions` for error handling
- `config` for settings

## Architecture

```
BatchProcessor
├── process_folder()           # Main entry point
├── _process_files_concurrent() # Concurrency control
├── _process_file_with_semaphore() # Semaphore wrapper
└── _process_single_file()     # Individual file processing
    └── SupabaseNFeImporter.import_nfe()  # Reused from db.py

JobManager
├── create_job()               # Create new job
├── get_job_status()           # Get job status
├── list_jobs()                # List all jobs
├── cleanup_old_jobs()         # Clean up old jobs
└── get_statistics()           # Get overall stats
```

## Notes

- The batch processor **reuses** the existing `SupabaseNFeImporter` from `db.py`
- No modifications to the database schema are needed
- All imports use the same logic as single-file imports
- Failed files don't stop the batch - processing continues
- Job status is kept in memory (consider persisting for production)
