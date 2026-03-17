"""Metadata panel: audiobook metadata fields and cover art picker."""

import logging
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

logger = logging.getLogger(__name__)


class MetadataPanel(ctk.CTkFrame):
    """Panel for editing audiobook metadata (title, author, cover art, etc.)."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._cover_art_path: Path | None = None
        self._create_widgets()

    def _create_widgets(self):
        # Collapsible header with arrow indicator
        self._header = ctk.CTkButton(
            self,
            text="\u25b6  Metadata (optional)",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="transparent",
            text_color=("gray40", "gray70"),
            hover_color=("gray85", "gray25"),
            anchor="w",
            command=self._toggle,
        )
        self._header.pack(fill="x", padx=10, pady=(5, 0))

        # Content frame (hidden by default)
        self._content = ctk.CTkFrame(self, fg_color="transparent")
        self._expanded = False

        # Text metadata fields
        self._fields: dict[str, ctk.CTkEntry] = {}
        for label in ["Title", "Author", "Narrator", "Year", "Genre", "Description"]:
            row = ctk.CTkFrame(self._content, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=2)
            ctk.CTkLabel(row, text=f"{label}:", width=80, anchor="w").pack(
                side="left"
            )
            entry = ctk.CTkEntry(row, width=250)
            entry.pack(side="left", fill="x", expand=True, padx=5)
            self._fields[label.lower()] = entry

        # Pre-fill genre
        self._fields["genre"].insert(0, "Audiobook")

        # Cover art row
        art_row = ctk.CTkFrame(self._content, fg_color="transparent")
        art_row.pack(fill="x", padx=15, pady=(8, 5))

        ctk.CTkLabel(art_row, text="Cover Art:", width=80, anchor="w").pack(
            side="left"
        )

        self._cover_label = ctk.CTkLabel(
            art_row,
            text="No image selected",
            text_color=("gray50", "gray60"),
            anchor="w",
        )
        self._cover_label.pack(side="left", fill="x", expand=True, padx=5)

        ctk.CTkButton(
            art_row,
            text="Browse",
            command=self._browse_cover_art,
            width=80,
            height=28,
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            art_row,
            text="Clear",
            command=self._clear_cover_art,
            width=60,
            height=28,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
        ).pack(side="left")

        # Thumbnail preview
        self._thumbnail_label = ctk.CTkLabel(
            self._content,
            text="",
            width=100,
            height=100,
        )

    def _toggle(self):
        """Toggle the metadata section open/closed."""
        if self._expanded:
            self._content.pack_forget()
            self._header.configure(text="\u25b6  Metadata (optional)")
        else:
            self._content.pack(fill="x", after=self._header)
            self._header.configure(text="\u25bc  Metadata (optional)")
        self._expanded = not self._expanded

    def _browse_cover_art(self):
        """Open file dialog to select cover art image."""
        path = filedialog.askopenfilename(
            title="Select Cover Art",
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("All Files", "*.*"),
            ],
        )
        if path:
            self._cover_art_path = Path(path)
            self._cover_label.configure(text=self._cover_art_path.name)
            self._show_thumbnail()

    def _clear_cover_art(self):
        """Clear the selected cover art."""
        self._cover_art_path = None
        self._cover_label.configure(text="No image selected")
        self._thumbnail_label.pack_forget()
        self._thumbnail_label.configure(image=None, text="")

    def _show_thumbnail(self):
        """Display a small thumbnail preview of the selected cover art."""
        if self._cover_art_path is None:
            return
        try:
            from PIL import Image

            img = Image.open(self._cover_art_path)
            img.thumbnail((100, 100))
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))
            self._thumbnail_label.configure(image=ctk_img, text="")
            self._thumbnail_label.pack(padx=15, pady=(5, 5))
            # Keep reference to prevent garbage collection
            self._thumbnail_label._ctk_image = ctk_img
        except Exception as e:
            logger.warning("Could not load cover art thumbnail: %s", e)
            self._thumbnail_label.pack_forget()

    def get_metadata(self) -> dict[str, str]:
        """Return metadata fields as a dict. Empty strings are omitted."""
        result = {}
        for key, entry in self._fields.items():
            value = entry.get().strip()
            if value:
                result[key] = value
        return result

    def get_cover_art(self) -> Path | None:
        """Return the path to the selected cover art image, or None."""
        return self._cover_art_path
