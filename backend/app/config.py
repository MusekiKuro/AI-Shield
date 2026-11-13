from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env", env_file_encoding="utf-8",
        extra="ignore", case_sensitive=False,
    )

    demo_mode: bool = True
    database_url: str = "sqlite:///./data/app.db"
    decision_timeout_ms: int = Field(default=3000, gt=0)
    approval_ttl_seconds: int = Field(default=120, gt=0)
    llm_base_url: str = ""
    llm_model: str = "gemma-4-12b-shield"
    llm_api_key: SecretStr = SecretStr("")
    llm_timeout_ms: int = Field(default=2500, gt=0)
    llm_fallback_base_url: str = ""
    llm_fallback_model: str = ""
    stt_base_url: str = ""
    stt_api_key: SecretStr = SecretStr("")
    stt_timeout_ms: int = Field(default=8000, gt=0)

    @field_validator("llm_base_url", "llm_fallback_base_url", "stt_base_url")
    @classmethod
    def validate_service_url(cls, value: str) -> str:
        value = value.strip().rstrip("/")
        if not value:
            return ""
        parsed = urlsplit(value)
        if (parsed.scheme not in {"http", "https"} or not parsed.hostname
                or parsed.username or parsed.password or parsed.query or parsed.fragment):
            raise ValueError("Expected an HTTP(S) base URL without credentials or query")
        return value

    @model_validator(mode="after")
    def validate_models(self) -> "Settings":
        if self.llm_base_url and not self.llm_model.strip():
            raise ValueError("LLM_MODEL is required when LLM_BASE_URL is set")
        if self.llm_fallback_base_url and not self.llm_fallback_model.strip():
            raise ValueError("LLM_FALLBACK_MODEL is required for the fallback server")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
