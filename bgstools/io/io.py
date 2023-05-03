import os
import yaml


def load_yaml(filepath: str) -> dict:
    """Load a YAML file from a given file path and return a dictionary object containing the parsed data.

    Parameters:
    filepath (str): The file path to the YAML file to be loaded.

    Returns:
    dict: A dictionary object containing the parsed data.

    Raises:
    IOError: If the file path does not exist or if there is an error loading the file.
    """
    if not os.path.isfile(filepath):
        raise IOError(f"`filepath` does not exist = `{filepath}`")

    try:
        with open(filepath, 'r') as file_descriptor:
            yaml_data = yaml.safe_load(file_descriptor)
    except Exception as e:
        raise IOError(f"Error loading file `{filepath}`: {str(e)}")

    return yaml_data