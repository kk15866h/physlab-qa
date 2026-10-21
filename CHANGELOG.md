# Changelog

All notable changes to PhysLab QA are documented here. The project follows semantic versioning once public releases begin.

## [Unreleased]

### Added

- A provenance-documented real-data damped-pendulum case study using a licensed raw sensor export, with reproducible peak-envelope analysis and independent closed-form OLS verification.

### Fixed

- CLI JSON output represents undefined or non-finite diagnostics as `null`, avoiding non-standard `NaN` and `Infinity` tokens.

### Planned

- Nonlinear fitting with explicit model definitions.
- Diagnostics for influential observations and residual structure.
- Validation against additional independent datasets and implementations.
- A documented public release workflow.

## [0.1.0] - release candidate

### Added

- CSV validation for missing cells, malformed numeric values, absent columns, and duplicate rows.
- Ordinary and weighted linear least-squares fitting.
- First-order propagation of independent standard uncertainties.
- Markdown analysis reports and optional diagnostic plots.
- Command-line interface with machine-readable JSON output.
- Synthetic pendulum case study with a physics-based cross-check.
- Automated tests on Python 3.10 through 3.13.
- Wheel/source-distribution build and installed-package smoke tests in CI.

### Correctness and validation

- Constant-response R² is reported as undefined instead of forcing a numeric value.
- Weighted fits use weighted residual and total sums of squares for R².
- Coefficient covariance is computed from the SVD of the design matrix rather than by explicitly inverting the normal matrix.
- Fit invariance, CSV edge cases, uncertainty propagation, and CLI behavior are covered by regression tests.

### Limitations

- The package is alpha software and has not undergone broad external scientific validation.
- Uncertainty in x, correlated uncertainties, model discrepancy, and nonlinear fitting are not yet supported.
- The included pendulum data are synthetic and are not experimental evidence.

[Unreleased]: https://github.com/kk15866h/physlab-qa/compare/main...HEAD
[0.1.0]: https://github.com/kk15866h/physlab-qa
