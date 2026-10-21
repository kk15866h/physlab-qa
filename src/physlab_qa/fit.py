"""Transparent ordinary and weighted linear least-squares fitting."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class LinearFitResult:
    """Result for y = intercept + slope * x."""

    intercept: float
    slope: float
    intercept_stderr: float
    slope_stderr: float
    r_squared: float
    rmse: float
    residual_sum_squares: float
    degrees_of_freedom: int
    fitted: tuple[float, ...]
    residuals: tuple[float, ...]
    chi_square: float | None = None
    reduced_chi_square: float | None = None
    weighted: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "model": "linear",
            "intercept": self.intercept,
            "slope": self.slope,
            "intercept_stderr": self.intercept_stderr,
            "slope_stderr": self.slope_stderr,
            "r_squared": self.r_squared,
            "rmse": self.rmse,
            "residual_sum_squares": self.residual_sum_squares,
            "degrees_of_freedom": self.degrees_of_freedom,
            "chi_square": self.chi_square,
            "reduced_chi_square": self.reduced_chi_square,
            "weighted": self.weighted,
            "fitted": list(self.fitted),
            "residuals": list(self.residuals),
        }


def _design_covariance(design: np.ndarray) -> np.ndarray:
    """Compute (X.T @ X)^-1 from the SVD without explicitly inverting X.T @ X."""
    _, singular_values, right_vectors = np.linalg.svd(design, full_matrices=False)
    if np.any(singular_values <= 0):
        raise ValueError("design matrix is rank deficient")
    return (right_vectors.T / (singular_values**2)) @ right_vectors


def linear_fit(x, y, *, sigma_y=None) -> LinearFitResult:
    """Fit y = intercept + slope*x.

    If sigma_y is supplied, it is interpreted as known, independent absolute
    standard uncertainties in y. The weighted fit covariance is not rescaled
    by reduced chi-square. For weighted fits, R-squared uses weighted sums.
    """
    x_arr, y_arr = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if x_arr.ndim != 1 or y_arr.ndim != 1:
        raise ValueError("x and y must be one-dimensional arrays")
    if len(x_arr) != len(y_arr):
        raise ValueError("x and y must have the same number of observations")
    if len(x_arr) < 2:
        raise ValueError("at least two observations are required")
    if not np.all(np.isfinite(x_arr)) or not np.all(np.isfinite(y_arr)):
        raise ValueError("x and y must contain only finite values")
    design = np.column_stack((np.ones_like(x_arr), x_arr))
    if np.ptp(x_arr) == 0:
        raise ValueError("x values must not all be identical")

    weighted = sigma_y is not None
    sigma_arr = None
    if weighted:
        sigma_arr = np.asarray(sigma_y, dtype=float)
        if sigma_arr.ndim != 1 or len(sigma_arr) != len(x_arr):
            raise ValueError("sigma_y must be one-dimensional and match x and y")
        if not np.all(np.isfinite(sigma_arr)) or np.any(sigma_arr <= 0):
            raise ValueError("sigma_y values must be finite and strictly positive")
        weighted_design = design / sigma_arr[:, None]
        params, _, rank, _ = np.linalg.lstsq(weighted_design, y_arr / sigma_arr, rcond=None)
        if rank < 2:
            raise ValueError("design matrix is rank deficient")
        covariance = _design_covariance(weighted_design)
    else:
        params, _, rank, _ = np.linalg.lstsq(design, y_arr, rcond=None)
        if rank < 2:
            raise ValueError("design matrix is rank deficient")
        covariance = None

    intercept, slope = map(float, params)
    fitted = design @ params
    residuals = y_arr - fitted
    rss = float(np.dot(residuals, residuals))
    dof = len(x_arr) - 2
    rmse = math.sqrt(rss / len(x_arr))
    chi_square = reduced_chi_square = None

    if weighted:
        normalized_weights = (float(np.min(sigma_arr)) / sigma_arr) ** 2
        weighted_mean = float(np.average(y_arr, weights=normalized_weights))
        weighted_total_ss = float(np.sum(normalized_weights * (y_arr - weighted_mean) ** 2))
        chi_square = float(np.sum((residuals / sigma_arr) ** 2))
        reduced_chi_square = chi_square / dof if dof > 0 else None
        r_squared = float("nan") if weighted_total_ss == 0 else 1.0 - chi_square / weighted_total_ss
        intercept_stderr = math.sqrt(max(0.0, float(covariance[0, 0])))
        slope_stderr = math.sqrt(max(0.0, float(covariance[1, 1])))
    else:
        total_ss = float(np.dot(y_arr - np.mean(y_arr), y_arr - np.mean(y_arr)))
        # R² has a zero denominator for constant response data, so it is undefined.
        r_squared = float("nan") if total_ss == 0 else 1.0 - rss / total_ss
        if dof > 0:
            covariance = (rss / dof) * _design_covariance(design)
            intercept_stderr = math.sqrt(max(0.0, float(covariance[0, 0])))
            slope_stderr = math.sqrt(max(0.0, float(covariance[1, 1])))
        else:
            intercept_stderr = slope_stderr = float("nan")

    return LinearFitResult(
        intercept,
        slope,
        intercept_stderr,
        slope_stderr,
        r_squared,
        rmse,
        rss,
        dof,
        tuple(map(float, fitted)),
        tuple(map(float, residuals)),
        chi_square,
        reduced_chi_square,
        weighted,
    )
