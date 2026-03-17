"""Shared test fixtures."""

import pytest
from pathlib import Path
import tempfile


@pytest.fixture
def tmp_dir():
    """Provide a temporary directory that is cleaned up after the test."""
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def sample_files(tmp_dir):
    """Create sample audio files (empty, just for path/extension testing)."""
    files = {}
    for name in ["track1.mp3", "track2.flac", "track3.wav", "track4.m4a", "readme.txt", "data.json"]:
        path = tmp_dir / name
        path.write_bytes(b"\x00" * 16)
        files[name] = path
    return files
