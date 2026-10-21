import math
import runpy
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "examples" / "analyze_damped_pendulum.py"
_SCRIPT = runpy.run_path(str(SCRIPT_PATH))
_extract_peak_envelope = _SCRIPT["_extract_peak_envelope"]
analyze_damped_pendulum = _SCRIPT["analyze_damped_pendulum"]


def test_peak_extractor_rejects_non_monotonic_time():
    with pytest.raises(ValueError, match="strictly increasing"):
        _extract_peak_envelope([0.0, 2.0, 1.0], [0.0, 1.0, 0.0])


def test_real_damped_pendulum_fit_matches_independent_closed_form_reference(tmp_path):
    result, peaks, report_path, observation_count = analyze_damped_pendulum(
        output_path=tmp_path / "damped-pendulum-report.md"
    )

    assert observation_count == 6896
    assert len(peaks) == 125
    assert peaks[0] == pytest.approx((5.49, 0.760))
    assert peaks[-1] == pytest.approx((68.56, 0.427))

    times = [time for time, _ in peaks]
    log_amplitudes = [math.log(amplitude) for _, amplitude in peaks]
    mean_time = sum(times) / len(times)
    mean_log_amplitude = sum(log_amplitudes) / len(log_amplitudes)
    sxx = sum((time - mean_time) ** 2 for time in times)
    sxy = sum(
        (time - mean_time) * (value - mean_log_amplitude)
        for time, value in zip(times, log_amplitudes)
    )
    reference_slope = sxy / sxx
    reference_intercept = mean_log_amplitude - reference_slope * mean_time
    residuals = [
        value - (reference_intercept + reference_slope * time)
        for time, value in zip(times, log_amplitudes)
    ]
    rss = sum(residual**2 for residual in residuals)
    tss = sum((value - mean_log_amplitude) ** 2 for value in log_amplitudes)
    reference_r_squared = 1.0 - rss / tss
    reference_slope_stderr = math.sqrt(rss / (len(peaks) - 2) / sxx)

    assert result.slope == pytest.approx(reference_slope, rel=1e-12, abs=1e-12)
    assert result.slope_stderr == pytest.approx(reference_slope_stderr, rel=1e-12)
    assert result.r_squared == pytest.approx(reference_r_squared, rel=1e-12)
    assert result.slope == pytest.approx(-0.008387558082566122, abs=1e-10)
    assert result.r_squared == pytest.approx(0.9698774967402621, abs=1e-10)

    report = report_path.read_text(encoding="utf-8")
    assert "Dataset provenance" in report
    assert "Apache-2.0" in report
    assert "peak-selection uncertainty" in report
    assert "full nonlinear damped-pendulum model" in report
