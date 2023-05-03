import os


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

