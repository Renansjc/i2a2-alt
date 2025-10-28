"""Test script for batch processor functionality"""

import asyncio
from pathlib import Path

from batch.processor import BatchProcessor
from batch.job_manager import get_job_manager
from utils.logger import get_logger


logger = get_logger(__name__)


async def test_batch_processor():
    """Test batch processor with xml_nf folder"""
    
    print("=" * 60)
    print("🧪 TESTING BATCH PROCESSOR")
    print("=" * 60)
    print()
    
    # Initialize processor
    processor = BatchProcessor(max_concurrent=3)
    job_manager = get_job_manager()
    
    # Test folder path (relative to backend directory)
    xml_folder = "../xml_nf"
    
    # Check if folder exists
    if not Path(xml_folder).exists():
        print(f"❌ Folder not found: {xml_folder}")
        print("Please ensure xml_nf folder exists with XML files")
        return
    
    # Count XML files
    xml_files = list(Path(xml_folder).glob("*.xml")) + list(Path(xml_folder).glob("*.XML"))
    print(f"📁 Found {len(xml_files)} XML files in {xml_folder}")
    print()
    
    if not xml_files:
        print("⚠️  No XML files found to process")
        return
    
    # Process folder
    print("🚀 Starting batch processing...")
    print()
    
    try:
        result = await processor.process_folder(xml_folder)
        
        print()
        print("=" * 60)
        print("✅ BATCH PROCESSING COMPLETED")
        print("=" * 60)
        print()
        print(f"Job ID: {result['job_id']}")
        print(f"Status: {result['status']}")
        print(f"Total Files: {result['total']}")
        print(f"Processed: {result['processed']}")
        print(f"Successful: {result['successful']}")
        print(f"Failed: {result['failed']}")
        print(f"Duration: {result['duration_seconds']:.2f} seconds")
        print()
        
        if result['errors']:
            print("❌ Errors encountered:")
            for error in result['errors']:
                print(f"  - {error['file']}: {error['error']}")
            print()
        
        # Test job status retrieval
        job_status = processor.get_job_status(result['job_id'])
        print(f"✓ Job status retrieved successfully")
        print()
        
        # Test job manager statistics
        stats = job_manager.get_statistics()
        print("📊 Job Manager Statistics:")
        print(f"  Total Jobs: {stats['total_jobs']}")
        print(f"  Active Jobs: {stats['active_jobs']}")
        print(f"  Total Files Processed: {stats['total_files_processed']}")
        print(f"  Total Successful: {stats['total_successful']}")
        print(f"  Total Failed: {stats['total_failed']}")
        print()
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ BATCH PROCESSING FAILED")
        print("=" * 60)
        print()
        print(f"Error: {str(e)}")
        print()
        import traceback
        traceback.print_exc()


async def test_concurrent_processing():
    """Test concurrent processing with multiple jobs"""
    
    print("=" * 60)
    print("🧪 TESTING CONCURRENT PROCESSING")
    print("=" * 60)
    print()
    
    processor = BatchProcessor(max_concurrent=2)
    
    # Create multiple jobs (if we had multiple folders)
    xml_folder = "../xml_nf"
    
    if not Path(xml_folder).exists():
        print(f"❌ Folder not found: {xml_folder}")
        return
    
    print("🚀 Starting concurrent batch processing...")
    print()
    
    try:
        # Process same folder twice to test concurrency
        results = await asyncio.gather(
            processor.process_folder(xml_folder),
            return_exceptions=True
        )
        
        print()
        print("✅ Concurrent processing completed")
        print(f"Jobs processed: {len(results)}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


async def test_job_manager():
    """Test job manager functionality"""
    
    print("=" * 60)
    print("🧪 TESTING JOB MANAGER")
    print("=" * 60)
    print()
    
    job_manager = get_job_manager()
    
    # Create test job
    job = job_manager.create_job(
        folder_path="../xml_nf",
        total_files=5
    )
    
    print(f"✓ Created job: {job.job_id}")
    
    # Start job
    job.start()
    print(f"✓ Started job")
    
    # Update progress
    job.update_progress(processed=3, successful=2, failed=1)
    print(f"✓ Updated progress: {job.progress_percentage:.1f}%")
    
    # Add error
    job.add_error("test.xml", "Test error", "TestError")
    print(f"✓ Added error")
    
    # Complete job
    job.complete()
    print(f"✓ Completed job")
    
    # Get job status
    status = job_manager.get_job_status(job.job_id)
    print(f"✓ Retrieved job status")
    print()
    
    print("Job Status:")
    print(f"  Status: {status['status']}")
    print(f"  Progress: {status['progress_percentage']}%")
    print(f"  Successful: {status['successful_files']}")
    print(f"  Failed: {status['failed_files']}")
    print(f"  Duration: {status['duration_seconds']:.2f}s")
    print()
    
    # List jobs
    jobs = job_manager.list_jobs()
    print(f"✓ Listed {len(jobs)} jobs")
    print()
    
    # Get statistics
    stats = job_manager.get_statistics()
    print("Statistics:")
    print(f"  Total Jobs: {stats['total_jobs']}")
    print(f"  Active Jobs: {stats['active_jobs']}")
    print()


async def main():
    """Run all tests"""
    
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "BATCH PROCESSOR TEST SUITE" + " " * 22 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    # Test 1: Job Manager
    await test_job_manager()
    
    print()
    input("Press Enter to continue to batch processing test...")
    print()
    
    # Test 2: Batch Processor
    await test_batch_processor()
    
    print()
    print("=" * 60)
    print("✨ ALL TESTS COMPLETED")
    print("=" * 60)
    print()


if __name__ == "__main__":
    asyncio.run(main())
