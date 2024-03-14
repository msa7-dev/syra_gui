import os
import h5py
import json
import pickle
import numpy as np
import scipy.io as sio

class MIRA_HDF5_CTRL:
    def __init__(self, filename):
        self.filename = filename
        self.datasets = {}
        self.metadata = {}
        self.frame_data_cube = None
        self.delta_time = None
        self.shape = None
        self.timestamp = None
        self.mira_config = None
        self.mira_bgt_reg_content = None
        self.mira_bgt_reg_content_readable = None
        self.radar_param = None
        # self.load_all_data()

    def load_all_data(self):
        self.load_datasets()
        self.load_metadata()
        self.load_specific_dataset_attributes('/Data/Frame_Data_Cube_0000_0000')
        self.load_specific_metadata_attributes()

    def load_datasets(self):
        with h5py.File(self.filename, 'r') as file:
            for dataset_name in file['/Data']:
                data = np.array(file['/Data'][dataset_name][:], dtype=np.float32)
                self.datasets[dataset_name] = np.expand_dims(data, axis=0)
            if self.datasets:
                self.mira_data_cube = np.concatenate(list(self.datasets.values()), axis=0)

    def load_metadata(self):
        with h5py.File(self.filename, 'r') as file:
            if 'Metadata' in file:
                metadata_group = file['Metadata']
                for item in metadata_group:
                    self.metadata[item] = metadata_group[item].attrs

    def load_specific_dataset_attributes(self, path):
        with h5py.File(self.filename, 'r') as file:
            if path in file:
                dataset = file[path]
                self.frame_data_cube = np.array(dataset, dtype=np.float32)
                self.delta_time = dataset.attrs['delta_time']
                self.shape = dataset.attrs['shape']
                self.timestamp = dataset.attrs['timestamp']

    def load_specific_metadata_attributes(self):
        # self.mira_config = self.metadata.get('mira_config', {}).get('mira_config')
        # self.mira_bgt_reg_content = self.metadata.get('mira_bgt_reg_content', {}).get('mira_bgt_reg_content')
        # self.mira_bgt_reg_content_readable = self.metadata.get('mira_bgt_reg_content_readable', {}).get('mira_bgt_reg_content_readable')
        # radar_param_data = self.metadata.get('mira_radar_parameters', {}).get('mira_radar_parameters')
        # if radar_param_data is not None:
        #     self.radar_param = pickle.loads(radar_param_data.tobytes())
        pass


    def print_hdf5_structure(self, output_filename=None):
        with h5py.File(self.filename, "r") as file:
            if output_filename:
                with open(output_filename, "w") as output_file:
                    self._print_structure("/", file, output_file=output_file)
            else:
                self._print_structure("/", file)

    def _print_structure(self, name, item, depth=0, output_file=None):
        indent = "  " * depth
        if isinstance(item, h5py.Group):
            if depth == 0:
                line = f"- /"
            else:
                line = f"{indent}- {name.split('/')[-1]}"
            if output_file:
                output_file.write(f"{line}\n")
            else:
                print(line)

            for attr_name, attr_value in item.attrs.items():
                attr_line = f"{indent}  - @{attr_name}: {attr_value}"
                if output_file:
                    output_file.write(f"{attr_line}\n")
                else:
                    print(attr_line)

            for key, subitem in item.items():
                self._print_structure(key, subitem, depth + 1, output_file)  # Corrected recursive call
        elif isinstance(item, h5py.Dataset):
            line = f"{indent}- {name.split('/')[-1]} (Dataset)"
            if output_file:
                output_file.write(f"{line}\n")
            else:
                print(line)

            for attr_name, attr_value in item.attrs.items():
                attr_line = f"{indent}  - @{attr_name}: {attr_value}"
                if output_file:
                    output_file.write(f"{attr_line}\n")
                else:
                    print(attr_line)

    def read_dataset(self, dataset_path):
        with h5py.File(self.filename, 'r') as file:
            if dataset_path in file:
                data = file[dataset_path][()]
                return data
            else:
                print(f"Dataset {dataset_path} not found in file.")
                return None

    def get_dataset_statistics(self, dataset_path):
        data = self.read_dataset(dataset_path)
        if data is not None:
            stats = {
                'mean': np.mean(data),
                'std_dev': np.std(data),
                'min': np.min(data),
                'max': np.max(data)
            }
            return stats
        else:
            return None

    def find_datasets_with_attribute(self, attribute_name, attribute_value=None):
        datasets = []
        with h5py.File(self.filename, 'r') as file:
            self._find_attr(file, attribute_name, attribute_value, datasets)
        return datasets

    def _find_attr(self, item, attribute_name, attribute_value, datasets, path='/'):
        if isinstance(item, h5py.Dataset):
            if attribute_name in item.attrs:
                if attribute_value is None or item.attrs[attribute_name] == attribute_value:
                    datasets.append(path)
        elif isinstance(item, h5py.Group):
            for key, subitem in item.items():
                new_path = f"{path}/{key}" if path != '/' else f"{path}{key}"
                self._find_attr(subitem, attribute_name, attribute_value, datasets, new_path)

    def get_dataset_slice(self, dataset_path, slice_tuple=None):
        with h5py.File(self.filename, 'r') as file:
            if dataset_path in file:
                data = file[dataset_path]
                if slice_tuple:
                    sliced_data = data[slice_tuple]
                    return sliced_data
                else:
                    return data[()]
            else:
                print(f"Dataset {dataset_path} not found in file.")
                return None

    def list_all_datasets(self):
        datasets = []
        with h5py.File(self.filename, 'r') as file:
            file.visititems(lambda name, obj: datasets.append(name) if isinstance(obj, h5py.Dataset) else None)
        return datasets

    def get_dataset_info(self, dataset_path):
        with h5py.File(self.filename, 'r') as file:
            if dataset_path in file:
                dataset = file[dataset_path]
                return dataset.shape, dataset.dtype
            else:
                print(f"Dataset {dataset_path} not found in file.")
                return None, None

    def search_datasets_by_name(self, search_string):
        matching_datasets = []
        with h5py.File(self.filename, 'r') as file:
            def search(name, obj):
                if isinstance(obj, h5py.Dataset) and search_string in name:
                    matching_datasets.append(name)
            file.visititems(search)
        return matching_datasets

    def extract_metadata(self, output_folder):
        with h5py.File(self.filename, "r") as file:
            if "Metadata" in file:
                metadata = json.loads(file["Metadata"].attrs.get("MiRa_Radar_System_Info", "{}"))
                metadata_json_filename = os.path.join(output_folder, "metadata.json")
                with open(metadata_json_filename, "w") as metadata_json_file:
                    json.dump(metadata, metadata_json_file, indent=4)

    def convert_dataset(self, output_folder):
        with h5py.File(self.filename, "r") as file:
            npy_folder = os.path.join(f'{output_folder}', "npy")
            mat_folder = os.path.join(f'{output_folder}', "mat")
            os.makedirs(npy_folder, exist_ok=True)
            os.makedirs(mat_folder, exist_ok=True)

            dataset_names = [name for name in file['Data']]
            if not dataset_names:
                print("No datasets found for conversion.")
                return

            first_dataset = self.read_dataset(f'/Data/{dataset_names[0]}')
            radar_data_cube_shape = first_dataset.shape + (len(dataset_names),)
            radar_data_cube = np.zeros(radar_data_cube_shape, np.uint16)

            for i, dataset_name in enumerate(dataset_names):
                dataset = self.read_dataset(f'/Data/{dataset_name}')
                radar_data_cube[..., i] = np.array(dataset, np.uint16)

            # Save dataset in different formats
            base_name = os.path.splitext(os.path.basename(self.filename))[0]
            
            self._save_as_npy(npy_folder, base_name, radar_data_cube)
            # self._save_as_mat(mat_folder, base_name, radar_data_cube)

    def _save_as_npy(self, folder, base_name, data_cube):
        filename = os.path.join(folder, f"{base_name}.npy")
        print(data_cube.shape)
        np.save(filename, data_cube)

    def _save_as_mat(self, folder, base_name, data_cube):
        filename = os.path.join(folder, f"{base_name}.mat")
        print(data_cube.shape)
        sio.savemat(filename, {"data": data_cube})

    def load_radar_data_cube(self, group_path='/Data', dtype=np.float32):
        datasets = []
        with h5py.File(self.filename, 'r') as file:
            for dataset_name in file[group_path]:
                data = np.array(file[f'{group_path}/{dataset_name}'][:], dtype=dtype)
                datasets.append(np.expand_dims(data, axis=0))
        mira_data_cube = np.concatenate(datasets, axis=0)
        return mira_data_cube

    def read_dataset_with_attributes(self, dataset_path):

        with h5py.File(self.filename, 'r') as file:
            if dataset_path in file:
                dataset = file[dataset_path]
                data = np.array(dataset, dtype=np.float32)
                attrs = {attr: dataset.attrs[attr] for attr in dataset.attrs}
                return data, attrs
            else:
                print(f"Dataset {dataset_path} not found in file.")
                return None, None

    def read_metadata(self, metadata_path='Metadata'):

        metadata = {}
        with h5py.File(self.filename, 'r') as file:
            if metadata_path in file:
                metadata_group = file[metadata_path]
                for name in metadata_group:
                    item = metadata_group[name]
                    if isinstance(item, h5py.Group) or isinstance(item, h5py.Dataset):
                        metadata[name] = {attr: item.attrs[attr] for attr in item.attrs}
        return metadata

    def unpickle_metadata(self, metadata_path='Metadata/mira_radar_parameters/mira_radar_parameters'):

        with h5py.File(self.filename, 'r') as file:
            if metadata_path in file:
                item = file[metadata_path]
                radar_param_data = item[()].tobytes()
                radar_param = pickle.loads(radar_param_data)
                return radar_param
            else:
                print(f"Metadata path {metadata_path} not found in file.")
                return None
