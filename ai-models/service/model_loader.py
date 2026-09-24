import json
from pathlib import Path
from typing import Dict, Any, Optional
import joblib
from service.config import settings


class ModelContainer:
    """Container holding loaded model pipeline, schema, and metadata."""

    def __init__(self):
        self.model: Optional[Any] = None
        self.schema: Optional[Dict[str, Any]] = None
        self.metadata: Optional[Dict[str, Any]] = None
        self.is_loaded: bool = False
        self.error_message: Optional[str] = None

    def load_artifacts(self) -> None:
        """Loads model.joblib, schema.json, and metadata.json into memory."""
        try:
            model_path = settings.abs_model_path
            schema_path = settings.abs_schema_path
            metadata_path = settings.abs_metadata_path

            if not model_path.exists():
                raise FileNotFoundError(f"Model file missing at: {model_path}")
            if not schema_path.exists():
                raise FileNotFoundError(f"Schema file missing at: {schema_path}")
            if not metadata_path.exists():
                raise FileNotFoundError(f"Metadata file missing at: {metadata_path}")

            print(f"[AI-SERVICE] Loading production model from: {model_path}")
            self.model = joblib.load(model_path)

            print(f"[AI-SERVICE] Loading schema from: {schema_path}")
            with open(schema_path, "r", encoding="utf-8") as f:
                self.schema = json.load(f)

            print(f"[AI-SERVICE] Loading metadata from: {metadata_path}")
            with open(metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)

            self.is_loaded = True
            self.error_message = None
            print(f"[AI-SERVICE] Successfully loaded model v{self.metadata.get('model_version', '1.0.0')} ({self.metadata.get('model_name', 'knn')})")
        except Exception as e:
            self.is_loaded = False
            self.error_message = str(e)
            print(f"[AI-SERVICE ERROR] Failed to load model artifacts: {e}")


# Singleton instance
container = ModelContainer()
