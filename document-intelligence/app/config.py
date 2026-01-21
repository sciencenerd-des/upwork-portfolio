"""
Configuration management for Document Intelligence System.
Loads settings from YAML files and environment variables.
"""

import os
from pathlib import Path
from typing import Any, Optional
from functools import lru_cache

import yaml
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings


# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"


class DocumentConfig(BaseModel):
    """Document processing configuration."""
    max_file_size_mb: int = 25
    max_pages: int = 50
    supported_formats: list[str] = [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif"]
    temp_dir: str = "/tmp/doc-intelligence"


class OCRConfig(BaseModel):
    """OCR engine configuration."""
    engine: str = "tesseract"
    language: str = "eng"
    timeout_per_page_seconds: int = 30
    dpi: int = 300
    preprocessing: dict = Field(default_factory=lambda: {
        "enabled": True,
        "deskew": True,
        "denoise": True,
        "enhance_contrast": True
    })
    confidence_threshold: int = 60


class TextProcessingConfig(BaseModel):
    """Text processing configuration."""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    min_chunk_size: int = 100
    sentence_boundary_detection: bool = True
    normalize_whitespace: bool = True
    remove_artifacts: bool = True


class EntityExtractionConfig(BaseModel):
    """Entity extraction configuration."""
    spacy_model: str = "en_core_web_sm"
    confidence_threshold: float = 0.7
    deduplicate: bool = True
    patterns: dict = Field(default_factory=dict)


class VectorStoreConfig(BaseModel):
    """Vector store configuration."""
    provider: str = "chromadb"
    collection_prefix: str = "doc_intelligence"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536
    top_k: int = 5
    relevance_threshold: float = 0.7


class LLMConfig(BaseModel):
    """LLM configuration via OpenRouter."""
    provider: str = "openrouter"
    base_url: str = "https://openrouter.ai/api/v1"
    primary_model: str = "anthropic/claude-sonnet-4-20250514"
    fallback_model: str = "openai/gpt-4o"
    embedding_model: str = "openai/text-embedding-3-small"
    max_tokens: int = 2048
    temperature: float = 0.1
    timeout_seconds: int = 60


class SummarizationConfig(BaseModel):
    """Summarization configuration."""
    max_summary_words: int = 200
    min_key_points: int = 3
    max_key_points: int = 7
    include_document_type: bool = True


class QAConfig(BaseModel):
    """Q&A configuration."""
    max_context_chunks: int = 5
    max_conversation_history: int = 10
    response_timeout_seconds: int = 30
    include_citations: bool = True
    generate_followup_questions: bool = True
    no_answer_response: str = "I cannot find this information in the document."


class ExportConfig(BaseModel):
    """Export configuration."""
    json_indent: int = 2
    csv_delimiter: str = ","
    excel_sheet_names: dict = Field(default_factory=lambda: {
        "summary": "Summary",
        "entities": "Entities",
        "raw_text": "Raw Text"
    })


class SessionConfig(BaseModel):
    """Session/document store configuration."""
    ttl_minutes: int = 60
    cleanup_interval_seconds: int = 300
    max_documents_per_session: int = 5


class PerformanceConfig(BaseModel):
    """Performance configuration."""
    max_processing_time_seconds: int = 90
    async_processing: bool = True
    progress_update_interval: int = 1


class APIConfig(BaseModel):
    """API configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = ["http://localhost:8501", "http://127.0.0.1:8501"]
    rate_limit_requests_per_minute: int = 60
    api_key: Optional[str] = None  # If set, requires X-API-Key header
    require_auth: bool = False  # Enable/disable API key authentication


class AppConfig(BaseModel):
    """Application configuration."""
    name: str = "Document Intelligence System"
    version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"


class Settings(BaseSettings):
    """Main settings class combining all configurations."""

    # API Keys (from environment variables)
    openrouter_api_key: Optional[str] = Field(default=None, alias="OPENROUTER_API_KEY")

    # Sub-configurations (loaded from YAML)
    app: AppConfig = Field(default_factory=AppConfig)
    document: DocumentConfig = Field(default_factory=DocumentConfig)
    ocr: OCRConfig = Field(default_factory=OCRConfig)
    text_processing: TextProcessingConfig = Field(default_factory=TextProcessingConfig)
    entity_extraction: EntityExtractionConfig = Field(default_factory=EntityExtractionConfig)
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    summarization: SummarizationConfig = Field(default_factory=SummarizationConfig)
    qa: QAConfig = Field(default_factory=QAConfig)
    export: ExportConfig = Field(default_factory=ExportConfig)
    session: SessionConfig = Field(default_factory=SessionConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    api: APIConfig = Field(default_factory=APIConfig)

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "populate_by_name": True
    }

    @classmethod
    def from_yaml(cls, yaml_path: Optional[Path] = None) -> "Settings":
        """Load settings from YAML file and merge with environment variables."""
        if yaml_path is None:
            yaml_path = CONFIG_DIR / "settings.yaml"

        yaml_config = {}
        if yaml_path.exists():
            with open(yaml_path, "r") as f:
                yaml_config = yaml.safe_load(f) or {}

        # Build nested config objects from YAML
        config_data = {}

        if "app" in yaml_config:
            config_data["app"] = AppConfig(**yaml_config["app"])
        if "document" in yaml_config:
            config_data["document"] = DocumentConfig(**yaml_config["document"])
        if "ocr" in yaml_config:
            config_data["ocr"] = OCRConfig(**yaml_config["ocr"])
        if "text_processing" in yaml_config:
            config_data["text_processing"] = TextProcessingConfig(**yaml_config["text_processing"])
        if "entity_extraction" in yaml_config:
            config_data["entity_extraction"] = EntityExtractionConfig(**yaml_config["entity_extraction"])
        if "vector_store" in yaml_config:
            config_data["vector_store"] = VectorStoreConfig(**yaml_config["vector_store"])
        if "llm" in yaml_config:
            config_data["llm"] = LLMConfig(**yaml_config["llm"])
        if "summarization" in yaml_config:
            config_data["summarization"] = SummarizationConfig(**yaml_config["summarization"])
        if "qa" in yaml_config:
            config_data["qa"] = QAConfig(**yaml_config["qa"])
        if "export" in yaml_config:
            config_data["export"] = ExportConfig(**yaml_config["export"])
        if "session" in yaml_config:
            config_data["session"] = SessionConfig(**yaml_config["session"])
        if "performance" in yaml_config:
            config_data["performance"] = PerformanceConfig(**yaml_config["performance"])
        if "api" in yaml_config:
            config_data["api"] = APIConfig(**yaml_config["api"])

        return cls(**config_data)


class Prompts:
    """Prompt templates loaded from YAML."""

    def __init__(self, prompts_path: Optional[Path] = None):
        if prompts_path is None:
            prompts_path = CONFIG_DIR / "prompts.yaml"

        self._prompts: dict = {}
        if prompts_path.exists():
            with open(prompts_path, "r") as f:
                self._prompts = yaml.safe_load(f) or {}

    @property
    def summarization_system(self) -> str:
        """Get summarization system prompt."""
        return self._prompts.get("summarization", {}).get("system", "")

    @property
    def summarization_user(self) -> str:
        """Get summarization user prompt template."""
        return self._prompts.get("summarization", {}).get("user", "")

    @property
    def qa_system(self) -> str:
        """Get Q&A system prompt."""
        return self._prompts.get("qa", {}).get("system", "")

    @property
    def qa_user(self) -> str:
        """Get Q&A user prompt template."""
        return self._prompts.get("qa", {}).get("user", "")

    @property
    def entity_extraction_system(self) -> str:
        """Get entity extraction system prompt."""
        return self._prompts.get("entity_extraction_enhancement", {}).get("system", "")

    @property
    def entity_extraction_user(self) -> str:
        """Get entity extraction user prompt template."""
        return self._prompts.get("entity_extraction_enhancement", {}).get("user", "")

    @property
    def document_type_patterns(self) -> dict:
        """Get document type classification patterns."""
        return self._prompts.get("document_type_classification", {}).get("patterns", {})

    def format_summarization_prompt(
        self,
        document_text: str,
        min_points: int = 3,
        max_points: int = 7
    ) -> tuple[str, str]:
        """Format summarization prompts with document text."""
        user_prompt = self.summarization_user.format(
            document_text=document_text,
            min_points=min_points,
            max_points=max_points
        )
        return self.summarization_system, user_prompt

    def format_qa_prompt(
        self,
        context: str,
        question: str,
        conversation_history: str = "",
        no_answer_response: str = "I cannot find this information in the document."
    ) -> tuple[str, str]:
        """Format Q&A prompts with context and question."""
        system_prompt = self.qa_system.format(no_answer_response=no_answer_response)
        user_prompt = self.qa_user.format(
            context=context,
            question=question,
            conversation_history=conversation_history or "No previous conversation."
        )
        return system_prompt, user_prompt


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings.from_yaml()


@lru_cache()
def get_prompts() -> Prompts:
    """Get cached prompts instance."""
    return Prompts()


# Convenience exports
settings = get_settings()
prompts = get_prompts()
