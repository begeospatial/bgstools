import os
import sys
from importlib.util import spec_from_file_location, module_from_spec


def script_as_module(module_filepath: str, services_dirpath: str) -> bool:
    """
    Loads a Python script as a module, registers it, and makes it available for the package path.
    This function is particularly useful for populating services in a Streamlit app.

    Args:
        module_filepath (str): The file path to the Python script that needs to be loaded as a module.
        services_dirpath (str): The directory path where the service resides.

    Returns:
        bool: True if the module was loaded successfully; otherwise, False.

    Raises:
        TypeError: If module_filepath or services_dirpath are not strings.
        NotADirectoryError: If services_dirpath is not a directory.
        FileNotFoundError: If module_filepath does not exist.
    """
    if not isinstance(services_dirpath, str):
        raise TypeError(f"`services_dirpath` must be a string, not {type(services_dirpath).__name__}")
    if not isinstance(module_filepath, str):
        raise TypeError(f"`module_filepath` must be a string, not {type(module_filepath).__name__}")
    if not os.path.isdir(services_dirpath):
        raise NotADirectoryError(f"No such directory: '{services_dirpath}'")

    abs_module_filepath = os.path.join(services_dirpath, module_filepath)

    if not os.path.isfile(abs_module_filepath):
        raise FileNotFoundError(f"No such file: '{abs_module_filepath}'")

    module_name = os.path.basename(abs_module_filepath).replace('.py', '')

    spec = spec_from_file_location(name=module_name, location=abs_module_filepath, submodule_search_locations=[services_dirpath])

    if spec:
        try:
            module = module_from_spec(spec)
            spec.loader.exec_module(module)
            sys.modules[module_name] = module
            return True
        except Exception as e:
            print(f"Failed to load module {module_name}: {e}")
            return False

    return False


def create_subdirectory(path: str, subdir: str) -> str:
    """Create a new subdirectory within a specified parent directory if it does not already exist.

    Args:
        path (str): The path to the parent directory.
        subdir (str): The name of the subdirectory to create.

    Returns:
        str: The full path to the subdirectory.

    Raises:
        OSError: If an error occurs while creating the subdirectory.
    """

    # Create the full path to the subdirectory
    full_path = os.path.join(path, subdir)

    # Check if the subdirectory exists
    if os.path.isdir(full_path):
        print(f'Subdirectory {full_path} already exists')
    else:
        # Create the subdirectory if it does not exist
        try:
            os.mkdir(full_path)
            print(f'Subdirectory {full_path} created')
        except OSError as e:
            raise OSError(f'Error occurred while creating subdirectory: {e.strerror}')

    return full_path

