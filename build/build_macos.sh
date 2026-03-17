#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Building AudioForge for macOS..."
pip install -e ".[dev]"
pyinstaller build/audioforge.spec --distpath dist/macos_raw --workpath build/tmp --clean

# Only keep the .app bundle for distribution
mkdir -p dist/macos
cp -R dist/macos_raw/AudioForge.app dist/macos/AudioForge.app
rm -rf dist/macos_raw

echo "Build complete: dist/macos/AudioForge.app"
