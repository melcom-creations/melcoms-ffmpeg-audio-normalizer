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
import utils


def _center_window(root) -> None:
    """Center the mapped main window without changing its configured size."""
    root.update_idletasks()
    if root.state() == "zoomed":
        return

    window_width = root.winfo_width()
    window_height = root.winfo_height()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x_position = max((screen_width - window_width) // 2, 0)
    y_position = max((screen_height - window_height) // 2, 0)

    root.geometry(f"+{x_position}+{y_position}")
    root.update_idletasks()


# --- Application Entry Point ---
if __name__ == "__main__":
    root = TkinterDnD.Tk() if TkinterDnD is not None else tk.Tk()
    utils.prepare_window(root)

    app = AudioNormalizerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    root.deiconify()
    _center_window(root)
    root.attributes("-alpha", 1.0)
    root.lift()
    root.focus_force()

    root.mainloop()
