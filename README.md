# PhysLab QA

**Reproducible, uncertainty-aware analysis for experimental CSV data.**

PhysLab QA is an early-stage Python toolkit for validating experimental tables, fitting ordinary or weighted linear models, propagating first-order measurement uncertainty, and generating traceable Markdown reports.

> **Status: alpha (0.1.0).** The project is not certified scientific software and has not yet undergone broad external validation. Verify results against analytical cases or an independent implementation before using them in research-critical work.

## Features

- CSV quality checks for missing values, malformed rows, non-numeric cells, and duplicate records.
- Ordinary and weighted least-squares linear regression with fit diagnostics.
- First-order uncertainty propagation for independent input quantities.
- Markdown reports and optional residual plots.
- Python API, command-line interface, unit tests, and GitHub Actions CI.

## Installation

Python 3.10 or newer is required.

```bash
python -m pip install "physlab-qa[plot]"
```

For development:

```bash
python -m pip install -e ".[dev,plot]"
pytest
```

## Quick start

The `examples/pendulum.csv` file is synthetic demonstration data, not experimental evidence.

```bash
physlab-qa validate examples/pendulum.csv --numeric-cols length_m,period_squared_s2
physlab-qa fit examples/pendulum.csv --x length_m --y period_squared_s2 --output build/report.md --plot build/fit.png
```

## Scientific limitations

- Regression is linear only; the software does not automatically remove outliers.
- Weighted fitting treats supplied `sigma_y` values as known, independent standard uncertainties in the response variable.
- Uncertainty in x, correlated errors, and model discrepancy are not currently handled.
- First-order uncertainty propagation assumes independent inputs and may be inaccurate for strongly nonlinear functions.
- High R² alone does not establish that a model is physically appropriate.

See [docs/numerical-design.md](docs/numerical-design.md) for assumptions and validation notes. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## Roadmap

- [x] CSV validation and numeric-column parsing
- [x] Linear and weighted-linear regression
- [x] Markdown report and optional diagnostic plot
- [x] First-order uncertainty propagation
- [x] Unit tests and CI configuration
- [ ] Nonlinear fitting with explicit model definitions
- [ ] Additional diagnostics for influential points and residual structure
- [ ] Independent review of more laboratory examples

## License

MIT. See [LICENSE](LICENSE).
