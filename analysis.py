"""Parse FFmpeg measurements without coupling audio analysis to the UI."""

from dataclasses import dataclass, field
import json
import math
import re


def finite_number(value):
    """Return a finite measurement, preserving missing and silent values as None."""
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def loudnorm_data(log):
    """Read the last complete loudnorm JSON object from mixed FFmpeg stderr."""
    for match in reversed(list(re.finditer(r'\{[^{}]*"input_i"[^{}]*\}', log, re.DOTALL))):
        try:
            data = json.loads(match.group())
        except (ValueError, TypeError):
            continue
        if all(key in data for key in ("input_i", "input_tp", "input_lra", "input_thresh")):
            return data
    raise ValueError("FFmpeg did not return a complete loudnorm measurement.")


def normalization_mode(log):
    try:
        mode = loudnorm_data(log).get("normalization_type", "").lower()
    except ValueError:
        match = re.search(r"Normalization Type:\s*(Linear|Dynamic)", log, re.IGNORECASE)
        mode = match[1].lower() if match else ""
    return mode if mode in ("linear", "dynamic") else "unknown"


@dataclass(frozen=True)
class AudioMeasurements:
    integrated_lufs: float | None
    true_peak_dbtp: float | None
    loudness_range_lu: float | None
    sample_peak_dbfs: float | None = None
    rms_dbfs: float | None = None
    raw: dict = field(default_factory=dict, repr=False, compare=False)

    @property
    def measurable(self):
        values = (self.integrated_lufs, self.true_peak_dbtp, self.loudness_range_lu)
        return all(finite_number(value) is not None for value in values) and self.loudness_range_lu >= 0

    @property
    def peak_to_loudness_ratio_lu(self):
        """Derive PLR from true peak and integrated loudness of the same measurement."""
        peak = finite_number(self.true_peak_dbtp)
        loudness = finite_number(self.integrated_lufs)
        if peak is None or loudness is None:
            return None
        return finite_number(peak - loudness)

    def inspector_data(self):
        data = dict(self.raw)
        for key in ("input_i", "input_tp", "input_lra", "input_thresh"):
            if finite_number(data.get(key)) is None:
                data[key] = "N/A"
        data["plr_lu"] = self.peak_to_loudness_ratio_lu
        return data


def parse_analysis(log):
    data = loudnorm_data(log)
    # astats reports channel summaries before its final Overall section.
    overall = log[log.rfind("Overall"): ] if "Overall" in log else ""
    for key, label in {
        "dc_offset": "DC offset", "min_level": "Min level", "max_level": "Max level",
        "peak_db": "Peak level dB", "rms_db": "RMS level dB",
        "crest_factor_raw": "Crest factor", "bit_depth_measured": "Bit depth",
    }.items():
        match = re.search(re.escape(label) + r":\s*([^\r\n]+)", overall)
        data[key] = match[1].strip() if match else "N/A"
    peak, rms = finite_number(data["peak_db"]), finite_number(data["rms_db"])
    data["crest_factor"] = "N/A"
    if peak is not None and rms is not None:
        crest_db = peak - rms
        data["crest_factor"] = f"{10 ** (crest_db / 20):.2f} ({crest_db:.2f} dB)"
    return AudioMeasurements(
        finite_number(data["input_i"]), finite_number(data["input_tp"]),
        finite_number(data["input_lra"]), peak, rms, data,
    )
