import h3
from pyproj import Proj, transform


def get_h3_geohash(decimalLatitude:float, decimalLongitude:float, resolution:int=12) -> str:
    """Get the H3 geohash for a given latitude and longitude at a specified resolution.

    Args:
        decimalLatitude (float): The latitude in decimal degrees.
        decimalLongitude (float): The longitude in decimal degrees.
        resolution (int, optional): The resolution of the H3 geohash. Defaults to 12.

    Returns:
        str: The H3 geohash.

    """
    return h3.geo_to_h3(decimalLatitude, decimalLongitude, resolution)


def reproject_coordinates(x_or_longitude:float, y_or_latitude:float, inProj:str='epsg:4326', outProj:str='epsg:3006') -> tuple:
    """Reproject coordinates from one projection system to another.

    Args:
        x_or_longitude (float): The x-coordinate or longitude.
        y_or_latitude (float): The y-coordinate or latitude.
        inProj (str, optional): The input projection system as an EPSG string. Defaults to 'epsg:4326'.
        outProj (str, optional): The output projection system as an EPSG string. Defaults to 'epsg:3006'.

    Returns:
        tuple: The reprojected coordinates as a tuple containing x and y.

    """
    in_proj = Proj(init=inProj)
    out_proj = Proj(init=outProj)

    # Convert coordinates
    x, y = transform(in_proj, out_proj, x_or_longitude, y_or_latitude)
    return x, y


def get_h3_geohash_epsg3006(x:float, y:float, resolution:int=12) -> str:
    """Get the H3 geohash for a given x and y coordinate in the SWEREF99TM projection system.

    Args:
        x (float): The x-coordinate in SWEREF99TM.
        y (float): The y-coordinate in SWEREF99TM.
        resolution (int, optional): The resolution of the H3 geohash. Defaults to 12.

    Returns:
        str: The H3 geohash.

    """
    decimal_longitude, decimal_latitude = reproject_coordinates(x, y, inProj='epsg:3006', outProj='epsg:4326')
    return get_h3_geohash(decimal_latitude, decimal_longitude, resolution)


def get_coordinates_epsg3006_from_geohash(geohash:str, outProj:str='epsg:3006') -> tuple:
    """Convert a H3 geohash to SWEREF99TM coordinates.

    Args:
        geohash (str): The H3 geohash.
        outProj (str, optional): The output projection system as an EPSG string. Defaults to 'epsg:3006'.

    Returns:
        tuple: The SWEREF99TM coordinates as a tuple containing x and y.

    """
    # Get the coordinates from the H3 geohash
    latitude, longitude = h3.h3_to_geo(geohash)
    in_proj = Proj(init='epsg:4326')
    # Convert coordinates to SWEREF99TM
    x, y = transform(in_proj, outProj, longitude, latitude)
    return x, y
