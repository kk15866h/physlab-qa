# PhysLab QA

[![CI](https://github.com/kk15866h/physlab-qa/actions/workflows/ci.yml/badge.svg)](https://github.com/kk15866h/physlab-qa/actions/workflows/ci.yml)

**Reproducible, uncertainty-aware analysis for experimental CSV data.**

PhysLab QA is an early-stage Python toolkit for validating experimental tables, fitting ordinary or weighted linear models, propagating first-order measurement uncertainty, and generating traceable Markdown reports.

> **Status: alpha (0.1.0).** The project is not certified scientific software and has not yet undergone broad external validation. Verify results against analytical cases or an independent implementation before using them in research-critical work.

## Features

- CSV quality checks for missing values, malformed rows, non-numeric cells, and duplicate records.
- Ordinary and weighted least-squares linear regression with fit diagnostics.
- First-order uncertainty propagation for independent input quantities.
- Markdown reports and optional residual plots.
- Human-readable CLI output plus machine-readable JSON for automation.
- Python API, regression tests, distribution checks, and CI on Python 3.10–3.13.

## Installation from source

Python 3.10 or newer is required. This project has not yet been published to PyPI, so install directly from the repository:

```bash
git clone https://github.com/kk15866h/physlab-qa.git
cd physlab-qa
python -m pip install -e ".[plot]"
```

For development and tests:

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

For machine-readable output:

```bash
physlab-qa fit examples/pendulum.csv --x length_m --y period_squared_s2 --output build/report.md --json
```

Undefined or non-finite statistics are represented as JSON `null`, rather than non-standard `NaN` or `Infinity` tokens.

To see a physics-focused end-to-end example, run:

```bash
python examples/analyze_pendulum.py
```

It fits the linearized simple-pendulum model $T^2 = (4\\pi^2/g)L + b$, estimates $g$, propagates the fitted slope's standard error, and writes a Markdown report. The supplied data are synthetic, so the result is only a software demonstration and must not be cited as an experimental measurement. The propagated uncertainty excludes timing and length uncertainties, correlations, and systematic effects. See [examples/README.md](examples/README.md) for provenance and interpretation details.

## Validation approach

PhysLab QA does not rely only on self-consistency tests. The test suite includes independent closed-form reference calculations for ordinary and weighted least squares, analytical-derivative checks for uncertainty propagation, CSV edge cases, CLI behavior, fit invariance properties, and the synthetic pendulum cross-check.

CI runs the tests on Python 3.10–3.13, builds both a source distribution and wheel, validates package metadata, installs the built wheel, checks dependencies, and exercises the installed CLI. See [docs/numerical-design.md](docs/numerical-design.md) for numerical assumptions and the validation strategy.

## Scientific limitations

- Regression is linear only; the software does not automatically remove outliers.
- Weighted fitting treats supplied `sigma_y` values as known, independent standard uncertainties in the response variable.
- For weighted fits, R² uses weighted sums, while RMSE and residual sum of squares are unweighted summaries.
- Uncertainty in x, correlated errors, and model discrepancy are not currently handled.
- First-order uncertainty propagation assumes independent inputs and may be inaccurate for strongly nonlinear functions.
- High R² alone does not establish that a model is physically appropriate.

## Project documentation

- [Numerical design and validation](docs/numerical-design.md)
- [Release checklist](docs/release-checklist.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
- [Citation metadata](CITATION.cff)
- [Security policy](SECURITY.md)

## Roadmap

- [x] CSV validation and numeric-column parsing
- [x] Linear and weighted-linear regression
- [x] Markdown report and optional residual plot
- [x] First-order uncertainty propagation
- [x] Synthetic physics case study and end-to-end CI check
- [x] Independent closed-form numerical cross-checks
- [ ] Add a provenance-reviewed real laboratory dataset and reproducible analysis
- [ ] Nonlinear fitting with explicit model definitions
- [ ] Additional diagnostics for influential observations and residual structure

Current work is tracked in [GitHub Issues](https://github.com/kk15866h/physlab-qa/issues).

## License

MIT. See [LICENSE](LICENSE).
