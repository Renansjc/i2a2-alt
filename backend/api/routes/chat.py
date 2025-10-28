"""Chat endpoints for Multi-Agent NF-e System

This module implements the chat API endpoints that allow users to interact
with the multi-agent system through natural language conversations.

Requirements satisfied:
- 7.1: REST API endpoint for sending messages
- 7.2: Endpoint receives messages via API
- 7.3: Messages processed through Agente Master (NFeCrew)
- 7.4: Response returned via API
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from typing import Optional
import time

from api.models.requests import ChatRequest
from api.models.responses import ChatResponse, AgentType
from agents.crew import NFeCrew
from memory.chat_memory import ChatMemory
from utils.exceptions import (
    AppException,
    ErrorCode,
    OpenAIException,
    AgentException,
    ValidationException
)
from utils.logger import get_logger

logger = get_logger(__name__)

# Initialize router
router = APIRouter(prefix="/api/chat", tags=["chat"])

# Global instances (will be initialized in main.py startup)
nfe_crew: Optional[NFeCrew] = None
chat_memory: Optional[ChatMemory] = None


def initialize_chat_services(crew: NFeCrew, memory: ChatMemory):
    """Initialize chat services with crew and memory instances
    
    This function should be called during application startup to inject
    the NFeCrew and ChatMemory dependencies.
    
    Args:
        crew: Initialized NFeCrew instance
        memory: Initialized ChatMemory instance
    """
    global nfe_crew, chat_memory
    nfe_crew = crew
    chat_memory = memory
    
    logger.info(
        "chat_services_initialized",
        crew_initialized=nfe_crew is not None,
        memory_initialized=chat_memory is not None
    )


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Process chat message",
    description="""
    Process a user message through the multi-agent system.
    
    The system will:
    1. Retrieve conversation history from memory
    2. Process the message through the NFeCrew (coordinator, SQL specialist, conversation specialist)
    3. Save the interaction to memory
    4. Return the agent's response
    
    The coordinator agent automatically determines whether to:
    - Query the database (delegates to SQL specialist)
    - Provide a conversational response (delegates to conversation specialist)
    """,
    responses={
        200: {
            "description": "Message processed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "session_id": "user-123-session",
                        "message": "Foram emitidas 42 notas fiscais este mês, totalizando R$ 125.430,50.",
                        "agent_used": "coordinator",
                        "timestamp": "2025-10-27T10:30:00",
                        "metadata": {
                            "processing_time_ms": 1250,
                            "history_messages": 4
                        }
                    }
                }
            }
        },
        400: {"description": "Invalid request data"},
        500: {"description": "Internal server error"},
        502: {"description": "OpenAI API error"}
    }
)
async def process_chat_message(request: ChatRequest) -> ChatResponse:
    """Process a chat message through the multi-agent system
    
    Requirements:
    - 7.1: REST API endpoint for sending messages
    - 7.2: Endpoint receives messages via API
    - 7.3: Messages processed through Agente Master (NFeCrew)
    - 7.4: Response returned via API
    - 6.3: Provides history to agents during processing
    - 6.4: Saves interactions to memory after processing
    
    Args:
        request: ChatRequest with session_id and message
        
    Returns:
        ChatResponse with agent's response and metadata
        
    Raises:
        HTTPException: If services not initialized or processing fails
    """
    start_time = time.time()
    
    # Validate services are initialized
    if nfe_crew is None or chat_memory is None:
        logger.error(
            "chat_services_not_initialized",
            session_id=request.session_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat services not initialized"
        )
    
    logger.info(
        "chat_request_received",
        session_id=request.session_id,
        message_length=len(request.message)
    )
    
    try:
        # Step 1: Retrieve conversation history from memory
        # Requirement 6.3: Provides history to agents during processing
        chat_history = chat_memory.get_history(request.session_id)
        
        logger.debug(
            "chat_history_retrieved",
            session_id=request.session_id,
            history_length=len(chat_history)
        )
        
        # Step 2: Process message through NFeCrew
        # Requirement 7.3: Messages processed through Agente Master
        try:
            response_message = nfe_crew.process_message(
                message=request.message,
                chat_history=chat_history,
                session_id=request.session_id
            )
            
            # Determine which agent was primarily used
            # In hierarchical process, coordinator manages everything
            agent_used = AgentType.COORDINATOR.value
            
        except Exception as e:
            # Handle OpenAI API errors
            if "openai" in str(type(e).__module__).lower():
                logger.error(
                    "openai_api_error_in_chat",
                    session_id=request.session_id,
                    error=str(e),
                    error_type=type(e).__name__
                )
                raise OpenAIException(
                    message=f"Error communicating with OpenAI: {str(e)}",
                    details={
                        "session_id": request.session_id,
                        "error_type": type(e).__name__
                    }
                )
            
            # Handle agent processing errors
            logger.error(
                "agent_processing_error",
                session_id=request.session_id,
                error=str(e),
                error_type=type(e).__name__
            )
            raise AgentException(
                message=f"Error processing message: {str(e)}",
                details={
                    "session_id": request.session_id,
                    "error_type": type(e).__name__
                }
            )
        
        # Step 3: Save interaction to memory
        # Requirement 6.4: Saves interactions to memory after processing
        try:
            # Save user message
            chat_memory.add_message(
                session_id=request.session_id,
                role="user",
                content=request.message,
                metadata={"timestamp": datetime.now().isoformat()}
            )
            
            # Save assistant response
            chat_memory.add_message(
                session_id=request.session_id,
                role="assistant",
                content=response_message,
                metadata={
                    "timestamp": datetime.now().isoformat(),
                    "agent_used": agent_used
                }
            )
            
            logger.debug(
                "interaction_saved_to_memory",
                session_id=request.session_id,
                total_messages=chat_memory.get_message_count(request.session_id)
            )
            
        except Exception as e:
            # Log memory error but don't fail the request
            logger.warning(
                "memory_save_failed",
                session_id=request.session_id,
                error=str(e),
                message="Continuing with response despite memory error"
            )
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Step 4: Return response
        # Requirement 7.4: Response returned via API
        response = ChatResponse(
            session_id=request.session_id,
            message=response_message,
            agent_used=agent_used,
            timestamp=datetime.now(),
            metadata={
                "processing_time_ms": round(processing_time_ms, 2),
                "history_messages": len(chat_history),
                "message_length": len(response_message)
            }
        )
        
        logger.info(
            "chat_request_completed",
            session_id=request.session_id,
            processing_time_ms=round(processing_time_ms, 2),
            response_length=len(response_message)
        )
        
        return response
        
    except AppException:
        # Re-raise application exceptions (already logged)
        raise
        
    except Exception as e:
        # Catch any unexpected errors
        logger.exception(
            "unexpected_error_in_chat",
            e,
            session_id=request.session_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get(
    "/history/{session_id}",
    summary="Get chat history",
    description="Retrieve the conversation history for a specific session",
    responses={
        200: {
            "description": "Chat history retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "session_id": "user-123-session",
                        "messages": [
                            {
                                "role": "user",
                                "content": "Olá",
                                "timestamp": "2025-10-27T10:29:00"
                            },
                            {
                                "role": "assistant",
                                "content": "Olá! Como posso ajudar?",
                                "timestamp": "2025-10-27T10:29:01"
                            }
                        ],
                        "message_count": 2
                    }
                }
            }
        },
        404: {"description": "Session not found"}
    }
)
async def get_chat_history(session_id: str):
    """Get conversation history for a session
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        Dictionary with session history
        
    Raises:
        HTTPException: If services not initialized or session not found
    """
    if chat_memory is None:
        logger.error("chat_memory_not_initialized")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat memory not initialized"
        )
    
    # Check if session exists
    if not chat_memory.session_exists(session_id):
        logger.warning(
            "session_not_found",
            session_id=session_id
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found"
        )
    
    # Get full history with metadata
    full_history = chat_memory.get_full_history(session_id)
    
    # Format response
    messages = [
        {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat(),
            "metadata": msg.metadata
        }
        for msg in full_history
    ]
    
    logger.info(
        "chat_history_retrieved",
        session_id=session_id,
        message_count=len(messages)
    )
    
    return {
        "session_id": session_id,
        "messages": messages,
        "message_count": len(messages)
    }


@router.delete(
    "/history/{session_id}",
    summary="Clear chat history",
    description="Clear the conversation history for a specific session",
    responses={
        200: {
            "description": "Chat history cleared successfully",
            "content": {
                "application/json": {
                    "example": {
                        "session_id": "user-123-session",
                        "cleared": True,
                        "message": "Chat history cleared successfully"
                    }
                }
            }
        },
        404: {"description": "Session not found"}
    }
)
async def clear_chat_history(session_id: str, clear_vectors: bool = False):
    """Clear conversation history for a session
    
    Args:
        session_id: Unique session identifier
        clear_vectors: Whether to also clear vectorized data (default: False)
        
    Returns:
        Dictionary with operation result
        
    Raises:
        HTTPException: If services not initialized or session not found
    """
    if chat_memory is None:
        logger.error("chat_memory_not_initialized")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat memory not initialized"
        )
    
    # Clear session
    cleared = chat_memory.clear_session(session_id, clear_vectors=clear_vectors)
    
    if not cleared:
        logger.warning(
            "session_clear_failed",
            session_id=session_id,
            reason="session_not_found"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found"
        )
    
    logger.info(
        "chat_history_cleared",
        session_id=session_id,
        vectors_cleared=clear_vectors
    )
    
    return {
        "session_id": session_id,
        "cleared": True,
        "message": "Chat history cleared successfully"
    }


@router.get(
    "/stats",
    summary="Get memory statistics",
    description="Get statistics about memory usage and active sessions",
    responses={
        200: {
            "description": "Memory statistics retrieved successfully"
        }
    }
)
async def get_memory_stats():
    """Get memory statistics
    
    Returns:
        Dictionary with memory statistics
        
    Raises:
        HTTPException: If services not initialized
    """
    if chat_memory is None:
        logger.error("chat_memory_not_initialized")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat memory not initialized"
        )
    
    stats = chat_memory.get_memory_stats()
    
    logger.debug("memory_stats_retrieved", stats=stats)
    
    return stats
