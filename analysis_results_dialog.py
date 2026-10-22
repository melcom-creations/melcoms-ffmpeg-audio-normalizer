"""Display, copy, and export original-file batch measurements."""

import csv
import os
import tkinter as tk
from tkinter import ttk

import core
import i18n
from analysis import finite_number
from results_dialog import ResultsDialog, csv_value, number


def status_text(result):
    return i18n.get_text("analysis_status_" + result.status)


def metric_values(result):
    measurement = result.measurements
    if measurement is None:
        return [None] * 11
    raw = measurement.raw
    peak, rms = measurement.sample_peak_dbfs, measurement.rms_dbfs
    crest = peak - rms if peak is not None and rms is not None else None
    return [measurement.integrated_lufs, measurement.true_peak_dbtp,
            measurement.loudness_range_lu, measurement.peak_to_loudness_ratio_lu,
            peak, rms, finite_number(crest), finite_number(raw.get("input_thresh")),
            finite_number(raw.get("dc_offset")), raw.get("bit_depth_measured"),
            " / ".join(str(raw.get(key, "N/A")) for key in ("min_level", "max_level"))]


def metric_labels():
    text = i18n.get_text
    return [text("results_integrated"), text("results_true_peak"), text("results_lra"),
            text("inspect_lbl_plr").rstrip(":") + " (LU)", text("inspect_lbl_samplepeak").rstrip(":") + " (dBFS)",
            text("inspect_lbl_rmsaverage").rstrip(":") + " (dBFS)", text("inspect_lbl_crest").rstrip(":") + " (dB)",
            text("inspect_lbl_threshold").rstrip(":") + " (LUFS)", text("inspect_lbl_dc").rstrip(":"),
            text("inspect_lbl_bitdepth_measured").rstrip(":"), text("inspect_lbl_minmax").rstrip(":")]


def metric_rows(result):
    values = metric_values(result)
    unavailable = i18n.get_text("results_not_available")
    rows = []
    for index, (label, value) in enumerate(zip(metric_labels(), values)):
        target = number(result.target_lufs) if index == 0 else number(result.target_tp) if index == 1 else unavailable
        delta = number(result.loudness_delta, True) if index == 0 else number(result.peak_delta, True) if index == 1 else unavailable
        if index == 8 and value is not None:
            measured = format(value, ".6f")
            if core.app_config.language.startswith(("de", "pl", "sv")):
                measured = measured.replace(".", ",")
        elif index >= 9:
            measured = str(value) if value not in (None, "N/A") else unavailable
        else:
            measured = number(value)
        rows.append((label, measured, target, delta))
    return rows


def detail_lines(result):
    text = i18n.get_text
    lines = [status_text(result), text("analysis_read_only"), text("analysis_reference_note"),
             text("inspect_plr_hint")]
    if result.status == "unmeasurable":
        lines.append(text("analysis_unmeasurable_hint"))
    if result.error_details:
        lines.extend((text("results_error_details"), result.error_details[-10000:]))
    return lines


def format_result(result):
    text = i18n.get_text
    lines = [text("analysis_results_title"), f"{text('results_input')}: {result.input_file}", "",
             "\t".join(text(key) for key in ("results_metric", "analysis_measured", "results_target", "analysis_delta"))]
    lines.extend("\t".join(row) for row in metric_rows(result))
    lines.extend(("", *detail_lines(result)))
    return "\n".join(lines)


def write_csv(stream, results):
    """Write numeric measurements without locale-dependent decimal formatting."""
    text = i18n.get_text
    writer = csv.writer(stream, delimiter=";")
    writer.writerow([text("results_input"), text("results_status"), *metric_labels(),
                     text("analysis_target_lufs"), text("analysis_target_tp"),
                     text("analysis_loudness_delta"), text("analysis_peak_delta"), text("results_error_details")])
    for result in results:
        values = [result.input_file, status_text(result), *metric_values(result),
                  result.target_lufs, result.target_tp, result.loudness_delta, result.peak_delta, result.error_details]
        writer.writerow([csv_value(value) for value in values])


class AnalysisResultsDialog(ResultsDialog):
    """Reuse the result-window lifecycle, language refresh, and theme handling."""

    format_result = staticmethod(format_result)
    write_csv = staticmethod(write_csv)
    export_filename = "audio-analysis.csv"

    def create_widgets(self, selected="0"):
        text = i18n.get_text
        self.win.title(text("analysis_results_title"))
        self.win.configure(bg=self.colors["bg"])
        body = ttk.Frame(self.win, padding=18)
        body.pack(fill=tk.BOTH, expand=True)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(2, weight=1)
        body.rowconfigure(4, weight=2)
        ttk.Label(body, text=text("analysis_results_title"), font=("Segoe UI", 16, "bold")).grid(row=0, column=0, sticky="w")
        description = ttk.Label(body, text=text("analysis_results_description"), wraplength=990)
        description.grid(row=1, column=0, sticky="ew", pady=(4, 10))
        body.bind("<Configure>", lambda event: description.configure(wraplength=max(100, event.width)))
        table_frame = ttk.Frame(body)
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        columns = ("file", "status", "lufs", "tp", "lra", "plr")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", height=4, selectmode="browse")
        labels = ("results_file", "results_status", "results_integrated", "results_true_peak", "results_lra", "analysis_plr")
        for column, key, width in zip(columns, labels, (250, 190, 140, 140, 130, 100)):
            self.table.heading(column, text=text(key))
            self.table.column(column, width=width, minwidth=90)
        self.table.grid(row=0, column=0, sticky="nsew")
        for orient, command, row, column, sticky in ((tk.VERTICAL, self.table.yview, 0, 1, "ns"),
                                                    (tk.HORIZONTAL, self.table.xview, 1, 0, "ew")):
            scrollbar = ttk.Scrollbar(table_frame, orient=orient, command=command)
            scrollbar.grid(row=row, column=column, sticky=sticky)
            self.table.configure(**{"yscrollcommand" if orient == tk.VERTICAL else "xscrollcommand": scrollbar.set})
        for index, result in enumerate(self.results):
            self.table.insert("", "end", iid=str(index), values=(os.path.basename(result.input_file), status_text(result),
                              *(number(value) for value in metric_values(result)[:4])))
        self.input_var = tk.StringVar()
        ttk.Entry(body, textvariable=self.input_var, state="readonly").grid(row=3, column=0, sticky="ew", pady=8)
        metrics_frame = ttk.Frame(body)
        metrics_frame.grid(row=4, column=0, sticky="nsew")
        metrics_frame.columnconfigure(0, weight=1)
        metrics_frame.rowconfigure(0, weight=1)
        self.metrics = ttk.Treeview(metrics_frame, columns=("metric", "measured", "target", "delta"), show="headings", height=11)
        for column, key in zip(("metric", "measured", "target", "delta"),
                               ("results_metric", "analysis_measured", "results_target", "analysis_delta")):
            self.metrics.heading(column, text=text(key))
            self.metrics.column(column, width=260 if column == "metric" else 170, minwidth=100)
        self.metrics.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(metrics_frame, orient=tk.VERTICAL, command=self.metrics.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.metrics.configure(yscrollcommand=scrollbar.set)
        detail_frame = ttk.Frame(body)
        detail_frame.grid(row=5, column=0, sticky="ew", pady=8)
        detail_frame.columnconfigure(0, weight=1)
        self.details = tk.Text(detail_frame, height=4, wrap="word", relief="flat", font=("Segoe UI", 10),
                               bg=self.colors["info_bg"], fg=self.colors["fg"])
        self.details.grid(row=0, column=0, sticky="ew")
        scrollbar = ttk.Scrollbar(detail_frame, orient=tk.VERTICAL, command=self.details.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.details.configure(yscrollcommand=scrollbar.set)
        footer = ttk.Frame(body)
        footer.grid(row=6, column=0, sticky="ew")
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
        self.metrics.delete(*self.metrics.get_children())
        for row in metric_rows(result):
            self.metrics.insert("", "end", values=row)
        self.details.configure(state="normal")
        self.details.delete("1.0", "end")
        self.details.insert("1.0", "\n".join(detail_lines(result)))
        self.details.configure(state="disabled")
