# Third-party experimental data

This directory contains one data file redistributed from the [Damped Pendulum Dataset](https://github.com/EnzeXu/Damped_Pendulum_Dataset) maintained by Enze Xu and collaborators.

## Source and provenance

- Upstream raw file, pinned to commit `cbf82673641ecd65e902ad5c38a048387649a2a0`: [`raw_data/len1_cond1_1.csv`](https://github.com/EnzeXu/Damped_Pendulum_Dataset/blob/cbf82673641ecd65e902ad5c38a048387649a2a0/raw_data/len1_cond1_1.csv)
- Upstream dataset documentation: [README](https://github.com/EnzeXu/Damped_Pendulum_Dataset/blob/cbf82673641ecd65e902ad5c38a048387649a2a0/README.md)
- Upstream Git blob SHA: `d21ea5a044e8ac65abf300e51c5e073cffdb0cbc`
- The upstream project describes the file as an unprocessed sensor export recorded with a PASCO Wireless Rotary Motion Sensor (PS-3220).
- Configuration: length setting `len1` = 0.236 m; damping condition `cond1` = air only; repeat 1.
- The file contains 6,896 time-angle observations spanning 0 to 68.95 s at nominal 0.01 s sampling. It includes the original time, angle, angular velocity, angular acceleration, position, velocity, and acceleration columns. Blank cells in the export are retained.

The data values are copied from the upstream raw export; this project does not silently delete or alter stored measurement rows. The analysis uses only the time and angle columns and selects peak observations in a documented, reproducible step. The upstream acquisition details are attributed to the source documentation and have not been independently re-measured by PhysLab QA.

## License

This external data asset is redistributed under the Apache License, Version 2.0. A copy is provided in `LICENSE-APACHE-2.0.txt`. The root MIT license applies to PhysLab QA code and does not replace the separate license for this third-party data.

## Citation

The upstream project requests citation of:

Enze Xu, Toon Tran, Hongjue Zhao, Yuchen Wang, Mengdi Huai, and Huajie Shao, “Identifying Invariant Physical Dynamics Across Multiple Environments,” *Transactions on Machine Learning Research* (2026). https://openreview.net/forum?id=xvQYvYEGhj.

The upstream project also acknowledges Dr. Bjorg Larson and the Physics Department of William & Mary for access to the experimental facilities.
