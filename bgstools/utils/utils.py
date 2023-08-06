import os
import sys
from importlib.util import spec_from_file_location, module_from_spec
import datetime


def find_value_in_dict(data:dict, search_value:str, nested_path:list=[])->list:
    """
    This function recursively searches a nested dictionary (traverse) for a given value or key
    and returns all paths of keys to the value or key.
    
    Parameters:
    data (dict): The dictionary to search.
    search_value: The value or key to search for.
    nested_path (list, optional): The current path of keys. Defaults to an empty list.
    
    Returns:
    list: A list of paths of keys to the value or key.
    """
    paths = []
    if isinstance(data, dict):
        for k, v in data.items():
            new_path = nested_path + [k]
            if k == search_value:
                paths.append(new_path)
            paths += find_value_in_dict(v, search_value, new_path)
    elif isinstance(data, list):
        for i, v in enumerate(data):
            new_path = nested_path + [i]
            paths += find_value_in_dict(v, search_value, new_path)
    elif data == search_value:
        paths.append(nested_path)
    return paths



def get_dynamic_nested_key_value(data:dict, keys_list:list)->dict:
    """
    This function retrieves the value of a nested key in a dictionary,
    where one of the keys in the path is unknown and needs to be looked up dynamically.
    
    Parameters:
    data (dict): The dictionary to search.
    keys_list (list): The list of keys that represents the path to the nested key.
    
    Returns:
    dict or None: The value of the nested key if it exists and is not empty, None otherwise.

    Usage:
        Return a dictionary nested just after the unknown key, or None if no such dictionary exists.

        `frames = get_dynamic_nested_key_value(data, ['APP', 'SURVEYS', None, 'FRAMES'])
    """
    for key in keys_list:
        if key is None:
            for k, v in data.items():
                if isinstance(v, dict):
                    return v
            return None
        try:
            data = data[key]
        except (KeyError, TypeError):
            return None
    return data if data else None


def get_nested_dict_value(data_dict, keys_list, default=None):
    """
    This function retrieves a value from a nested dictionary using a list of keys. 
    If a KeyError is encountered at any level, the function will return a default value.

    Args:
        data_dict (dict): The dictionary from which to retrieve the value.
        keys_list (list): A list of keys, ordered by their level in the dictionary.
        default (any, optional): The default value to return if any key in keys_list is not found. 
            Defaults to None.

    Returns:
        The value at the nested key if it exists, otherwise the default value.
    """
    try:
        for key in keys_list:
            data_dict = data_dict.get(key, None)
        return data_dict
    except KeyError:
        return default



def str_as_dtype(datatype: str, callback: callable = None):
    """
    Converts a string representation of a data type to the corresponding Python data type.

    Args:
        datatype (str): The string representation of the data type.
        callback (callable, optional): A callback function to handle exceptions.

    Returns:
        The corresponding Python data type if `datatype` is a valid type, otherwise None.
        The exception is `datetime` which is returned as a string.

    Raises:
        TypeError: If `datatype` is not a string.
        ValueError: If `datatype` is not a recognized data type.

    Example:
        str_as_dtype('int')  # returns <class 'int'>
        str_as_dtype('bool')  # returns <class 'bool'>
    """
    try:
        if not isinstance(datatype, str):
            raise TypeError("Input 'datatype' must be a string.")

        if datatype == 'str':
            return str
        elif datatype == 'int':
            return int
        elif datatype == 'float':
            return float
        elif datatype == 'bool':
            return bool
        elif datatype == 'datetime':
            return datetime
        else:
            raise ValueError(f"Unrecognized data type: '{datatype}'")

    except Exception as e:
        if callback is not None and callable(callback):
            exception_message = f"**`str_as_dtype` exception occurred:** {e}"
            callback(exception_message)
        else:
            raise


def colnames_dtype_mapping(colnames_dtype_dict: dict | list)-> dict:
    """
    Maps column names to their corresponding data types based on the provided dictionary.

    Args:
        colnames_dtype_dict (dict): A dictionary mapping column names to their data types.

    Returns:
        A new dictionary where keys are column names and values are the corresponding data types.

    Raises:
        TypeError: If `colnames_dtype_dict` is not a dictionary.
        ValueError: If `colnames_dtype_dict` is empty or contains invalid data types.

    Example:
        colnames_dtype_mapping({'col1': 'int', 'col2': 'str', 'col3': 'float'})
        # returns {'col1': <class 'int'>, 'col2': <class 'str'>, 'col3': <class 'float'>}
    """
    _colnames_dtype_dict = colnames_dtype_dict
    try:
        if isinstance(colnames_dtype_dict, list):
            for item in colnames_dtype_dict:
                _colnames_dtype_dict = {item['colname']: item['dtype'] for item in colnames_dtype_dict}

        if not isinstance(_colnames_dtype_dict, dict):
            raise TypeError("Input 'colnames_dtype_dict' must be a dictionary.")

        if not _colnames_dtype_dict:
            raise ValueError("Input 'colnames_dtype_dict' cannot be empty.")

        mapping = {}
        for colname, dtype in _colnames_dtype_dict.items():
            mapping[colname] = str_as_dtype(dtype)

        return mapping

    except (TypeError, ValueError) as e:
        # Handle the exception or re-raise it
        raise e



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

