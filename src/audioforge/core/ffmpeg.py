"""FFmpeg/ffprobe binary detection and real-time progress parsing."""

import logging
import re
import shutil
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

_TIME_PATTERN = re.compile(r"time=(\d+):(\d+):(\d+(?:\.\d+)?)")


def find_ffmpeg() -> Path | None:
    """Find the ffmpeg binary. Returns the path or None."""
    # Check PATH first
    path = shutil.which("ffmpeg")
    if path:
        return Path(path)

    # Platform-specific common locations
    if sys.platform == "win32":
        candidates = [
            Path(r"C:\ffmpeg\bin\ffmpeg.exe"),
            Path(r"C:\Program Files\ffmpeg\bin\ffmpeg.exe"),
        ]
    elif sys.platform == "darwin":
        candidates = [
            Path("/opt/homebrew/bin/ffmpeg"),
            Path("/usr/local/bin/ffmpeg"),
        ]
    else:
        candidates = [
            Path("/usr/bin/ffmpeg"),
            Path("/usr/local/bin/ffmpeg"),
        ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


def find_ffprobe() -> Path | None:
    """Find the ffprobe binary. Returns the path or None."""
    path = shutil.which("ffprobe")
    if path:
        return Path(path)

    # Try to find ffprobe next to ffmpeg
    ffmpeg = find_ffmpeg()
    if ffmpeg:
        ffprobe = ffmpeg.parent / ffmpeg.name.replace("ffmpeg", "ffprobe")
        if ffprobe.exists():
            return ffprobe

    return None


def check_ffmpeg() -> bool:
    """Check if ffmpeg is available and working."""
    ffmpeg = find_ffmpeg()
    if ffmpeg is None:
        return False
    try:
        subprocess.run(
            [str(ffmpeg), "-version"],
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def parse_progress(line: str, total_duration_ms: float) -> float | None:
    """Parse an FFmpeg stderr line and return progress percentage (0-100).

    Returns None if the line doesn't contain time information.
    """
    match = _TIME_PATTERN.search(line)
    if not match:
        return None

    hours = int(match.group(1))
    minutes = int(match.group(2))
    seconds = float(match.group(3))

    current_ms = (hours * 3600 + minutes * 60 + seconds) * 1000

    if total_duration_ms <= 0:
        return 0.0

    percent = (current_ms / total_duration_ms) * 100.0
    return min(percent, 100.0)


class CancelledError(Exception):
    """Raised when a conversion is cancelled by the user."""
    pass


def read_ffmpeg_progress(process: subprocess.Popen, total_duration_ms: float, callback) -> str:
    """Read FFmpeg stderr in real-time and call callback with progress percentage.

    FFmpeg outputs progress on stderr using \\r for line updates.
    We read byte-by-byte and split on both \\r and \\n to get each status line.

    Returns all stderr output as a string (for error reporting if FFmpeg fails).
    """
    buffer = []
    all_lines = []
    stderr = process.stderr

    while True:
        byte = stderr.read(1)
        if not byte:
            break

        char = byte.decode("utf-8", errors="replace")

        if char in ("\r", "\n"):
            if buffer:
                line = "".join(buffer)
                buffer.clear()
                all_lines.append(line)

                progress = parse_progress(line, total_duration_ms)
                if progress is not None:
                    callback(progress)
        else:
            buffer.append(char)

    # Process any remaining buffer
    if buffer:
        line = "".join(buffer)
        all_lines.append(line)
        progress = parse_progress(line, total_duration_ms)
        if progress is not None:
            callback(progress)

    return "\n".join(all_lines)
