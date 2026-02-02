"""File utility functions."""

import json
from pathlib import Path
from typing import Any, Dict


def ensure_directory(path: Path) -> Path:
    """Ensure directory exists, create if not.

    Args:
        path: Path to directory

    Returns:
        Path object
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json(file_path: Path) -> Dict[str, Any]:
    """Read JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        Dictionary from JSON

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    file_path = Path(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(file_path: Path, data: Dict[str, Any], indent: int = 2) -> None:
    """Write data to JSON file.

    Args:
        file_path: Path to JSON file
        data: Data to write
        indent: JSON indentation (default: 2)
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
