"""Request models for API endpoints"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ChatRequest(BaseModel):
    """Request model for chat endpoint
    
    Requirements: 7.1, 7.2
    """
    session_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="ID único da sessão do usuário",
        examples=["user-123-session"]
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Mensagem do usuário",
        examples=["Quantas notas fiscais foram emitidas este mês?"]
    )
    
    @field_validator('session_id')
    @classmethod
    def validate_session_id(cls, v: str) -> str:
        """Validate session_id format"""
        if not v or v.isspace():
            raise ValueError("session_id não pode estar vazio ou conter apenas espaços")
        return v.strip()
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate message content"""
        if not v or v.isspace():
            raise ValueError("message não pode estar vazio ou conter apenas espaços")
        return v.strip()
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "user-123-session",
                    "message": "Quantas notas fiscais foram emitidas este mês?"
                }
            ]
        }
    }


class BatchUploadRequest(BaseModel):
    """Request model for batch upload endpoint
    
    Requirements: 7.5, 1.1
    """
    xml_folder: str = Field(
        default="xml_nf",
        min_length=1,
        max_length=500,
        description="Pasta contendo arquivos XML de NF-e para processar",
        examples=["xml_nf", "uploads/nfe"]
    )
    max_concurrent: Optional[int] = Field(
        default=None,
        ge=1,
        le=20,
        description="Número máximo de uploads concorrentes (opcional, usa configuração padrão se não especificado)"
    )
    
    @field_validator('xml_folder')
    @classmethod
    def validate_xml_folder(cls, v: str) -> str:
        """Validate xml_folder path"""
        if not v or v.isspace():
            raise ValueError("xml_folder não pode estar vazio ou conter apenas espaços")
        
        # Remove leading/trailing whitespace and normalize path separators
        v = v.strip().replace('\\', '/')
        
        # Basic path validation - prevent directory traversal
        if '..' in v:
            raise ValueError("xml_folder não pode conter '..' (directory traversal não permitido)")
        
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "xml_folder": "xml_nf",
                    "max_concurrent": 5
                }
            ]
        }
    }
