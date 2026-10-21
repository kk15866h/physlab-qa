import json
import math

import pytest

from physlab_qa.cli import main


def _reject_nonstandard_json_constant(value):
    raise ValueError(f"Non-standard JSON constant: {value}")


def test_nonlinear_cli_fits_explicit_exponential_model(tmp_path, capsys):
    data = tmp_path / "decay.csv"
    report = tmp_path / "nonlinear-report.md"
    rows = ["time_s,signal"]
    for index in range(31):
        time = index / 6.0
        signal = 2.5 * math.exp(-0.8 * time) + 0.3 + 0.015 * math.sin(2.7 * time)
        rows.append(f"{time:.8f},{signal:.12g}")
    data.write_text("\n".join(rows) + "\n", encoding="utf-8")

    exit_code = main(
        [
            "fit-nonlinear",
            str(data),
            "--x",
            "time_s",
            "--y",
            "signal",
            "--model",
            "exponential-decay",
            "--p0",
            "2,0.5,0.1",
            "--output",
            str(report),
            "--json",
        ]
    )

    assert exit_code == 0
    output = capsys.readouterr().out
    payload = json.loads(output, parse_constant=_reject_nonstandard_json_constant)
    assert payload["model"] == "exponential-decay"
    assert payload["converged"] is True
    assert payload["parameters"]["amplitude"] == pytest.approx(2.5, abs=0.03)
    assert payload["parameters"]["decay_rate"] == pytest.approx(0.8, abs=0.03)
    assert payload["parameters"]["offset"] == pytest.approx(0.3, abs=0.02)
    assert report.exists()
    report_text = report.read_text(encoding="utf-8")
    assert "Parameter covariance matrix" in report_text
    assert "Optimizer status" in report_text


def test_nonlinear_cli_rejects_wrong_initial_parameter_count(tmp_path, capsys):
    data = tmp_path / "decay.csv"
    data.write_text("time_s,signal\n0,2.8\n1,1.4\n2,0.8\n3,0.4\n", encoding="utf-8")

    exit_code = main(
        [
            "fit-nonlinear",
            str(data),
            "--x",
            "time_s",
            "--y",
            "signal",
            "--model",
            "exponential-decay",
            "--p0",
            "1,0.2",
        ]
    )

    assert exit_code == 2
    assert "--p0 for exponential-decay requires 3 values" in capsys.readouterr().err
