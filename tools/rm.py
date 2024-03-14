import os
import shutil

def remove_pycache(path, exclude_folder):
    for root, dirs, files in os.walk(path):
        if exclude_folder in dirs:
            dirs.remove(exclude_folder)  # Exclude the folder from further traversal
        for d in dirs:
            if d == '__pycache__':
                pycache_path = os.path.join(root, d)
                print("Removing:", pycache_path)
                shutil.rmtree(pycache_path)

# Usage
remove_pycache('./', 'sykno_env')
