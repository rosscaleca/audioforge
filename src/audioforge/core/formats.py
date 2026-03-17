"""Audio format definitions, codec mappings, and quality presets."""

SUPPORTED_INPUT = {
    ".mp3",
    ".m4a",
    ".aac",
    ".flac",
    ".wav",
    ".ogg",
    ".opus",
    ".wma",
    ".aiff",
    ".aif",
}

OUTPUT_FORMATS = {
    "m4b": {
        "label": "M4B (Audiobook)",
        "extension": ".m4b",
        "codec": "aac",
        "container_flags": ["-movflags", "+faststart"],
        "supports_chapters": True,
    },
    "m4a": {
        "label": "M4A (AAC Audio)",
        "extension": ".m4a",
        "codec": "aac",
        "container_flags": ["-movflags", "+faststart"],
        "supports_chapters": False,
    },
    "mp3": {
        "label": "MP3 (MPEG Audio)",
        "extension": ".mp3",
        "codec": "libmp3lame",
        "container_flags": [],
        "supports_chapters": False,
    },
}

QUALITY_PRESETS = {
    "Low (64 kbps)": {"bitrate": "64k", "sample_rate": 22050},
    "Medium (96 kbps)": {"bitrate": "96k", "sample_rate": 44100},
    "Standard (128 kbps)": {"bitrate": "128k", "sample_rate": 44100},
    "High (192 kbps)": {"bitrate": "192k", "sample_rate": 44100},
    "Very High (256 kbps)": {"bitrate": "256k", "sample_rate": 48000},
}

DEFAULT_QUALITY = "Standard (128 kbps)"
DEFAULT_OUTPUT_FORMAT = "m4b"


def get_input_filetypes() -> list[tuple[str, str]]:
    """Return file type tuples for use in file dialogs."""
    extensions = " ".join(f"*{ext}" for ext in sorted(SUPPORTED_INPUT))
    return [
        ("Audio Files", extensions),
        ("MP3 Files", "*.mp3"),
        ("M4A Files", "*.m4a"),
        ("FLAC Files", "*.flac"),
        ("WAV Files", "*.wav"),
        ("OGG Files", "*.ogg"),
        ("OPUS Files", "*.opus"),
        ("All Files", "*.*"),
    ]


def is_supported_input(filename: str) -> bool:
    """Check if a filename has a supported input extension."""
    from pathlib import Path

    return Path(filename).suffix.lower() in SUPPORTED_INPUT


def get_output_extension(format_key: str) -> str:
    """Get the file extension for an output format."""
    return OUTPUT_FORMATS[format_key]["extension"]


def get_codec(format_key: str) -> str:
    """Get the FFmpeg codec name for an output format."""
    return OUTPUT_FORMATS[format_key]["codec"]


def get_quality(preset_name: str) -> dict:
    """Get bitrate and sample rate for a quality preset."""
    return QUALITY_PRESETS[preset_name]
