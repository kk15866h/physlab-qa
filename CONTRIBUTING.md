# Contributing

Thanks for considering a contribution to PhysLab QA.

## Good first contributions

- Report reproducible bugs with a minimal example.
- Add tests for numerical edge cases.
- Improve documentation of assumptions and limitations.
- Add synthetic examples with independently checkable expected results.

## Development

Use Python 3.10 or newer.

    python -m pip install -e ".[dev]"
    pytest

If you change numerical behavior, include tests that justify the expected result and update the numerical-design documentation. Do not silently remove or modify data points to improve a fit.

## Pull requests

Keep changes focused. Explain the problem, the approach, the tests run, and any limitations. Do not submit private, confidential, or unpublished experimental data without permission. Be respectful and constructive in review discussions.
