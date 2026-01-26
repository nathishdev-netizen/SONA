"""
SONA AI Configuration Management
Centralized settings using Pydantic Settings
"""

from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = "SONA AI"
    app_version: str = "0.1.0"
    debug: bool = True
    log_level: str = "INFO"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    cors_origins: str = "http://localhost:3000,http://localhost:8501"
    
    # LLM Providers
    openai_api_key: str
    groq_api_key: str = ""
    default_llm_provider: Literal["openai", "groq"] = "openai"
    openai_model: str = "gpt-4o-mini"
    groq_model: str = "llama-3.3-70b-versatile"
    
    # Opik
    opik_api_key: str = ""
    opik_workspace: str = "sona-ai"
    opik_project_name: str = "sona-evaluation"
    opik_url: str = "https://www.comet.com/opik"
    
    # Pinecone
    pinecone_api_key: str
    pinecone_environment: str = "us-east-1"
    pinecone_index_name: str = "sona-embeddings"
    pinecone_dimension: int = 1536
    
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/sona"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_enabled: bool = False
    
    # Voice
    whisper_model: str = "base"
    whisper_device: str = "cpu"
    tts_engine: Literal["piper", "coqui", "openai"] = "piper"
    tts_model: str = "en_US-lessac-medium"
    tts_speed: float = 1.0
    openai_tts_voice: str = "alloy"
    
    # Content Extraction
    youtube_api_key: str = ""
    user_agent: str = "Mozilla/5.0 (SONA AI Bot)"
    scraping_timeout: int = 30
    
    # Session Configuration
    min_questions: int = 3
    max_questions: int = 15
    confidence_threshold: float = 0.85
    
    # Guardrails
    guardrails_enabled: bool = True
    toxic_threshold: float = 0.7
    jailbreak_detection: bool = True
    
    # File Upload
    max_upload_size: int = 10485760  # 10MB
    allowed_extensions: str = "pdf,txt,doc,docx"
    
    # MCP
    mcp_enabled: bool = False
    mcp_server_port: int = 3001
    
    # Testing
    testing: bool = False
    mock_llm: bool = False
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def allowed_extensions_list(self) -> list[str]:
        """Parse allowed file extensions"""
        return [ext.strip() for ext in self.allowed_extensions.split(",")]


# Global settings instance
settings = Settings()
