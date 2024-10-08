import os
import numpy as np
import h5py
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pathlib import Path
from scipy.signal import hanning
from IPython.display import HTML
import ipywidgets as widgets

# Define constants
c0 = 3e8  # Speed of light

# Load the HDF5 radar measurement data
radar_meas_hdf5_path = './radar_eval/measurement/hdf5/'
file = 'SY60I11_Measurement_24_09_2024_13_29_00_Default_Session.hdf5'
hdf5_file_path = Path(radar_meas_hdf5_path + file).resolve()

# Function to load HDF5 file and metadata
def load_radar_data_and_params(file_path):
    with h5py.File(file_path, 'r') as f:
        # Load radar parameters
        radar_param = {}
        for key, value in f['radar_parameters'].attrs.items():
            radar_param[key] = value
        
        # Load radar data cube
        radar_data = np.array(f['radar_data'], dtype=np.float32)
    return radar_param, radar_data

# Load the radar parameters and data cube
radar_param, mira_data_cube = load_radar_data_and_params(hdf5_file_path)
print(f"Radar Data Cube Shape: {mira_data_cube.shape}")

# Extract radar parameters
f0 = radar_param['start_frequency'][0]
f1 = radar_param['end_frequency'][0]
fs = radar_param['sampling_frequency']
Tc = radar_param['ramp_time'][0]
B = radar_param['ramp_bandwidth'][0]
PRT = radar_param['pulse_repetition_time']

# Calculate max range and velocity
Rmax = c0 / (2 * B) * (mira_data_cube.shape[1] - 1) / 2
Vmax = c0 / ((f1 + f0) / 2) / (4 * PRT) * 3.6  # in km/h
print(f"Max Range: {Rmax} meters, Max Velocity: {Vmax} km/h")

# Signal processing parameters
fft1_padding = 64
fft2_padding = 64

# Preprocess and perform FFT on radar data to generate range-Doppler maps
def process_range_doppler(data_cube):
    # Apply Hanning window in fast time (range FFT)
    data_win = hanning(data_cube.shape[1])[np.newaxis, :, np.newaxis, np.newaxis, np.newaxis] * data_cube
    
    # Pad for range FFT
    data_pad = np.concatenate((data_win, np.zeros((data_win.shape[0], fft1_padding, data_win.shape[2], data_win.shape[3], data_win.shape[4]))), axis=1)
    fft1_pro = np.fft.rfft(data_pad, axis=1)
    fft1pro_abs = np.abs(fft1_pro)
    
    # Apply Hanning window in Doppler (velocity FFT)
    fft1_win = hanning(fft1_pro.shape[4])[np.newaxis, np.newaxis, np.newaxis, np.newaxis, :] * fft1_pro
    
    # Pad for velocity FFT
    fft1_pad = np.concatenate((fft1_win, np.zeros((fft1_pro.shape[0], fft1_pro.shape[1], fft1_pro.shape[2], fft1_pro.shape[3], fft2_padding))), axis=4)
    fft2_pro = np.fft.fft(fft1_pad, axis=4)
    
    # Compute the absolute value and apply fftshift to center the Doppler frequencies
    fft2pro_abs = np.fft.fftshift(np.abs(fft2_pro), axes=4)
    return fft2pro_abs

# Process the radar data cube
range_doppler_data = process_range_doppler(mira_data_cube)
print(f"Processed Range Doppler Data Shape: {range_doppler_data.shape}")

# Create a meshgrid for plotting
num_range_bins = range_doppler_data.shape[1]
num_doppler_bins = range_doppler_data.shape[4]
range_grid = np.linspace(0, Rmax, num_range_bins)
doppler_grid = np.linspace(-Vmax, Vmax, num_doppler_bins)

# Set up the figure for animation
fig, ax = plt.subplots(figsize=(10, 6))
im = ax.imshow(range_doppler_data[0, :, 0, 0, :], origin='lower', extent=[-Vmax, Vmax, 0, Rmax], aspect=2*Vmax/Rmax, cmap='viridis')

# Labels and color bar
ax.set_xlabel('Speed (km/h)')
ax.set_ylabel('Range (m)')
cbar = fig.colorbar(im)
cbar.set_label('Magnitude (dB)')

# Update function for animation
def update(frame):
    im.set_data(range_doppler_data[frame, :, 0, 0, :])
    return [im]

# Create the animation
ani = animation.FuncAnimation(fig, update, frames=range_doppler_data.shape[0], interval=100)

# Save the animation as a GIF
ani.save('./radar_range_doppler_animation.gif', writer='pillow', fps=10)
print("Animation saved as radar_range_doppler_animation.gif")

# To display animation in notebooks, use the following
# HTML(ani.to_jshtml())
