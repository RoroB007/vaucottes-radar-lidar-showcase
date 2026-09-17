# Vaucottes Radar & Lidar Showcase

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22813736.svg)](https://doi.org/10.5281/zenodo.22813736)

Quick-look visualization scripts (MATLAB and Python) for the synchronized X-band marine radar
and UAV lidar sea-surface dataset acquired at Vaucottes (Normandy, France) on 7 May 2025.

This code is archived on Zenodo: https://doi.org/10.5281/zenodo.22813736

The dataset itself is published on PANGAEA: **[DOI link to be added once the dataset is
published — PANGAEA ticket PDI-45262]**.

## What this is

Two equivalent quick-look scripts that load the PANGAEA-published NetCDF (`.nc`) and
TAB-delimited (`.tab`) files and render a 2x3 dashboard: UAV trajectory, lidar-derived sea
surface elevation (native and radar-synchronized grids), and X-band radar backscatter
(cropped-cartesian and full polar snapshot).

- `showcase_PANGAEA.m` — MATLAB version (uses `ncread`, no extra toolboxes beyond base MATLAB).
- `showcase_PANGAEA.py` — Python version (requires `netCDF4`, `pandas`, `matplotlib`).

This repository contains **code only** — no data. It is referenced from the PANGAEA dataset
entry as supplementary software, per PANGAEA's policy of not accepting code as a data file.

## Usage

1. Download the dataset files from the PANGAEA entry linked above.
2. Place all downloaded files (the `.nc` files and `drone_position.tab`) in the same directory
   as the script you want to run (or edit the `exportdir` / `EXPORT_DIR` variable at the top of
   the script to point elsewhere).
3. Run:
   - MATLAB: open `showcase_PANGAEA.m` and run it, or `matlab -batch "showcase_PANGAEA"`.
   - Python: `pip install netCDF4 pandas matplotlib` then `python showcase_PANGAEA.py`.

## Coordinate convention

Some of the NetCDF files use coordinates local to the fixed radar position (in metres) rather
than absolute geographic coordinates; the radar's absolute WGS84 position is given in each
file's global attributes (`radar_position_lat` / `radar_position_lon`). See the PANGAEA dataset
description for the full coordinate convention.

## Cross-tool note (MATLAB-written NetCDF files)

These NetCDF files were written from MATLAB (`nccreate`/`ncwrite`). Because MATLAB is
column-major and NetCDF-4/HDF5 is row-major (the convention followed by Python's `netCDF4`,
`ncdump`, etc.), any variable with 2+ dimensions comes back from non-MATLAB tools with its
dimensions in the reverse order (same names, same sizes, reversed order). `showcase_PANGAEA.py`
calls `.transpose()` after reading each such variable to compensate — see the comments in that
script for details.

## License

Code in this repository is released under the MIT License (see `LICENSE`). The dataset itself
is released separately under CC-BY 4.0 on PANGAEA.

## Citation

If you use these scripts, please cite:

Barthélémy, R. (2026). vaucottes-radar-lidar-showcase (v1.0.1) [Software]. Zenodo.
https://doi.org/10.5281/zenodo.22813736

and the associated PANGAEA dataset (citation to be added once published).
