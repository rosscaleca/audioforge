"""Progress panel: progress bar, status label, and ETA display."""

import customtkinter as ctk


class ProgressPanel(ctk.CTkFrame):
    """Panel showing conversion progress, status text, and ETA."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._create_widgets()

    def _create_widgets(self):
        self._progress_bar = ctk.CTkProgressBar(self, height=12)
        self._progress_bar.pack(fill="x", padx=15, pady=(10, 5))
        self._progress_bar.set(0)

        # Status and ETA on the same row
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=(0, 10))

        self._status_label = ctk.CTkLabel(
            info_frame,
            text="Ready",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60"),
            anchor="w",
        )
        self._status_label.pack(side="left")

        self._eta_label = ctk.CTkLabel(
            info_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60"),
            anchor="e",
        )
        self._eta_label.pack(side="right")

    def set_progress(self, percent: float):
        """Set progress bar value (0.0 to 100.0). Thread-safe."""
        self.after(0, lambda: self._progress_bar.set(percent / 100.0))

    def set_status(self, text: str):
        """Update the status text. Thread-safe."""
        self.after(0, lambda: self._status_label.configure(text=text))

    def set_eta(self, text: str):
        """Update the ETA text. Thread-safe."""
        self.after(0, lambda: self._eta_label.configure(text=text))

    def reset(self):
        """Reset to initial state. Thread-safe."""
        self.after(0, self._reset)

    def _reset(self):
        self._progress_bar.set(0)
        self._status_label.configure(text="Ready")
        self._eta_label.configure(text="")
