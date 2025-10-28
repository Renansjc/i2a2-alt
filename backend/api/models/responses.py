"""Response models for API endpoints"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AgentType(str, Enum):
    """Types of agents that can process requests"""
    COORDINATOR = "coordinator"
    SQL_SPECIALIST = "sql_specialist"
    CONVERSATION_SPECIALIST = "conversation_specialist"
    SYSTEM = "system"


class ChatResponse(BaseModel):
    """Response model for chat endpoint
    
    Requirements: 7.1, 7.2, 7.3, 7.4
    """
    session_id: str = Field(
        ...,
        description="ID da sessão do usuário"
    )
    message: str = Field(
        ...,
        description="Resposta do sistema"
    )
    agent_used: str = Field(
        ...,
        description="Agente que processou a requisição"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp da resposta"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Metadados adicionais sobre o processamento"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "user-123-session",
                    "message": "Foram emitidas 42 notas fiscais este mês, totalizando R$ 125.430,50.",
                    "agent_used": "sql_specialist",
                    "timestamp": "2025-10-27T10:30:00",
                    "metadata": {
                        "query_executed": True,
                        "processing_time_ms": 1250
                    }
                }
            ]
        }
    }


class BatchJobStatus(str, Enum):
    """Status of batch processing job"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BatchUploadResponse(BaseModel):
    """Response model for batch upload endpoint
    
    Requirements: 7.5, 1.1, 1.3, 1.4, 1.5
    """
    job_id: str = Field(
        ...,
        description="ID único do job de processamento em lote"
    )
    status: BatchJobStatus = Field(
        ...,
        description="Status atual do job"
    )
    total_files: int = Field(
        ...,
        ge=0,
        description="Total de arquivos XML encontrados"
    )
    successful: int = Field(
        default=0,
        ge=0,
        description="Número de arquivos processados com sucesso"
    )
    failed: int = Field(
        default=0,
        ge=0,
        description="Número de arquivos que falharam no processamento"
    )
    errors: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Lista de erros encontrados durante o processamento"
    )
    duration_seconds: Optional[float] = Field(
        default=None,
        ge=0,
        description="Duração do processamento em segundos (disponível quando completo)"
    )
    started_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp de início do processamento"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp de conclusão do processamento"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "job_id": "batch-20251027-103000-abc123",
                    "status": "completed",
                    "total_files": 10,
                    "successful": 8,
                    "failed": 2,
                    "errors": [
                        {
                            "file": "nota_invalida.xml",
                            "error": "XML malformado: tag de fechamento ausente"
                        },
                        {
                            "file": "nota_duplicada.xml",
                            "error": "Chave de acesso já existe no banco de dados"
                        }
                    ],
                    "duration_seconds": 45.3,
                    "started_at": "2025-10-27T10:30:00",
                    "completed_at": "2025-10-27T10:30:45"
                }
            ]
        }
    }


class BatchStatusResponse(BaseModel):
    """Response model for batch status endpoint
    
    Requirements: 7.5, 1.1
    """
    job_id: str = Field(
        ...,
        description="ID do job de processamento"
    )
    status: BatchJobStatus = Field(
        ...,
        description="Status atual do job"
    )
    progress: int = Field(
        ...,
        ge=0,
        le=100,
        description="Progresso do processamento em porcentagem (0-100)"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total de arquivos a processar"
    )
    processed: int = Field(
        default=0,
        ge=0,
        description="Número de arquivos já processados"
    )
    successful: int = Field(
        default=0,
        ge=0,
        description="Número de arquivos processados com sucesso"
    )
    failed: int = Field(
        default=0,
        ge=0,
        description="Número de arquivos que falharam"
    )
    current_file: Optional[str] = Field(
        default=None,
        description="Nome do arquivo sendo processado atualmente"
    )
    errors: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Lista de erros encontrados"
    )
    started_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp de início"
    )
    estimated_completion: Optional[datetime] = Field(
        default=None,
        description="Estimativa de conclusão (se disponível)"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "job_id": "batch-20251027-103000-abc123",
                    "status": "running",
                    "progress": 60,
                    "total": 10,
                    "processed": 6,
                    "successful": 5,
                    "failed": 1,
                    "current_file": "nota_007.xml",
                    "errors": [
                        {
                            "file": "nota_003.xml",
                            "error": "Timeout ao conectar com Supabase"
                        }
                    ],
                    "started_at": "2025-10-27T10:30:00",
                    "estimated_completion": "2025-10-27T10:31:00"
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: Dict[str, Any] = Field(
        ...,
        description="Detalhes do erro"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": {
                        "code": "validation_error",
                        "message": "Dados de entrada inválidos",
                        "details": {
                            "field": "session_id",
                            "issue": "Campo obrigatório ausente"
                        }
                    }
                }
            ]
        }
    }


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str = Field(
        ...,
        description="Status da aplicação"
    )
    version: str = Field(
        ...,
        description="Versão da aplicação"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp da verificação"
    )
    services: Dict[str, str] = Field(
        default_factory=dict,
        description="Status dos serviços externos"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "healthy",
                    "version": "1.0.0",
                    "timestamp": "2025-10-27T10:30:00",
                    "services": {
                        "openai": "connected",
                        "supabase": "connected",
                        "crewai": "initialized"
                    }
                }
            ]
        }
    }
