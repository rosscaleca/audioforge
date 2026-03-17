# AudioForge

Cross-platform desktop app for merging audio files into a single output with chapter markers, metadata, and cover art. Built with CustomTkinter and FFmpeg.

## Quick Reference

```bash
# Install (dev mode)
pip install -e ".[dev]"

# Run
python -m audioforge

# Run with debug logging
python -m audioforge --log-level debug

# Run all tests (requires ffmpeg)
python -m pytest tests/ -v

# Run unit tests only (no ffmpeg needed)
python -m pytest tests/ -v -m "not integration" --ignore=tests/test_converter.py

# Build distributable (macOS)
bash build/build_macos.sh
```

## Architecture

```
src/audioforge/
├── __main__.py          # Entry point, CLI arg parsing, logging setup
├── app.py               # Main window, panel orchestration, conversion threading
├── logging_config.py    # RotatingFileHandler to ~/.audioforge/logs/
├── core/                # Pure logic (no GUI imports)
│   ├── converter.py     # Conversion pipeline: validate → probe → chapters → ffmpeg
│   ├── ffmpeg.py        # Binary detection, progress parsing, CancelledError
│   ├── formats.py       # SUPPORTED_INPUT, OUTPUT_FORMATS, QUALITY_PRESETS
│   ├── metadata.py      # Duration probing (concurrent), chapter/concat file generation
│   └── validator.py     # Filename sanitization, input file validation
├── platform/
│   └── compat.py        # Per-OS fonts, DPI scaling, ffmpeg install hints
└── ui/                  # CTkFrame subclasses (one per panel)
    ├── file_panel.py    # Drop zone, file list, add/remove/reorder
    ├── settings_panel.py # Output name, dir, format dropdown, quality preset
    ├── metadata_panel.py # Title/author/narrator/year/genre/cover art (collapsible)
    └── progress_panel.py # Progress bar, status label, ETA (thread-safe)
```

### Key patterns

- **core/ has no GUI imports.** All audio logic is testable without Tkinter. UI panels call into core/ via the converter pipeline.
- **Threading:** Conversion runs in a daemon thread. UI updates from the background thread use `widget.after(0, callback)`. Never call Tkinter methods directly from the conversion thread.
- **Cancellation:** `threading.Event` is passed to `convert()`. The app attaches the FFmpeg `subprocess.Popen` to the event object (`cancel_event._process`), then calls `process.terminate()` directly from the main thread on cancel. The converter checks `cancel_event.is_set()` after the progress reader exits.
- **FFmpeg command ordering:** All `-i` inputs must be declared before any output options (`-map_metadata`, `-map`, `-c:a`, etc.). Mixing them causes FFmpeg errors.
- **Progress parsing:** `read_ffmpeg_progress()` reads stderr byte-by-byte, splits on `\r`/`\n`, regex-matches `time=HH:MM:SS.ss`, and returns all stderr output as a string for error reporting.

### Supported formats

- **Input:** `.mp3`, `.m4a`, `.aac`, `.flac`, `.wav`, `.ogg`, `.opus`, `.wma`, `.aiff`, `.aif`
- **Output:** M4B (audiobook w/ chapters), M4A, MP3
- Codec is determined by output format: AAC for M4B/M4A, libmp3lame for MP3
- Chapters are only embedded in M4B output

## Testing

- **pytest** with `conftest.py` providing `tmp_dir` and `sample_files` fixtures
- `test_validator.py` and `test_formats.py` — pure unit tests, no external deps
- `test_ffmpeg_progress.py` — unit tests for stderr progress parsing
- `test_converter.py` — integration tests marked `@pytest.mark.integration`, require ffmpeg on PATH
- CI runs unit tests only; integration tests run locally

## Build & Release

- **PyInstaller** packages the app. Spec file: `build/audioforge.spec` (uses `SPECPATH` for CI-safe path resolution)
- **GitHub Actions** (`.github/workflows/build.yml`): test → build matrix (macOS/Windows/Linux) → release on `v*` tags
- macOS build outputs only `AudioForge.app` (not the raw COLLECT directory)
- Release artifacts are zipped per-platform and attached to the GitHub Release
- To create a release: `git tag v0.x.0 && git push origin v0.x.0`

## Dependencies

- `customtkinter` — GUI framework (wraps Tkinter)
- `tkinterdnd2` — Drag-and-drop (optional; graceful fallback)
- `Pillow` — Cover art thumbnails, icon loading
- `pyobjc-framework-Cocoa` — macOS only; sets dock icon via AppKit
- **FFmpeg** — External system dependency, not bundled

## Logs

Application logs: `~/.audioforge/logs/audioforge.log` (5 MB rotation, 3 backups)
