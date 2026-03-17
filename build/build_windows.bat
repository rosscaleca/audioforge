@echo off
cd /d "%~dp0\.."

echo Building AudioForge for Windows...
pip install -e ".[dev]"
pyinstaller build\audioforge.spec --distpath dist\windows --workpath build\tmp --clean

echo Build complete: dist\windows\AudioForge\AudioForge.exe
