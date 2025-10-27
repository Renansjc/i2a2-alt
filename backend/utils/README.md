# Utils Module - Exception and Logging System

## Overview

This module provides a robust exception handling and structured logging system for the Multi-Agent NF-e System.

## Components

### 1. Exception System (`exceptions.py`)

#### ErrorCode Enum
Comprehensive error codes for categorizing exceptions:
- **OpenAI Errors**: `OPENAI_API_ERROR`, `OPENAI_RATE_LIMIT`, `OPENAI_TIMEOUT`
- **Database Errors**: `DATABASE_ERROR`, `DATABASE_CONNECTION_ERROR`, `DATABASE_QUERY_ERROR`, `INVALID_SQL`
- **XML Processing Errors**: `XML_PARSE_ERROR`, `XML_VALIDATION_ERROR`, `XML_FILE_NOT_FOUND`
- **Agent Errors**: `AGENT_ERROR`, `AGENT_DELEGATION_ERROR`, `AGENT_TIMEOUT`
- **Validation Errors**: `VALIDATION_ERROR`, `INVALID_INPUT`, `MISSING_REQUIRED_FIELD`
- **Memory Errors**: `MEMORY_ERROR`, `SESSION_NOT_FOUND`
- **Batch Processing Errors**: `BATCH_PROCESSING_ERROR`, `BATCH_JOB_NOT_FOUND`, `BATCH_TIMEOUT`
- **Configuration Errors**: `CONFIG_ERROR`, `MISSING_ENV_VAR`
- **General Errors**: `INTERNAL_ERROR`, `NOT_FOUND`, `UNAUTHORIZED`, `FORBIDDEN`

#### AppException Class
Base exception class with:
- `code`: ErrorCode enum value
- `message`: Human-readable error message
- `details`: Dictionary with additional context
- `status_code`: HTTP status code for API responses
- `to_dict()`: Convert to JSON-serializable dictionary

#### Convenience Exception Classes
Pre-configured exceptions for common scenarios:
- `OpenAIException`: OpenAI API errors (502 status)
- `DatabaseException`: Database errors (500 status)
- `ValidationException`: Validation errors (400 status)
- `XMLProcessingException`: XML processing errors (400 status)
- `AgentException`: Agent processing errors (500 status)
- `BatchProcessingException`: Batch processing errors (500 status)

### 2. Logging System (`logger.py`)

#### StructuredLogger Class
JSON-formatted structured logging with:

**Standard Log Methods:**
- `debug(event, **kwargs)`: Debug-level logs
- `info(event, **kwargs)`: Info-level logs
- `warning(event, **kwargs)`: Warning-level logs
- `error(event, **kwargs)`: Error-level logs
- `critical(event, **kwargs)`: Critical-level logs
- `exception(event, exc, **kwargs)`: Exception logs with traceback

**Specialized Log Methods:**
- `log_api_request(method, path, status_code, duration_ms, **kwargs)`: API request logging
- `log_agent_action(agent_name, action, success, duration_ms, **kwargs)`: Agent action logging
- `log_database_query(query_type, table, duration_ms, rows_affected, **kwargs)`: Database query logging
- `log_batch_processing(job_id, status, total_files, processed, successful, failed, **kwargs)`: Batch processing logging

**Features:**
- JSON-formatted output for easy parsing
- Automatic timestamp and environment tagging
- Configurable log levels via settings
- Suppression of noisy third-party loggers

#### Helper Functions
- `get_logger(name, level=None)`: Get or create a logger instance (cached)
- `configure_logging()`: Configure root logging settings

### 3. FastAPI Exception Handlers (`api/exception_handlers.py`)

#### Exception Handlers
- `app_exception_handler`: Handle AppException instances
- `validation_exception_handler`: Handle Pydantic validation errors
- `generic_exception_handler`: Catch-all for unexpected exceptions
- `openai_exception_handler`: Handle OpenAI-specific exceptions

#### Registration Function
- `register_exception_handlers(app)`: Register all handlers with FastAPI app

## Usage Examples

### Raising Exceptions

```python
from utils.exceptions import AppException, ErrorCode, ValidationException

# Using AppException directly
raise AppException(
    code=ErrorCode.DATABASE_ERROR,
    message="Failed to connect to database",
    details={"host": "localhost", "error": "Connection refused"},
    status_code=500
)

# Using convenience classes
raise ValidationException(
    message="Missing required field",
    details={"field": "session_id"}
)
```

### Logging

```python
from utils.logger import get_logger

logger = get_logger(__name__)

# Basic logging
logger.info("user_login", user_id="123", ip_address="192.168.1.1")
logger.error("database_error", error_code="DB001", table="notas_fiscais")

# Specialized logging
logger.log_api_request(
    method="POST",
    path="/api/chat",
    status_code=200,
    duration_ms=125.5
)

logger.log_agent_action(
    agent_name="sql_specialist",
    action="execute_query",
    success=True,
    duration_ms=89.3
)

# Exception logging
try:
    # Some operation
    pass
except Exception as e:
    logger.exception("operation_failed", e, context="batch_processing")
```

### FastAPI Integration

```python
from fastapi import FastAPI
from api.exception_handlers import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)
```

## Requirements Mapping

This implementation satisfies **Requirement 9** acceptance criteria:

1. ✅ **9.1**: Error logging with continuation - `AppException` allows catching and logging errors while continuing execution
2. ✅ **9.2**: User-friendly error messages - `AppException.to_dict()` provides structured, friendly error responses
3. ✅ **9.3**: OpenAI error handling - `OpenAIException` and `openai_exception_handler` handle OpenAI failures
4. ✅ **9.4**: Supabase error handling - `DatabaseException` handles database connection failures
5. ✅ **9.5**: Structured logging - `StructuredLogger` provides JSON-formatted logs for all critical operations

## Testing

Run the test script to verify functionality:

```bash
cd backend
python test_exceptions_logging.py
```

Note: Requires dependencies from `requirements.txt` to be installed.

## Log Output Format

All logs are output in JSON format:

```json
{
  "timestamp": "2025-10-27T10:30:45.123456",
  "logger": "agents.crew",
  "event": "agent_action",
  "environment": "development",
  "context": {
    "agent_name": "sql_specialist",
    "action": "execute_query",
    "success": true,
    "duration_ms": 89.3
  }
}
```

## Configuration

Log level is controlled via environment variable:

```bash
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```
