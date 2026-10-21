"""Markdown report generation."""
from pathlib import Path
def _fmt(v): return "undefined" if v != v else f"{v:.8g}"
def write_fit_report(result, *, x_name, y_name, source_path, output_path, title="Linear fit report", plot_path=None):
    p=Path(output_path); p.parent.mkdir(parents=True,exist_ok=True)
    lines=[f"# {title}","","## Provenance","",f"- Source CSV: {source_path}",f"- x column: {x_name}",f"- y column: {y_name}",f"- Fit type: {'weighted least squares' if result.weighted else 'ordinary least squares'}",f"- Observations: {len(result.fitted)}","","## Model","",f"{y_name} = intercept + slope * {x_name}","","| Quantity | Estimate | Standard error |","|---|---:|---:|",f"| Intercept | {_fmt(result.intercept)} | {_fmt(result.intercept_stderr)} |",f"| Slope | {_fmt(result.slope)} | {_fmt(result.slope_stderr)} |","","## Diagnostics","",f"- R squared: {_fmt(result.r_squared)}",f"- RMSE: {_fmt(result.rmse)}",f"- Residual sum of squares: {_fmt(result.residual_sum_squares)}",f"- Degrees of freedom: {result.degrees_of_freedom}"]
    if result.chi_square is not None: lines += [f"- Chi-square: {_fmt(result.chi_square)}",f"- Reduced chi-square: {_fmt(result.reduced_chi_square) if result.reduced_chi_square is not None else 'undefined'}"]
    if plot_path: lines += ["","## Plot","",f"![Fit plot]({plot_path})"]
    lines += ["","## Interpretation notes","","- These statistics do not establish that the selected model is physically appropriate.","- Inspect residual structure and experimental assumptions.","- Standard errors do not include every possible systematic uncertainty.",""]
    p.write_text("\n".join(lines),encoding="utf-8"); return p
