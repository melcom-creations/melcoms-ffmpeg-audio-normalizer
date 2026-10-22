"""Keep original-file analysis results separate from rendered output results."""

from dataclasses import dataclass

from analysis import AudioMeasurements, finite_number


@dataclass
class AnalysisResult:
    input_file: str
    target_lufs: float
    target_tp: float
    measurements: AudioMeasurements | None = None
    status: str = "failed"
    error_details: str = ""

    @property
    def loudness_delta(self):
        value = self.measurements.integrated_lufs if self.measurements else None
        value, target = finite_number(value), finite_number(self.target_lufs)
        return finite_number(value - target) if value is not None and target is not None else None

    @property
    def peak_delta(self):
        value = self.measurements.true_peak_dbtp if self.measurements else None
        value, target = finite_number(value), finite_number(self.target_tp)
        return finite_number(value - target) if value is not None and target is not None else None
