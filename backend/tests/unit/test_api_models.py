"""Unit tests for API models"""

import pytest
from pydantic import ValidationError
from datetime import datetime

from api.models import (
    ChatRequest,
    BatchUploadRequest,
    ChatResponse,
    BatchUploadResponse,
    BatchStatusResponse,
    BatchJobStatus,
    AgentType
)


class TestChatRequest:
    """Tests for ChatRequest model"""
    
    def test_valid_chat_request(self):
        """Test creating a valid ChatRequest"""
        request = ChatRequest(
            session_id="user-123",
            message="Quantas notas fiscais foram emitidas?"
        )
        assert request.session_id == "user-123"
        assert request.message == "Quantas notas fiscais foram emitidas?"
    
    def test_empty_session_id(self):
        """Test that empty session_id raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(session_id="", message="test")
        assert "session_id" in str(exc_info.value)
    
    def test_whitespace_session_id(self):
        """Test that whitespace-only session_id raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(session_id="   ", message="test")
        assert "session_id" in str(exc_info.value)
    
    def test_empty_message(self):
        """Test that empty message raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(session_id="user-123", message="")
        assert "message" in str(exc_info.value)
    
    def test_whitespace_trimming(self):
        """Test that whitespace is trimmed from fields"""
        request = ChatRequest(
            session_id="  user-123  ",
            message="  test message  "
        )
        assert request.session_id == "user-123"
        assert request.message == "test message"


class TestBatchUploadRequest:
    """Tests for BatchUploadRequest model"""
    
    def test_valid_batch_request_defaults(self):
        """Test creating BatchUploadRequest with defaults"""
        request = BatchUploadRequest()
        assert request.xml_folder == "xml_nf"
        assert request.max_concurrent is None
    
    def test_valid_batch_request_custom(self):
        """Test creating BatchUploadRequest with custom values"""
        request = BatchUploadRequest(
            xml_folder="uploads/nfe",
            max_concurrent=10
        )
        assert request.xml_folder == "uploads/nfe"
        assert request.max_concurrent == 10
    
    def test_directory_traversal_prevention(self):
        """Test that directory traversal is prevented"""
        with pytest.raises(ValidationError) as exc_info:
            BatchUploadRequest(xml_folder="../etc/passwd")
        assert "directory traversal" in str(exc_info.value).lower()
    
    def test_max_concurrent_validation(self):
        """Test max_concurrent bounds validation"""
        # Valid range
        request = BatchUploadRequest(max_concurrent=5)
        assert request.max_concurrent == 5
        
        # Too low
        with pytest.raises(ValidationError):
            BatchUploadRequest(max_concurrent=0)
        
        # Too high
        with pytest.raises(ValidationError):
            BatchUploadRequest(max_concurrent=21)


class TestChatResponse:
    """Tests for ChatResponse model"""
    
    def test_valid_chat_response(self):
        """Test creating a valid ChatResponse"""
        response = ChatResponse(
            session_id="user-123",
            message="Foram emitidas 42 notas fiscais",
            agent_used="sql_specialist"
        )
        assert response.session_id == "user-123"
        assert response.message == "Foram emitidas 42 notas fiscais"
        assert response.agent_used == "sql_specialist"
        assert isinstance(response.timestamp, datetime)
    
    def test_chat_response_with_metadata(self):
        """Test ChatResponse with metadata"""
        metadata = {"query_executed": True, "processing_time_ms": 1250}
        response = ChatResponse(
            session_id="user-123",
            message="Test",
            agent_used="coordenador",
            metadata=metadata
        )
        assert response.metadata == metadata


class TestBatchUploadResponse:
    """Tests for BatchUploadResponse model"""
    
    def test_valid_batch_upload_response(self):
        """Test creating a valid BatchUploadResponse"""
        response = BatchUploadResponse(
            job_id="batch-123",
            status=BatchJobStatus.COMPLETED,
            total_files=10,
            successful=8,
            failed=2
        )
        assert response.job_id == "batch-123"
        assert response.status == BatchJobStatus.COMPLETED
        assert response.total_files == 10
        assert response.successful == 8
        assert response.failed == 2
        assert response.errors == []
    
    def test_batch_upload_response_with_errors(self):
        """Test BatchUploadResponse with error list"""
        errors = [
            {"file": "nota1.xml", "error": "XML malformado"},
            {"file": "nota2.xml", "error": "Chave duplicada"}
        ]
        response = BatchUploadResponse(
            job_id="batch-123",
            status=BatchJobStatus.FAILED,
            total_files=10,
            successful=8,
            failed=2,
            errors=errors
        )
        assert len(response.errors) == 2
        assert response.errors[0]["file"] == "nota1.xml"


class TestBatchStatusResponse:
    """Tests for BatchStatusResponse model"""
    
    def test_valid_batch_status_response(self):
        """Test creating a valid BatchStatusResponse"""
        response = BatchStatusResponse(
            job_id="batch-123",
            status=BatchJobStatus.RUNNING,
            progress=60,
            total=10,
            processed=6,
            successful=5,
            failed=1
        )
        assert response.job_id == "batch-123"
        assert response.status == BatchJobStatus.RUNNING
        assert response.progress == 60
        assert response.total == 10
        assert response.processed == 6
    
    def test_progress_bounds_validation(self):
        """Test that progress is validated between 0-100"""
        # Valid progress
        response = BatchStatusResponse(
            job_id="batch-123",
            status=BatchJobStatus.RUNNING,
            progress=50,
            total=10
        )
        assert response.progress == 50
        
        # Invalid progress - too high
        with pytest.raises(ValidationError):
            BatchStatusResponse(
                job_id="batch-123",
                status=BatchJobStatus.RUNNING,
                progress=101,
                total=10
            )
        
        # Invalid progress - negative
        with pytest.raises(ValidationError):
            BatchStatusResponse(
                job_id="batch-123",
                status=BatchJobStatus.RUNNING,
                progress=-1,
                total=10
            )


class TestEnums:
    """Tests for enum types"""
    
    def test_batch_job_status_values(self):
        """Test BatchJobStatus enum values"""
        assert BatchJobStatus.PENDING == "pending"
        assert BatchJobStatus.RUNNING == "running"
        assert BatchJobStatus.COMPLETED == "completed"
        assert BatchJobStatus.FAILED == "failed"
        assert BatchJobStatus.CANCELLED == "cancelled"
    
    def test_agent_type_values(self):
        """Test AgentType enum values"""
        assert AgentType.coordenador == "coordenador"
        assert AgentType.SQL_SPECIALIST == "sql_specialist"
        assert AgentType.CONVERSATION_SPECIALIST == "conversation_specialist"
        assert AgentType.SYSTEM == "system"
