#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Building AudioForge for Linux..."
pip install -e ".[dev]"
pyinstaller build/audioforge.spec --distpath dist/linux --workpath build/tmp --clean

echo "Build complete: dist/linux/AudioForge/"
echo "To create an AppImage, use appimagetool on the output directory."
