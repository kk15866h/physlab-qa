from physlab_qa.cli import main

def test_validate_cli(tmp_path):
    p=tmp_path/"d.csv"; p.write_text("x,y\n1,2\n2,4\n",encoding="utf-8")
    assert main(["validate",str(p),"--numeric-cols","x,y"]) == 0
