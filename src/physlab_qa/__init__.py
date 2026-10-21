"""PhysLab QA: reproducible analysis for experimental CSV data."""

from physlab_qa.fit import LinearFitResult, linear_fit
from physlab_qa.uncertainty import UncertaintyResult, propagate_uncertainty

__version__ = "0.1.0"

__all__ = [
    "LinearFitResult",
    "UncertaintyResult",
    "linear_fit",
    "propagate_uncertainty",
    "__version__",
]
