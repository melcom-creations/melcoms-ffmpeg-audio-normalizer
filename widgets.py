"""
widgets.py
Reusable Tkinter widgets and lightweight UI helpers.
"""

import tkinter as tk
import random

class TreeviewTooltip:
    """Tooltip helper for treeview rows with fixed positioning."""
    def __init__(self, treeview):
        """Initializes the treeview tooltip helper."""
        self.treeview = treeview
        self.tooltip = None

    def show(self, text, x, y):
        """Displays the tooltip at the requested screen position."""
        self.hide()
        self.tooltip = tk.Toplevel(self.treeview)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x + 15}+{y + 10}")

        label = tk.Label(
            self.tooltip,
            text=text,
            justify=tk.LEFT,
            relief="solid",
            borderwidth=1,
            padx=6,
            pady=3,
            background="#ffffe0"
        )
        label.pack()

    def hide(self):
        """Destroys the tooltip window if it is visible."""
        if self.tooltip is not None:
            self.tooltip.destroy()
            self.tooltip = None


class HoverTooltip:
    """Reusable tooltip helper that can be attached to arbitrary widgets."""
    def __init__(self, widget, background="#ffffe0"):
        """Initializes the hover tooltip helper."""
        self.widget = widget
        self.background = background
        self.tooltip = None
        self.label = None

    def show(self, text, x, y):
        """Shows or updates the tooltip near the pointer."""
        if self.tooltip is None or not self.tooltip.winfo_exists():
            self.tooltip = tk.Toplevel(self.widget)
            self.tooltip.wm_overrideredirect(True)
            try:
                self.tooltip.wm_attributes("-topmost", True)
            except Exception:
                pass
            self.label = tk.Label(
                self.tooltip,
                text=text,
                justify=tk.LEFT,
                relief="solid",
                borderwidth=1,
                padx=6,
                pady=3,
                background=self.background
            )
            self.label.pack()
        elif self.label is not None:
            self.label.config(text=text)

        self.tooltip.wm_geometry(f"+{x + 15}+{y + 10}")
        self.tooltip.deiconify()
        self.tooltip.lift()

    def hide(self):
        """Hides the tooltip and releases its cached widget references."""
        if self.tooltip is not None:
            try:
                self.tooltip.destroy()
            except Exception:
                pass
        self.tooltip = None
        self.label = None


class AudioVisualizer(tk.Canvas):
    """Animated bar visualizer used to indicate active playback."""
    def __init__(self, parent, num_bars=15, bar_width=4, bar_spacing=2, max_height=20, color="#00ff00", bg_color="#000000", **kwargs):
        """Creates the visualizer bars and initializes the animation state."""
        width = num_bars * (bar_width + bar_spacing)
        super().__init__(parent, width=width, height=max_height, bg=bg_color, highlightthickness=0, **kwargs)
        self.num_bars = num_bars
        self.bar_width = bar_width
        self.bar_spacing = bar_spacing
        self.max_height = max_height
        self.color = color
        self.bg_color = bg_color
        self.bars = []
        self.targets = []
        self.currents = []
        self.is_animating = False
        self.after_id = None

        for i in range(num_bars):
            x0 = i * (self.bar_width + self.bar_spacing)
            y0 = self.max_height - 2
            x1 = x0 + self.bar_width
            y1 = self.max_height
            bar = self.create_rectangle(x0, y0, x1, y1, fill=self.color, outline="")
            self.bars.append(bar)
            self.targets.append(2)
            self.currents.append(2)

    def start(self):
        """Starts the visualizer animation."""
        if not self.is_animating:
            self.is_animating = True
            self._animate()

    def stop(self):
        """Stops the animation and resets the bars."""
        self.is_animating = False
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
        for i in range(self.num_bars):
            self.targets[i] = 2
            self.currents[i] = 2
            self._update_bar(i)

    def _update_bar(self, index):
        """Updates a single bar to match its current height."""
        x0 = index * (self.bar_width + self.bar_spacing)
        y0 = self.max_height - self.currents[index]
        x1 = x0 + self.bar_width
        y1 = self.max_height
        self.coords(self.bars[index], x0, y0, x1, y1)

    def _animate(self):
        """Advances the bar animation and schedules the next frame."""
        if not self.is_animating:
            return

        try:
            for i in range(self.num_bars):
                diff = self.targets[i] - self.currents[i]
                if abs(diff) < 2:
                    self.currents[i] = self.targets[i]
                    if random.random() < 0.2:
                        self.targets[i] = random.randint(int(self.max_height * 0.5), self.max_height)
                    else:
                        self.targets[i] = random.randint(2, int(self.max_height * 0.4))
                else:
                    self.currents[i] += diff * 0.5

                self._update_bar(i)
        except Exception:
            self.is_animating = False
            return

        if self.is_animating:
            self.after_id = self.after(50, self._animate)

    def update_colors(self, bg_color, accent_color):
        """Applies the active background and accent colors."""
        self.bg_color = bg_color
        self.color = accent_color
        self.config(bg=bg_color)
        for bar in self.bars:
            self.itemconfig(bar, fill=self.color)