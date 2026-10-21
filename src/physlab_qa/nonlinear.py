"""Explicit nonlinear least-squares fitting with local covariance diagnostics."""

from __future__ import annotations

import math
import warnings
from collections.abc import Callable, Sequence
from dataclasses import dataclass

import numpy as np


class NonlinearFitError(RuntimeError):
    """Raised when a nonlinear optimizer cannot return a trustworthy fit result."""


@dataclass(frozen=True)
class NonlinearFitResult:
    """Parameter estimates and local diagnostics for an explicit nonlinear model."""

    model_name: str
    parameter_names: tuple[str, ...]
    parameters: tuple[float, ...]
    parameter_stderr: tuple[float, ...]
    parameter_covariance: tuple[tuple[float, ...], ...]
    r_squared: float
    rmse: float
    residual_sum_squares: float
    degrees_of_freedom: int
    fitted: tuple[float, ...]
    residuals: tuple[float, ...]
    chi_square: float | None
    reduced_chi_square: float | None
    weighted: bool
    converged: bool
    optimizer_status: int
    optimizer_message: str

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-friendly structure; the CLI normalizes non-finite values."""
        return {
            "model": self.model_name,
            "parameters": dict(zip(self.parameter_names, self.parameters)),
            "parameter_stderr": dict(zip(self.parameter_names, self.parameter_stderr)),
            "parameter_covariance": [list(row) for row in self.parameter_covariance],
            "r_squared": self.r_squared,
            "rmse": self.rmse,
            "residual_sum_squares": self.residual_sum_squares,
            "degrees_of_freedom": self.degrees_of_freedom,
            "chi_square": self.chi_square,
            "reduced_chi_square": self.reduced_chi_square,
            "weighted": self.weighted,
            "converged": self.converged,
            "optimizer_status": self.optimizer_status,
            "optimizer_message": self.optimizer_message,
            "fitted": list(self.fitted),
            "residuals": list(self.residuals),
        }


def _finite_difference_jacobian(
    evaluate: Callable[..., np.ndarray],
    x: np.ndarray,
    parameters: np.ndarray,
) -> np.ndarray:
    """Estimate the model Jacobian with central differences for identifiability checks."""
    columns: list[np.ndarray] = []
    for index, parameter in enumerate(parameters):
        step = math.sqrt(np.finfo(float).eps) * max(abs(float(parameter)), 1.0)
        plus, minus = parameters.copy(), parameters.copy()
        plus[index] += step
        minus[index] -= step
        columns.append((evaluate(x, *plus) - evaluate(x, *minus)) / (2.0 * step))
    return np.column_stack(columns)


def nonlinear_fit(
    x: Sequence[float] | np.ndarray,
    y: Sequence[float] | np.ndarray,
    *,
    model: Callable[..., object],
    p0: Sequence[float] | np.ndarray,
    parameter_names: Sequence[str] | None = None,
    model_name: str | None = None,
    sigma_y: Sequence[float] | np.ndarray | None = None,
    maxfev: int = 10000,
) -> NonlinearFitResult:
    """Fit an explicit vectorized model function using SciPy.

    The supplied p0 values are initial parameter estimates. If sigma_y is
    provided, it is treated as known, independent, absolute standard uncertainty
    in each y observation. The returned covariance is a local approximation from
    the fitted Jacobian, not a guarantee of complete parameter uncertainty.
    """
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    p0_arr = np.asarray(p0, dtype=float)
    if x_arr.ndim != 1 or y_arr.ndim != 1:
        raise ValueError("x and y must be one-dimensional arrays")
    if len(x_arr) != len(y_arr):
        raise ValueError("x and y must have the same number of observations")
    if not np.all(np.isfinite(x_arr)) or not np.all(np.isfinite(y_arr)):
        raise ValueError("x and y must contain only finite values")
    if p0_arr.ndim != 1 or len(p0_arr) == 0 or not np.all(np.isfinite(p0_arr)):
        raise ValueError("p0 must be a non-empty one-dimensional array of finite values")
    if len(x_arr) <= len(p0_arr):
        raise ValueError("the number of observations must exceed the number of fitted parameters")
    if not callable(model):
        raise ValueError("model must be callable")
    if isinstance(maxfev, bool) or not isinstance(maxfev, int) or maxfev < 1:
        raise ValueError("maxfev must be a positive integer")

    if parameter_names is None:
        names = tuple(f"parameter_{index + 1}" for index in range(len(p0_arr)))
    else:
        names = tuple(str(name).strip() for name in parameter_names)
    if (
        len(names) != len(p0_arr)
        or any(not name or "|" in name or "\n" in name for name in names)
        or len(set(names)) != len(names)
    ):
        raise ValueError("parameter_names must be unique, non-empty names matching p0")

    resolved_model_name = model_name or getattr(model, "__name__", type(model).__name__)
    if not resolved_model_name.strip():
        raise ValueError("model_name must be non-empty")

    weighted = sigma_y is not None
    sigma_arr = None
    if weighted:
        sigma_arr = np.asarray(sigma_y, dtype=float)
        if sigma_arr.ndim != 1 or len(sigma_arr) != len(x_arr):
            raise ValueError("sigma_y must be one-dimensional and match x and y")
        if not np.all(np.isfinite(sigma_arr)) or np.any(sigma_arr <= 0):
            raise ValueError("sigma_y values must be finite and strictly positive")

    def evaluate(x_values, *parameters):
        x_values = np.asarray(x_values, dtype=float)
        try:
            predictions = np.asarray(model(x_values, *parameters), dtype=float)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("model must return finite numeric predictions") from exc
        if predictions.ndim != 1 or predictions.shape != x_values.shape:
            raise ValueError("model must return a one-dimensional array matching x")
        if not np.all(np.isfinite(predictions)):
            raise ValueError("model returned non-finite predictions")
        return predictions

    evaluate(x_arr, *p0_arr)
    try:
        from scipy.optimize import OptimizeWarning, curve_fit
    except ImportError as exc:
        raise RuntimeError(
            "Nonlinear fitting requires SciPy; install physlab-qa with the [nonlinear] extra."
        ) from exc

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", OptimizeWarning)
        try:
            parameters, covariance, _, message, status = curve_fit(
                evaluate,
                x_arr,
                y_arr,
                p0=p0_arr,
                sigma=sigma_arr,
                absolute_sigma=weighted,
                maxfev=maxfev,
                full_output=True,
            )
        except RuntimeError as exc:
            raise NonlinearFitError(f"nonlinear fit did not converge: {exc}") from exc

    if int(status) not in (1, 2, 3, 4):
        raise NonlinearFitError(f"nonlinear optimizer returned unsuccessful status {status}")

    jacobian = _finite_difference_jacobian(evaluate, x_arr, np.asarray(parameters, dtype=float))
    if not np.all(np.isfinite(jacobian)):
        raise NonlinearFitError("the fitted model Jacobian contains non-finite values")
    if np.linalg.matrix_rank(jacobian) < len(p0_arr):
        raise ValueError("model Jacobian is rank deficient at the fitted parameters")

    optimizer_warnings = [
        item for item in caught if issubclass(item.category, OptimizeWarning)
    ]
    if optimizer_warnings:
        raise NonlinearFitError(
            "optimizer converged but parameter covariance could not be estimated: "
            f"{optimizer_warnings[0].message}"
        )
    if covariance.shape != (len(p0_arr), len(p0_arr)) or not np.all(np.isfinite(covariance)):
        raise NonlinearFitError("optimizer returned an invalid parameter covariance matrix")

    diagonal = np.diag(covariance)
    if np.any(diagonal < -1e-12):
        raise NonlinearFitError("parameter covariance has a negative variance on its diagonal")
    parameter_stderr = np.sqrt(np.maximum(diagonal, 0.0))
    fitted = evaluate(x_arr, *parameters)
    residuals = y_arr - fitted
    rss = float(np.dot(residuals, residuals))
    dof = len(x_arr) - len(p0_arr)
    rmse = math.sqrt(rss / len(x_arr))
    chi_square = reduced_chi_square = None

    if weighted:
        scale = float(np.min(sigma_arr))
        normalized_weights = (scale / sigma_arr) ** 2
        weighted_mean = float(np.average(y_arr, weights=normalized_weights))
        weighted_total_ss = float(
            np.sum(normalized_weights * (y_arr - weighted_mean) ** 2)
        )
        weighted_residual_ss = float(np.sum(normalized_weights * residuals**2))
        r_squared = (
            float("nan")
            if weighted_total_ss == 0
            else 1.0 - weighted_residual_ss / weighted_total_ss
        )
        chi_square = float(np.sum((residuals / sigma_arr) ** 2))
        if not math.isfinite(chi_square):
            raise NonlinearFitError("chi-square overflowed; inspect y and sigma_y scales")
        reduced_chi_square = chi_square / dof
    else:
        total_ss = float(np.dot(y_arr - np.mean(y_arr), y_arr - np.mean(y_arr)))
        r_squared = float("nan") if total_ss == 0 else 1.0 - rss / total_ss

    return NonlinearFitResult(
        model_name=resolved_model_name,
        parameter_names=names,
        parameters=tuple(map(float, parameters)),
        parameter_stderr=tuple(map(float, parameter_stderr)),
        parameter_covariance=tuple(
            tuple(map(float, row)) for row in np.asarray(covariance, dtype=float)
        ),
        r_squared=float(r_squared),
        rmse=rmse,
        residual_sum_squares=rss,
        degrees_of_freedom=dof,
        fitted=tuple(map(float, fitted)),
        residuals=tuple(map(float, residuals)),
        chi_square=chi_square,
        reduced_chi_square=reduced_chi_square,
        weighted=weighted,
        converged=True,
        optimizer_status=int(status),
        optimizer_message=str(message).strip(),
    )
