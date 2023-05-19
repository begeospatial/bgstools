import os
import pytest
from bgstools.io import load_yaml
from bgstools.utils import create_subdirectory
from bgstools.spatial import get_h3_geohash, reproject_coordinates, get_h3_geohash_epsg3006, get_coordinates_epsg3006_from_geohash


# ------------------------------------------------------------
# IO
# ------------------------------------------------------------

def test_load_yaml():
    # Test valid YAML file
    expected_output = {'name': 'Alice', 'age': 30, 'city': 'New York'}
    assert load_yaml('test.yaml') == expected_output

    # Test invalid YAML file
    assert load_yaml('invalid.yaml') is None

    # Test missing file
    assert load_yaml('missing.yaml') is None

    # Test directory instead of file
    with pytest.raises(IOError, match=r'.*is not a file.*'):
        load_yaml('dir')

    # Test file without read permission
    with open('test.yaml', 'r') as f:
        os.chmod('test.yaml', 0o200)
        with pytest.raises(IOError, match=r'.*Permission denied.*'):
            load_yaml('test.yaml')
        os.chmod('test.yaml', 0o600)  # Reset permissions


# ------------------------------------------------------------
# UTILS
# ------------------------------------------------------------

def test_create_subdirectory(tmpdir):
    # Test creating a new subdirectory
    subdir = 'test'
    path = str(tmpdir)
    full_path = os.path.join(path, subdir)
    assert create_subdirectory(path, subdir) == full_path
    assert os.path.isdir(full_path)

    # Test creating an existing subdirectory
    assert create_subdirectory(path, subdir) == full_path

    # Test creating a subdirectory with invalid characters
    invalid_subdir = 'invalid<>dir'
    assert create_subdirectory(path, invalid_subdir) is None
    assert not os.path.exists(os.path.join(path, invalid_subdir))

    # Test creating a subdirectory with invalid path
    invalid_path = os.path.join(path, 'invalid', 'dir')
    assert create_subdirectory(invalid_path, subdir) is None
    assert not os.path.exists(os.path.join(invalid_path, subdir))


# ------------------------------------------------------------
# SPATIAL
# ------------------------------------------------------------

def test_get_h3_geohash():
    # Test with known coordinates
    lat = 51.5074
    lon = -0.1278
    assert get_h3_geohash(lat, lon) == '891c00000000000'

def test_reproject_coordinates():
    # Test with known coordinates
    x = 177308
    y = 6582278
    assert reproject_coordinates(x, y, inProj='epsg:3006', outProj='epsg:4326') == (-0.11676966121944642, 51.52165656202548)

def test_get_h3_geohash_epsg3006():
    # Test with known coordinates
    x = 177308
    y = 6582278
    assert get_h3_geohash_epsg3006(x, y) == '891c00000000000'

def test_get_coordinates_epsg3006_from_geohash():
    # Test with known H3 geohash
    h3_geohash = '891c00000000000'
    assert get_coordinates_epsg3006_from_geohash(h3_geohash) == (177307.8097919605, 6582278.142429417)
    assert get_coordinates_epsg3006_from_geohash('u2yj8qx') == (658888.4528398266, 6589409.871393275)
    assert get_coordinates_epsg3006_from_geohash('u2yj8qx', 'epsg:4326') == (55.68382579254553, 12.56616944464342)
    assert get_coordinates_epsg3006_from_geohash('9q9v6h5j') == (535423.8084271612, 6162047.729307233)
    assert get_coordinates_epsg3006_from_geohash('9q9v6h5j', 'epsg:4326') == (55.61348405346341, 12.294719162887248)

