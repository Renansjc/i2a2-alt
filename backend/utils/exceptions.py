"""Exception handling for Multi-Agent NF-e System"""

from enum import Enum
from typing import Optional, Dict, Any


class ErrorCode(Enum):
    """Error codes for application exceptions"""
    
    # OpenAI API Errors
    OPENAI_API_ERROR = "openai_api_error"
    OPENAI_RATE_LIMIT = "openai_rate_limit"
    OPENAI_TIMEOUT = "openai_timeout"
    
    # Database Errors
    DATABASE_ERROR = "database_error"
    DATABASE_CONNECTION_ERROR = "database_connection_error"
    DATABASE_QUERY_ERROR = "database_query_error"
    INVALID_SQL = "invalid_sql"
    
    # XML Processing Errors
    XML_PARSE_ERROR = "xml_parse_error"
    XML_VALIDATION_ERROR = "xml_validation_error"
    XML_FILE_NOT_FOUND = "xml_file_not_found"
    
    # Agent Errors
    AGENT_ERROR = "agent_error"
    AGENT_DELEGATION_ERROR = "agent_delegation_error"
    AGENT_TIMEOUT = "agent_timeout"
    
    # Validation Errors
    VALIDATION_ERROR = "validation_error"
    INVALID_INPUT = "invalid_input"
    MISSING_REQUIRED_FIELD = "missing_required_field"
    
    # Memory Errors
    MEMORY_ERROR = "memory_error"
    SESSION_NOT_FOUND = "session_not_found"
    
    # Batch Processing Errors
    BATCH_PROCESSING_ERROR = "batch_processing_error"
    BATCH_JOB_NOT_FOUND = "batch_job_not_found"
    BATCH_TIMEOUT = "batch_timeout"
    
    # Configuration Errors
    CONFIG_ERROR = "config_error"
    MISSING_ENV_VAR = "missing_env_var"
    
    # General Errors
    INTERNAL_ERROR = "internal_error"
    NOT_FOUND = "not_found"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"


class AppException(Exception):
    """Base exception class for application-specific errors
    
    This exception provides structured error information including:
    - Error code for categorization
    - Human-readable message
    - Additional details for debugging
    - HTTP status code for API responses
    """
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 400
    ):
        """Initialize application exception
        
        Args:
            code: Error code from ErrorCode enum
            message: Human-readable error message
            details: Additional error details (optional)
            status_code: HTTP status code for API responses (default: 400)
        """
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON serialization
        
        Returns:
            Dictionary with error information
        """
        return {
            "error": {
                "code": self.code.value,
                "message": self.message,
                "details": self.details
            }
        }
    
    def __str__(self) -> str:
        """String representation of the exception"""
        details_str = f", details={self.details}" if self.details else ""
        return f"AppException({self.code.value}: {self.message}{details_str})"
    
    def __repr__(self) -> str:
        """Detailed representation of the exception"""
        return (
            f"AppException(code={self.code}, message='{self.message}', "
            f"details={self.details}, status_code={self.status_code})"
        )


# Convenience exception classes for common scenarios

class OpenAIException(AppException):
    """Exception for OpenAI API errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=ErrorCode.OPENAI_API_ERROR,
            message=message,
            details=details,
            status_code=502
        )


class DatabaseException(AppException):
    """Exception for database errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=ErrorCode.DATABASE_ERROR,
            message=message,
            details=details,
            status_code=500
        )


class ValidationException(AppException):
    """Exception for validation errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=ErrorCode.VALIDATION_ERROR,
            message=message,
            details=details,
            status_code=400
        )


class XMLProcessingException(AppException):
    """Exception for XML processing errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=ErrorCode.XML_PARSE_ERROR,
            message=message,
            details=details,
            status_code=400
        )


class AgentException(AppException):
    """Exception for agent processing errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=ErrorCode.AGENT_ERROR,
            message=message,
            details=details,
            status_code=500
        )


class BatchProcessingException(AppException):
    """Exception for batch processing errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=ErrorCode.BATCH_PROCESSING_ERROR,
            message=message,
            details=details,
            status_code=500
        )
