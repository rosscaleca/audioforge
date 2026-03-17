"""Audio metadata: duration probing and chapter file generation."""

import logging
import os
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from audioforge.core.ffmpeg import find_ffprobe

logger = logging.getLogger(__name__)


def get_duration(file_path: Path) -> float:
    """Get the duration of an audio file in milliseconds using ffprobe.

    Returns 0.0 if the duration cannot be determined.
    """
    ffprobe = find_ffprobe()
    if ffprobe is None:
        logger.warning("ffprobe not found, cannot determine duration for %s", file_path)
        return 0.0

    try:
        cmd = [
            str(ffprobe),
            "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(file_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return float(result.stdout.strip()) * 1000  # Convert to milliseconds
    except (ValueError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        logger.warning("Failed to get duration for %s: %s", file_path, e)
        return 0.0


def get_durations(files: list[Path], max_workers: int = 4) -> list[float]:
    """Get durations for multiple files concurrently.

    Returns a list of durations in milliseconds, one per file.
    """
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(get_duration, files))


def create_chapters_file(files: list[Path], durations: list[float]) -> Path:
    """Create an FFMETADATA1 file with chapter markers.

    Each file becomes a chapter. Chapter titles are derived from filenames.
    Returns the path to the temporary metadata file.
    """
    content = ";FFMETADATA1\n"
    current_time = 0.0

    for file_path, duration in zip(files, durations):
        if duration <= 0:
            continue

        chapter_title = file_path.stem
        content += "\n[CHAPTER]\n"
        content += "TIMEBASE=1/1000\n"
        content += f"START={int(current_time)}\n"
        content += f"END={int(current_time + duration)}\n"
        content += f"title={chapter_title}\n"

        current_time += duration

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        f.write(content)
        return Path(f.name)


def create_concat_file(files: list[Path]) -> Path:
    """Create an FFmpeg concat demuxer file.

    Returns the path to the temporary concat file.
    """
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        for file_path in files:
            # Escape single quotes for FFmpeg concat format
            escaped = str(file_path).replace("'", "'\\''")
            f.write(f"file '{escaped}'\n")
        return Path(f.name)
