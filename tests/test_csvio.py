from physlab_qa.csvio import read_numeric_columns,validate_csv

def test_numeric_read_and_validation(tmp_path):
    p=tmp_path/"data.csv"
    p.write_text("x,y\n1,2\n2,4\n",encoding="utf-8")
    c=read_numeric_columns(p,x_column="x",y_column="y")
    assert c.x == [1,2] and c.y == [2,4]
    r=validate_csv(p,numeric_columns=["x","y"])
    assert r.ok and r.rows == 2

def test_invalid_numeric_is_reported(tmp_path):
    p=tmp_path/"bad.csv"; p.write_text("x,y\n1,abc\n",encoding="utf-8")
    r=validate_csv(p,numeric_columns=["y"])
    assert not r.ok and r.non_numeric_cells
