import json

from physlab_qa.cli import main


def _reject_nonstandard_json_constant(value):
    raise ValueError(f"Non-standard JSON constant: {value}")


def test_fit_cli_writes_report_and_json(tmp_path, capsys):
    data = tmp_path / "data.csv"
    report = tmp_path / "report.md"
    data.write_text("x,y\n0,1\n1,3\n2,5\n3,7\n", encoding="utf-8")

    exit_code = main(
        [
            "fit",
            str(data),
            "--x",
            "x",
            "--y",
            "y",
            "--output",
            str(report),
            "--json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out, parse_constant=_reject_nonstandard_json_constant)
    assert payload["slope"] == 2.0
    assert payload["intercept"] == 1.0
    assert payload["weighted"] is False
    assert payload["report_path"] == str(report)
    assert report.exists()
    text = report.read_text(encoding="utf-8")
    assert "ordinary least squares" in text
    assert "R²" in text


def test_fit_cli_returns_nonzero_for_bad_column(tmp_path, capsys):
    data = tmp_path / "data.csv"
    data.write_text("x,y\n0,1\n1,3\n", encoding="utf-8")

    exit_code = main(["fit", str(data), "--x", "missing", "--y", "y"])

    assert exit_code == 2
    assert "column(s) not found" in capsys.readouterr().err


def test_fit_cli_emits_strict_json_for_undefined_statistics(tmp_path, capsys):
    data = tmp_path / "constant.csv"
    report = tmp_path / "report.md"
    data.write_text("x,y\n0,5\n1,5\n", encoding="utf-8")

    exit_code = main(
        [
            "fit",
            str(data),
            "--x",
            "x",
            "--y",
            "y",
            "--output",
            str(report),
            "--json",
        ]
    )

    assert exit_code == 0
    output = capsys.readouterr().out
    payload = json.loads(output, parse_constant=_reject_nonstandard_json_constant)
    assert payload["r_squared"] is None
    assert payload["intercept_stderr"] is None
    assert payload["slope_stderr"] is None
    assert "NaN" not in output
    assert "Infinity" not in output
