"""Configuration management for Multi-Agent NF-e System"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.5
    openai_max_tokens: Optional[int] = None
    
    # Supabase Configuration
    supabase_url: str
    supabase_service_key: str
    
    # Application Configuration
    app_env: str = "development"
    app_name: str = "Multi-Agent NF-e System"
    app_version: str = "1.0.0"
    log_level: str = "INFO"
    
    # Chat Memory Configuration
    max_chat_history: int = 4  # 2 interactions = 4 messages (user + assistant)
    memory_storage_dir: Optional[str] = None  # Custom storage dir for CrewAI memory
    enable_semantic_search: bool = True  # Enable RAG-based semantic search
    memory_search_limit: int = 5  # Max results for semantic 
    
    # Batch Processing Configuration
    xml_folder: str = "xml_nf"
    max_concurrent_uploads: int = 5
    batch_timeout_seconds: int = 300
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    cors_origins: list[str] = ["*"]
    
    # Database Configuration
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
