# Examples

The files in this directory are intended to demonstrate reproducible workflows. They are not interchangeable with validated experimental datasets.

## `pendulum.csv`

**Status:** synthetic teaching data.

Columns:

- `length_m`: pendulum length in metres.
- `period_squared_s2`: squared period in seconds squared.

The companion script `analyze_pendulum.py` fits

\[
T^2 = \frac{4\pi^2}{g}L + b
\]

and converts the fitted slope to an estimate of gravitational acceleration. The data were chosen to give a physically plausible result near standard terrestrial gravity, but they do not come from an apparatus and must not be represented as experimental evidence.

The uncertainty reported by the example is obtained only from the regression slope standard error. It intentionally does **not** claim to include timing resolution, length calibration, finite-amplitude effects, air drag, pivot friction, correlations, or other systematic contributions.

## Adding a real dataset

A real-data example should include all of the following before it is merged:

1. A source or contributor statement and redistribution permission/license.
2. A description of the apparatus or measurement context.
3. Column definitions and units.
4. Raw measurements without silent point deletion.
5. Measurement-resolution and uncertainty assumptions.
6. A reproducible script that starts from the raw file.
7. An independently checked expected result or comparison target.
8. A clear separation between statistical and systematic uncertainty.

See issue #2 for the current real-data validation task.
