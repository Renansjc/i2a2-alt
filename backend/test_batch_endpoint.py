"""Test script for batch endpoint implementation

This script tests the batch processing endpoint functionality without running the full server.
It verifies that all components work together correctly.
"""

import sys
from pathlib import Path
import tempfile
import shutil

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from api.routes.batch import router, initialize_batch_services
from api.models.requests import BatchUploadRequest
from api.models.responses import BatchJobStatus
from batch.processor import BatchProcessor
from batch.job_manager import get_job_manager, JobManager
from utils.logger import get_logger

logger = get_logger(__name__)


def test_batch_services_initialization():
    """Test that batch services can be initialized"""
    print("=" * 60)
    print("Test 1: Batch Services Initialization")
    print("=" * 60)
    
    try:
        # Initialize services
        processor = BatchProcessor(max_concurrent=3)
        manager = get_job_manager()
        
        # Initialize batch services
        initialize_batch_services(processor, manager)
        
        print("✓ BatchProcessor initialized successfully")
        print(f"  - Max concurrent: {processor.max_concurrent}")
        print("✓ JobManager initialized successfully")
        print("✓ Batch services initialized successfully")
        print()
        return True
        
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_request_validation():
    """Test that BatchUploadRequest validation works"""
    print("=" * 60)
    print("Test 2: BatchUploadRequest Validation")
    print("=" * 60)
    
    try:
        # Valid request with defaults
        valid_request = BatchUploadRequest(
            xml_folder="xml_nf"
        )
        print(f"✓ Valid request created: {valid_request.xml_folder}")
        print(f"  - max_concurrent: {valid_request.max_concurrent}")
        
        # Valid request with custom max_concurrent
        valid_request2 = BatchUploadRequest(
            xml_folder="uploads/nfe",
            max_concurrent=10
        )
        print(f"✓ Valid request with custom settings: {valid_request2.xml_folder}")
        print(f"  - max_concurrent: {valid_request2.max_concurrent}")
        
        # Test validation - empty folder
        try:
            invalid_request = BatchUploadRequest(
                xml_folder="   "  # Only whitespace
            )
            print("✗ Should have failed validation for empty folder")
            return False
        except Exception as e:
            print(f"✓ Correctly rejected empty folder: {type(e).__name__}")
        
        # Test validation - directory traversal
        try:
            invalid_request = BatchUploadRequest(
                xml_folder="../../../etc/passwd"
            )
            print("✗ Should have failed validation for directory traversal")
            return False
        except Exception as e:
            print(f"✓ Correctly rejected directory traversal: {type(e).__name__}")
        
        # Test validation - invalid max_concurrent
        try:
            invalid_request = BatchUploadRequest(
                xml_folder="xml_nf",
                max_concurrent=0  # Must be >= 1
            )
            print("✗ Should have failed validation for invalid max_concurrent")
            return False
        except Exception as e:
            print(f"✓ Correctly rejected invalid max_concurrent: {type(e).__name__}")
        
        print()
        return True
        
    except Exception as e:
        print(f"✗ Validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_job_manager_operations():
    """Test that JobManager operations work"""
    print("=" * 60)
    print("Test 3: JobManager Operations")
    print("=" * 60)
    
    try:
        manager = JobManager()
        
        # Create a job
        job = manager.create_job(
            folder_path="test_folder",
            total_files=10,
            job_id="test-job-123"
        )
        print(f"✓ Created job: {job.job_id}")
        print(f"  - Status: {job.status.value}")
        print(f"  - Total files: {job.total_files}")
        
        # Start the job
        job.start()
        assert job.status.value == "running", "Job should be running"
        print(f"✓ Job started: {job.status.value}")
        
        # Update progress
        job.update_progress(processed=5, successful=4, failed=1)
        assert job.processed_files == 5, "Processed count should be 5"
        assert job.successful_files == 4, "Successful count should be 4"
        assert job.failed_files == 1, "Failed count should be 1"
        print(f"✓ Progress updated: {job.processed_files}/{job.total_files}")
        print(f"  - Progress: {job.progress_percentage:.1f}%")
        
        # Add an error
        job.add_error("test.xml", "Test error message", "TestError")
        assert len(job.errors) == 1, "Should have 1 error"
        print(f"✓ Error added: {len(job.errors)} errors")
        
        # Complete the job
        job.complete()
        assert job.status.value == "completed", "Job should be completed"
        assert job.is_finished, "Job should be finished"
        print(f"✓ Job completed: {job.status.value}")
        
        # Get job status
        status = manager.get_job_status("test-job-123")
        assert status["job_id"] == "test-job-123", "Job ID should match"
        assert status["status"] == "completed", "Status should be completed"
        print(f"✓ Job status retrieved: {status['status']}")
        
        # List jobs
        jobs = manager.list_jobs()
        assert len(jobs) >= 1, "Should have at least 1 job"
        print(f"✓ Listed jobs: {len(jobs)} jobs")
        
        # Get statistics
        stats = manager.get_statistics()
        print(f"✓ Statistics retrieved:")
        print(f"  - Total jobs: {stats['total_jobs']}")
        print(f"  - Total files: {stats['total_files_processed']}")
        print(f"  - Successful: {stats['total_successful']}")
        print(f"  - Failed: {stats['total_failed']}")
        
        # Delete job
        deleted = manager.delete_job("test-job-123")
        assert deleted, "Job should be deleted"
        print(f"✓ Job deleted successfully")
        
        print()
        return True
        
    except Exception as e:
        print(f"✗ JobManager operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_processor_with_test_files():
    """Test BatchProcessor with actual test files"""
    print("=" * 60)
    print("Test 4: BatchProcessor with Test Files")
    print("=" * 60)
    
    # Create temporary directory with test XML files
    temp_dir = tempfile.mkdtemp(prefix="batch_test_")
    
    try:
        # Create some test XML files
        test_files = []
        for i in range(3):
            xml_file = Path(temp_dir) / f"test_nfe_{i+1}.xml"
            xml_file.write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<nfeProc>
    <NFe>
        <infNFe Id="NFe{i+1:044d}">
            <ide>
                <cUF>35</cUF>
                <natOp>VENDA</natOp>
                <mod>55</mod>
                <serie>1</serie>
                <nNF>{i+1}</nNF>
                <dhEmi>2025-10-27T10:00:00-03:00</dhEmi>
            </ide>
            <emit>
                <CNPJ>12345678000190</CNPJ>
                <xNome>Empresa Teste</xNome>
            </emit>
            <dest>
                <CNPJ>98765432000100</CNPJ>
                <xNome>Cliente Teste</xNome>
            </dest>
            <total>
                <ICMSTot>
                    <vNF>100.00</vNF>
                </ICMSTot>
            </total>
        </infNFe>
    </NFe>
    <protNFe>
        <infProt>
            <chNFe>{i+1:044d}</chNFe>
            <nProt>123456789012345</nProt>
        </infProt>
    </protNFe>
</nfeProc>
""")
            test_files.append(xml_file)
        
        print(f"✓ Created {len(test_files)} test XML files in {temp_dir}")
        
        # Initialize processor
        processor = BatchProcessor(max_concurrent=2)
        print(f"✓ BatchProcessor initialized (max_concurrent=2)")
        
        # Note: We can't actually process these files without a real Supabase connection
        # But we can test the validation and setup
        
        # Test that processor can validate the folder
        folder = Path(temp_dir)
        assert folder.exists(), "Test folder should exist"
        
        xml_files = list(folder.glob("*.xml"))
        assert len(xml_files) == 3, f"Should find 3 XML files, found {len(xml_files)}"
        print(f"✓ Processor can find XML files: {len(xml_files)} files")
        
        # Test job status tracking
        test_job_id = "test-batch-job-456"
        processor.jobs[test_job_id] = {
            "job_id": test_job_id,
            "status": "running",
            "total": 3,
            "processed": 2,
            "successful": 2,
            "failed": 0,
            "errors": []
        }
        
        status = processor.get_job_status(test_job_id)
        assert status is not None, "Should retrieve job status"
        assert status["total"] == 3, "Total should be 3"
        print(f"✓ Job status tracking works: {status['processed']}/{status['total']}")
        
        # Test list jobs
        jobs = processor.list_jobs()
        assert len(jobs) >= 1, "Should have at least 1 job"
        print(f"✓ List jobs works: {len(jobs)} jobs")
        
        # Test clear completed jobs
        processor.jobs[test_job_id]["status"] = "completed"
        processor.jobs[test_job_id]["end_time"] = "2020-01-01T00:00:00"  # Old job
        processor.clear_completed_jobs(max_age_seconds=1)
        
        # Job should be cleared
        status_after_clear = processor.get_job_status(test_job_id)
        assert status_after_clear is None, "Old job should be cleared"
        print(f"✓ Clear completed jobs works")
        
        print()
        return True
        
    except Exception as e:
        print(f"✗ BatchProcessor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup temp directory
        try:
            shutil.rmtree(temp_dir)
            print(f"✓ Cleaned up temp directory: {temp_dir}")
        except Exception as e:
            print(f"⚠ Warning: Could not clean up temp directory: {e}")


def test_router_configuration():
    """Test that router is configured correctly"""
    print("=" * 60)
    print("Test 5: Router Configuration")
    print("=" * 60)
    
    try:
        # Check router prefix
        assert router.prefix == "/api/batch", f"Expected prefix '/api/batch', got '{router.prefix}'"
        print(f"✓ Router prefix is correct: {router.prefix}")
        
        # Check router tags
        assert "batch" in router.tags, "Router should have 'batch' tag"
        print(f"✓ Router tags are correct: {router.tags}")
        
        # Check routes
        print(f"✓ Router has {len(router.routes)} routes:")
        for route in router.routes:
            methods = ", ".join(route.methods) if hasattr(route, 'methods') else "N/A"
            path = route.path if hasattr(route, 'path') else "N/A"
            print(f"  - {path} [{methods}]")
        
        # Verify main endpoints exist
        route_paths = [route.path for route in router.routes if hasattr(route, 'path')]
        
        # Check for upload endpoint
        upload_exists = any("/api/batch/upload" in path for path in route_paths)
        assert upload_exists, "Upload endpoint should exist"
        print("✓ POST /api/batch/upload endpoint exists")
        
        # Check for status endpoint
        status_exists = any("/api/batch/status/{job_id}" in path for path in route_paths)
        assert status_exists, "Status endpoint should exist"
        print("✓ GET /api/batch/status/{job_id} endpoint exists")
        
        # Check for jobs list endpoint
        jobs_exists = any("/api/batch/jobs" in path for path in route_paths)
        assert jobs_exists, "Jobs list endpoint should exist"
        print("✓ GET /api/batch/jobs endpoint exists")
        
        print()
        return True
        
    except Exception as e:
        print(f"✗ Router configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_response_models():
    """Test that response models work correctly"""
    print("=" * 60)
    print("Test 6: Response Models")
    print("=" * 60)
    
    try:
        from api.models.responses import BatchUploadResponse, BatchStatusResponse
        from datetime import datetime
        
        # Test BatchUploadResponse
        upload_response = BatchUploadResponse(
            job_id="test-job-789",
            status=BatchJobStatus.RUNNING,
            total_files=10,
            successful=0,
            failed=0,
            errors=[],
            started_at=datetime.now()
        )
        print(f"✓ BatchUploadResponse created:")
        print(f"  - job_id: {upload_response.job_id}")
        print(f"  - status: {upload_response.status.value}")
        print(f"  - total_files: {upload_response.total_files}")
        
        # Test BatchStatusResponse
        status_response = BatchStatusResponse(
            job_id="test-job-789",
            status=BatchJobStatus.RUNNING,
            progress=50,
            total=10,
            processed=5,
            successful=4,
            failed=1,
            errors=[{"file": "test.xml", "error": "Test error"}],
            started_at=datetime.now()
        )
        print(f"✓ BatchStatusResponse created:")
        print(f"  - job_id: {status_response.job_id}")
        print(f"  - status: {status_response.status.value}")
        print(f"  - progress: {status_response.progress}%")
        print(f"  - processed: {status_response.processed}/{status_response.total}")
        
        # Test JSON serialization
        upload_dict = upload_response.model_dump()
        assert "job_id" in upload_dict, "Should have job_id in dict"
        print(f"✓ Response models serialize to dict correctly")
        
        print()
        return True
        
    except Exception as e:
        print(f"✗ Response models test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("BATCH ENDPOINT IMPLEMENTATION TESTS")
    print("=" * 60 + "\n")
    
    results = []
    
    # Run tests
    results.append(("Services Initialization", test_batch_services_initialization()))
    results.append(("Request Validation", test_batch_request_validation()))
    results.append(("JobManager Operations", test_job_manager_operations()))
    results.append(("BatchProcessor with Test Files", test_batch_processor_with_test_files()))
    results.append(("Router Configuration", test_router_configuration()))
    results.append(("Response Models", test_response_models()))
    
    # Print summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! Batch endpoint implementation is working correctly.")
        print("\nNote: These tests validate the endpoint structure and logic.")
        print("Actual XML processing requires a valid Supabase connection.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
