#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Building AudioForge for macOS..."
pip install -e ".[dev]"
pyinstaller build/audioforge.spec --distpath dist/macos --workpath build/tmp --clean

echo "Build complete: dist/macos/AudioForge.app"
