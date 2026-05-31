"""
Core configuration — loads settings from .env via pydantic-settings.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv('../../')

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    APP_NAME: str = "KaburAjaDulu.AI.API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = False

    # Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY") or "[GCP_API_KEY]"

    # Paths
    ARTIFACTS_DIR: str = "artifacts"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    @property
    def artifacts_path(self) -> Path:
        return Path(self.ARTIFACTS_DIR)

    @property
    def model_path(self) -> Path:
        return self.artifacts_path / "kaburajadulu_model.keras"

    @property
    def tokenizer_path(self) -> Path:
        return self.artifacts_path / "tokenizer.json"

    @property
    def label_classes_path(self) -> Path:
        return self.artifacts_path / "label_classes.json"

    @property
    def industry_skills_path(self) -> Path:
        return self.artifacts_path / "industry_skills.json"


settings = Settings()
