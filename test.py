import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from scipy.interpolate import griddata

# Define the transformation function
def transform_range_azimuth_to_half_circle(range_azimuth_map):
        num_azimuths, num_ranges = range_azimuth_map.shape
        segment_min_az_deg = -90
        segment_max_az_deg = 90
        min_az_rad = np.deg2rad(segment_min_az_deg)
        max_az_rad = np.deg2rad(segment_max_az_deg)
        
        # Adjust grid to match the dimensions of data
        r_edges = np.linspace(0, num_ranges, num_ranges + 1)
        az_edges = np.linspace(min_az_rad, max_az_rad, num_azimuths + 1)
        R, AZ = np.meshgrid(r_edges[:-1], az_edges[:-1])  # Use all but last edge to fit data
    
        # Convert polar to Cartesian coordinates for grid edges
        grid_x = R * np.cos(AZ)
        grid_y = R * np.sin(AZ)
    
        points = np.vstack((grid_x.flatten(), grid_y.flatten())).T
        values = range_azimuth_map.flatten()
    
        target_x = np.linspace(grid_x.min(), grid_x.max(), num_ranges)
        target_y = np.linspace(grid_y.min(), grid_y.max(), num_azimuths)
        grid_x_target, grid_y_target = np.meshgrid(target_x, target_y)
    
        output_map = griddata(points, values, (grid_x_target, grid_y_target), method='linear')
        return (grid_x_target, grid_y_target, output_map)

# Radar parameters
N_S = 180  # Number of azimuth spokes
N_PR = 200  # Number of range points

# Visualization normalization parameters
MIN_RETURN = 0
MAX_RETURN = 20
vis_norm = colors.Normalize(MIN_RETURN, MAX_RETURN)

# Generate a range-azimuth map with zeros and a rectangle of ones in the middle
ra_map = np.zeros((N_S, N_PR))
rect_width = 20  # Width of the rectangle in range bins
rect_height = 40  # Height of the rectangle in azimuth spokes
rect_start_range = N_PR // 2 - rect_width // 2
rect_start_azimuth = N_S // 2 - rect_height // 2
ra_map[rect_start_azimuth:rect_start_azimuth + rect_height, rect_start_range:rect_start_range + rect_width] = 10

# Transform the map
transformed_map = transform_range_azimuth_to_half_circle(ra_map)

# Plotting
fig, axs = plt.subplots(1, 2, figsize=(12, 6))

# Plot the test data
im1 = axs[0].imshow(ra_map, extent=[0, N_PR, 0, N_S], cmap='gray', origin='lower')
axs[0].set_title('Test Data')
axs[0].set_xlabel('Range Index')
axs[0].set_ylabel('Azimuth Index')
plt.colorbar(im1, ax=axs[0], orientation='vertical', label='Radar Return')

# Plot the transformed map
im2 = axs[1].imshow(transformed_map[2], extent=[transformed_map[0].min(), transformed_map[0].max(), transformed_map[1].min(), transformed_map[1].max()], cmap='gray', origin='lower')
axs[1].set_title('Transformed Map')
axs[1].set_xlabel('X')
axs[1].set_ylabel('Y')
plt.colorbar(im2, ax=axs[1], orientation='vertical', label='Radar Return')

plt.tight_layout()
plt.show()
