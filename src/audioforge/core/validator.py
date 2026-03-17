"""Input validation and filename sanitization."""

import re
from pathlib import Path

from audioforge.core.formats import SUPPORTED_INPUT

# Characters invalid in filenames on Windows (also problematic elsewhere)
_INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

# Windows reserved names
_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}

MAX_FILENAME_LENGTH = 200


def sanitize_filename(name: str) -> str:
    """Sanitize a filename by removing or replacing invalid characters.

    Returns a safe filename string, or "Untitled" if the input is empty
    after sanitization.
    """
    # Strip leading/trailing whitespace
    name = name.strip()

    # Replace invalid characters with underscores
    name = _INVALID_CHARS.sub("_", name)

    # Strip leading/trailing dots and spaces (Windows doesn't like these)
    name = name.strip(". ")

    # Check for reserved names (Windows)
    if name.upper() in _RESERVED_NAMES:
        name = f"_{name}"

    # Enforce max length
    if len(name) > MAX_FILENAME_LENGTH:
        name = name[:MAX_FILENAME_LENGTH]

    # Fallback if empty
    if not name:
        name = "Untitled"

    return name


def validate_input_files(files: list[Path]) -> list[str]:
    """Validate a list of input files.

    Returns a list of error messages. An empty list means all files are valid.
    """
    errors = []

    for file in files:
        if not file.exists():
            errors.append(f"File not found: {file.name}")
        elif not file.is_file():
            errors.append(f"Not a file: {file.name}")
        elif file.suffix.lower() not in SUPPORTED_INPUT:
            errors.append(
                f"Unsupported format '{file.suffix}': {file.name}"
            )
        elif not _is_readable(file):
            errors.append(f"Cannot read file: {file.name}")

    return errors


def _is_readable(path: Path) -> bool:
    """Check if a file is readable."""
    try:
        with open(path, "rb") as f:
            f.read(1)
        return True
    except (OSError, PermissionError):
        return False
