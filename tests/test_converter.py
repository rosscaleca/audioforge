"""Integration tests for the conversion pipeline. Requires ffmpeg."""

import struct
import wave
from pathlib import Path

import pytest

from audioforge.core.ffmpeg import check_ffmpeg


def _create_wav(path: Path, duration_seconds: float = 1.0, sample_rate: int = 44100):
    """Create a minimal WAV file with silence."""
    num_frames = int(sample_rate * duration_seconds)
    with wave.open(str(path), "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(b"\x00\x00" * num_frames)


@pytest.fixture
def wav_files(tmp_dir):
    """Create a few short WAV files for testing."""
    files = []
    for i in range(3):
        path = tmp_dir / f"chapter_{i + 1}.wav"
        _create_wav(path, duration_seconds=0.5)
        files.append(path)
    return files


@pytest.mark.integration
class TestConversion:
    @pytest.fixture(autouse=True)
    def _require_ffmpeg(self):
        if not check_ffmpeg():
            pytest.skip("ffmpeg not available")

    def test_convert_to_m4b(self, wav_files, tmp_dir):
        from audioforge.core.converter import convert

        output = tmp_dir / "test_output.m4b"
        progress_values = []

        convert(
            files=wav_files,
            output_path=output,
            output_format="m4b",
            quality_preset="Standard (128 kbps)",
            on_progress=progress_values.append,
        )

        assert output.exists()
        assert output.stat().st_size > 0
        assert len(progress_values) > 0

    def test_convert_to_mp3(self, wav_files, tmp_dir):
        from audioforge.core.converter import convert

        output = tmp_dir / "test_output.mp3"

        convert(
            files=wav_files,
            output_path=output,
            output_format="mp3",
            quality_preset="Standard (128 kbps)",
        )

        assert output.exists()
        assert output.stat().st_size > 0

    def test_convert_to_m4a(self, wav_files, tmp_dir):
        from audioforge.core.converter import convert

        output = tmp_dir / "test_output.m4a"

        convert(
            files=wav_files,
            output_path=output,
            output_format="m4a",
            quality_preset="Low (64 kbps)",
        )

        assert output.exists()
        assert output.stat().st_size > 0

    def test_convert_with_metadata(self, wav_files, tmp_dir):
        from audioforge.core.converter import convert

        output = tmp_dir / "test_metadata.m4b"

        convert(
            files=wav_files,
            output_path=output,
            output_format="m4b",
            quality_preset="Standard (128 kbps)",
            metadata={"title": "Test Book", "author": "Test Author"},
        )

        assert output.exists()
        assert output.stat().st_size > 0

    def test_convert_invalid_files_raises(self, tmp_dir):
        from audioforge.core.converter import convert

        with pytest.raises(ValueError, match="validation failed"):
            convert(
                files=[tmp_dir / "nonexistent.mp3"],
                output_path=tmp_dir / "out.m4b",
                output_format="m4b",
                quality_preset="Standard (128 kbps)",
            )
