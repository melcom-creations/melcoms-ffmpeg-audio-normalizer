"""
utils.py
Contains shared utility functions used across multiple modules.
"""

# --- Window Helpers ---
def center_window(window):
    """Centers a top-level window on the current screen."""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')
    window.update_idletasks()


def prepare_window(window):
    """Keeps a top-level window invisible while its content and position are prepared."""
    window.withdraw()
    try:
        window.attributes("-alpha", 0.0)
    except Exception:
        pass


def show_prepared_window(window):
    """Maps a prepared window invisibly before revealing it at its requested position."""
    window.update_idletasks()
    target_geometry = window.geometry()
    width = window.winfo_width()
    height = window.winfo_height()

    # Force Windows to create the native window handle away from the visible desktop.
    window.geometry(f"{width}x{height}+100000+100000")
    window.deiconify()
    window.update()

    # Move the already-mapped but transparent window to its final position.
    window.geometry(target_geometry)
    window.update()
    try:
        window.attributes("-alpha", 1.0)
    except Exception:
        pass


def format_time(seconds):
    """Formats a duration in seconds as HH:MM:SS."""
    if seconds is None: 
        return "00:00:00"
    try:
        secs = float(seconds)
        m, s = divmod(secs, 60)
        h, m = divmod(m, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"
    except (ValueError, TypeError):
        return "00:00:00"

def format_duration(seconds):
    """Formats a duration in seconds with millisecond precision."""
    try:
        secs = float(seconds)
        m, s = divmod(secs, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{int(h):02d}:{int(m):02d}:{s:06.3f}"
        else:
            return f"{int(m):02d}:{s:06.3f}"
    except (ValueError, TypeError):
        return "00:00.000"

def format_size(bytes_val):
    """Formats a byte value using a human-readable unit."""
    try:
        val = float(bytes_val)
        for unit in ['Bytes', 'KB', 'MB', 'GB', 'TB']:
            if val < 1024.0:
                return f"{val:.2f} {unit}"
            val /= 1024.0
        return f"{val:.2f} PB"
    except (ValueError, TypeError):
        return "0 Bytes"
