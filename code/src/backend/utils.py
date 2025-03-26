import os

def list_files_in_dir(directory):
    """Returns a list of file paths in a given directory."""
    if not os.path.exists(directory):
        return []
    return [os.path.join(directory, file) for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file))]