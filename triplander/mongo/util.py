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


def get_distance(coord_1, coord_2, distance_fmt="km"):
    """
    Calculates the distance between two coordinates.
    """
    if distance_fmt == "km":
        radius = 6374.0
    elif distance_fmt == "mt":
        radius = 6374000.0
    elif distance_fmt == "miles":
        radius = 3959.0
        
    lat_1, lng_1 = coord_1
    lat_2, lng_2 = coord_2
    degrees_to_radians = math.pi / 180.0
    phi1 = (90.0 - lat_1) * degrees_to_radians
    phi2 = (90.0 - lat_2) * degrees_to_radians
    
    theta1 = lng_1 * degrees_to_radians
    theta2 = lng_2 * degrees_to_radians
    
    cos = (math.sin(phi1) * math.sin(phi2) * math.cos(theta1 - theta2) +
           math.cos(phi1) * math.cos(phi2))
    distance = math.acos(cos) * radius

    return distance
