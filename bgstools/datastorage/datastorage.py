import os
from typing import Dict, Callable
import yaml
from dataclasses import dataclass, field
import chardet


@dataclass
class StorageStrategy:
    """A base class for storage strategies that manage data.

    Attributes:
        data (Dict): A dictionary representing the data being managed by the storage strategy.
    """
    data: Dict = field(default_factory=dict)

    def store_data(self, data: Dict):
        """Stores the given data in the storage strategy.

        Args:
            data (Dict): The data to store in the storage strategy.
        """
        self.data = data

    def load_data(self):
        """Loads the data from the storage strategy into the `data` attribute."""
        pass

    def update_data(self, update_func: Callable):
        """Updates the data in the storage strategy using the given update function.

        Args:
            update_func (Callable): A function that takes the current data as input and returns the updated data.
        """
        self.data = update_func(self.data)

    def delete_data(self):
        """Deletes the data stored in the storage strategy."""
        self.data = {}


@dataclass
class YamlStorage(StorageStrategy):
    """A storage strategy that stores and retrieves data in a YAML file.

    Use:

    ```
    def update_func(data):
        data.append({'new_key': 'new_value'})
        return data

    data_store = DataStore(YamlStorage('/path/to/data.yaml'))

    data_store.update_data(update_func)

    loaded_data = data_store.load_data()
    print(loaded_data)
    ```

    Args:
        file_path (str): The path to the YAML file to store the data in.
    """

    file_path: str = field(default_factory=str)

    def __post_init__(self):
        """Checks if the YAML file exists and loads it if it does, otherwise initializes the `data` property to an empty dictionary."""
        if os.path.isfile(self.file_path):
            self.load_data()
        else:
            self.data = {}

    def store_data(self, data:Dict):
        """Stores the data in the YAML file."""
        
        with open(self.file_path, 'w') as f:
            yaml.safe_dump(self.data, f, encoding='utf-8')
            self.data = data

    def load_data(self):
        """Loads the data from the YAML file into the `data` attribute of the `StorageStrategy` class."""
        try:
            with open(self.file_path, 'rb') as f:
                yaml_bytes = f.read()

            # Use chardet to detect the encoding of the yaml file
            result = chardet.detect(yaml_bytes)
            encoding = 'utf-8' if result['encoding'] is None else result['encoding']
            yaml_str = yaml_bytes.decode(encoding=encoding)

            self.data = yaml.safe_load(yaml_str)
        except (FileNotFoundError, IOError):
            self.data = {}

    def update_data(self, update_func: Callable):
        """Updates the data in the YAML file using the given update function.

        Args:
            update_func (Callable): A function that takes the current data as input and returns the updated data.
        """
        #self.load_data()
        self.data = update_func(self.data)
        self.store_data(data=self.data)

    def delete_data(self):
        """Deletes the YAML file containing the data."""
        try:
            os.remove(self.file_path)
        except (FileNotFoundError, IOError):
            pass


@dataclass
class DataStore:
    """The DataStore class is responsible for managing the storage strategy used to store and retrieve data.

        Usage example:
        ```
        data_store = DataStore(YamlStorage('data.yaml'))
        data = {'key': 'value'}
        data_store.store_data(data)
        loaded_data = data_store.load_data()
        ````

    Attributes:
        storage_strategy (StorageStrategy): The storage strategy used to store and retrieve data.
    """
    storage_strategy: StorageStrategy

    def store_data(self, data:Dict):
        """Stores the given data using the current storage strategy.

        Args:
            data (Dict): The data to store.
        """
        self.storage_strategy.data = data
        self.storage_strategy.store_data(data=self.storage_strategy.data)

    def load_data(self) -> Dict:
        """Loads the data from the current storage strategy into the `data` attribute of the `StorageStrategy` class and returns it."""
        self.storage_strategy.load_data()
        return self.storage_strategy.data

    def update_data(self, update_func: Callable):
        """Updates the data using the current storage strategy and the given update function.

        Args:
            update_func (Callable): A function that takes the current data as input and returns the updated data.
        """
        self.storage_strategy.update_data(update_func)

    def delete_data(self):
        """Deletes the data stored by the current storage strategy."""
        self.storage_strategy.delete_data() 



def update_datastore(DATASTORE: DataStore, kwargs: Dict = None, callback: Callable = None) -> Dict:
    """Updates the data in the datastore using the given keyword arguments.

    Args:
        DATASTORE (DataStore): The datastore to update.
        kwargs (Dict, optional): The keyword arguments to update the datastore with.
        callback (Callable, optional): A function to call in case of an error.

    Returns:
        Dict: The updated data in the datastore.

    Raises:
        Exception: If there is an error while updating the datastore.
    """
    current_data = DATASTORE.storage_strategy.data

    if kwargs:
        current_data.update(kwargs)

    try:
        DATASTORE.store_data(data=current_data)
    except Exception as e:
        if callback:
            callback(f'Error updating datastore: {e}')
        raise Exception(f'Error updating datastore: {e}')
    
    return current_data


class Status:
    """
    Status class to store and access data from a DataStore object.

    Attributes:
        Any number of attributes specified by the keys parameter in the constructor.
    """

    def __init__(
        self, 
        data_store: DataStore, 
        keys: list
    ):
        """
        Initialize a new instance of the Status class.

        Args:
            data_store: A DataStore object that contains the data.
            keys (list): A list of keys to extract from the data store. Examples of default keys are: 
                         ['SURVEY_DATASTORE', 'SELECTED_SURVEY_FILEPATH', 'SELECTED_STATION',
                         'SELECTED_SURVEY', 'SELECTED_STATION_DIRPATH', 'SELECTED_VIDEO_FILEPATH'].
        """
        
        # Check if data_store has the required attribute
        if not hasattr(data_store, 'storage_strategy') or not hasattr(data_store.storage_strategy, 'data'):
            raise ValueError("The provided data store does not have a storage_strategy with a data attribute")

        # Check if keys is a list
        if not isinstance(keys, list):
            raise TypeError("Keys must be a list")

        # Set attributes from the data store
        for key in keys:
            setattr(self, key, data_store.storage_strategy.data.get(key, None))

    def get_attributes(self):
        """
        Get a dictionary of all attributes that are not None.

        Returns:
            A dictionary where the keys are the attribute names and the values are the attribute values.
        """
        return {key: getattr(self, key) for key in self.__dict__ if getattr(self, key) is not None}


class AttributeRemover:
    """
    AttributeRemover class to remove specified attributes from an object.

    Attributes:
        target_object: The object from which to remove attributes.

    Usage:
        ```
        class SomeClass:
            def __init__(self):
                self.attribute1 = "value1"
                self.attribute2 = "value2"
                self.attribute3 = "value3"

        obj = SomeClass()
        remover = AttributeRemover(obj)
        removed_keys = remover.remove_attributes(['attribute1', 'attribute2'])

        print(removed_keys)  # ['attribute1', 'attribute2']
        print(hasattr(obj, 'attribute1'))  # False
        print(hasattr(obj, 'attribute2'))  # False
        print(hasattr(obj, 'attribute3'))  # True
        ```
        In this example, the AttributeRemover successfully removes attribute1 and attribute2 from obj, 
        but attribute3 is still present.

    """

    def __init__(self, target_object):
        """
        Initialize a new instance of the AttributeRemover class.

        Args:
            target_object: The object from which to remove attributes.
        """
        
        self.target_object = target_object

    def remove_attributes(self, keys: list):
        """
        Remove specified attributes from the target object.

        Args:
            keys (list): A list of attribute names to remove.

        Returns:
            A list of attribute names that were successfully removed.
        """

        # Check if keys is a list
        if not isinstance(keys, list):
            raise TypeError("Keys must be a list")

        removed_keys = []
        for key in keys:
            if hasattr(self.target_object, key):
                delattr(self.target_object, key)
                removed_keys.append(key)

        return removed_keys
