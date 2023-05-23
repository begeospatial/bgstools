import os
import yaml
from collections import OrderedDict
import requests


def load_yaml(filepath: str) -> dict:
    """
    Loads a YAML file.

    Can be used as stand-alone script by providing a command-line argument:
        python load_yaml.py --filepath /file/path/to/filename.yaml

    Args:
        filepath (str): The absolute path to the YAML file.

    Returns:
        dict: The contents of the YAML file as a dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        yaml.YAMLError: If there is an error while loading the YAML file.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"No such file or directory: '{filepath}'")

    with open(filepath, 'r') as file_descriptor:
        try:
            yaml_data = yaml.safe_load(file_descriptor)
        except yaml.YAMLError as msg:
            raise yaml.YAMLError(f'File `{filepath}` loading error. \n {msg}')
        else:
            return yaml_data

def get_available_services(services_filepath: str) -> OrderedDict:
    """
    Retrieves available services from a yaml file. These services can be used to
    create a multi-page app using Streamlit. 

    Args:
        services_filepath (str): The absolute path to the yaml file containing the services.

    Returns:
        OrderedDict: An ordered dictionary of services if any are available. 
                     The dictionary is ordered based on the order of services in the yaml file.
                     Each key-value pair corresponds to a service name and its associated information.
                     Returns None if the yaml file does not contain any services.
    Raises:
        FileNotFoundError: If the services_filepath does not exist.
    """
    if not os.path.isfile(services_filepath):
        raise FileNotFoundError(f"No such file or directory: '{services_filepath}'")

    available_services = load_yaml(filepath=os.path.abspath(services_filepath))

    if available_services:
        services_dict = OrderedDict({service['name']: service for service in available_services})
        return services_dict

    return None


def path_exists(path):
    """
    Checks if a given path exists, whether it's a local file, remote URL, or LAN path.

    Args:
        path (str): The path to check.

    Returns:
        bool: True if the path exists, False otherwise.
    """
    if is_remote_url(path):
        return check_remote_path_exists(path)
    elif is_lan_path(path):
        return check_lan_path_exists(path)
    else:
        return check_local_path_exists(path)


def is_remote_url(path):
    """
    Checks if the given path is a remote URL.

    Args:
        path (str): The path to check.

    Returns:
        bool: True if the path is a remote URL, False otherwise.
    """
    return path.startswith('http://') or path.startswith('https://')


def is_lan_path(path):
    """
    Checks if the given path is a LAN path.

    Args:
        path (str): The path to check.

    Returns:
        bool: True if the path is a LAN path, False otherwise.
    """
    return path.startswith('\\\\')


def check_remote_path_exists(url):
    """
    Checks if the given remote URL exists.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL exists, False otherwise.
    """
    try:
        response = requests.head(url)
        return response.status_code == requests.codes.ok
    except requests.exceptions.RequestException:
        return False


def check_lan_path_exists(path):
    """
    Checks if the given LAN path exists.

    Args:
        path (str): The path to check.

    Returns:
        bool: True if the path exists, False otherwise.
    """
    return os.path.exists(path)


def check_local_path_exists(path):
    """
    Checks if the given local path exists.

    Args:
        path (str): The path to check.

    Returns:
        bool: True if the path exists, False otherwise.
    """
    return os.path.exists(path)
