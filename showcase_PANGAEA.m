
% Quick-start visualization for the PANGAEA-formatted Vaucottes dataset
% (PANGAEA_export/*.nc + drone_position.tab). Mirrors the original
% Acquisitions/showcase.m, adapted to the NetCDF/TAB files produced by
% export_pangaea.m. NOT part of the PANGAEA submission itself (PANGAEA
% does not accept code/software as data files) -- local QA/demo only.
clc; clear; close all;

disp('Loading Vaucottes PANGAEA-formatted Dataset...');
exportdir = fileparts(mfilename('fullpath'));

%% 1. LOAD DRONE TRAJECTORY (TAB-delimited, absolute UTM31N, unchanged)
opts = detectImportOptions(fullfile(exportdir, "drone_position.tab"), 'FileType', 'text', 'Delimiter', '\t');
opts.VariableNames = ["DateTimeUTC", "EastingUTM31N_m", "NorthingUTM31N_m"];
opts.VariableTypes = ["string", "double", "double"];
drone_data = readtable(fullfile(exportdir, "drone_position.tab"), opts);

%% 2. LOAD LIDAR ELEVATION (RADAR-SYNCED, LOCAL/RADAR-CENTERED COORDINATES)
f_lidar = fullfile(exportdir, "lidar_eta_radar_synced.nc");
eta_time = ncread(f_lidar, "time");
eta_x_extended = ncread(f_lidar, "x_local_ext");
eta_y_extended = ncread(f_lidar, "y_local_ext");
eta_z_extended = ncread(f_lidar, "eta_z_extended");
eta_x = ncread(f_lidar, "x_local_raw");
eta_y = ncread(f_lidar, "y_local_raw");
eta_z = ncread(f_lidar, "eta_z");

%% 3. LOAD RADAR SIGNAL (DRONE-MATCHED, LOCAL/RADAR-CENTERED COORDINATES)
f_raddrone = fullfile(exportdir, "radar_raw_drone.nc");
time_unix_raw = ncread(f_raddrone, "time");
padded_x = ncread(f_raddrone, "x_local");
padded_y = ncread(f_raddrone, "y_local");
padded_sig = ncread(f_raddrone, "sig");

sig_double = double(padded_sig);
sig_double(sig_double == 32767) = NaN; % documented missing-value convention (see .nc 'comment' attribute)
% Note: 0 denotes array padding beyond a given time step's actual extent
% (NOT part of the missing-value convention) -- left unmasked here, as in
% the original showcase.m; treat with care.

%% 4. LOAD FULL RADAR SNAPSHOT (NATIVE POLAR, RADAR-CENTERED)
f_snap = fullfile(exportdir, "radar_snap.nc");
radar_snap_time = ncread(f_snap, "time");
radar_snap_az = ncread(f_snap, "az");
radar_snap_r = ncread(f_snap, "r");
radar_snap_sig = ncread(f_snap, "sig");
snap_double = double(radar_snap_sig);
snap_double(snap_double == 32767) = NaN;

% Convert continuous snapshot polar coordinates to local Cartesian
[R_snap, AZ_snap] = meshgrid(radar_snap_r, radar_snap_az);
X_snap = R_snap .* cos(AZ_snap);
Y_snap = R_snap .* sin(AZ_snap);

%% PLOTTING THE DASHBOARD
disp('Generating figures...');
to_paris_str = @(t) char(datetime(t, 'ConvertFrom', 'posixtime', 'TimeZone', 'Europe/Paris', 'Format', 'yyyy-MM-dd HH:mm:ss'));
figure('Name', 'Vaucottes PANGAEA Dataset Showcase', 'Position', [100, 100, 1500, 450]);

% --- Plot 1: Drone Trajectory (absolute UTM31N) ---
subplot(2, 3, 1);
plot(drone_data.EastingUTM31N_m - mean(drone_data.EastingUTM31N_m), ...
     drone_data.NorthingUTM31N_m - mean(drone_data.NorthingUTM31N_m), 'r-', 'LineWidth', 2);
axis equal
hold on;
scatter(drone_data.EastingUTM31N_m(1) - mean(drone_data.EastingUTM31N_m), ...
        drone_data.NorthingUTM31N_m(1) - mean(drone_data.NorthingUTM31N_m), 70, 'b', 'filled');
title('Drone Trajectory around mean position (UTM 31N, absolute)');
xlabel('X (m)'); ylabel('Y (m)');
grid on;
legend('Drone Path', 'Start Point', 'Location', 'best');

% --- Plot 2: Lidar Elevation Surface (Frame 1, Filter 4 = veryhighfilt) ---
subplot(2, 3, 2);
lidar_frame = squeeze(eta_z_extended(1, :, :, 4));
pcolor(eta_x_extended, eta_y_extended, lidar_frame);
axis equal
shading flat;
cb1 = colorbar;
cb1.Label.String = 'Elevation (m)';
title(sprintf('Lidar Surface (local coords.)\n%s (Europe/Paris)', to_paris_str(eta_time(1))));
xlabel('Local X (m)'); ylabel('Local Y (m)');

% --- Plot 3: Radar Signal (Frame 1, local Cartesian) ---
subplot(2, 3, 3);
radar_frame = squeeze(sig_double(1, :, :));
X_rad = squeeze(padded_x(1, :, :));
Y_rad = squeeze(padded_y(1, :, :));
pcolor(X_rad, Y_rad, radar_frame);
axis equal
shading flat;
colormap(gca, 'parula');
cb2 = colorbar;
cb2.Label.String = 'Signal Strength';
title(sprintf('Radar Signal (local coords.)\n%s (Europe/Paris)', to_paris_str(time_unix_raw(1))));
xlabel('Local X (m)'); ylabel('Local Y (m)');

% --- Plot 5 (Bottom Middle): Lidar Surface, original-resolution grid ---
subplot(2, 3, 5);
pcolor(eta_x, eta_y, squeeze(eta_z(1, :, :)));
shading flat; axis equal;
cb3 = colorbar; cb3.Label.String = 'Elevation (m)';
title(sprintf('Lidar Surface (local coords.)\n%s (Europe/Paris)', to_paris_str(eta_time(1))));
xlabel('Local X [m]'); ylabel('Local Y [m]');

% --- Plot 6: Full Radar Snapshot (Frame 1, native polar -> local Cartesian) ---
subplot(2, 3, 6);
pcolor(X_snap, Y_snap, squeeze(snap_double(:, :, 1)));
shading flat; axis equal; colormap(gca, 'parula');
cb4 = colorbar; cb4.Label.String = 'Signal Strength';
title(sprintf('Full Radar Snapshot (radar-centered polar)\n%s (Europe/Paris)', to_paris_str(radar_snap_time(1))));
xlabel('Local X [m]'); ylabel('Local Y [m]');
