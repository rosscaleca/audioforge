"""Main AudioForge application window."""

import logging
import sys
import threading
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image, ImageTk

from audioforge.platform.compat import get_dpi_scaling
from audioforge.ui.file_panel import FilePanel
from audioforge.ui.metadata_panel import MetadataPanel
from audioforge.ui.progress_panel import ProgressPanel
from audioforge.ui.settings_panel import SettingsPanel

logger = logging.getLogger(__name__)


def _create_root() -> ctk.CTk:
    """Create the root window, optionally with drag-and-drop support."""
    try:
        from tkinterdnd2 import TkinterDnD

        class DnDCTk(ctk.CTk, TkinterDnD.DnDWrapper):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.TkdndVersion = TkinterDnD._require(self)

        return DnDCTk()
    except Exception:
        logger.info("tkinterdnd2 not available, drag-and-drop disabled")
        return ctk.CTk()


class AudioForgeApp:
    """Main application: creates the window and wires panels together."""

    def __init__(self):
        self.root = _create_root()
        self.root.title("AudioForge")
        self.root.geometry("780x750")
        self.root.minsize(650, 600)

        # Apply appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Set app icon
        self._set_icon()

        # DPI scaling (Windows)
        scaling = get_dpi_scaling()
        if scaling is not None:
            ctk.set_widget_scaling(scaling)

        self._converting = False
        self._cancel_event: threading.Event | None = None
        self._create_layout()

    def _find_icon_path(self) -> Path | None:
        """Locate the icon.png asset, handling both dev and packaged layouts."""
        # Development: relative to source
        candidates = [
            Path(__file__).parent.parent.parent / "assets" / "icon.png",
            Path(__file__).parent.parent / "assets" / "icon.png",
        ]
        # PyInstaller bundle: assets copied next to executable
        if getattr(sys, "_MEIPASS", None):
            candidates.insert(0, Path(sys._MEIPASS) / "assets" / "icon.png")
        for p in candidates:
            if p.exists():
                return p
        return None

    def _set_icon(self):
        """Set the app/dock icon."""
        icon_path = self._find_icon_path()
        if icon_path is None:
            logger.debug("Icon not found, using default")
            return

        try:
            icon_image = Image.open(icon_path)

            # Set window/taskbar icon via Tk (works on Windows & Linux)
            self._icon_photo = ImageTk.PhotoImage(icon_image.resize((256, 256), Image.LANCZOS))
            self.root.iconphoto(True, self._icon_photo)

            # macOS: set the dock icon via AppKit if available
            if sys.platform == "darwin":
                try:
                    from AppKit import NSApplication, NSImage
                    ns_app = NSApplication.sharedApplication()
                    ns_icon = NSImage.alloc().initByReferencingFile_(str(icon_path))
                    ns_app.setApplicationIconImage_(ns_icon)
                except ImportError:
                    logger.debug("PyObjC not available, dock icon unchanged")
        except Exception as e:
            logger.debug("Could not set icon: %s", e)

    def _create_layout(self):
        """Build the main UI layout with scrollable content."""
        # Scrollable container for all content
        self._scroll_frame = ctk.CTkScrollableFrame(
            self.root, fg_color="transparent"
        )
        self._scroll_frame.pack(fill="both", expand=True)

        container = self._scroll_frame

        # Title
        ctk.CTkLabel(
            container,
            text="AudioForge",
            font=ctk.CTkFont(size=26, weight="bold"),
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            container,
            text="Audio File Converter",
            font=ctk.CTkFont(size=13),
            text_color=("gray50", "gray60"),
        ).pack(pady=(0, 10))

        # Panels
        self.file_panel = FilePanel(container)
        self.file_panel.pack(fill="x", padx=10, pady=5)

        self.settings_panel = SettingsPanel(container)
        self.settings_panel.pack(fill="x", padx=10, pady=5)

        self.metadata_panel = MetadataPanel(container)
        self.metadata_panel.pack(fill="x", padx=10, pady=5)

        self.progress_panel = ProgressPanel(container)
        self.progress_panel.pack(fill="x", padx=10, pady=5)

        # Button frame for convert/cancel
        self._btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        self._btn_frame.pack(fill="x", padx=20, pady=(5, 15))

        self._convert_btn = ctk.CTkButton(
            self._btn_frame,
            text="Convert",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=45,
            command=self._start_conversion,
        )
        self._convert_btn.pack(fill="x")

        self._cancel_btn = ctk.CTkButton(
            self._btn_frame,
            text="Cancel",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=45,
            fg_color=("#d94040", "#c03030"),
            hover_color=("#b83030", "#a02525"),
            command=self._cancel_conversion,
        )

    def _start_conversion(self):
        """Validate inputs and kick off conversion in a background thread."""
        if self._converting:
            return

        files = self.file_panel.get_files()
        if not files:
            messagebox.showwarning("No Files", "Please add audio files to convert.")
            return

        output_dir = self.settings_panel.get_output_dir()
        if not output_dir.is_dir():
            messagebox.showwarning(
                "Invalid Directory", "Please select a valid output directory."
            )
            return

        # Check ffmpeg
        from audioforge.core.ffmpeg import find_ffmpeg

        ffmpeg_path = find_ffmpeg()
        if ffmpeg_path is None:
            from audioforge.platform.compat import get_ffmpeg_install_hint

            messagebox.showerror("FFmpeg Not Found", get_ffmpeg_install_hint())
            return

        output_name = self.settings_panel.get_output_name()
        output_format = self.settings_panel.get_output_format()
        quality_preset = self.settings_panel.get_quality_preset()
        metadata = self.metadata_panel.get_metadata()
        cover_art = self.metadata_panel.get_cover_art()

        from audioforge.core.formats import get_output_extension

        ext = get_output_extension(output_format)
        output_path = output_dir / f"{output_name}{ext}"

        # Overwrite check
        if output_path.exists():
            if not messagebox.askyesno(
                "File Exists",
                f"'{output_path.name}' already exists.\n\nOverwrite?",
            ):
                return

        self._converting = True
        self._cancel_event = threading.Event()
        self._convert_btn.pack_forget()
        self._cancel_btn.pack(fill="x")
        self.progress_panel.set_progress(0)

        thread = threading.Thread(
            target=self._run_conversion,
            args=(files, output_path, output_format, quality_preset, metadata, cover_art),
            daemon=True,
        )
        thread.start()

    def _cancel_conversion(self):
        """Kill the FFmpeg process and signal cancellation."""
        if self._cancel_event is not None:
            self._cancel_event.set()
            # Terminate the FFmpeg process directly — this unblocks
            # the stderr reader immediately instead of waiting for
            # a cancel flag check in a blocking read loop.
            process = getattr(self._cancel_event, "_process", None)
            if process is not None:
                try:
                    process.terminate()
                except OSError:
                    pass
            self._cancel_btn.configure(state="disabled", text="Cancelling...")

    def _run_conversion(self, files, output_path, output_format, quality_preset, metadata, cover_art):
        """Run the conversion pipeline in a background thread."""
        try:
            from audioforge.core.converter import convert

            convert(
                files=files,
                output_path=output_path,
                output_format=output_format,
                quality_preset=quality_preset,
                metadata=metadata,
                cover_art=cover_art,
                on_progress=self.progress_panel.set_progress,
                on_status=self.progress_panel.set_status,
                cancel_event=self._cancel_event,
            )

            self.progress_panel.set_progress(100)
            self.progress_panel.set_status(f"Done: {output_path.name}")
            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Success",
                    f"Conversion complete!\n\n{output_path}",
                ),
            )

        except Exception as e:
            from audioforge.core.ffmpeg import CancelledError

            if isinstance(e, CancelledError):
                logger.info("Conversion cancelled by user")
                self.progress_panel.set_status("Cancelled")
                self.progress_panel.set_progress(0)
            else:
                logger.exception("Conversion failed")
                error_msg = str(e)
                self.progress_panel.set_status("Conversion failed")
                self.root.after(
                    0,
                    lambda: messagebox.showerror("Conversion Failed", error_msg),
                )

        finally:
            self._converting = False
            self._cancel_event = None
            self.root.after(0, self._restore_convert_btn)

    def _restore_convert_btn(self):
        """Swap cancel button back to convert button."""
        self._cancel_btn.pack_forget()
        self._cancel_btn.configure(state="normal", text="Cancel")
        self._convert_btn.pack(fill="x")

    def mainloop(self):
        """Start the Tkinter event loop."""
        self.root.mainloop()
