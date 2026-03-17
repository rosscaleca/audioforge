"""Main conversion pipeline: orchestrates FFmpeg conversion with progress."""

import logging
import os
import subprocess
import threading
from pathlib import Path
from typing import Callable

from audioforge.core.ffmpeg import CancelledError, find_ffmpeg, read_ffmpeg_progress
from audioforge.core.formats import OUTPUT_FORMATS, get_codec, get_quality
from audioforge.core.metadata import (
    create_chapters_file,
    create_concat_file,
    get_durations,
)
from audioforge.core.validator import validate_input_files

logger = logging.getLogger(__name__)


def convert(
    files: list[Path],
    output_path: Path,
    output_format: str,
    quality_preset: str,
    metadata: dict[str, str] | None = None,
    cover_art: Path | None = None,
    on_progress: Callable[[float], None] | None = None,
    on_status: Callable[[str], None] | None = None,
    cancel_event: threading.Event | None = None,
) -> None:
    """Run the full conversion pipeline.

    Args:
        files: Ordered list of input audio files.
        output_path: Path for the output file.
        output_format: Output format key (e.g., 'm4b', 'mp3').
        quality_preset: Quality preset name (e.g., 'Standard (128 kbps)').
        metadata: Optional dict of metadata tags (title, author, etc.).
        cover_art: Optional path to a cover art image (JPG/PNG).
        on_progress: Callback for progress updates (0-100).
        on_status: Callback for status text updates.
        cancel_event: Optional threading.Event; set it to cancel the conversion.

    Raises:
        ValueError: If input validation fails.
        RuntimeError: If FFmpeg conversion fails.
        CancelledError: If the conversion is cancelled.
    """
    if on_progress is None:
        on_progress = lambda _: None
    if on_status is None:
        on_status = lambda _: None
    if metadata is None:
        metadata = {}

    # Validate inputs
    on_status("Validating files...")
    errors = validate_input_files(files)
    if errors:
        raise ValueError("Input validation failed:\n" + "\n".join(errors))

    # Find ffmpeg
    ffmpeg = find_ffmpeg()
    if ffmpeg is None:
        raise RuntimeError("FFmpeg not found")

    concat_file = None
    chapters_file = None

    try:
        # Probe durations concurrently
        on_status("Analyzing audio files...")
        on_progress(5)
        durations = get_durations(files)
        total_duration_ms = sum(durations)
        logger.info("Total duration: %.1f seconds", total_duration_ms / 1000)

        # Create concat file
        concat_file = create_concat_file(files)

        # Build FFmpeg command
        fmt = OUTPUT_FORMATS[output_format]
        quality = get_quality(quality_preset)
        codec = get_codec(output_format)

        cmd = [
            str(ffmpeg), "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
        ]

        # Track input indices
        input_idx = 1  # 0 = concat input
        chapters_input_idx = None
        cover_input_idx = None

        # Declare ALL inputs first (order matters for FFmpeg)
        if fmt["supports_chapters"]:
            on_status("Generating chapter markers...")
            chapters_file = create_chapters_file(files, durations)
            cmd.extend(["-i", str(chapters_file)])
            chapters_input_idx = input_idx
            input_idx += 1

        has_cover = (
            cover_art is not None
            and cover_art.exists()
            and output_format in ("m4b", "m4a")
        )
        if has_cover:
            cmd.extend(["-i", str(cover_art)])
            cover_input_idx = input_idx
            input_idx += 1

        # Output options (must come AFTER all -i inputs)
        if chapters_input_idx is not None:
            cmd.extend(["-map_metadata", str(chapters_input_idx)])

        if cover_input_idx is not None:
            cmd.extend([
                "-map", "0:a",
                "-map", f"{cover_input_idx}:v",
                "-c:v", "copy",
                "-disposition:v", "attached_pic",
            ])

        # Audio encoding
        cmd.extend([
            "-c:a", codec,
            "-b:a", quality["bitrate"],
            "-ar", str(quality["sample_rate"]),
        ])

        # Container-specific flags
        cmd.extend(fmt["container_flags"])

        # Metadata tags
        _METADATA_MAP = {
            "title": "title",
            "author": "artist",
            "narrator": "composer",
            "year": "date",
            "genre": "genre",
            "description": "comment",
        }
        for key, value in metadata.items():
            ffmpeg_tag = _METADATA_MAP.get(key)
            if ffmpeg_tag:
                cmd.extend(["-metadata", f"{ffmpeg_tag}={value}"])

        # Output path
        cmd.append(str(output_path))

        logger.info("FFmpeg command: %s", " ".join(cmd))
        on_status("Converting...")
        on_progress(10)

        # Run FFmpeg with real-time progress
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Expose the process so it can be killed externally on cancel
        if cancel_event is not None:
            cancel_event._process = process

        # Scale progress from 10-95% during conversion
        def scaled_progress(pct):
            on_progress(10 + (pct * 0.85))

        stderr_output = read_ffmpeg_progress(process, total_duration_ms, scaled_progress)
        process.wait()

        # Check if cancelled (process was killed externally)
        if cancel_event is not None and cancel_event.is_set():
            raise CancelledError("Conversion cancelled")

        if process.returncode != 0:
            # Log full error
            logger.error("FFmpeg failed (exit %d):\n%s", process.returncode, stderr_output)
            # Show last 2000 chars to user
            display_error = stderr_output[-2000:] if len(stderr_output) > 2000 else stderr_output
            raise RuntimeError(f"FFmpeg conversion failed:\n{display_error}")

        on_progress(100)
        on_status(f"Done: {output_path.name}")
        logger.info("Conversion complete: %s", output_path)

    except CancelledError:
        # Clean up partial output file on cancel
        if output_path.exists():
            try:
                os.unlink(output_path)
                logger.info("Removed partial output: %s", output_path)
            except OSError:
                pass
        raise

    finally:
        # Clean up temp files
        for tmp in (concat_file, chapters_file):
            if tmp is not None:
                try:
                    os.unlink(tmp)
                except OSError:
                    pass
