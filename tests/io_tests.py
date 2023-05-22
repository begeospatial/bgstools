import unittest
import yaml
from collections import OrderedDict
from bgstools.io import load_yaml, get_available_services
from bgstools.utils import script_as_module


class TestFunctions(unittest.TestCase):

    def test_load_yaml(self):
        valid_yaml_path = "/path/to/valid/yaml"
        invalid_yaml_path = "/path/to/invalid/yaml"
        nonexistent_path = "/nonexistent/path"

        # Test valid case
        self.assertIsInstance(load_yaml(valid_yaml_path), dict)

        # Test invalid case
        with self.assertRaises(yaml.YAMLError):
            load_yaml(invalid_yaml_path)

        # Test nonexistent file
        with self.assertRaises(FileNotFoundError):
            load_yaml(nonexistent_path)

    def test_get_available_services(self):
        valid_services_path = "/path/to/valid/services"
        nonexistent_path = "/nonexistent/path"

        # Test valid case
        self.assertIsInstance(get_available_services(valid_services_path), OrderedDict)

        # Test nonexistent file
        with self.assertRaises(FileNotFoundError):
            get_available_services(nonexistent_path)

    def test_script_as_module(self):
        valid_module_path = "/path/to/valid/module"
        valid_services_path = "/path/to/valid/services"
        nonexistent_path = "/nonexistent/path"

        # Test valid case
        self.assertTrue(script_as_module(valid_module_path, valid_services_path))

        # Test invalid module path
        with self.assertRaises(FileNotFoundError):
            script_as_module(nonexistent_path, valid_services_path)

        # Test invalid services path
        with self.assertRaises(NotADirectoryError):
            script_as_module(valid_module_path, nonexistent_path)

if __name__ == "__main__":
    unittest.main()
