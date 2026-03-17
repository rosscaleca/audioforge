# AudioForge

A cross-platform desktop application for merging multiple audio files into a single output with chapter markers, metadata, and cover art. Built for creating audiobooks, but works for any audio merging task.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey)

## Download

| Platform | Download |
|----------|----------|
| macOS | [AudioForge-macOS.zip](https://github.com/rosscaleca/audioforge/releases/latest/download/AudioForge-macOS.zip) |
| Windows | [AudioForge-Windows.zip](https://github.com/rosscaleca/audioforge/releases/latest/download/AudioForge-Windows.zip) |
| Linux | [AudioForge-Linux.zip](https://github.com/rosscaleca/audioforge/releases/latest/download/AudioForge-Linux.zip) |

> **Requires [FFmpeg](https://ffmpeg.org/)** installed on your system. See [Installing FFmpeg](#installing-ffmpeg) below.

## Features

- **Multi-format input** — MP3, M4A, AAC, FLAC, WAV, OGG, Opus, WMA, AIFF
- **Multiple output formats** — M4B (audiobook with chapters), M4A, MP3
- **Chapter markers** — Automatically generated from input filenames (M4B output)
- **Metadata editing** — Title, author, narrator, year, genre, description
- **Cover art** — Embed JPG/PNG artwork with thumbnail preview
- **Quality presets** — Low (64 kbps) through Very High (256 kbps)
- **Real-time progress** — Live progress bar tracking FFmpeg conversion
- **Drag and drop** — Drop audio files directly into the app
- **Cancel support** — Stop a conversion at any time
- **Cross-platform** — Native look on macOS, Windows, and Linux

## How to Use

### 1. Add Audio Files

- **Drag and drop** files onto the drop zone, or
- Click **Add Files** to browse and select audio files
- Use **Move Up / Move Down** to reorder files (this determines chapter order)
- Use **Remove** or **Clear** to manage your file list

### 2. Configure Output

- **Name** — Set the output filename (invalid characters are automatically sanitized)
- **Save to** — Choose the output directory (defaults to ~/Downloads)
- **Format** — Select the output format:
  - **M4B** — Audiobook format with chapter markers (recommended for audiobooks)
  - **M4A** — AAC audio without chapter markers
  - **MP3** — Universal compatibility
- **Quality** — Choose a quality preset:
  - Low (64 kbps) — Smallest file size
  - Medium (96 kbps)
  - Standard (128 kbps) — Good balance of size and quality
  - High (192 kbps)
  - Very High (256 kbps) — Best quality

### 3. Add Metadata (Optional)

Click **Metadata (optional)** to expand the metadata panel:

- **Title** — Book or album title
- **Author** — Writer or artist
- **Narrator** — Reader or performer
- **Year** — Publication year
- **Genre** — Pre-filled with "Audiobook"
- **Description** — Additional notes
- **Cover Art** — Browse for a JPG or PNG image

### 4. Convert

Click **Convert** to start. The progress bar shows real-time conversion progress. Click the red **Cancel** button at any time to stop the conversion (partial output is automatically cleaned up).

## Installing FFmpeg

AudioForge requires FFmpeg to be installed on your system.

**macOS (Homebrew):**
```bash
brew install ffmpeg
```

**Windows (winget):**
```bash
winget install ffmpeg
```
Or download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to your PATH.

**Linux (apt):**
```bash
sudo apt install ffmpeg
```

**Linux (dnf):**
```bash
sudo dnf install ffmpeg
```

## Running from Source

```bash
git clone https://github.com/rosscaleca/audioforge.git
cd audioforge
pip install -e .
python -m audioforge
```

### Running Tests

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
```

## FAQ

**Q: What audio formats can I use as input?**
MP3, M4A, AAC, FLAC, WAV, OGG, Opus, WMA, AIFF, and AIF files are all supported.

**Q: Which output format should I choose?**
For audiobooks, use **M4B** — it's the standard audiobook format and supports chapter markers. Use **MP3** if you need maximum compatibility with older devices. Use **M4A** for general audio merging without chapter markers.

**Q: How are chapters created?**
Each input file becomes one chapter. The chapter title is the filename (without the extension). Reorder files in the list to control chapter order. Chapters are only embedded in M4B output.

**Q: What quality should I use?**
For spoken word (audiobooks, podcasts), **Standard (128 kbps)** or **Medium (96 kbps)** is plenty. For music, use **High (192 kbps)** or **Very High (256 kbps)**.

**Q: Can I embed cover art?**
Yes. Expand the Metadata section and click Browse next to Cover Art to select a JPG or PNG image. Cover art is supported for M4B and M4A output formats.

**Q: Why is FFmpeg required?**
AudioForge uses FFmpeg under the hood for audio decoding, encoding, and container muxing. It's the industry-standard tool for audio/video processing.

**Q: The conversion failed. What should I do?**
Check the error message in the dialog — it shows the FFmpeg error output. Common issues:
- FFmpeg is not installed or not in your PATH
- Input files are corrupted or not valid audio
- The output directory doesn't exist or isn't writable
- Disk space is full

**Q: Can I mix different audio formats in one conversion?**
Yes. You can combine MP3, FLAC, WAV, and any other supported format in a single conversion. FFmpeg handles the transcoding automatically.

**Q: Where are log files stored?**
Logs are stored in `~/.audioforge/logs/audioforge.log` with automatic rotation (5 MB max, 3 backups).

## Building Distributable Packages

```bash
pip install -e ".[dev]"

# macOS
bash build/build_macos.sh

# Windows
build\build_windows.bat

# Linux
bash build/build_linux.sh
```

Builds are output to `dist/<platform>/`. The GitHub Actions workflow automatically builds for all three platforms on push to `main` or when a version tag is created.

## License

MIT
