import fitz
from pathlib import Path
from typing import Union

PDF = Union[Path, bytes]


def to_PDF(file: PDF) -> fitz.Document:
    if isinstance(file, Path):
        doc = fitz.open(str(file))
    elif isinstance(file, bytes):
        doc = fitz.open("pdf", file)
    else:
        raise ValueError("Input data must be a file path or bytes.")
    return doc


def validate_path(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"The path {path} does not exist.")


def remove_temp(temp_path: Path) -> None:
    try:
        temp_path.unlink()
    except Exception as e:
        raise InterruptedError(f"Error cleaning up temporary file: {e}")
