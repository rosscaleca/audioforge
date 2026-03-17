"""Tests for audioforge.core.validator."""

from pathlib import Path

import pytest

from audioforge.core.validator import (
    MAX_FILENAME_LENGTH,
    sanitize_filename,
    validate_input_files,
)


class TestSanitizeFilename:
    def test_normal_name_unchanged(self):
        assert sanitize_filename("My Audiobook") == "My Audiobook"

    def test_strips_whitespace(self):
        assert sanitize_filename("  hello  ") == "hello"

    def test_replaces_invalid_chars(self):
        assert sanitize_filename('file<>:"/\\|?*name') == "file_________name"

    def test_strips_leading_trailing_dots(self):
        assert sanitize_filename("...hidden...") == "hidden"

    def test_reserved_windows_names(self):
        assert sanitize_filename("CON") == "_CON"
        assert sanitize_filename("nul") == "_nul"
        assert sanitize_filename("COM1") == "_COM1"
        assert sanitize_filename("LPT9") == "_LPT9"

    def test_empty_string_returns_untitled(self):
        assert sanitize_filename("") == "Untitled"

    def test_only_dots_returns_untitled(self):
        assert sanitize_filename("...") == "Untitled"

    def test_only_spaces_returns_untitled(self):
        assert sanitize_filename("   ") == "Untitled"

    def test_max_length_enforced(self):
        long_name = "a" * 300
        result = sanitize_filename(long_name)
        assert len(result) <= MAX_FILENAME_LENGTH

    def test_control_characters_replaced(self):
        assert sanitize_filename("file\x00\x01name") == "file__name"

    def test_normal_special_chars_preserved(self):
        assert sanitize_filename("book (2024) - chapter 1") == "book (2024) - chapter 1"

    def test_unicode_preserved(self):
        assert sanitize_filename("日本語のタイトル") == "日本語のタイトル"


class TestValidateInputFiles:
    def test_valid_files(self, sample_files):
        files = [sample_files["track1.mp3"], sample_files["track2.flac"]]
        errors = validate_input_files(files)
        assert errors == []

    def test_nonexistent_file(self, tmp_dir):
        files = [tmp_dir / "nonexistent.mp3"]
        errors = validate_input_files(files)
        assert len(errors) == 1
        assert "not found" in errors[0].lower()

    def test_unsupported_format(self, sample_files):
        files = [sample_files["readme.txt"]]
        errors = validate_input_files(files)
        assert len(errors) == 1
        assert "unsupported" in errors[0].lower()

    def test_directory_instead_of_file(self, tmp_dir):
        subdir = tmp_dir / "subdir"
        subdir.mkdir()
        errors = validate_input_files([subdir])
        assert len(errors) == 1
        assert "not a file" in errors[0].lower()

    def test_mixed_valid_and_invalid(self, sample_files, tmp_dir):
        files = [
            sample_files["track1.mp3"],  # valid
            tmp_dir / "missing.mp3",  # nonexistent
            sample_files["data.json"],  # unsupported
        ]
        errors = validate_input_files(files)
        assert len(errors) == 2

    def test_empty_list(self):
        assert validate_input_files([]) == []

    def test_all_supported_extensions(self, tmp_dir):
        from audioforge.core.formats import SUPPORTED_INPUT

        files = []
        for ext in SUPPORTED_INPUT:
            path = tmp_dir / f"test{ext}"
            path.write_bytes(b"\x00" * 16)
            files.append(path)

        errors = validate_input_files(files)
        assert errors == []
