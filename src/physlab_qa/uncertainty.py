"""First-order uncertainty propagation for independent input quantities."""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class UncertaintyResult:
    """Nominal result, propagated standard uncertainty, and sensitivities."""

    value: float
    standard_uncertainty: float
    sensitivities: tuple[float, ...]


def propagate_uncertainty(
    function: Callable[[np.ndarray], float],
    values: Sequence[float] | np.ndarray,
    standard_uncertainties: Sequence[float] | np.ndarray,
    *,
    relative_step: float = 1e-6,
    steps: Sequence[float] | np.ndarray | None = None,
) -> UncertaintyResult:
    """Propagate independent standard uncertainties using central differences."""
    x = np.asarray(values, dtype=float)
    u = np.asarray(standard_uncertainties, dtype=float)
    if x.ndim != 1 or u.ndim != 1 or len(x) != len(u) or len(x) == 0:
        raise ValueError("values and standard_uncertainties must be non-empty 1D arrays of equal length")
    if not np.all(np.isfinite(x)):
        raise ValueError("values must be finite")
    if not np.all(np.isfinite(u)) or np.any(u < 0):
        raise ValueError("standard uncertainties must be finite and non-negative")
    if not math.isfinite(relative_step) or relative_step <= 0:
        raise ValueError("relative_step must be finite and positive")

    if steps is None:
        step_array = relative_step * np.maximum(np.abs(x), 1.0)
    else:
        step_array = np.asarray(steps, dtype=float)
        if step_array.ndim != 1 or len(step_array) != len(x):
            raise ValueError("steps must be a 1D array matching values")
        if not np.all(np.isfinite(step_array)) or np.any(step_array <= 0):
            raise ValueError("steps must be finite and strictly positive")

    try:
        nominal = float(function(x.copy()))
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("function must return a finite scalar for the nominal input") from exc
    if not math.isfinite(nominal):
        raise ValueError("function must return a finite scalar for the nominal input")

    sensitivities: list[float] = []
    for index, step in enumerate(step_array):
        plus, minus = x.copy(), x.copy()
        plus[index] += step
        minus[index] -= step
        try:
            f_plus, f_minus = float(function(plus)), float(function(minus))
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"function failed during finite difference for input {index}") from exc
        derivative = (f_plus - f_minus) / (2.0 * float(step))
        if not math.isfinite(derivative):
            raise ValueError(f"non-finite sensitivity for input {index}; try a different step")
        sensitivities.append(derivative)

    propagated = math.sqrt(sum((s * ui) ** 2 for s, ui in zip(sensitivities, u)))
    return UncertaintyResult(nominal, propagated, tuple(sensitivities))
