"""File panel: drag-and-drop zone, file list, add/remove/reorder controls."""

import logging
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from audioforge.core.formats import SUPPORTED_INPUT, get_input_filetypes

logger = logging.getLogger(__name__)


class FilePanel(ctk.CTkFrame):
    """Panel for managing the list of input audio files."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._files: list[Path] = []
        self._create_widgets()
        self._setup_drag_drop()

    def _create_widgets(self):
        # Drop zone
        self._drop_frame = ctk.CTkFrame(self, height=120, corner_radius=10)
        self._drop_frame.pack(fill="x", padx=10, pady=(10, 5))
        self._drop_frame.pack_propagate(False)

        self._drop_label = ctk.CTkLabel(
            self._drop_frame,
            text="Drop Audio Files Here\nor click to browse",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray60"),
        )
        self._drop_label.pack(expand=True)

        # Bind click to browse
        self._drop_frame.bind("<Button-1>", lambda e: self.browse_files())
        self._drop_label.bind("<Button-1>", lambda e: self.browse_files())

        # File list with scrollbar
        self._list_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self._file_listbox = tk.Listbox(
            self._list_frame,
            bg="#2b2b2b",
            fg="#ffffff",
            font=("Consolas", 11),
            selectmode=tk.EXTENDED,
            highlightthickness=0,
            borderwidth=0,
            selectbackground="#4a9eff",
            selectforeground="#ffffff",
            activestyle="none",
        )
        scrollbar = ctk.CTkScrollbar(
            self._list_frame, command=self._file_listbox.yview
        )
        self._file_listbox.configure(yscrollcommand=scrollbar.set)

        self._file_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # File count
        self._count_label = ctk.CTkLabel(
            self,
            text="0 files selected",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60"),
        )
        self._count_label.pack(anchor="w", padx=15)

        # Button row
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(5, 10))

        buttons = [
            ("Add Files", self.browse_files),
            ("Remove", self._remove_selected),
            ("Clear", self._clear_files),
            ("Move Up", self._move_up),
            ("Move Down", self._move_down),
        ]
        for text, cmd in buttons:
            ctk.CTkButton(
                btn_frame,
                text=text,
                command=cmd,
                width=90,
                height=30,
                font=ctk.CTkFont(size=12),
            ).pack(side="left", padx=3)

    def _setup_drag_drop(self):
        """Set up drag-and-drop if tkinterdnd2 is available."""
        try:
            from tkinterdnd2 import DND_FILES

            self._drop_frame.drop_target_register(DND_FILES)
            self._drop_frame.dnd_bind("<<Drop>>", self._handle_drop)
            logger.info("Drag-and-drop enabled")
        except Exception:
            logger.info("Drag-and-drop not available, using file browser fallback")

    def _handle_drop(self, event):
        """Handle dropped files."""
        raw = self.tk.splitlist(event.data)
        self.add_files([Path(f) for f in raw])

    def browse_files(self):
        """Open file dialog to select audio files."""
        files = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=get_input_filetypes(),
        )
        if files:
            self.add_files([Path(f) for f in files])

    def add_files(self, files: list[Path]):
        """Add files to the list, filtering for supported formats and duplicates."""
        added = 0
        for f in files:
            if f.suffix.lower() in SUPPORTED_INPUT and f not in self._files:
                self._files.append(f)
                self._file_listbox.insert(tk.END, f.name)
                added += 1

        if added:
            self._update_count()
            self._drop_label.configure(
                text="Files added — drop more or click to browse"
            )
            logger.info("Added %d file(s), total: %d", added, len(self._files))

    def _remove_selected(self):
        """Remove selected files from the list."""
        selected = list(self._file_listbox.curselection())
        for idx in reversed(selected):
            del self._files[idx]
            self._file_listbox.delete(idx)
        self._update_count()

    def _clear_files(self):
        """Clear all files."""
        self._files.clear()
        self._file_listbox.delete(0, tk.END)
        self._update_count()
        self._drop_label.configure(
            text="Drop Audio Files Here\nor click to browse"
        )

    def _move_up(self):
        """Move selected item up."""
        selected = self._file_listbox.curselection()
        if not selected or selected[0] == 0:
            return
        idx = selected[0]
        self._files[idx], self._files[idx - 1] = (
            self._files[idx - 1],
            self._files[idx],
        )
        text = self._file_listbox.get(idx)
        self._file_listbox.delete(idx)
        self._file_listbox.insert(idx - 1, text)
        self._file_listbox.selection_set(idx - 1)

    def _move_down(self):
        """Move selected item down."""
        selected = self._file_listbox.curselection()
        if not selected or selected[0] == len(self._files) - 1:
            return
        idx = selected[0]
        self._files[idx], self._files[idx + 1] = (
            self._files[idx + 1],
            self._files[idx],
        )
        text = self._file_listbox.get(idx)
        self._file_listbox.delete(idx)
        self._file_listbox.insert(idx + 1, text)
        self._file_listbox.selection_set(idx + 1)

    def _update_count(self):
        """Update the file count label."""
        count = len(self._files)
        self._count_label.configure(
            text=f"{count} file{'s' if count != 1 else ''} selected"
        )

    def get_files(self) -> list[Path]:
        """Return the current ordered list of files."""
        return list(self._files)
