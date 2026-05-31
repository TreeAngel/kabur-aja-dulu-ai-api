"""
Core configuration — loads settings from .env via pydantic-settings.
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

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
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Gemini
    GEMINI_API_KEY: str

    # Paths
    ARTIFACTS_DIR: str = BASE_DIR / "artifacts"

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
