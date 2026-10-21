# Examples

The examples demonstrate reproducible analysis workflows. Synthetic teaching data and real sensor measurements are labelled separately.

## `pendulum.csv` — synthetic demonstration

**Status:** synthetic teaching data; not an experimental dataset.

Columns:

- `length_m`: pendulum length in metres.
- `period_squared_s2`: squared period in seconds squared.

The companion script `analyze_pendulum.py` fits

```math
T^2 = \frac{4\pi^2}{g}L + b
```

and converts the fitted slope to an estimate of gravitational acceleration. The data do not come from an apparatus and must not be represented as experimental evidence.

The uncertainty reported by this example uses only the regression slope's statistical standard error. It excludes timing resolution, length calibration, finite-amplitude effects, air drag, pivot friction, correlations, and other systematic contributions.

## Real experimental data — damped pendulum

The case study uses `examples/data/raw_data/len1_cond1_1.csv`, a raw sensor-export file from the [Damped Pendulum Dataset](https://github.com/EnzeXu/Damped_Pendulum_Dataset). The upstream project describes its measurements as collected using a PASCO Wireless Rotary Motion Sensor (PS-3220). This run uses length setting `len1` (0.236 m), condition `cond1` (air only), repeat 1. The source CSV contains 6,896 time-angle observations; other sensor/export columns and their blank cells are preserved even though the analysis uses only time and angle.

Run from the repository root after installing the package:

```bash
python examples/analyze_damped_pendulum.py
```

The script reads the raw CSV and selects local extrema of `|angle|` after 5 s whose amplitude exceeds 0.05 rad. Consecutive same-sign candidates are grouped, retaining the largest absolute-angle candidate in each group. It then fits

```math
\ln(|\theta_{\mathrm{peak}}| / 1\,\mathrm{rad}) = a + bt
```

Under an exponential-envelope approximation, the amplitude-decay rate is `\lambda=-b`. For the included dataset, the script selects 125 peaks and obtains a slope of approximately −0.00838756 s⁻¹ with transformed-fit R² ≈ 0.9698775. The test suite compares the fit with independent scalar closed-form OLS calculations rather than using the production fitter as its own reference.

The peak selection is an explicit analysis step; it does not remove or rewrite rows in the stored CSV. The reported slope standard error covers only ordinary least-squares statistical uncertainty in the log-transformed peaks. It excludes sensor calibration, timing, peak-selection uncertainty, correlated residuals, and systematic effects. This is a diagnostic envelope fit, not a complete physical damping characterization.

### Data provenance and license

- Upstream raw file, pinned to commit `cbf82673641ecd65e902ad5c38a048387649a2a0`: [`raw_data/len1_cond1_1.csv`](https://github.com/EnzeXu/Damped_Pendulum_Dataset/blob/cbf82673641ecd65e902ad5c38a048387649a2a0/raw_data/len1_cond1_1.csv)
- Dataset documentation: [upstream README](https://github.com/EnzeXu/Damped_Pendulum_Dataset/blob/cbf82673641ecd65e902ad5c38a048387649a2a0/README.md)
- The included data file is redistributed under Apache-2.0; see [the bundled license](data/LICENSE-APACHE-2.0.txt) and [data README](data/README.md).
- The upstream project requests citation of Xu et al., “Identifying Invariant Physical Dynamics Across Multiple Environments,” *Transactions on Machine Learning Research* (2026): https://openreview.net/forum?id=xvQYvYEGhj.

The acquisition details above are attributed to the upstream documentation and have not been independently re-measured by PhysLab QA.
