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

## Validation strategy

Tests cover exact and noisy linear data, weighted-fit diagnostics, fit invariance properties, undefined R², uncertainty propagation, CSV edge cases, and a synthetic pendulum case study. These tests are a starting point, not broad scientific validation. Before research use, compare results with hand calculations or an independent implementation and include uncertainties not covered by this software.
