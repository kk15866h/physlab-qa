# Numerical design and validation

## Linear least squares

The fitted model is y = a + bx. Parameters are obtained with NumPy's SVD-backed least-squares solver. The coefficient covariance is calculated from the singular-value decomposition of the design matrix rather than explicitly inverting the normal matrix.

For ordinary least squares, the residual variance estimate is RSS/(n-2) when there are positive residual degrees of freedom. The coefficient covariance estimate is this variance multiplied by (XᵀX)⁻¹. With exactly two observations, the model has no residual degrees of freedom and ordinary-fit standard errors are undefined.

For weighted least squares, the supplied sigma_y values are treated as known, independent, absolute standard uncertainties. The design and response are divided by sigma_y; the covariance is (XᵀWX)⁻¹ without rescaling by reduced chi-square. Weighted R² uses weighted residual and total sums of squares. The reported RMSE and residual sum of squares remain unweighted summaries, so they are comparable in the original y units. Users must not interpret these diagnostics as proof that the physical model is valid.

For constant response data, R² is undefined because its denominator is zero. The API returns NaN; reports display this as "undefined".

## First-order uncertainty propagation

For independent input quantities xᵢ with standard uncertainties uᵢ, the first-order estimate is

u_f = sqrt(sum((∂f/∂xᵢ · uᵢ)²)).

Sensitivities are approximated with central finite differences. The result can be inaccurate for strongly nonlinear functions, poor step choices, discontinuities, or correlated inputs. Where feasible, compare with analytical derivatives or an independent Monte Carlo calculation.

## CSV validation

Validation reports missing cells, malformed numeric values in selected columns, absent required columns, and duplicate rows. The tool never deletes rows automatically. Duplicate measurements can be legitimate and require domain-specific review.

## Independent reference checks

The validation suite deliberately includes calculations that do not call the production fitting implementation:

- Ordinary least squares is cross-checked against the closed-form formulas based on x̄, ȳ, Sxx, and Sxy, including analytical standard errors.
- Weighted least squares is cross-checked against an explicit scalar-sum reference using weights 1/σ², including coefficient standard errors and weighted R².
- First-order uncertainty propagation is cross-checked against analytical derivatives of a nonlinear test function.

These reference tests are intended to catch implementation errors that self-consistency tests could miss. They use deterministic, well-conditioned datasets and tight numerical tolerances. Passing them does not establish correctness for every experiment or every ill-conditioned dataset.

## Nonlinear least squares

The optional nonlinear_fit API accepts a user-supplied vectorized model function, initial parameter values, optional parameter names, and optional sigma_y. Install SciPy with `python -m pip install "physlab-qa[nonlinear]"`. The CLI deliberately exposes a small explicit model registry (`exponential-decay` and `quadratic`) rather than evaluating user-provided expressions.

The implementation uses SciPy's least-squares optimizer and requests its convergence status. A non-converged optimizer raises `NonlinearFitError`; a rank-deficient fitted model Jacobian is rejected because its parameters are not locally identifiable. The reported covariance is a local Jacobian-based approximation. For unweighted fits, SciPy scales covariance by the residual variance estimate; for weighted fits, sigma_y is treated as known, independent absolute standard uncertainty and covariance is not rescaled by reduced chi-square.

Weighted R² uses weighted residual and total sums of squares; RMSE and residual sum of squares remain unweighted summaries in y units. The test suite compares a quadratic model against independent linear-algebra reference calculations, checks weighted covariance, fits deterministic exponential-decay data with known parameters, and exercises rank-deficiency and non-convergence failures. Optimizer convergence does not establish physical model validity, and local covariance estimates may be unreliable for strongly nonlinear or weakly identifiable models. No observations are automatically removed.

## Real-data damped-pendulum case study

The reproducible case study reads a publicly attributed raw sensor-export CSV and uses only its time and angle columns. It preserves the source file, selects local extrema of absolute angle after 5 s with amplitude above 0.05 rad, groups adjacent same-sign candidates, and fits the logarithm of the selected peak amplitudes against time. Under an exponential-envelope approximation, the negative fitted slope estimates the amplitude-decay rate.

The fit is cross-checked in tests against independent scalar closed-form ordinary least-squares formulas for the slope, slope standard error, and R². This verifies the regression implementation for the selected peak series; it does not independently verify the sensor acquisition, peak-detection assumptions, or the physical adequacy of an exponential envelope. The report therefore separates the statistical standard error from unquantified calibration, timing, peak-selection, correlation, and systematic effects. The external CSV is licensed separately under Apache-2.0; its source and license are documented in `examples/data/README.md`.

## Validation strategy

Tests cover exact and noisy linear data, weighted-fit diagnostics, fit invariance properties, undefined R², uncertainty propagation, CSV edge cases, machine-readable CLI output, synthetic and real-data pendulum case studies, nonlinear-fit reference checks, and independent closed-form cross-checks. CI runs on Python 3.10–3.13 and also validates the built wheel and source distribution.

These checks are a starting point, not broad scientific validation. Before research use, compare results with hand calculations or an independent implementation and include uncertainties not covered by this software.
