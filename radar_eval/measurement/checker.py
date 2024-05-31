import h5py

def check_hdf5_file(hdf5_filename):
    expected_datasets = set()
    max_dataframe_counter = 5  # Adjust based on your requirements
    dataframe_count = 4095  # Adjust based on your requirements

    # Generate all expected dataset names
    for i in range(max_dataframe_counter):
        for j in range(dataframe_count):
            dataset_name = f"Frame_Data_Cube_{i:04d}_{j:04d}"
            expected_datasets.add(dataset_name)
            if i == 1 and j > 4095:
                break
            
    missing_datasets = expected_datasets.copy()

    # Open the HDF5 file and check each dataset
    with h5py.File(hdf5_filename, "r") as file:
        actual_datasets = set(file['/Data'].keys())
        missing_datasets.difference_update(actual_datasets)

    if missing_datasets:
        print("Missing Datasets:")
        for missing in missing_datasets:
            print(missing)
    else:
        print("No missing datasets.")

    print(f"Total expected datasets: {len(expected_datasets)}, Found: {len(expected_datasets) - len(missing_datasets)}")
    return len(missing_datasets) == 0

# Usage
hdf5_filename = "MiRa6024_Measurement_02_02_2024_00_58_11.hdf5"  # Specify the path to your HDF5 file
result = check_hdf5_file(hdf5_filename)
print("Check result:", "Passed" if result else "Failed")
