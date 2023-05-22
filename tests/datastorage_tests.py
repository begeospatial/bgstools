import unittest
import os
import yaml
from unittest.mock import patch, mock_open
from tempfile import TemporaryDirectory
from bgstools.datastorage import DataStore, YamlStorage, StorageStrategy


class TestStorageStrategy(unittest.TestCase):
    def setUp(self):
        self.storage_strategy = StorageStrategy()

    def test_store_data(self):
        data = {"test_key": "test_value"}
        self.storage_strategy.store_data(data)
        self.assertEqual(self.storage_strategy.data, data)

    def test_load_data(self):
        self.storage_strategy.load_data()
        self.assertEqual(self.storage_strategy.data, {})

    def test_update_data(self):
        data = {"test_key": "test_value"}
        self.storage_strategy.store_data(data)
        self.storage_strategy.update_data(lambda x: {"new_key": "new_value"})
        self.assertEqual(self.storage_strategy.data, {"new_key": "new_value"})

    def test_delete_data(self):
        data = {"test_key": "test_value"}
        self.storage_strategy.store_data(data)
        self.storage_strategy.delete_data()
        self.assertEqual(self.storage_strategy.data, {})


class TestYamlStorage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.file_path = os.path.join(self.temp_dir.name, "temp.yaml")
        self.yaml_storage = YamlStorage(self.file_path)

    def test_store_data(self):
        data = {"test_key": "test_value"}
        self.yaml_storage.store_data(data)
        with open(self.file_path, 'r') as f:
            loaded_data = yaml.safe_load(f)
        self.assertEqual(loaded_data, data)

    def test_load_data(self):
        data = {"test_key": "test_value"}
        with open(self.file_path, 'w') as f:
            yaml.safe_dump(data, f)
        self.yaml_storage.load_data()
        self.assertEqual(self.yaml_storage.data, data)

    def test_update_data(self):
        data = {"test_key": "test_value"}
        self.yaml_storage.store_data(data)
        self.yaml_storage.update_data(lambda x: {"new_key": "new_value"})
        with open(self.file_path, 'r') as f:
            loaded_data = yaml.safe_load(f)
        self.assertEqual(loaded_data, {"new_key": "new_value"})

    def test_delete_data(self):
        data = {"test_key": "test_value"}
        self.yaml_storage.store_data(data)
        self.yaml_storage.delete_data()
        self.assertFalse(os.path.exists(self.file_path))

    def tearDown(self):
        self.temp_dir.cleanup()


class TestDataStore(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.file_path = os.path.join(self.temp_dir.name, "temp.yaml")
        self.storage_strategy = YamlStorage(self.file_path)
        self.data_store = DataStore(self.storage_strategy)

    def test_store_data(self):
        data = {"test_key": "test_value"}
        self.data_store.store_data(data)
        self.assertEqual(self.data_store.load_data(), data)

    def test_load_data(self):
        data = {"test_key": "test_value"}
        self.data_store.store_data(data)
        self.assertEqual(self.data_store.load_data(), data)

    def test_update_data(self):
        data = {"test_key": "test_value"}
        self.data_store.store_data(data)
        self.data_store.update_data(lambda x: {"new_key": "new_value"})
        self.assertEqual(self.data_store.load_data(), {"new_key": "new_value"})

    def test_delete_data(self):
        data = {"test_key": "test_value"}
        self.data_store.store_data(data)
        self.data_store.delete_data()
        self.assertEqual(self.data_store.load_data(), {})

    def tearDown(self):
        self.temp_dir.cleanup()


if __name__ == '__main__':
    unittest.main()
