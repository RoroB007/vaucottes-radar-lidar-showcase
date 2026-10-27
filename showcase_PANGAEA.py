"""
Quick-start visualization for the PANGAEA-formatted Vaucottes dataset
(19 acquisitions, files AccNN_*.nc + AccNN_drone_position.tab). Mirrors the original
Acquisitions/showcase.py, adapted to the NetCDF/TAB files produced by
export_pangaea.m. NOT part of the PANGAEA submission itself (PANGAEA does
not accept code/software as data files) -- local QA/demo only.

Usage: python showcase_PANGAEA.py [acquisition number, 1-19, default 8]

Requires: pip install netCDF4 pandas matplotlib
On Windows, `pip install tzdata` if ZoneInfo raises ZoneInfoNotFoundError.
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from netCDF4 import Dataset

PARIS_TZ = ZoneInfo('Europe/Paris')
EXPORT_DIR = os.path.dirname(os.path.abspath(__file__))
ACQ = int(sys.argv[1]) if len(sys.argv) > 1 else 8


def data_file(name):
    """Path of a dataset file of acquisition ACQ (AccNN_<name>), falling back to the
    unprefixed name used by the earlier single-acquisition export."""
    prefixed = os.path.join(EXPORT_DIR, f'Acq{ACQ:02d}_{name}')
    return prefixed if os.path.exists(prefixed) else os.path.join(EXPORT_DIR, name)


def to_paris_str(unix_time):
    """Convert a POSIX (UNIX) timestamp to a formatted Europe/Paris local time string."""
    return datetime.fromtimestamp(float(unix_time), tz=timezone.utc).astimezone(PARIS_TZ).strftime('%Y-%m-%d %H:%M:%S')


def main():
    print(f"Loading Vaucottes PANGAEA-formatted Dataset, acquisition {ACQ}...")

    # ==========================================
    # 1. LOAD DRONE TRAJECTORY (TAB-delimited, absolute UTM31N, unchanged)
    # ==========================================
    drone_df = pd.read_csv(data_file('drone_position.tab'), sep='\t')
    easting_col = [c for c in drone_df.columns if 'Easting' in c][0]
    northing_col = [c for c in drone_df.columns if 'Northing' in c][0]
    x_mean = drone_df[easting_col].mean()
    y_mean = drone_df[northing_col].mean()
    drone_x_centered = drone_df[easting_col] - x_mean
    drone_y_centered = drone_df[northing_col] - y_mean

    # ==========================================
    # 2. LOAD LIDAR ELEVATION, RADAR-SYNCED (NetCDF, local/radar-centered coords.)
    # ==========================================
    # NOTE on axis order: these files were written from MATLAB via
    # nccreate/ncwrite. MATLAB (column-major) and netCDF-4/HDF5 (row-major,
    # the convention Python's netCDF4 and ncdump follow) disagree on which
    # axis varies fastest, so every variable with 2+ dimensions comes back
    # from Python with its dimensions in the REVERSE order of what
    # showcase_PANGAEA.m sees (same names, same sizes, reversed order) --
    # call .transpose() (no args = reverse all axes) to restore the
    # intended (time, y, x, ...) order. This mirrors the manual
    # transposition the original showcase.py already needed for the source
    # .mat/HDF5 files; see README_PANGAEA.md for details.
    with Dataset(data_file('lidar_eta_radar_synced.nc')) as ds:
        eta_time = ds.variables['time'][:]
        eta_x_extended = ds.variables['x_local_ext'][:].transpose()
        eta_y_extended = ds.variables['y_local_ext'][:].transpose()
        eta_z_extended = ds.variables['eta_z_extended'][:].transpose()
        eta_x = ds.variables['x_local_raw'][:].transpose()
        eta_y = ds.variables['y_local_raw'][:].transpose()
        eta_z = ds.variables['eta_z'][:].transpose()

    # ==========================================
    # 3. LOAD RADAR SIGNAL, DRONE-MATCHED (local/radar-centered coords.)
    # ==========================================
    with Dataset(data_file('radar_raw_drone.nc')) as ds:
        time_unix_raw = ds.variables['time'][:]
        padded_x = ds.variables['x_local'][:].transpose()
        padded_y = ds.variables['y_local'][:].transpose()
        padded_sig = ds.variables['sig'][:].transpose()

    # Convert radar integer array to float and mask out documented missing values
    sig_double = np.asarray(padded_sig).astype(float)
    sig_double[sig_double == 32767] = np.nan
    # Note: 0 denotes array padding beyond a given time step's actual extent
    # (NOT part of the missing-value convention) -- left unmasked here, as in
    # the original showcase.py; treat with care.

    # ==========================================
    # 4. LOAD FULL RADAR SNAPSHOT (native polar, radar-centered)
    # ==========================================
    with Dataset(data_file('radar_snap.nc')) as ds:
        radar_snap_time = ds.variables['time'][:]
        radar_snap_az = ds.variables['az'][:]
        radar_snap_r = ds.variables['r'][:]
        radar_snap_sig = ds.variables['sig'][:].transpose()

    snap_double = np.asarray(radar_snap_sig).astype(float)
    snap_double[snap_double == 32767] = np.nan

    # Convert polar to local Cartesian for the continuous snapshot
    R_snap, AZ_snap = np.meshgrid(radar_snap_r, radar_snap_az)
    X_snap = R_snap * np.cos(AZ_snap)
    Y_snap = R_snap * np.sin(AZ_snap)

    # ==========================================
    # PLOTTING THE DASHBOARD
    # ==========================================
    print("Generating figures...")
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.canvas.manager.set_window_title(f'Vaucottes PANGAEA Dataset Showcase - Acq{ACQ:02d}')

    # --- Plot 1 (Top Left): Drone Trajectory ---
    ax = axes[0, 0]
    ax.plot(drone_x_centered, drone_y_centered, c='red', linewidth=2, label='Drone Path')
    ax.scatter(drone_x_centered.iloc[0], drone_y_centered.iloc[0], c='blue', s=70, label='Start')
    ax.set_title('Drone Trajectory around mean position (UTM 31N, absolute)')
    ax.set_xlabel('X [m]')
    ax.set_ylabel('Y [m]')
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_aspect('equal')
    ax.legend(loc='best')

    # --- Plot 2 (Top Middle): Extended Lidar Surface (Filter index 3 = veryhighfilt) ---
    ax = axes[0, 1]
    lidar_frame = eta_z_extended[0, :, :, 3]
    c1 = ax.pcolormesh(eta_x_extended, eta_y_extended, lidar_frame, cmap='terrain', shading='auto')
    fig.colorbar(c1, ax=ax, label='Elevation [m]')
    ax.set_title(f'Lidar Surface (local coords.)\n{to_paris_str(eta_time[0])} (Europe/Paris)')
    ax.set_xlabel('Local X [m]')
    ax.set_ylabel('Local Y [m]')
    ax.set_aspect('equal')

    # --- Plot 3 (Top Right): Padded Drone Radar (local coords.) ---
    ax = axes[0, 2]
    radar_frame = sig_double[0, :, :]
    X_rad = padded_x[0, :, :]
    Y_rad = padded_y[0, :, :]
    c2 = ax.scatter(X_rad, Y_rad, c=radar_frame, cmap='viridis', s=15, marker='s')
    fig.colorbar(c2, ax=ax, label='Signal Strength')
    ax.set_title(f'Radar Signal (local coords.)\n{to_paris_str(time_unix_raw[0])} (Europe/Paris)')
    ax.set_xlabel('Local X [m]')
    ax.set_ylabel('Local Y [m]')
    ax.set_aspect('equal')

    # --- Plot 4 (Bottom Left): Hidden ---
    axes[1, 0].axis('off')

    # --- Plot 5 (Bottom Middle): Original-resolution Lidar Surface ---
    ax = axes[1, 1]
    c3 = ax.pcolormesh(eta_x, eta_y, eta_z[0, :, :], cmap='terrain', shading='auto')
    fig.colorbar(c3, ax=ax, label='Elevation [m]')
    ax.set_title(f'Lidar Surface (local coords.)\n{to_paris_str(eta_time[0])} (Europe/Paris)')
    ax.set_xlabel('Local X [m]')
    ax.set_ylabel('Local Y [m]')
    ax.set_aspect('equal')

    # --- Plot 6 (Bottom Right): Continuous Radar Snapshot (native polar) ---
    ax = axes[1, 2]
    c4 = ax.pcolormesh(X_snap, Y_snap, snap_double[:, :, 0], cmap='viridis', shading='auto')
    fig.colorbar(c4, ax=ax, label='Signal Strength')
    ax.set_title(f'Full Radar Snapshot (radar-centered polar)\n{to_paris_str(radar_snap_time[0])} (Europe/Paris)')
    ax.set_xlabel('Local X [m]')
    ax.set_ylabel('Local Y [m]')
    ax.set_aspect('equal')

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
