import os
import json
from pathlib import Path
from typing import Any, Union


def get_project_root() -> Path:
    """Returns the absolute path to the repository root directory."""
    # src/utils.py is 2 levels deep from ai-models, 3 levels deep from root
    current_file = Path(__file__).resolve()
    return current_file.parent.parent.parent


def get_ai_models_root() -> Path:
    """Returns the absolute path to the ai-models directory."""
    current_file = Path(__file__).resolve()
    return current_file.parent.parent


def ensure_dir(dir_path: Union[str, Path]) -> Path:
    """Ensures a directory exists, creating parent directories if necessary."""
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_json(data: Any, file_path: Union[str, Path], indent: int = 2) -> None:
    """Saves data to a JSON file with specified formatting."""
    path = Path(file_path)
    ensure_dir(path.parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def load_json(file_path: Union[str, Path]) -> Any:
    """Loads and returns data from a JSON file."""
    path = Path(file_path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
