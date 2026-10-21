"""Reproducible case study using a real damped-pendulum sensor export."""

from __future__ import annotations

import math
from collections.abc import Sequence
from pathlib import Path

from physlab_qa.csvio import read_numeric_columns
from physlab_qa.fit import LinearFitResult, linear_fit
from physlab_qa.report import write_fit_report

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data" / "raw_data" / "len1_cond1_1.csv"
OUTPUT = ROOT / "build" / "damped-pendulum-report.md"
TIME_COLUMN = "Time (s) Run #1"
ANGLE_COLUMN = "Angle (rad) Run #1"
ANALYSIS_START_TIME_S = 5.0
MIN_PEAK_AMPLITUDE_RAD = 0.05
UPSTREAM_SOURCE_URL = "https://github.com/EnzeXu/Damped_Pendulum_Dataset/blob/cbf82673641ecd65e902ad5c38a048387649a2a0/raw_data/len1_cond1_1.csv"


def _extract_peak_envelope(
    time_s: Sequence[float],
    angle_rad: Sequence[float],
    *,
    start_time_s: float = ANALYSIS_START_TIME_S,
    min_abs_angle_rad: float = MIN_PEAK_AMPLITUDE_RAD,
) -> tuple[tuple[float, float], ...]:
    """Select one absolute-angle maximum per same-sign group of local extrema."""
    if len(time_s) != len(angle_rad) or len(time_s) < 3:
        raise ValueError("time and angle must have equal lengths of at least three")
    if not math.isfinite(start_time_s):
        raise ValueError("start_time_s must be finite")
    if not math.isfinite(min_abs_angle_rad) or min_abs_angle_rad < 0:
        raise ValueError("min_abs_angle_rad must be finite and non-negative")
    if not all(math.isfinite(float(value)) for value in time_s):
        raise ValueError("time values must be finite")
    if not all(math.isfinite(float(value)) for value in angle_rad):
        raise ValueError("angle values must be finite")
    if any(time_s[i + 1] <= time_s[i] for i in range(len(time_s) - 1)):
        raise ValueError("time values must be strictly increasing")

    candidates: list[int] = []
    for index in range(1, len(time_s) - 1):
        amplitude = abs(angle_rad[index])
        if time_s[index] < start_time_s or amplitude <= min_abs_angle_rad:
            continue
        if amplitude >= abs(angle_rad[index - 1]) and amplitude > abs(angle_rad[index + 1]):
            candidates.append(index)

    groups: list[list[int]] = []
    signs: list[int] = []
    for index in candidates:
        sign = 1 if angle_rad[index] > 0 else -1
        if not groups or sign != signs[-1]:
            groups.append([index])
            signs.append(sign)
        else:
            groups[-1].append(index)

    peaks: list[tuple[float, float]] = []
    for group in groups:
        index = max(group, key=lambda item: abs(angle_rad[item]))
        peaks.append((float(time_s[index]), abs(float(angle_rad[index]))))
    if len(peaks) < 3:
        raise ValueError("fewer than three peak-envelope observations were found")
    return tuple(peaks)


def analyze_damped_pendulum(
    data_path: str | Path = DATA,
    output_path: str | Path = OUTPUT,
) -> tuple[LinearFitResult, tuple[tuple[float, float], ...], Path, int]:
    """Fit the log peak envelope and write a provenance-rich Markdown report."""
    data_path = Path(data_path)
    columns = read_numeric_columns(
        data_path,
        x_column=TIME_COLUMN,
        y_column=ANGLE_COLUMN,
    )
    peaks = _extract_peak_envelope(columns.x, columns.y)
    times = [time for time, _ in peaks]
    log_amplitudes = [math.log(amplitude) for _, amplitude in peaks]
    result = linear_fit(times, log_amplitudes)

    try:
        source_label = data_path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        source_label = str(data_path)
    report_path = write_fit_report(
        result,
        x_name="time_s",
        y_name="ln_abs_angle_over_rad",
        source_path=source_label,
        output_path=output_path,
        title="Damped pendulum: real sensor-data case study",
    )

    decay_rate = -result.slope
    if result.slope < 0:
        decay_interpretation = (
            f"- Exponential-envelope decay rate: λ = −slope = {decay_rate:.8g} "
            f"± {result.slope_stderr:.3g} s⁻¹."
        )
    else:
        decay_interpretation = (
            "- The fitted log-envelope slope is non-negative; this fit does not "
            "support a positive exponential decay rate."
        )
    report_lines = [
        "",
        "## Dataset provenance",
        "",
        "- Upstream dataset: [Damped Pendulum Dataset](" + UPSTREAM_SOURCE_URL + ")",
        "- The upstream project describes this file as a raw sensor export collected with a "
        "PASCO Wireless Rotary Motion Sensor (PS-3220).",
        "- Configuration: length setting len1 (0.236 m), condition cond1 (air only), repeat 1.",
        "- The source CSV is distributed under Apache-2.0; see "
        "[the bundled license](../examples/data/LICENSE-APACHE-2.0.txt).",
        f"- Numeric time-angle observations loaded: {len(columns.x)}.",
        f"- Peak-envelope observations selected for fitting: {len(peaks)}.",
        "",
        "## Transformation and interpretation",
        "",
        "- The stored source CSV is not modified. For fitting only, local extrema of "
        "|angle| at times ≥ 5 s and with amplitude > 0.05 rad are selected. Adjacent "
        "same-sign candidates are grouped, retaining the largest absolute-angle value "
        "in each group.",
        "- The response is y = ln(|θ_peak| / 1 rad); the fitted model is y = a + b t.",
        "- Under an exponential-envelope approximation, |θ_env(t)| = θ₀ exp(−λt), "
        "so λ = −b.",
        f"- Fitted log-envelope slope: {result.slope:.8g} s⁻¹.",
        f"- R² for the transformed peak-envelope fit: {result.r_squared:.8g}.",
        decay_interpretation,
        "",
        "## Limitations",
        "",
        "- The standard error is the ordinary least-squares statistical estimate in the "
        "log-transformed peak data. It does not include sensor calibration, peak-selection "
        "uncertainty, timing uncertainty, correlated residuals, or systematic effects.",
        "- Peak selection is an explicit analysis step, not deletion from the stored source data.",
        "- This is a diagnostic exponential-envelope fit, not a full nonlinear damped-pendulum "
        "model or a complete determination of the physical damping mechanism.",
        "- Acquisition details are attributed to the upstream dataset documentation and have "
        "not been independently re-measured by this project.",
        "",
    ]
    with report_path.open("a", encoding="utf-8") as report:
        report.write("\n".join(report_lines))
    return result, peaks, report_path, len(columns.x)


def main() -> int:
    result, peaks, report_path, observation_count = analyze_damped_pendulum()
    print("Real-data case study; see the report for source, method, and limitations.")
    print(f"Loaded time-angle observations: {observation_count}")
    print(f"Selected peak-envelope observations: {len(peaks)}")
    print(f"Log-envelope slope: {result.slope:.8g} ± {result.slope_stderr:.3g} s⁻¹")
    print(
        f"Estimated exponential amplitude-decay rate: {-result.slope:.8g} ± "
        f"{result.slope_stderr:.3g} s⁻¹"
    )
    print(f"R²: {result.r_squared:.8g}")
    print(f"Markdown report: {report_path.relative_to(ROOT)}")
    print("Uncertainty excludes sensor calibration, peak selection, timing, and systematic effects.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
