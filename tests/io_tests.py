import unittest
import yaml
from collections import OrderedDict
from bgstools.utils import script_as_module
from bgstools.io import load_yaml, get_available_services, path_exists, is_remote_url, is_lan_path, check_remote_path_exists, check_lan_path_exists, check_local_path_exists



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



class PathExistsTests(unittest.TestCase):
    def test_check_local_path_exists(self):
        # Create a temporary file for testing
        with open('test_file.txt', 'w') as f:
            f.write('Test')

        self.assertTrue(check_local_path_exists('test_file.txt'))
        self.assertFalse(check_local_path_exists('non_existent_file.txt'))

        # Clean up the temporary file
        os.remove('test_file.txt')

    def test_check_remote_path_exists(self):
        # Patch the requests.head() method to return a mock response
        def mock_head(url):
            response = requests.Response()
            if url == 'http://example.com/existent_file.txt':
                response.status_code = requests.codes.ok
            else:
                response.status_code = 404
            return response

        with patch('requests.head', side_effect=mock_head):
            self.assertTrue(check_remote_path_exists('http://example.com/existent_file.txt'))
            self.assertFalse(check_remote_path_exists('http://example.com/non_existent_file.txt'))

    def test_is_remote_url(self):
        self.assertTrue(is_remote_url('http://example.com/file.txt'))
        self.assertTrue(is_remote_url('https://example.com/file.txt'))
        self.assertFalse(is_remote_url('file.txt'))

    def test_check_lan_path_exists(self):
        # Create a temporary file for testing
        with open('test_lan_file.txt', 'w') as f:
            f.write('Test')

        self.assertTrue(check_lan_path_exists('\\\\server\\shared_folder\\test_lan_file.txt'))
        self.assertFalse(check_lan_path_exists('\\\\server\\shared_folder\\non_existent_file.txt'))

        # Clean up the temporary file
        os.remove('test_lan_file.txt')

    def test_is_lan_path(self):
        self.assertTrue(is_lan_path('\\\\server\\shared_folder\\file.txt'))
        self.assertFalse(is_lan_path('file.txt'))

    @patch('os.path.exists', return_value=True)
    def test_path_exists_local(self, mock_exists):
        self.assertTrue(path_exists('file.txt'))
        mock_exists.assert_called_with('file.txt')

    @patch('requests.head')
    def test_path_exists_remote(self, mock_head):
        # Test with an existing remote URL
        response = requests.Response()
        response.status_code = requests.codes.ok
        mock_head.return_value = response
        self.assertTrue(path_exists('http://example.com/file.txt'))
        mock_head.assert_called_with('http://example.com/file.txt')

        # Test with a non-existent remote URL
        response.status_code = 404
        self.assertFalse(path_exists('http://example.com/non_existent_file.txt'))

    @patch('os.path.exists', return_value=True)
    def test_path_exists_lan(self, mock_exists):
        self.assertTrue(path_exists('\\\\server\\shared_folder\\file.txt'))
        mock_exists.assert_called_with('\\\\server\\shared_folder\\file.txt')


if __name__ == '__main__':
    unittest.main()

