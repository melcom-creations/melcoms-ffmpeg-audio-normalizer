"""
main.py
Application Entry Point for melcom's FFmpeg Audio Normalizer.
"""

try:
    from tkinterdnd2 import TkinterDnD
except Exception:
    TkinterDnD = None
    import tkinter as tk

from gui import AudioNormalizerApp


def _center_window(root) -> None:
    """Center the main window on the active screen before showing it."""
    root.update_idletasks()

    window_width = root.winfo_reqwidth()
    window_height = root.winfo_reqheight()

    # Fallbacks in case the requested size is not yet reliable.
    if window_width <= 1:
        window_width = max(root.winfo_width(), 1)
    if window_height <= 1:
        window_height = max(root.winfo_height(), 1)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x_position = max((screen_width - window_width) // 2, 0)
    y_position = max((screen_height - window_height) // 2, 0)

    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")


# --- Application Entry Point ---
if __name__ == "__main__":
    root = TkinterDnD.Tk() if TkinterDnD is not None else tk.Tk()
    root.withdraw()

    app = AudioNormalizerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    _center_window(root)
    root.deiconify()
    root.lift()
    root.focus_force()

    root.mainloop()
