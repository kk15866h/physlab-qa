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
            "model": "linear", "intercept": self.intercept, "slope": self.slope,
            "intercept_stderr": self.intercept_stderr, "slope_stderr": self.slope_stderr,
            "r_squared": self.r_squared, "rmse": self.rmse,
            "residual_sum_squares": self.residual_sum_squares,
            "degrees_of_freedom": self.degrees_of_freedom,
            "chi_square": self.chi_square, "reduced_chi_square": self.reduced_chi_square,
            "weighted": self.weighted, "fitted": list(self.fitted), "residuals": list(self.residuals),
        }


def linear_fit(x, y, *, sigma_y=None) -> LinearFitResult:
    """Fit y = intercept + slope*x. sigma_y contains known independent y uncertainties."""
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
        covariance = np.linalg.inv(weighted_design.T @ weighted_design)
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
    total_ss = float(np.dot(y_arr - np.mean(y_arr), y_arr - np.mean(y_arr)))
    r_squared = 1.0 if total_ss == 0 and rss == 0 else (float("nan") if total_ss == 0 else 1 - rss / total_ss)
    rmse = math.sqrt(rss / len(x_arr))
    chi_square = reduced_chi_square = None
    if weighted:
        chi_square = float(np.sum((residuals / sigma_arr) ** 2))
        reduced_chi_square = chi_square / dof if dof > 0 else None
        intercept_stderr = math.sqrt(max(0.0, float(covariance[0, 0])))
        slope_stderr = math.sqrt(max(0.0, float(covariance[1, 1])))
    elif dof > 0:
        covariance = (rss / dof) * np.linalg.inv(design.T @ design)
        intercept_stderr = math.sqrt(max(0.0, float(covariance[0, 0])))
        slope_stderr = math.sqrt(max(0.0, float(covariance[1, 1])))
    else:
        intercept_stderr = slope_stderr = float("nan")
    return LinearFitResult(
        intercept, slope, intercept_stderr, slope_stderr, r_squared, rmse, rss, dof,
        tuple(map(float, fitted)), tuple(map(float, residuals)), chi_square, reduced_chi_square, weighted,
    )
