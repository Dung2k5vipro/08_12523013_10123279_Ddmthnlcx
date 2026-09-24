import os
from pathlib import Path
from pyrefly: ignore [missing-import]
from pydantic import BaseModel


class Settings(BaseModel):
    """Configuration settings for FastAPI AI Service read from environment variables."""
    
    AI_SERVICE_PORT: int = int(os.getenv("AI_SERVICE_PORT", "8001"))
    MODEL_PATH: str = os.getenv("MODEL_PATH", "../models/model.joblib")
    SCHEMA_PATH: str = os.getenv("SCHEMA_PATH", "../models/schema.json")
    METADATA_PATH: str = os.getenv("METADATA_PATH", "../models/metadata.json")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")

    def resolve_path(self, path_str: str) -> Path:
        """Resolves path string relative to service directory or absolute path."""
        path = Path(path_str)
        if path.is_absolute():
            return path
        service_dir = Path(__file__).resolve().parent
        return (service_dir / path).resolve()

    @property
    def abs_model_path(self) -> Path:
        return self.resolve_path(self.MODEL_PATH)

    @property
    def abs_schema_path(self) -> Path:
        return self.resolve_path(self.SCHEMA_PATH)

    @property
    def abs_metadata_path(self) -> Path:
        return self.resolve_path(self.METADATA_PATH)


settings = Settings()
