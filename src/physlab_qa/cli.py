"""Command-line interface."""
import argparse,json,os,sys
from pathlib import Path
from physlab_qa.csvio import read_numeric_columns,validate_csv
from physlab_qa.fit import linear_fit
from physlab_qa.report import write_fit_report

def main(argv=None):
    p=argparse.ArgumentParser(prog="physlab-qa"); p.add_argument("--version",action="version",version="physlab-qa 0.1.0")
    s=p.add_subparsers(dest="command",required=True)
    v=s.add_parser("validate"); v.add_argument("csv"); v.add_argument("--required-cols"); v.add_argument("--numeric-cols"); v.add_argument("--delimiter",default=","); v.add_argument("--json",action="store_true")
    f=s.add_parser("fit"); f.add_argument("csv"); f.add_argument("--x",required=True); f.add_argument("--y",required=True); f.add_argument("--sigma-y"); f.add_argument("--delimiter",default=","); f.add_argument("--output",default="fit-report.md"); f.add_argument("--plot"); f.add_argument("--title",default="Linear fit report"); f.add_argument("--x-label"); f.add_argument("--y-label")
    a=p.parse_args(argv)
    try:
        if a.command=="validate":
            r=validate_csv(a.csv,required_columns=[x.strip() for x in (a.required_cols or "").split(",") if x.strip()],numeric_columns=[x.strip() for x in (a.numeric_cols or "").split(",") if x.strip()],delimiter=a.delimiter)
            print(json.dumps(r.to_dict(),ensure_ascii=False,indent=2) if a.json else f"{'PASS' if r.ok else 'FAIL'}: {r.path}\nRows: {r.rows}; columns: {', '.join(r.columns)}\nMissing: {len(r.missing_cells)}; non-numeric: {len(r.non_numeric_cells)}; duplicate rows: {len(r.duplicate_rows)}")
            return 0 if r.ok else 2
        c=read_numeric_columns(a.csv,x_column=a.x,y_column=a.y,sigma_y_column=a.sigma_y,delimiter=a.delimiter); r=linear_fit(c.x,c.y,sigma_y=c.sigma_y); plot=None
        if a.plot:
            from physlab_qa.plotting import save_fit_plot
            save_fit_plot(c.x,c.y,r,x_label=a.x_label or a.x,y_label=a.y_label or a.y,output_path=a.plot,title=a.title)
            plot=os.path.relpath(Path(a.plot).resolve(),Path(a.output).resolve().parent).replace(os.sep,"/")
        write_fit_report(r,x_name=a.x,y_name=a.y,source_path=a.csv,output_path=a.output,title=a.title,plot_path=plot)
        print(f"Slope: {r.slope:.8g} +/- {r.slope_stderr:.3g}\nIntercept: {r.intercept:.8g} +/- {r.intercept_stderr:.3g}\nR2: {r.r_squared:.8g}; RMSE: {r.rmse:.8g}\nReport: {a.output}")
        return 0
    except (OSError,ValueError,RuntimeError) as e:
        print(f"physlab-qa: error: {e}",file=sys.stderr); return 2
if __name__=="__main__": raise SystemExit(main())
