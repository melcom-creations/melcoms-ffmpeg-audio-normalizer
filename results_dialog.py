"""Present batch results using the current language and application theme."""

import csv
import os
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import core
import i18n
import utils
from normalization_results import LUFS_TOLERANCE, TRUE_PEAK_TOLERANCE


def number(value, signed=False):
    if value is None:
        return i18n.get_text("results_not_available")
    text = format(value, "+.2f" if signed else ".2f")
    return text.replace(".", ",") if core.app_config.language.startswith(("de", "pl", "sv")) else text


def status_text(result):
    group = "verification" if result.output_created else "processing"
    return i18n.get_text(f"results_{group}_{result.status}")


def metric_rows(result):
    before, after = result.before, result.after
    return [
        (i18n.get_text("results_integrated"), number(before.integrated_lufs if before else None),
         number(result.target_lufs), number(after.integrated_lufs if after else None)),
        (i18n.get_text("results_true_peak"), number(before.true_peak_dbtp if before else None),
         number(result.target_tp), number(after.true_peak_dbtp if after else None)),
        (i18n.get_text("results_lra"), number(before.loudness_range_lu if before else None),
         i18n.get_text("results_not_available"), number(after.loudness_range_lu if after else None)),
    ]


def detail_lines(result):
    text = i18n.get_text
    lines = [status_text(result),
             f"{text('results_requested_mode')}: {text('results_mode_' + result.requested_mode)}",
             f"{text('results_actual_mode')}: {text('results_mode_' + result.actual_mode)}",
             f"{text('results_mastering')}: {i18n.get_mastering_preset_display_name(result.mastering_preset)}"]
    if result.output_created and result.requested_mode == "linear" and result.actual_mode == "dynamic":
        lines.append(text("results_linear_fallback"))
    if result.output_created and result.mastering_preset in ("Cohesive", "Punchy", "Aggressive"):
        lines.append(text("results_mastering_dynamics"))
    if result.output_format and result.output_quality:
        lines.append(text("results_encoding", format=result.output_format, quality=result.output_quality))
    if result.encoder_headroom_db > 0 and result.processing_tp is not None:
        lines.append(text("results_encoder_headroom", requested=number(result.encoder_headroom_db),
                          applied=number(result.target_tp - result.processing_tp), limit=number(result.processing_tp)))
        lines.append(text("results_encoder_headroom_note"))
    if result.verification_status == "deviation" and result.after:
        if result.loudness_ok is False:
            lines.append(text("results_loudness_deviation", delta=number(result.after.integrated_lufs - result.target_lufs, True)))
        if result.peak_ok is False:
            lines.append(text("results_peak_deviation", delta=number(result.after.true_peak_dbtp - result.target_tp, True)))
    if result.verification_status == "unmeasurable":
        lines.append(text("results_unmeasurable_hint"))
    if result.error_code:
        lines.append(text(result.error_code))
    if result.error_details:
        lines.extend((text("results_error_details"), result.error_details[-30000:]))
    return lines


def format_result(result):
    text = i18n.get_text
    lines = [text("results_title"), f"{text('results_input')}: {result.input_file}",
             f"{text('results_output')}: {result.output_file}", "",
             "\t".join(text(key) for key in ("results_metric", "results_before", "results_target", "results_after"))]
    lines.extend("\t".join(row) for row in metric_rows(result))
    lines.extend(("", *detail_lines(result), "", text("results_tolerances", lufs=number(LUFS_TOLERANCE), tp=number(TRUE_PEAK_TOLERANCE))))
    return "\n".join(lines)


def csv_value(value):
    """Keep text cells from becoming spreadsheet formulas."""
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def write_csv(stream, results):
    text = i18n.get_text
    writer = csv.writer(stream, delimiter=";")
    metric_specs = (("results_integrated", "integrated_lufs", "target_lufs"),
                    ("results_true_peak", "true_peak_dbtp", "target_tp"),
                    ("results_lra", "loudness_range_lu", None))
    headers = [text("results_input"), text("results_output"), text("results_status")]
    for key, attribute, target in metric_specs:
        headers.extend(text(group) + " - " + text(key) for group in ("results_before", "results_target", "results_after"))
    headers.extend((text("results_requested_mode"), text("results_actual_mode"), text("results_mastering"),
                    text("file_list_header_format"), text("output_format_quality_label").rstrip(":"),
                    text("encoder_headroom_label"), text("results_details")))
    writer.writerow(headers)
    for result in results:
        values = [result.input_file, result.output_file, status_text(result)]
        for key, attribute, target in metric_specs:
            values.extend((getattr(result.before, attribute, None), getattr(result, target) if target else None,
                           getattr(result.after, attribute, None)))
        values.extend((text("results_mode_" + result.requested_mode), text("results_mode_" + result.actual_mode),
                       i18n.get_mastering_preset_display_name(result.mastering_preset), result.output_format,
                       result.output_quality, result.encoder_headroom_db, "\n".join(detail_lines(result))))
        writer.writerow([csv_value(value) for value in values])


class ResultsDialog:
    format_result = staticmethod(format_result)
    write_csv = staticmethod(write_csv)
    export_filename = "normalization-results.csv"

    def __init__(self, parent, app, results, colors):
        self.app, self.results, self.colors = app, results, colors
        self._copy_feedback_after = None
        self.win = tk.Toplevel(parent)
        utils.prepare_window(self.win)
        self.win.transient(parent)
        self.win.geometry("1080x720")
        self.win.minsize(940, 650)
        icon = os.path.join(core.get_base_path(), "favicon", "melcom.ico")
        if os.path.isfile(icon):
            self.win.iconbitmap(icon)
        self.win.protocol("WM_DELETE_WINDOW", self.close)
        self.create_widgets()
        utils.center_window(self.win)
        utils.show_prepared_window(self.win)

    def create_widgets(self, selected="0"):
        text = i18n.get_text
        self.win.title(text("results_title"))
        self.win.configure(bg=self.colors["bg"])
        body = ttk.Frame(self.win, padding=18)
        body.pack(fill=tk.BOTH, expand=True)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(2, weight=2)
        body.rowconfigure(5, weight=1)
        ttk.Label(body, text=text("results_title"), font=("Segoe UI", 16, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(body, text=text("results_description"), wraplength=990).grid(row=1, column=0, sticky="w", pady=(4, 12))
        table_frame = ttk.Frame(body)
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        self.table = ttk.Treeview(table_frame, columns=("file", "status", "lufs", "tp"), show="headings", height=5, selectmode="browse")
        for column, label, width in (("file", "results_file", 280), ("status", "results_status", 420),
                                     ("lufs", "results_integrated", 130), ("tp", "results_true_peak", 130)):
            self.table.heading(column, text=text(label))
            self.table.column(column, width=width, minwidth=90)
        self.table.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.table.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.table.configure(yscrollcommand=scroll.set)
        horizontal = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.table.xview)
        horizontal.grid(row=1, column=0, sticky="ew")
        self.table.configure(xscrollcommand=horizontal.set)
        for index, result in enumerate(self.results):
            self.table.insert("", "end", iid=str(index), values=(os.path.basename(result.input_file), status_text(result),
                              number(result.after.integrated_lufs if result.after else None),
                              number(result.after.true_peak_dbtp if result.after else None)))
        paths = ttk.Frame(body)
        paths.grid(row=3, column=0, sticky="ew", pady=10)
        paths.columnconfigure(1, weight=1)
        self.input_var, self.output_var = tk.StringVar(), tk.StringVar()
        for row, key, variable in ((0, "results_input", self.input_var), (1, "results_output", self.output_var)):
            ttk.Label(paths, text=text(key)).grid(row=row, column=0, sticky="w", padx=(0, 12), pady=2)
            ttk.Entry(paths, textvariable=variable, state="readonly").grid(row=row, column=1, sticky="ew", pady=2)
        self.metrics = ttk.Treeview(body, columns=("metric", "before", "target", "after"), show="headings", height=3, selectmode="none")
        for column, key in zip(("metric", "before", "target", "after"), ("results_metric", "results_before", "results_target", "results_after")):
            self.metrics.heading(column, text=text(key))
            self.metrics.column(column, width=220, minwidth=140, anchor="w" if column == "metric" else "center")
        self.metrics.grid(row=4, column=0, sticky="ew")
        detail_frame = ttk.Frame(body)
        detail_frame.grid(row=5, column=0, sticky="nsew", pady=10)
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(0, weight=1)
        self.details = tk.Text(detail_frame, height=7, wrap="word", relief="flat", font=("Segoe UI", 10),
                               bg=self.colors["info_bg"], fg=self.colors["fg"])
        self.details.grid(row=0, column=0, sticky="nsew")
        details_scroll = ttk.Scrollbar(detail_frame, orient=tk.VERTICAL, command=self.details.yview)
        details_scroll.grid(row=0, column=1, sticky="ns")
        self.details.configure(yscrollcommand=details_scroll.set)
        ttk.Label(body, text=text("results_tolerances", lufs=number(LUFS_TOLERANCE), tp=number(TRUE_PEAK_TOLERANCE)),
                  wraplength=990).grid(row=6, column=0, sticky="w", pady=(0, 12))
        footer = ttk.Frame(body)
        footer.grid(row=7, column=0, sticky="ew")
        self.export_button = ttk.Button(footer, text=text("results_export_csv"), command=self.export_csv)
        self.export_button.pack(side=tk.LEFT)
        self.copy_all_button = ttk.Button(footer, text=text("results_copy_all"), command=self.copy_all)
        self.copy_all_button.pack(side=tk.LEFT, padx=8)
        self.copy_button = ttk.Button(footer, text=text("results_copy"), command=self.copy_selected,
                                      width=max(len(text("results_copy")), len(text("inspect_btn_copied")) + 2))
        self.copy_button.pack(side=tk.LEFT)
        ttk.Button(footer, text=text("results_close"), command=self.close).pack(side=tk.RIGHT)
        self.table.bind("<<TreeviewSelect>>", self.select_result)
        if self.results:
            selected = selected if self.table.exists(selected) else "0"
            self.table.selection_set(selected)
            self.table.see(selected)
            self.select_result()
        else:
            for button in (self.copy_button, self.copy_all_button, self.export_button):
                button.configure(state="disabled")

    def select_result(self, event=None):
        self._cancel_copy_feedback()
        self._reset_copy_feedback()
        selection = self.table.selection()
        if not selection:
            return
        result = self.results[int(selection[0])]
        self.input_var.set(result.input_file)
        self.output_var.set(result.output_file)
        self.metrics.delete(*self.metrics.get_children())
        for row in metric_rows(result):
            self.metrics.insert("", "end", values=row)
        self.details.configure(state="normal")
        self.details.delete("1.0", "end")
        self.details.insert("1.0", "\n".join(detail_lines(result)))
        self.details.configure(state="disabled")

    def _copy(self, content, button):
        self.win.clipboard_clear()
        self.win.clipboard_append(content)
        self._cancel_copy_feedback()
        self._reset_copy_feedback()
        button.configure(text="\u2714 " + i18n.get_text("inspect_btn_copied"))
        self._copy_feedback_after = self.win.after(2000, self._reset_copy_feedback)

    def copy_selected(self):
        selection = self.table.selection()
        if selection:
            self._copy(self.format_result(self.results[int(selection[0])]), self.copy_button)

    def copy_all(self):
        self._copy("\n\n".join(self.format_result(result) for result in self.results), self.copy_all_button)

    def export_csv(self):
        path = filedialog.asksaveasfilename(parent=self.win, title=i18n.get_text("results_export_csv"),
                                          defaultextension=".csv", initialfile=self.export_filename,
                                          filetypes=[("CSV", "*.csv")])
        if not path:
            return
        temporary = None
        try:
            target = os.path.normcase(os.path.realpath(path))
            for result in self.results:
                for audio_path in (result.input_file, getattr(result, "output_file", "")):
                    if audio_path and (target == os.path.normcase(os.path.realpath(audio_path)) or
                                       (os.path.exists(path) and os.path.exists(audio_path) and
                                        os.path.samefile(path, audio_path))):
                        raise OSError(i18n.get_text("results_export_source_error"))
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8-sig", newline="", delete=False,
                                             dir=os.path.dirname(os.path.abspath(path)), suffix=".csv") as stream:
                temporary = stream.name
                self.write_csv(stream, self.results)
            os.replace(temporary, path)
            self._cancel_copy_feedback()
            self._reset_copy_feedback()
            self.export_button.configure(text="\u2714 " + i18n.get_text("results_csv_saved"))
            self._copy_feedback_after = self.win.after(2000, self._reset_copy_feedback)
        except (OSError, UnicodeError, csv.Error) as error:
            messagebox.showerror(i18n.get_text("results_export_error"), str(error), parent=self.win)
        finally:
            if temporary is not None and os.path.exists(temporary):
                try:
                    os.unlink(temporary)
                except OSError:
                    pass

    def _cancel_copy_feedback(self):
        """Cancel feedback before replacing widgets or closing the dialog."""
        if self._copy_feedback_after is not None:
            self.win.after_cancel(self._copy_feedback_after)
            self._copy_feedback_after = None

    def _reset_copy_feedback(self):
        self._copy_feedback_after = None
        self.copy_button.configure(text=i18n.get_text("results_copy"))
        self.copy_all_button.configure(text=i18n.get_text("results_copy_all"))
        self.export_button.configure(text=i18n.get_text("results_export_csv"))

    def refresh_language(self):
        self._cancel_copy_feedback()
        selected = next(iter(self.table.selection()), "0")
        for child in self.win.winfo_children():
            child.destroy()
        self.create_widgets(selected)

    def update_theme_colors(self, colors):
        self.colors = colors
        self.refresh_language()

    def close(self):
        self._cancel_copy_feedback()
        self.app.results_window = None
        self.win.destroy()
