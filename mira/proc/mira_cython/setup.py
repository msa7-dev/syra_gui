# $ python3 ./setup.py build_ext --inplace
import os
import shutil
import numpy as np
from pathlib import Path
from Cython.Build import cythonize
from setuptools import setup, Extension

cython_extraction_file = "mira6024_extract_from_raw_data"

# Convert the np.get_include() path to a string
numpy_include_path = str(Path(np.get_include()).resolve())

ext_modules = [
    Extension(
        cython_extraction_file,  # name of the module
        [f"{cython_extraction_file}.pyx"],  # list of source files
        include_dirs=[numpy_include_path]  # Convert to string here
    )
]

setup(
    name="mira6024_extract_from_raw_data",
    ext_modules=cythonize(ext_modules, compiler_directives={'language_level': '3'}),
    include_dirs=[numpy_include_path],  # Convert to string here
    zip_safe=False,
)

# Path to the directory you want to delete
folder_path = str(Path("./build").resolve())  # Convert to string here

# Remove the directory
if os.path.exists(folder_path):
    shutil.rmtree(folder_path)
else:
    print(f"The folder {folder_path} does not exist.")

# Check if the file exists and then remove it
c_file_path = f"{cython_extraction_file}.c"
if os.path.exists(c_file_path):
    os.remove(c_file_path)
else:
    print(f"The file {c_file_path} does not exist.")
