"""
Miscellaneous functions for MongoDB side.
"""
import math


def get_bounding_box(latitude, longitude, distance, distance_fmt="km"):
    """
    Calculates a bounding box from latitude, longitude and given distance.
    """
    if distance_fmt == "km":
        half_side = distance
    elif distance_fmt == "mt":
        half_side = distance / 1000.0
    elif distance_fmt == "miles":
        half_side = distance / 1.609344

    lat = math.radians(latitude)
    lon = math.radians(longitude)

    radius = 6371.0
    # radius of the parallel at given latitude

    rad2deg = math.degrees

    lat_min = lat - half_side / radius
    lat_max = lat + half_side / radius
    lon_min = lon - half_side / radius / math.cos(lat)
    lon_max = lon + half_side / radius / math.cos(lat)

    return [[rad2deg(lat_min), rad2deg(lon_min)],
            [rad2deg(lat_max), rad2deg(lon_max)]]
