"""Tests for audioforge.core.formats."""

from audioforge.core.formats import (
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_QUALITY,
    OUTPUT_FORMATS,
    QUALITY_PRESETS,
    SUPPORTED_INPUT,
    get_codec,
    get_input_filetypes,
    get_output_extension,
    get_quality,
    is_supported_input,
)


class TestSupportedInput:
    def test_mp3_supported(self):
        assert ".mp3" in SUPPORTED_INPUT

    def test_common_formats_supported(self):
        expected = {".mp3", ".m4a", ".flac", ".wav", ".ogg", ".opus", ".aac", ".wma", ".aiff", ".aif"}
        assert expected == SUPPORTED_INPUT

    def test_is_supported_input_mp3(self):
        assert is_supported_input("track.mp3")

    def test_is_supported_input_flac(self):
        assert is_supported_input("album/track.FLAC")

    def test_is_supported_input_case_insensitive(self):
        assert is_supported_input("file.MP3")
        assert is_supported_input("file.Flac")

    def test_is_supported_input_unsupported(self):
        assert not is_supported_input("file.txt")
        assert not is_supported_input("file.pdf")
        assert not is_supported_input("file.mp4")


class TestOutputFormats:
    def test_m4b_format(self):
        fmt = OUTPUT_FORMATS["m4b"]
        assert fmt["extension"] == ".m4b"
        assert fmt["codec"] == "aac"
        assert fmt["supports_chapters"] is True

    def test_m4a_format(self):
        fmt = OUTPUT_FORMATS["m4a"]
        assert fmt["extension"] == ".m4a"
        assert fmt["codec"] == "aac"
        assert fmt["supports_chapters"] is False

    def test_mp3_format(self):
        fmt = OUTPUT_FORMATS["mp3"]
        assert fmt["extension"] == ".mp3"
        assert fmt["codec"] == "libmp3lame"
        assert fmt["supports_chapters"] is False

    def test_all_formats_have_required_keys(self):
        required = {"label", "extension", "codec", "container_flags", "supports_chapters"}
        for key, fmt in OUTPUT_FORMATS.items():
            assert required.issubset(fmt.keys()), f"Format '{key}' missing keys"

    def test_get_output_extension(self):
        assert get_output_extension("m4b") == ".m4b"
        assert get_output_extension("mp3") == ".mp3"

    def test_get_codec(self):
        assert get_codec("m4b") == "aac"
        assert get_codec("mp3") == "libmp3lame"

    def test_default_output_format_exists(self):
        assert DEFAULT_OUTPUT_FORMAT in OUTPUT_FORMATS


class TestQualityPresets:
    def test_default_quality_exists(self):
        assert DEFAULT_QUALITY in QUALITY_PRESETS

    def test_all_presets_have_bitrate_and_sample_rate(self):
        for name, preset in QUALITY_PRESETS.items():
            assert "bitrate" in preset, f"Preset '{name}' missing bitrate"
            assert "sample_rate" in preset, f"Preset '{name}' missing sample_rate"

    def test_get_quality(self):
        q = get_quality("Standard (128 kbps)")
        assert q["bitrate"] == "128k"
        assert q["sample_rate"] == 44100

    def test_bitrates_are_ascending(self):
        bitrates = []
        for preset in QUALITY_PRESETS.values():
            # Extract numeric part from e.g. "128k"
            bitrates.append(int(preset["bitrate"].rstrip("k")))
        assert bitrates == sorted(bitrates)


class TestInputFiletypes:
    def test_returns_list_of_tuples(self):
        filetypes = get_input_filetypes()
        assert isinstance(filetypes, list)
        assert all(isinstance(ft, tuple) and len(ft) == 2 for ft in filetypes)

    def test_first_entry_is_all_audio(self):
        filetypes = get_input_filetypes()
        label, pattern = filetypes[0]
        assert label == "Audio Files"
        assert "*.mp3" in pattern
        assert "*.flac" in pattern

    def test_last_entry_is_all_files(self):
        filetypes = get_input_filetypes()
        label, pattern = filetypes[-1]
        assert label == "All Files"
        assert pattern == "*.*"
