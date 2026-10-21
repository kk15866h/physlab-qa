import pytest

from physlab_qa.csvio import read_numeric_columns, validate_csv


def test_duplicate_rows_are_reported_without_being_removed(tmp_path):
    path = tmp_path / "duplicates.csv"
    path.write_text("x,y\n1,2\n1,2\n", encoding="utf-8")

    report = validate_csv(path, numeric_columns=["x", "y"])

    assert report.ok
    assert report.rows == 2
    assert report.duplicate_rows == (3,)


def test_missing_required_column_is_reported(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("x,y\n1,2\n", encoding="utf-8")

    report = validate_csv(path, required_columns=["time_s"], numeric_columns=["x", "y"])

    assert not report.ok
    assert report.missing_required_columns == ("time_s",)


@pytest.mark.parametrize("value", ["nan", "inf", "-inf"])
def test_nonfinite_numeric_values_are_rejected_by_numeric_reader(tmp_path, value):
    path = tmp_path / "nonfinite.csv"
    path.write_text(f"x,y\n1,{value}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="not finite"):
        read_numeric_columns(path, x_column="x", y_column="y")


def test_extra_csv_field_is_rejected(tmp_path):
    path = tmp_path / "malformed.csv"
    path.write_text("x,y\n1,2,3\n", encoding="utf-8")

    with pytest.raises(ValueError, match="more fields"):
        validate_csv(path)
