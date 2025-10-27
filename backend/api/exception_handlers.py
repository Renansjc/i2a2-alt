"""Exception handlers for FastAPI application"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import traceback
from typing import Union

from utils.exceptions import AppException, ErrorCode
from utils.logger import get_logger

logger = get_logger(__name__)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle application-specific exceptions
    
    Args:
        request: FastAPI request object
        exc: Application exception
        
    Returns:
        JSON response with error details
    """
    # Log the error
    logger.error(
        "application_exception",
        error_code=exc.code.value,
        message=exc.message,
        details=exc.details,
        path=request.url.path,
        method=request.method,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )


async def validation_exception_handler(
    request: Request,
    exc: Union[RequestValidationError, ValidationError]
) -> JSONResponse:
    """Handle Pydantic validation errors
    
    Args:
        request: FastAPI request object
        exc: Validation error
        
    Returns:
        JSON response with validation error details
    """
    # Extract validation errors
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    # Log the validation error
    logger.warning(
        "validation_error",
        path=request.url.path,
        method=request.method,
        errors=errors
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": ErrorCode.VALIDATION_ERROR.value,
                "message": "Validation error in request data",
                "details": {
                    "errors": errors
                }
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions
    
    Args:
        request: FastAPI request object
        exc: Generic exception
        
    Returns:
        JSON response with error details
    """
    # Log the unexpected error with full traceback
    logger.exception(
        "unexpected_exception",
        exc,
        path=request.url.path,
        method=request.method,
        exception_type=type(exc).__name__,
    )
    
    # In production, don't expose internal error details
    if hasattr(request.app.state, "settings"):
        is_production = request.app.state.settings.app_env == "production"
    else:
        is_production = False
    
    error_details = {}
    if not is_production:
        error_details = {
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "traceback": traceback.format_exc()
        }
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": ErrorCode.INTERNAL_ERROR.value,
                "message": "An unexpected error occurred",
                "details": error_details
            }
        }
    )


async def openai_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle OpenAI API exceptions
    
    Args:
        request: FastAPI request object
        exc: OpenAI exception
        
    Returns:
        JSON response with error details
    """
    # Log OpenAI error
    logger.error(
        "openai_api_error",
        path=request.url.path,
        method=request.method,
        exception_type=type(exc).__name__,
        exception_message=str(exc),
    )
    
    # Determine error code based on exception type
    error_code = ErrorCode.OPENAI_API_ERROR
    status_code = status.HTTP_502_BAD_GATEWAY
    message = "Error communicating with OpenAI API"
    
    # Check for specific OpenAI error types
    exc_name = type(exc).__name__
    if "RateLimitError" in exc_name:
        error_code = ErrorCode.OPENAI_RATE_LIMIT
        status_code = status.HTTP_429_TOO_MANY_REQUESTS
        message = "OpenAI API rate limit exceeded. Please try again later."
    elif "Timeout" in exc_name:
        error_code = ErrorCode.OPENAI_TIMEOUT
        status_code = status.HTTP_504_GATEWAY_TIMEOUT
        message = "OpenAI API request timed out"
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": error_code.value,
                "message": message,
                "details": {
                    "exception_type": exc_name,
                    "exception_message": str(exc)
                }
            }
        }
    )


def register_exception_handlers(app):
    """Register all exception handlers with FastAPI app
    
    Args:
        app: FastAPI application instance
    """
    # Application-specific exceptions
    app.add_exception_handler(AppException, app_exception_handler)
    
    # Validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    
    # Generic exceptions (catch-all)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("exception_handlers_registered", handlers=[
        "AppException",
        "RequestValidationError",
        "ValidationError",
        "Exception"
    ])
