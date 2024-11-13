import os
import h5py
import json
import click
import numpy as np
from tqdm import tqdm
import scipy.io as sio

def convert_hdf5_file(hdf5_filename, output_folder):
    # Create subfolders for each file type
    npy_folder = os.path.join(output_folder, "npy")
    csv_folder = os.path.join(output_folder, "csv")
    mat_folder = os.path.join(output_folder, "mat")
    os.makedirs(npy_folder, exist_ok=True)
    os.makedirs(csv_folder, exist_ok=True)
    os.makedirs(mat_folder, exist_ok=True)

    with h5py.File(hdf5_filename, "r") as file:
        # Convert metadata to JSON
        metadata = json.loads(file["Metadata"].attrs["MiRa_Radar_System_Info"])
        metadata_json_filename = os.path.join(output_folder, "metadata.json")
        with open(metadata_json_filename, "w") as metadata_json_file:
            json.dump(metadata, metadata_json_file, indent=4)

        # Determine the shape of the first dataset (excluding 'Metadata' and 'Data')
        dataset_names = [name for name in file if name not in ['Metadata', 'Data']]
        first_dataset = file[dataset_names[0]]
        first_dataset_shape = first_dataset.shape

        # Initialize the radar data cube
        radar_data_cube_shape = first_dataset_shape + (len(dataset_names),)
        radar_data_cube = np.zeros(radar_data_cube_shape, np.uint16)

        # Process datasets
        for i, dataset_name in enumerate(dataset_names):
            dataset = file[dataset_name]  # Access the dataset
            radar_data_cube[..., i] = np.array(dataset, np.uint16)
            dataset_basename = dataset_name
            
            # Save dataset as CSV
            dataset_folder = os.path.join(csv_folder, (hdf5_filename.split('/')[1]).split('.')[0])
            os.makedirs(dataset_folder, exist_ok=True)
            for shape_pos in range(radar_data_cube.shape[3]):        
                dataset_csv_filename = os.path.join(dataset_folder, f"{dataset_basename}_shape{shape_pos:04d}.csv")
                reshaped = radar_data_cube[:, :, :, shape_pos, i].reshape(radar_data_cube.shape[0], -1)
                np.savetxt(dataset_csv_filename, reshaped, delimiter=",", fmt='%d')

        # Save dataset as NPY (NumPy binary)
        dataset_npy_filename = os.path.join(npy_folder, f"{(hdf5_filename.split('/')[1]).split('.')[0]}.npy")
        np.save(dataset_npy_filename, radar_data_cube)

        # Save dataset as MAT (MATLAB format)
        dataset_mat_filename = os.path.join(mat_folder, f"{(hdf5_filename.split('/')[1]).split('.')[0]}.mat")
        sio.savemat(dataset_mat_filename, {"data": radar_data_cube})


def convert_hdf5_files(input_folder, output_folder):
    # Get a list of HDF5 files in the input folder
    hdf5_files = [f for f in os.listdir(input_folder) if f.endswith('.hdf5')]

    for hdf5_file in tqdm(hdf5_files, desc='Converting Files'):
        hdf5_filename = os.path.join(input_folder, hdf5_file)
        convert_hdf5_file(hdf5_filename, output_folder)

if __name__ == "__main__":
    click.echo("Select the folder containing HDF5 files:")
    input_folder = click.prompt("Folder path", type=click.Path(exists=True, file_okay=False))
    output_folder = "./"  # Specify your desired output folder here
    convert_hdf5_files(input_folder, output_folder)
    click.echo("Conversion complete.")
