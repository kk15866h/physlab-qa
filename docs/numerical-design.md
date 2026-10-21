# Numerical design and validation

## Linear least squares

The fitted model is y = a + bx. The implementation solves the least-squares system with NumPy's SVD-backed least-squares routine rather than explicitly inverting the normal equations to estimate the parameters.

For ordinary least squares, the residual variance estimate is RSS/(n-2) when there are positive residual degrees of freedom. The coefficient covariance estimate is this variance multiplied by (XᵀX)⁻¹. With exactly two observations, the model has no residual degrees of freedom and standard errors are undefined.

For weighted least squares, the supplied sigma_y values are treated as known, independent, absolute standard uncertainties. The weighted design and response are divided by sigma_y, and the covariance matrix is (XᵀWX)⁻¹ without scaling by reduced chi-square. Users must not interpret the resulting diagnostics as proof that the physical model is valid.

## First-order uncertainty propagation

For independent input quantities xᵢ with standard uncertainties uᵢ, the first-order estimate is

u_f = sqrt(sum((∂f/∂xᵢ · uᵢ)²)).

Sensitivities are approximated with central finite differences. The result can be inaccurate for strongly nonlinear functions, poor step choices, discontinuities, or correlated inputs. Where feasible, compare with analytical derivatives or an independent Monte Carlo calculation.

## CSV validation

Validation reports missing cells, malformed numeric values in selected columns, absent required columns, and duplicate rows. The tool never deletes rows automatically. Duplicate measurements can be legitimate and require domain-specific review.

## Validation strategy

Tests cover exact linear data, weighted-fit diagnostics, invalid inputs, uncertainty propagation, and CSV parsing. These tests are a starting point, not broad scientific validation. Additional tests should compare against hand-calculated examples and independent implementations before research use.
