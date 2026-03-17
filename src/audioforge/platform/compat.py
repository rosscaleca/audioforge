"""Platform-specific compatibility: fonts, DPI scaling, FFmpeg install hints."""

import sys


def get_platform() -> str:
    """Return the current platform as a simple string."""
    if sys.platform == "darwin":
        return "macos"
    elif sys.platform == "win32":
        return "windows"
    else:
        return "linux"


def get_default_fonts() -> tuple[str, str]:
    """Return (ui_font, mono_font) appropriate for the current platform."""
    platform = get_platform()
    if platform == "macos":
        return ("SF Pro Display", "SF Mono")
    elif platform == "windows":
        return ("Segoe UI", "Consolas")
    else:
        return ("Ubuntu", "Ubuntu Mono")


def get_dpi_scaling() -> float | None:
    """Return a DPI scaling factor, or None to use the toolkit default.

    On macOS, Tk handles Retina scaling automatically with CustomTkinter.
    On Windows, we read the system DPI.
    On Linux, we defer to the toolkit.
    """
    platform = get_platform()
    if platform == "windows":
        try:
            import ctypes

            hdc = ctypes.windll.user32.GetDC(0)
            dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
            ctypes.windll.user32.ReleaseDC(0, hdc)
            return dpi / 96.0
        except Exception:
            return None
    return None


def get_ffmpeg_install_hint() -> str:
    """Return platform-appropriate FFmpeg installation instructions."""
    platform = get_platform()
    if platform == "macos":
        return (
            "FFmpeg is required but not installed.\n\n"
            "Install with Homebrew:\n"
            "  brew install ffmpeg"
        )
    elif platform == "windows":
        return (
            "FFmpeg is required but not installed.\n\n"
            "Install with winget:\n"
            "  winget install ffmpeg\n\n"
            "Or download from https://ffmpeg.org/download.html"
        )
    else:
        return (
            "FFmpeg is required but not installed.\n\n"
            "Install with your package manager:\n"
            "  sudo apt install ffmpeg        # Debian/Ubuntu\n"
            "  sudo dnf install ffmpeg        # Fedora\n"
            "  sudo pacman -S ffmpeg          # Arch"
        )
