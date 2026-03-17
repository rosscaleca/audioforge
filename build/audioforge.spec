# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for AudioForge."""

import os
import sys
from pathlib import Path

import customtkinter

block_cipher = None

# Resolve all paths relative to the project root (one level up from this spec file)
ROOT = Path(SPECPATH).parent
ctk_path = os.path.dirname(customtkinter.__file__)

a = Analysis(
    [str(ROOT / "src" / "audioforge" / "__main__.py")],
    pathex=[str(ROOT / "src")],
    binaries=[],
    datas=[
        (ctk_path, "customtkinter"),
    ],
    hiddenimports=[
        "audioforge",
        "audioforge.app",
        "audioforge.core",
        "audioforge.core.converter",
        "audioforge.core.ffmpeg",
        "audioforge.core.formats",
        "audioforge.core.metadata",
        "audioforge.core.validator",
        "audioforge.ui",
        "audioforge.ui.file_panel",
        "audioforge.ui.settings_panel",
        "audioforge.ui.metadata_panel",
        "audioforge.ui.progress_panel",
        "audioforge.platform",
        "audioforge.platform.compat",
        "audioforge.logging_config",
        "PIL",
        "PIL.Image",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AudioForge",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=str(ROOT / "assets" / "icon.icns") if sys.platform == "darwin" else (
        str(ROOT / "assets" / "icon.ico") if sys.platform == "win32" else None
    ),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="AudioForge",
)

# macOS .app bundle
if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="AudioForge.app",
        icon=str(ROOT / "assets" / "icon.icns"),
        bundle_identifier="com.audioforge.app",
        info_plist={
            "CFBundleName": "AudioForge",
            "CFBundleDisplayName": "AudioForge",
            "CFBundleVersion": "0.1.0",
            "CFBundleShortVersionString": "0.1.0",
            "NSHighResolutionCapable": True,
        },
    )
