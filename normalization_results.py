"""Keep file creation and post-encoding verification as separate outcomes."""

from dataclasses import dataclass
import math
from analysis import AudioMeasurements

LUFS_TOLERANCE = 0.2
TRUE_PEAK_TOLERANCE = 0.1


def valid_encoder_headroom(value):
    try:
        return not isinstance(value, bool) and math.isfinite(float(value)) and 0 <= float(value) <= 3
    except (TypeError, ValueError, OverflowError):
        return False


def valid_targets(lufs, tp):
    try:
        return (not isinstance(lufs, bool) and not isinstance(tp, bool)
                and math.isfinite(float(lufs)) and math.isfinite(float(tp))
                and -70 <= float(lufs) <= -5 and -9 <= float(tp) <= 0)
    except (TypeError, ValueError, OverflowError):
        return False


@dataclass
class NormalizationResult:
    input_file: str
    output_file: str
    target_lufs: float
    target_tp: float
    requested_mode: str
    mastering_preset: str
    verification_requested: bool = False
    before: AudioMeasurements | None = None
    after: AudioMeasurements | None = None
    actual_mode: str = "unknown"
    output_created: bool = False
    processing_status: str = "running"
    verification_status: str = "not_requested"
    error_code: str = ""
    error_details: str = ""
    loudness_ok: bool | None = None
    peak_ok: bool | None = None
    encoder_headroom_db: float = 0.0
    processing_tp: float | None = None
    output_format: str = ""
    output_quality: str = ""

    @property
    def status(self):
        if not self.output_created:
            return self.processing_status
        return self.verification_status if self.verification_requested else "not_requested"

    def evaluate(self):
        if not self.after or not self.after.measurable:
            self.verification_status = "unmeasurable"
            return
        if not all(math.isfinite(value) for value in (self.target_lufs, self.target_tp)):
            self.verification_status = "failed"
            return
        self.loudness_ok = abs(self.after.integrated_lufs - self.target_lufs) <= LUFS_TOLERANCE + 1e-9
        self.peak_ok = self.after.true_peak_dbtp <= self.target_tp + TRUE_PEAK_TOLERANCE + 1e-9
        self.verification_status = "passed" if self.loudness_ok and self.peak_ok else "deviation"
