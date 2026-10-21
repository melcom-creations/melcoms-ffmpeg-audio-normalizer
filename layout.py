"""Resizable work areas and validated, persistent window layout."""

from dataclasses import asdict, dataclass, replace
import tkinter as tk
from tkinter import ttk

MIN_FILES_WIDTH = 460
MIN_SETTINGS_WIDTH = 660
MIN_TOP_HEIGHT = 280
MIN_LOG_HEIGHT = 100

@dataclass(frozen=True)
class WindowLayout:
    width: int = 1759
    height: int = 1010
    files_width: int = 610
    log_height: int = 261
    maximized: bool = False

    @classmethod
    def from_settings(cls, settings):
        defaults = cls()
        values = {}
        for key, minimum in (("width", 600), ("height", 400), ("files_width", 100), ("log_height", 60)):
            value = settings.get(key, getattr(defaults, key))
            try:
                parsed = int(str(value)) if not isinstance(value, bool) else 0
            except (TypeError, ValueError, OverflowError):
                parsed = 0
            values[key] = parsed if minimum <= parsed <= 16384 else getattr(defaults, key)
        values["maximized"] = str(settings.get("maximized", False)).lower() in ("1", "yes", "true", "on")
        return cls(**values)

    def as_settings(self):
        return {key: str(value) for key, value in asdict(self).items()}

    def fitted(self, screen_width, screen_height):
        available_width = max(320, screen_width - 60)
        available_height = max(320, screen_height - 100)
        return replace(self, width=max(min(1200, available_width), min(self.width, available_width)),
                       height=max(min(650, available_height), min(self.height, available_height)))


class ThemedPanedWindow(tk.PanedWindow):
    """Draw a flat divider while retaining Tk's native sash drag behavior."""

    def __init__(self, parent, *, orient, colors):
        self._vertical = orient == tk.VERTICAL
        cursor = "sb_v_double_arrow" if self._vertical else "sb_h_double_arrow"
        super().__init__(parent, orient=orient, borderwidth=0, sashwidth=14, sashpad=0,
                         showhandle=False, opaqueresize=True, sashrelief=tk.FLAT,
                         background=colors["bg"], sashcursor=cursor)
        self._colors = colors
        self._active = False
        self._dragging = False
        self._draw_job = None
        self.divider = tk.Canvas(self, borderwidth=0, highlightthickness=0,
                                 background=colors["bg"], cursor=cursor, takefocus=False)
        self.divider.bind("<Enter>", lambda event: self._highlight(True))
        self.divider.bind("<Leave>", lambda event: self._highlight(False))
        for sequence in ("<ButtonPress-1>", "<B1-Motion>", "<ButtonRelease-1>"):
            self.divider.bind(sequence, lambda event, sequence=sequence: self._forward(event, sequence))
        self.bind("<Configure>", self._queue_draw, add="+")
        self.bind("<Destroy>", self._destroy_divider, add="+")

    def add(self, child, **options):
        # Keep Tk's temporary sash cursor from being inherited by pane controls.
        if not child.cget("cursor"):
            child.configure(cursor="arrow")
        super().add(child, **options)
        child.bind("<Configure>", self._queue_draw, add="+")
        self._queue_draw()

    def _queue_draw(self, event=None):
        if self._draw_job is None:
            self._draw_job = self.after_idle(self._draw_divider)

    def _draw_divider(self):
        self._draw_job = None
        panes = self.panes()
        if len(panes) != 2:
            return
        first, second = (self.nametowidget(str(name)) for name in panes)
        if self._vertical:
            start = first.winfo_y() + first.winfo_height()
            width, height = self.winfo_width(), second.winfo_y() - start
            x, y = 0, start
        else:
            start = first.winfo_x() + first.winfo_width()
            width, height = second.winfo_x() - start, self.winfo_height()
            x, y = start, 0
        if width <= 1 or height <= 1:
            return
        self.divider.place(x=x, y=y, width=width, height=height)
        tk.Misc.lift(self.divider)
        self.divider.delete("all")
        center_x, center_y = width // 2, height // 2
        color = self._colors["accent"] if self._active or self._dragging else self._colors["separator"]
        grip = self._colors["accent"] if self._active or self._dragging else self._colors["disabled_fg"]
        if self._vertical:
            self.divider.create_line(0, center_y, center_x - 18, center_y, fill=color)
            self.divider.create_line(center_x + 18, center_y, width, center_y, fill=color)
            for offset in (-6, 0, 6):
                self.divider.create_line(center_x + offset, center_y - 3,
                                         center_x + offset, center_y + 3, fill=grip, width=2)
        else:
            self.divider.create_line(center_x, 0, center_x, center_y - 18, fill=color)
            self.divider.create_line(center_x, center_y + 18, center_x, height, fill=color)
            for offset in (-6, 0, 6):
                self.divider.create_line(center_x - 3, center_y + offset,
                                         center_x + 3, center_y + offset, fill=grip, width=2)

    def _highlight(self, active):
        self._active = active
        self._queue_draw()

    def _forward(self, event, sequence):
        # Translate canvas coordinates so the native Panedwindow bindings own the drag.
        x = event.x_root - self.winfo_rootx()
        y = event.y_root - self.winfo_rooty()
        if sequence == "<ButtonPress-1>":
            self._dragging = True
        self.event_generate(sequence, x=x, y=y, state=event.state)
        if sequence == "<ButtonRelease-1>":
            self._dragging = False
            self._active = (self.divider.winfo_rootx() <= event.x_root < self.divider.winfo_rootx() + self.divider.winfo_width()
                            and self.divider.winfo_rooty() <= event.y_root < self.divider.winfo_rooty() + self.divider.winfo_height())
        self._queue_draw()
        return "break"

    def set_colors(self, colors):
        self._colors = colors
        self.configure(background=colors["bg"])
        self.divider.configure(background=colors["bg"])
        self._queue_draw()

    def _destroy_divider(self, event):
        if event.widget is self and self._draw_job is not None:
            self.after_cancel(self._draw_job)
            self._draw_job = None


class ScrollableSettings(ttk.Frame):
    """Keep settings reachable when the user allocates more space to the log."""

    def __init__(self, parent, colors):
        super().__init__(parent, style="TFrame")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.canvas = tk.Canvas(self, background=colors["bg"], borderwidth=0,
                                highlightthickness=0, yscrollincrement=20)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.scrollbar.grid_remove()
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.content = ttk.Frame(self.canvas, style="TFrame")
        self.window = self.canvas.create_window(0, 0, anchor="nw", window=self.content)
        self.content.bind("<Configure>", self._update_scroll_region)
        self.canvas.bind("<Configure>", self._resize_content)
        self._wheel_tag = "NormalizerSettingsWheel_" + str(id(self))
        self.bind_class(self._wheel_tag, "<MouseWheel>", self._wheel)
        self.bind("<Destroy>", self._destroy_bindings, add="+")

    def _resize_content(self, event):
        self.canvas.itemconfigure(self.window, width=max(1, event.width))
        self._update_scroll_region()

    def _update_scroll_region(self, event=None):
        height = max(1, self.content.winfo_reqheight())
        viewport = self.canvas.winfo_height()
        self.canvas.configure(scrollregion=(0, 0, self.canvas.winfo_width(), max(height, viewport)))
        if height > viewport + 1:
            self.scrollbar.grid()
        else:
            self.scrollbar.grid_remove()
            self.canvas.yview_moveto(0)

    def enable_mousewheel(self):
        def visit(widget):
            tags = widget.bindtags()
            if self._wheel_tag not in tags:
                widget.bindtags((self._wheel_tag, *tags))
            for child in widget.winfo_children():
                visit(child)
        visit(self.canvas)

    def _wheel(self, event):
        if self.content.winfo_reqheight() <= self.canvas.winfo_height():
            return None
        if event.delta:
            direction = -1 if event.delta > 0 else 1
            steps = max(1, abs(event.delta) // 120) * 3
            self.canvas.yview_scroll(direction * steps, "units")
        return "break"

    def _destroy_bindings(self, event):
        if event.widget is self:
            self.unbind_class(self._wheel_tag, "<MouseWheel>")

    def set_colors(self, colors):
        self.canvas.configure(background=colors["bg"])


class LayoutController:
    """Restore and save pane positions without reacting to child size requests."""

    def __init__(self, root, vertical, horizontal, files, settings, log, state, save_callback):
        self.root, self.vertical, self.horizontal = root, vertical, horizontal
        self.files, self.settings, self.log = files, settings, log
        self.state = state.fitted(root.winfo_screenwidth(), root.winfo_screenheight())
        self.save_callback = save_callback
        self.ready = False
        self.closed = False
        self._save_job = None
        self._restore_job = None
        self._normal_size = self.state.width, self.state.height
        self._maximized = self.state.maximized
        root.bind("<Map>", self._mapped, add="+")
        root.bind("<Configure>", self._configured, add="+")
        root.bind("<Destroy>", self._destroyed, add="+")
        for pane in (vertical, horizontal):
            pane.bind("<ButtonRelease-1>", self._released, add="+")
        if root.winfo_ismapped():
            self._restore_job = root.after_idle(self.restore)

    def _mapped(self, event):
        if event.widget is self.root and not self.ready and self._restore_job is None:
            self._restore_job = self.root.after_idle(self.restore)

    def restore(self, save=False):
        self._restore_job = None
        if self.closed:
            return
        self.ready = False
        if self.state.maximized:
            self.root.state("zoomed")
        self.root.update_idletasks()
        self._place_panes(self.state)
        self.root.update_idletasks()
        self.ready = True
        if save:
            self.persist()

    def _place_panes(self, state):
        # Adjust from actual pane sizes so handle widths and DPI do not add drift.
        horizontal_gap = self.horizontal.winfo_width() - self.files.winfo_width() - self.settings.winfo_width()
        files_width = max(MIN_FILES_WIDTH, min(state.files_width, self.horizontal.winfo_width() - MIN_SETTINGS_WIDTH - horizontal_gap))
        x, y = self.horizontal.sash_coord(0)
        self.horizontal.sash_place(0, x + files_width - self.files.winfo_width(), y)
        vertical_gap = self.vertical.winfo_height() - self.horizontal.winfo_height() - self.log.winfo_height()
        log_height = max(MIN_LOG_HEIGHT, min(state.log_height, self.vertical.winfo_height() - MIN_TOP_HEIGHT - vertical_gap))
        x, y = self.vertical.sash_coord(0)
        self.vertical.sash_place(0, x, y + self.log.winfo_height() - log_height)

    def _configured(self, event):
        if event.widget is not self.root or not self.ready or self.closed:
            return
        state = self.root.state()
        if state == "normal":
            self._normal_size = self.root.winfo_width(), self.root.winfo_height()
            self._maximized = False
        elif state == "zoomed":
            self._maximized = True
        else:
            return
        self._schedule_save()

    def _released(self, event):
        if self.ready and not self.closed:
            self._schedule_save()

    def _schedule_save(self):
        if self._save_job is not None:
            self.root.after_cancel(self._save_job)
        self._save_job = self.root.after(400, self.persist)

    def capture(self):
        if not self.ready:
            return self.state
        window_state = self.root.state()
        if window_state == "normal":
            self._normal_size = self.root.winfo_width(), self.root.winfo_height()
            self._maximized = False
        elif window_state == "zoomed":
            self._maximized = True
        return WindowLayout(*self._normal_size, self.files.winfo_width(), self.log.winfo_height(), self._maximized)

    def persist(self):
        if self._save_job is not None:
            self.root.after_cancel(self._save_job)
        self._save_job = None
        if self.closed or not self.ready:
            return
        state = self.capture()
        self.state = state
        self.save_callback(state)

    def reset(self):
        self._cancel_jobs()
        self.ready = False
        self.state = WindowLayout().fitted(self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        self._normal_size = self.state.width, self.state.height
        self._maximized = False
        self.root.state("normal")
        self.root.geometry(f"{self.state.width}x{self.state.height}")
        self._restore_job = self.root.after_idle(lambda: self.restore(save=True))

    def close(self):
        if not self.closed:
            self._cancel_jobs()
            self.persist()
            self.closed = True

    def _cancel_jobs(self):
        for name in ("_save_job", "_restore_job"):
            job = getattr(self, name)
            if job is not None:
                try:
                    self.root.after_cancel(job)
                except tk.TclError:
                    pass
                setattr(self, name, None)

    def _destroyed(self, event):
        if event.widget is self.root:
            self.closed = True
            self._cancel_jobs()
