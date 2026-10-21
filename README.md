# PhysLab QA

[![CI](https://github.com/kk15866h/physlab-qa/actions/workflows/ci.yml/badge.svg)](https://github.com/kk15866h/physlab-qa/actions/workflows/ci.yml)

**Reproducible, uncertainty-aware analysis for experimental CSV data.**

PhysLab QA is an early-stage Python toolkit for validating experimental tables, fitting ordinary or weighted linear models, propagating first-order measurement uncertainty, and generating traceable Markdown reports.

> **Status: alpha (0.1.0).** The project is not certified scientific software and has not yet undergone broad external validation. Verify results against analytical cases or an independent implementation before using them in research-critical work.

## Features

- CSV quality checks for missing values, malformed rows, non-numeric cells, and duplicate records.
- Ordinary and weighted least-squares linear regression with residual and influence diagnostics.
- Optional SciPy-based nonlinear fitting with explicit models, parameter covariance, and convergence diagnostics.
- First-order uncertainty propagation for independent input quantities.
- Markdown reports and optional residual plots.
- Human-readable CLI output plus standards-compliant machine-readable JSON for automation.
- A reproducible real-data case study using a licensed raw pendulum sensor export.
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
python -m pip install -e ".[dev,plot,nonlinear]"
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

## Nonlinear fitting (optional SciPy extra)

Install the optional dependency with `python -m pip install -e ".[nonlinear]"`. The CLI provides explicit `exponential-decay` and `quadratic` models; it never evaluates arbitrary expressions. For example:

```bash
physlab-qa fit-nonlinear data.csv --x time_s --y signal --model exponential-decay --p0 2,0.5,0 --output build/nonlinear-report.md --json
```

For `exponential-decay`, `--p0` values are ordered as amplitude, decay rate, and offset. For `quadratic`, they are ordered as quadratic, linear, and offset. The Python API also accepts a user-supplied vectorized model function and explicit initial parameters. Nonlinear fitting requires SciPy; convergence and local covariance estimates do not establish physical model validity.

## Real-data case study

The repository also includes a raw sensor-export CSV from the [Damped Pendulum Dataset](https://github.com/EnzeXu/Damped_Pendulum_Dataset). The source measurements are stored under `examples/data/raw_data/`; the analysis reads the file without rewriting the stored measurements. The external data are licensed under Apache-2.0, separately from this repository's MIT-licensed code; see [data provenance and license](examples/data/README.md).

Run the case study from the repository root:

```bash
python examples/analyze_damped_pendulum.py
```

The script selects local extrema of absolute angular displacement, fits the logarithm of the peak envelope, and estimates an exponential amplitude-decay rate. It does not fit a full nonlinear damped-pendulum equation. The reported slope uncertainty is the ordinary least-squares statistical standard error and excludes sensor calibration, peak-picking, timing, and systematic effects.

## Validation approach

PhysLab QA does not rely only on self-consistency tests. The test suite includes independent closed-form reference calculations for ordinary and weighted least squares, analytical-derivative checks for uncertainty propagation, CSV edge cases, CLI behavior, fit invariance properties, nonlinear-fit cross-checks, and synthetic and real-data pendulum case studies.

CI runs the tests on Python 3.10–3.13, builds both a source distribution and wheel, validates package metadata, installs the built wheel, checks dependencies, and exercises the installed CLI. See [docs/numerical-design.md](docs/numerical-design.md) for numerical assumptions and the validation strategy.

## Scientific limitations

- Regression is linear only; the software does not automatically remove outliers.
- Weighted fitting treats supplied `sigma_y` values as known, independent standard uncertainties in the response variable.
- For weighted fits, R² uses weighted sums, while RMSE and residual sum of squares are unweighted summaries.
- Uncertainty in x, correlated errors, and model discrepancy are not currently handled.
- First-order uncertainty propagation assumes independent inputs and may be inaccurate for strongly nonlinear functions.
- High R² alone does not establish that a model is physically appropriate.
- Influence thresholds are screening heuristics, not proof that an observation is erroneous; no outliers are automatically removed.
- Nonlinear parameter standard errors are local covariance approximations and can be unreliable for strongly nonlinear or weakly identifiable models.

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
- [x] Add a provenance-documented real laboratory dataset and reproducible analysis
- [x] Nonlinear fitting with explicit model definitions
- [x] Additional diagnostics for influential observations and residual structure

Current work is tracked in [GitHub Issues](https://github.com/kk15866h/physlab-qa/issues).

## License

MIT. See [LICENSE](LICENSE).
