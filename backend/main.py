"""
Multi-Agent NF-e System - FastAPI Application

This is the main entry point for the Multi-Agent NF-e System backend.
It initializes and configures the FastAPI application with:
- CrewAI multi-agent system for NF-e processing
- Chat memory with RAG capabilities
- Batch processing for XML imports
- REST API endpoints for frontend communication
- CORS middleware for cross-origin requests
- Health check endpoints

Requirements satisfied:
- 7.1: REST API using FastAPI
- 8.1: OpenAI API key from environment
- 8.2: Supabase credentials from environment
- 8.3: Error on missing required environment variables
"""

import os
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from config import settings
from agents.crew import NFeCrew
from memory.chat_memory import ChatMemory
from batch.processor import BatchProcessor
from batch.job_manager import get_job_manager
from api.routes import chat, batch
from utils.logger import get_logger
from utils.exceptions import AppException, ErrorCode

# Initialize logger
logger = get_logger(__name__)

# Global instances (initialized in lifespan)
nfe_crew: NFeCrew = None
chat_memory: ChatMemory = None
batch_processor: BatchProcessor = None
job_manager = None


def validate_environment():
    """
    Validate that all required environment variables are set.
    
    Requirements:
    - 8.1: OpenAI API key from environment
    - 8.2: Supabase credentials from environment
    - 8.3: Error on missing required environment variables
    
    Raises:
        SystemExit: If required environment variables are missing
    """
    logger.info("validating_environment_variables")
    
    required_vars = {
        "OPENAI_API_KEY": settings.openai_api_key,
        "SUPABASE_URL": settings.supabase_url,
        "SUPABASE_SERVICE_KEY": settings.supabase_service_key
    }
    
    missing_vars = []
    
    for var_name, var_value in required_vars.items():
        if not var_value:
            missing_vars.append(var_name)
            logger.error(
                "missing_environment_variable",
                variable=var_name
            )
    
    if missing_vars:
        error_message = (
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            f"Please set these variables in your .env file or environment.\n"
            f"See .env.example for reference."
        )
        logger.error(
            "environment_validation_failed",
            missing_variables=missing_vars
        )
        print(f"\n❌ ERROR: {error_message}\n", file=sys.stderr)
        sys.exit(1)
    
    logger.info(
        "environment_validation_successful",
        openai_model=settings.openai_model,
        supabase_url=settings.supabase_url[:30] + "...",
        app_env=settings.app_env
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events:
    - Startup: Initialize NFeCrew, ChatMemory, and BatchProcessor
    - Shutdown: Cleanup resources
    
    Requirements:
    - Initializes NFeCrew with CrewAI agents
    - Initializes ChatMemory with RAG capabilities
    - Initializes BatchProcessor for XML imports
    """
    # Startup
    logger.info(
        "application_startup",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env
    )
    
    # Validate environment variables
    validate_environment()
    
    # Set OpenAI environment variables for CrewAI
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key
    os.environ["OPENAI_MODEL_NAME"] = settings.openai_model
    
    logger.info(
        "openai_configured",
        model=settings.openai_model
    )
    
    try:
        # Initialize NFeCrew
        logger.info("initializing_nfe_crew")
        global nfe_crew
        nfe_crew = NFeCrew()
        logger.info(
            "nfe_crew_initialized",
            agents=["coordenador", "sql_specialist", "conversation_specialist"]
        )
        
        # Initialize ChatMemory
        logger.info("initializing_chat_memory")
        global chat_memory
        storage_dir = settings.memory_storage_dir
        chat_memory = ChatMemory(storage_dir=storage_dir)
        logger.info(
            "chat_memory_initialized",
            storage_dir=chat_memory.storage_dir,
            max_history=settings.max_chat_history
        )
        
        # Initialize BatchProcessor
        logger.info("initializing_batch_processor")
        global batch_processor
        batch_processor = BatchProcessor(
            max_concurrent=settings.max_concurrent_uploads
        )
        logger.info(
            "batch_processor_initialized",
            max_concurrent=settings.max_concurrent_uploads
        )
        
        # Initialize JobManager
        logger.info("initializing_job_manager")
        global job_manager
        job_manager = get_job_manager()
        logger.info("job_manager_initialized")
        
        # Inject dependencies into route modules
        chat.initialize_chat_services(nfe_crew, chat_memory)
        batch.initialize_batch_services(batch_processor, job_manager)
        
        logger.info(
            "application_startup_complete",
            message="All services initialized successfully"
        )
        
    except Exception as e:
        logger.exception(
            "application_startup_failed",
            e
        )
        print(f"\n❌ STARTUP ERROR: {str(e)}\n", file=sys.stderr)
        sys.exit(1)
    
    yield
    
    # Shutdown
    logger.info("application_shutdown")
    
    # Cleanup resources if needed
    try:
        # Clear old batch jobs
        if batch_processor:
            batch_processor.clear_completed_jobs()
        
        if job_manager:
            job_manager.cleanup_old_jobs()
        
        logger.info("application_shutdown_complete")
        
    except Exception as e:
        logger.exception(
            "application_shutdown_error",
            e
        )


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    Multi-Agent NF-e System API
    
    A multi-agent AI system for processing electronic invoices (NF-e) using CrewAI.
    
    Features:
    - **Chat Interface**: Natural language queries about NF-e data
    - **Batch Processing**: Import multiple XML files in batch
    - **Multi-Agent System**: coordenador, SQL Specialist, and Conversation Specialist
    - **Memory System**: RAG-based conversation memory with semantic search
    
    The system uses three specialized agents:
    - **coordenador**: Analyzes intent and delegates tasks
    - **SQL Specialist**: Generates and executes database queries
    - **Conversation Specialist**: Formats responses in natural language
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(
    "cors_configured",
    allowed_origins=settings.cors_origins
)

# Include routers
app.include_router(chat.router)
app.include_router(batch.router)

logger.info("routers_registered")


# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle application-specific exceptions
    
    Converts AppException instances to appropriate HTTP responses
    with structured error information.
    """
    logger.error(
        "app_exception_handled",
        error_code=exc.code.value,
        message=exc.message,
        details=exc.details,
        path=request.url.path
    )
    
    # Map error codes to HTTP status codes
    status_code_map = {
        ErrorCode.OPENAI_API_ERROR: status.HTTP_502_BAD_GATEWAY,
        ErrorCode.DATABASE_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ErrorCode.INVALID_SQL: status.HTTP_400_BAD_REQUEST,
        ErrorCode.XML_PARSE_ERROR: status.HTTP_400_BAD_REQUEST,
        ErrorCode.AGENT_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ErrorCode.VALIDATION_ERROR: status.HTTP_400_BAD_REQUEST,
        ErrorCode.BATCH_PROCESSING_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    
    status_code = status_code_map.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": exc.code.value,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors
    
    Converts Pydantic validation errors to structured HTTP responses.
    """
    logger.warning(
        "validation_error",
        errors=exc.errors(),
        path=request.url.path
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed",
                "details": exc.errors()
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions
    
    Catches any unhandled exceptions and returns a generic error response.
    """
    logger.exception(
        "unhandled_exception",
        exc,
        path=request.url.path
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "internal_server_error",
                "message": "An unexpected error occurred",
                "details": {"error": str(exc)} if settings.app_env == "development" else {}
            }
        }
    )


# Health check endpoints
@app.get(
    "/health",
    tags=["health"],
    summary="Health check",
    description="Check if the API is running and all services are initialized",
    responses={
        200: {
            "description": "API is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "version": "1.0.0",
                        "environment": "development"
                    }
                }
            }
        }
    }
)
async def health_check():
    """Basic health check endpoint
    
    Returns:
        Dictionary with health status
    """
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.app_env
    }


@app.get(
    "/health/detailed",
    tags=["health"],
    summary="Detailed health check",
    description="""
    Detailed health check with information about all system components.
    
    Includes:
    - CrewAI configuration and agent status
    - Memory system statistics
    - Batch processing statistics
    - Database connectivity
    """,
    responses={
        200: {
            "description": "Detailed health information",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "version": "1.0.0",
                        "environment": "development",
                        "services": {
                            "crewai": {
                                "initialized": True,
                                "agents": ["coordenador", "sql_specialist", "conversation_specialist"],
                                "model": "gpt-4o-mini"
                            },
                            "memory": {
                                "initialized": True,
                                "active_sessions": 5,
                                "total_messages": 42
                            },
                            "batch_processor": {
                                "initialized": True,
                                "active_jobs": 1,
                                "total_jobs": 10
                            }
                        }
                    }
                }
            }
        }
    }
)
async def detailed_health_check():
    """Detailed health check with service information
    
    Requirements:
    - Implements health check endpoint with CrewAI information
    
    Returns:
        Dictionary with detailed health status
    """
    health_info = {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.app_env,
        "services": {}
    }
    
    # CrewAI status
    if nfe_crew:
        health_info["services"]["crewai"] = {
            "initialized": True,
            "agents": [
                "coordenador",
                "sql_specialist",
                "conversation_specialist"
            ],
            "model": settings.openai_model,
            "process": "hierarchical",
            "memory_enabled": True,
            "tools": [
                "DatabaseQueryTool",
                "DatabaseJoinQueryTool",
                "SchemaInfoTool",
                "SchemaSearchTool"
            ]
        }
    else:
        health_info["services"]["crewai"] = {
            "initialized": False,
            "error": "NFeCrew not initialized"
        }
        health_info["status"] = "degraded"
    
    # Memory status
    if chat_memory:
        memory_stats = chat_memory.get_memory_stats()
        health_info["services"]["memory"] = {
            "initialized": True,
            "active_sessions": memory_stats["total_sessions"],
            "total_cached_messages": memory_stats["total_cached_messages"],
            "storage_directory": memory_stats["storage_directory"],
            "max_history": settings.max_chat_history,
            "memory_systems": memory_stats["memory_systems"]
        }
    else:
        health_info["services"]["memory"] = {
            "initialized": False,
            "error": "ChatMemory not initialized"
        }
        health_info["status"] = "degraded"
    
    # Batch processor status
    if batch_processor and job_manager:
        job_stats = job_manager.get_statistics()
        health_info["services"]["batch_processor"] = {
            "initialized": True,
            "active_jobs": job_stats["active_jobs"],
            "total_jobs": job_stats["total_jobs"],
            "total_files_processed": job_stats["total_files_processed"],
            "total_successful": job_stats["total_successful"],
            "total_failed": job_stats["total_failed"],
            "max_concurrent": settings.max_concurrent_uploads
        }
    else:
        health_info["services"]["batch_processor"] = {
            "initialized": False,
            "error": "BatchProcessor or JobManager not initialized"
        }
        health_info["status"] = "degraded"
    
    # Configuration
    health_info["configuration"] = {
        "openai_model": settings.openai_model,
        "max_chat_history": settings.max_chat_history,
        "max_concurrent_uploads": settings.max_concurrent_uploads,
        "xml_folder": settings.xml_folder,
        "log_level": settings.log_level
    }
    
    logger.debug(
        "detailed_health_check_completed",
        status=health_info["status"]
    )
    
    return health_info


@app.get(
    "/",
    tags=["root"],
    summary="API root",
    description="Welcome message and API information"
)
async def root():
    """Root endpoint with API information
    
    Returns:
        Dictionary with welcome message and links
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "documentation": "/docs",
        "health_check": "/health",
        "endpoints": {
            "chat": "/api/chat",
            "batch": "/api/batch"
        }
    }


# Run application (for development)
if __name__ == "__main__":
    import uvicorn
    
    logger.info(
        "starting_uvicorn_server",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )
