# Vaucottes Radar & Lidar Showcase

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22813736.svg)](https://doi.org/10.5281/zenodo.22813736)

Quick-look visualization scripts (MATLAB and Python) for the dataset *Synchronised X-band
marine radar sea clutter and UAV lidar sea surface elevation measurements at Vaucottes
(Normandy, France) on 6 and 7 May 2025* (19 acquisitions: 7 on 6 May, 12 on 7 May).

This code is archived on Zenodo: https://doi.org/10.5281/zenodo.22813736

The dataset itself is published on PANGAEA: https://doi.org/10.1594/PANGAEA.997511 (active
once the DOI is registered).

## What this is

Two equivalent quick-look scripts that load the PANGAEA-published NetCDF (`.nc`) and
TAB-delimited (`.tab`) files of one acquisition and render a 2x3 dashboard: UAV trajectory,
lidar-derived sea surface elevation (native and radar-synchronized grids), and X-band radar
backscatter (cropped-cartesian and full polar snapshot).

Each file of the dataset is prefixed by its acquisition number, from `Acq01_` to `Acq19_`
(e.g. `Acq08_radar_snap.nc`, `Acq08_drone_position.tab`). The scripts also read the unprefixed
names (`radar_snap.nc`, ...) of the earlier single-acquisition release.

- `showcase_PANGAEA.m` — MATLAB version (uses `ncread`, no extra toolboxes beyond base MATLAB).
- `showcase_PANGAEA.py` — Python version (requires `netCDF4`, `pandas`, `matplotlib`).

This repository contains **code only** — no data. It is referenced from the PANGAEA dataset
entry as supplementary software, per PANGAEA's policy of not accepting code as a data file.

## Usage

1. Download the dataset files from the PANGAEA entry linked above.
2. Place the files of the acquisitions you want (the `AccNN_*.nc` files and
   `AccNN_drone_position.tab`) in the same directory as the script you want to run (or edit
   the `exportdir` / `EXPORT_DIR` variable at the top of the script to point elsewhere).
3. Run, choosing the acquisition number (1 to 19, default 8):
   - MATLAB: set `acq = 3;` in the workspace and run `showcase_PANGAEA.m`, or
     `matlab -batch "acq = 3; showcase_PANGAEA"`.
   - Python: `pip install netCDF4 pandas matplotlib` then `python showcase_PANGAEA.py 3`.

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

Barthélémy, R. (2026). vaucottes-radar-lidar-showcase (v1.1.0) [Software]. Zenodo.
https://doi.org/10.5281/zenodo.22813736

and the associated PANGAEA dataset:

Barthelemy, R.; Merigaud, A.; Tona, P.; Moreaud, M.; Dias, F. (publication year): Synchronised
X-band marine radar sea clutter and UAV lidar sea surface elevation measurements at Vaucottes
(Normandy, France) on 6 and 7 May 2025 [dataset]. PANGAEA, https://doi.org/10.1594/PANGAEA.997511
