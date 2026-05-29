# -*- coding: utf-8 -*-
"""
main.py
Application Entry Point for melcom's FFmpeg Audio Normalizer.
"""

import tkinter as tk
from gui import AudioNormalizerApp

if __name__ == "__main__":
    # Initialize the Tkinter Main Event Loop
    root = tk.Tk()
    app = AudioNormalizerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()