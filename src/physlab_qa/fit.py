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
    leverage: tuple[float, ...] = ()
    standardized_residuals: tuple[float, ...] = ()
    cooks_distance: tuple[float, ...] = ()
    durbin_watson: float | None = None

    @property
    def potentially_influential_rows(self) -> tuple[int, ...]:
        """Return 1-based observation indices flagged by conventional screening heuristics."""
        n = len(self.fitted)
        if (
            n == 0
            or len(self.leverage) != n
            or len(self.standardized_residuals) != n
            or len(self.cooks_distance) != n
        ):
            return ()
        leverage_threshold = 4.0 / n  # 2p/n for a two-parameter linear model.
        cook_threshold = 4.0 / n
        flagged = []
        for index, (leverage, standardized, cook) in enumerate(
            zip(self.leverage, self.standardized_residuals, self.cooks_distance), start=1
        ):
            if (
                (math.isfinite(standardized) and abs(standardized) > 3.0)
                or (math.isfinite(leverage) and leverage > leverage_threshold)
                or (math.isfinite(cook) and cook > cook_threshold)
            ):
                flagged.append(index)
        return tuple(flagged)

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
            "leverage": list(self.leverage),
            "standardized_residuals": list(self.standardized_residuals),
            "cooks_distance": list(self.cooks_distance),
            "durbin_watson": self.durbin_watson,
            "potentially_influential_rows": list(self.potentially_influential_rows),
            "fitted": list(self.fitted),
            "residuals": list(self.residuals),
        }


def _design_covariance(design: np.ndarray) -> np.ndarray:
    """Compute (X.T @ X)^-1 from the SVD without explicitly inverting X.T @ X."""
    _, singular_values, right_vectors = np.linalg.svd(design, full_matrices=False)
    if np.any(singular_values <= 0):
        raise ValueError("design matrix is rank deficient")
    return (right_vectors.T / (singular_values**2)) @ right_vectors



def _residual_diagnostics(
    design: np.ndarray,
    response: np.ndarray,
    residuals: np.ndarray,
    rss: float,
    dof: int,
    sigma_y: np.ndarray | None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float | None]:
    """Calculate leverage, standardized residuals, Cook's distance, and Durbin-Watson."""
    observation_count, parameter_count = design.shape
    if sigma_y is None:
        covariance = _design_covariance(design)
        leverage = np.einsum("ij,jk,ik->i", design, covariance, design)
    else:
        weighted_design = design / sigma_y[:, None]
        covariance = _design_covariance(weighted_design)
        leverage = np.einsum("ij,jk,ik->i", weighted_design, covariance, weighted_design)
    leverage = np.clip(leverage, 0.0, 1.0)

    standardized = np.full(observation_count, np.nan, dtype=float)
    residual_tolerance = (
        np.finfo(float).eps * max(1.0, float(np.dot(response, response))) * observation_count
    )
    remaining_leverage = np.maximum(1.0 - leverage, 0.0)
    if sigma_y is None:
        if dof > 0 and rss > residual_tolerance:
            residual_scale = math.sqrt(rss / dof)
            denominator = residual_scale * np.sqrt(remaining_leverage)
            valid = denominator > 0
            standardized[valid] = residuals[valid] / denominator[valid]
        durbin_watson = (
            float(np.dot(np.diff(residuals), np.diff(residuals)) / rss)
            if rss > residual_tolerance
            else float("nan")
        )
    else:
        denominator = sigma_y * np.sqrt(remaining_leverage)
        valid = denominator > 0
        standardized[valid] = residuals[valid] / denominator[valid]
        # The usual Durbin-Watson interpretation is not implemented for WLS residuals.
        durbin_watson = None

    cooks = np.full(observation_count, np.nan, dtype=float)
    valid = np.isfinite(standardized) & (remaining_leverage > np.finfo(float).eps)
    cooks[valid] = (
        standardized[valid] ** 2
        * leverage[valid]
        / (parameter_count * remaining_leverage[valid])
    )
    return leverage, standardized, cooks, durbin_watson


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
        scale = float(np.min(sigma_arr))
        normalized_weights = (scale / sigma_arr) ** 2
        weighted_mean = float(np.average(y_arr, weights=normalized_weights))
        weighted_total_ss = float(np.sum(normalized_weights * (y_arr - weighted_mean) ** 2))
        normalized_residual_ss = float(np.sum((residuals * (scale / sigma_arr)) ** 2))
        chi_square = float(np.sum((residuals / sigma_arr) ** 2))
        reduced_chi_square = chi_square / dof if dof > 0 else None
        r_squared = (
            float("nan")
            if weighted_total_ss == 0
            else 1.0 - normalized_residual_ss / weighted_total_ss
        )
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

    leverage, standardized_residuals, cooks_distance, durbin_watson = _residual_diagnostics(
        design, y_arr, residuals, rss, dof, sigma_arr
    )

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
        tuple(map(float, leverage)),
        tuple(map(float, standardized_residuals)),
        tuple(map(float, cooks_distance)),
        durbin_watson,
    )
