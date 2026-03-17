"""Settings panel: output name, directory, format, and quality controls."""

import logging
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from audioforge.core.formats import (
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_QUALITY,
    OUTPUT_FORMATS,
    QUALITY_PRESETS,
    get_output_extension,
)
from audioforge.core.validator import sanitize_filename

logger = logging.getLogger(__name__)


class SettingsPanel(ctk.CTkFrame):
    """Panel for output settings: name, directory, format, and quality."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._output_dir = str(Path.home() / "Downloads")
        self._create_widgets()

    def _create_widgets(self):
        # Section label
        ctk.CTkLabel(
            self,
            text="Output Settings",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=15, pady=(10, 5))

        # Output name row
        name_frame = ctk.CTkFrame(self, fg_color="transparent")
        name_frame.pack(fill="x", padx=15, pady=3)

        ctk.CTkLabel(name_frame, text="Name:", width=60, anchor="w").pack(
            side="left"
        )
        self._name_entry = ctk.CTkEntry(
            name_frame, placeholder_text="Audiobook", width=250
        )
        self._name_entry.pack(side="left", padx=(5, 5), fill="x", expand=True)
        self._name_entry.insert(0, "Audiobook")

        self._ext_label = ctk.CTkLabel(
            name_frame,
            text=get_output_extension(DEFAULT_OUTPUT_FORMAT),
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray60"),
        )
        self._ext_label.pack(side="left")

        # Output directory row
        dir_frame = ctk.CTkFrame(self, fg_color="transparent")
        dir_frame.pack(fill="x", padx=15, pady=3)

        ctk.CTkLabel(dir_frame, text="Save to:", width=60, anchor="w").pack(
            side="left"
        )
        self._dir_entry = ctk.CTkEntry(dir_frame, width=250)
        self._dir_entry.pack(side="left", padx=(5, 5), fill="x", expand=True)
        self._dir_entry.insert(0, self._output_dir)

        ctk.CTkButton(
            dir_frame,
            text="Browse",
            command=self._browse_output,
            width=80,
            height=28,
        ).pack(side="left")

        # Format and quality row
        opts_frame = ctk.CTkFrame(self, fg_color="transparent")
        opts_frame.pack(fill="x", padx=15, pady=(3, 10))

        ctk.CTkLabel(opts_frame, text="Format:", width=60, anchor="w").pack(
            side="left"
        )
        format_labels = [OUTPUT_FORMATS[k]["label"] for k in OUTPUT_FORMATS]
        self._format_var = ctk.StringVar(
            value=OUTPUT_FORMATS[DEFAULT_OUTPUT_FORMAT]["label"]
        )
        self._format_menu = ctk.CTkOptionMenu(
            opts_frame,
            values=format_labels,
            variable=self._format_var,
            command=self._on_format_changed,
            width=160,
        )
        self._format_menu.pack(side="left", padx=(5, 15))

        ctk.CTkLabel(opts_frame, text="Quality:").pack(side="left")
        self._quality_var = ctk.StringVar(value=DEFAULT_QUALITY)
        self._quality_menu = ctk.CTkOptionMenu(
            opts_frame,
            values=list(QUALITY_PRESETS.keys()),
            variable=self._quality_var,
            width=170,
        )
        self._quality_menu.pack(side="left", padx=5)

    def _browse_output(self):
        """Open directory picker for output location."""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self._dir_entry.get(),
        )
        if directory:
            self._dir_entry.delete(0, "end")
            self._dir_entry.insert(0, directory)

    def _on_format_changed(self, _choice: str):
        """Update the extension label when output format changes."""
        fmt_key = self._get_format_key()
        self._ext_label.configure(text=get_output_extension(fmt_key))

    def _get_format_key(self) -> str:
        """Map the current format label back to its key."""
        label = self._format_var.get()
        for key, fmt in OUTPUT_FORMATS.items():
            if fmt["label"] == label:
                return key
        return DEFAULT_OUTPUT_FORMAT

    def get_output_name(self) -> str:
        """Return the sanitized output filename (without extension)."""
        raw = self._name_entry.get().strip()
        return sanitize_filename(raw) if raw else sanitize_filename("Audiobook")

    def get_output_dir(self) -> Path:
        """Return the selected output directory."""
        return Path(self._dir_entry.get().strip())

    def get_output_format(self) -> str:
        """Return the selected output format key (e.g., 'm4b')."""
        return self._get_format_key()

    def get_quality_preset(self) -> str:
        """Return the selected quality preset name."""
        return self._quality_var.get()
