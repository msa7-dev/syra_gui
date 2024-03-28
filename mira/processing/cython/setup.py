import os
import glob
import shutil
import numpy as np
from loguru import logger
from pathlib import Path
from Cython.Build import cythonize
from setuptools import setup, Extension

# Specify the module name without file extension
module_name = "mira_extract_raw_data"

# Path to the Cython file
cython_file = f"./mira/processing/cython/{module_name}.pyx"
output_dir = "./mira/processing/cython/"  
# Convert the np.get_include() path to a string
numpy_include_path = str(Path(np.get_include()).resolve())

ext_modules = [
    Extension(
        module_name,  # name of the module
        [cython_file],  # list of source files
        include_dirs=[numpy_include_path],
    )
]

setup(
    name="mira_extract_raw_data",
    ext_modules=cythonize(ext_modules, compiler_directives={'language_level': '3'}),
    include_dirs=[numpy_include_path],  # Convert to string here
    zip_safe=False,
)
# Search for files matching the pattern
files_to_move = glob.glob("./mira_extract_raw_data.*")

# Move each found file to the desired directory
for file_to_move in files_to_move:
    destination_path = "./mira/processing/cython"
    file_name = os.path.basename(file_to_move)
    destination_file_path = os.path.join(destination_path, file_name)
    
    # Remove the existing file if it already exists
    if os.path.exists(destination_file_path):
        os.remove(destination_file_path)
        
    # Move the file to the destination directory
    shutil.move(file_to_move, destination_path)
    
# Path to the directory you want to delete
folder_path = str(Path("./build").resolve())

# Remove the directory
if os.path.exists(folder_path):
    shutil.rmtree(folder_path)
else:
    print(f"The folder {folder_path} does not exist.")

# Check if the file exists and then remove it
c_file_path = f"{output_dir}/{module_name}.c"
if os.path.exists(c_file_path):
    os.remove(c_file_path)
else:
    print(f"The file {c_file_path} does not exist.")
    
logger.debug(f'Compiled cython module {files_to_move[0]} moved to {output_dir}')
