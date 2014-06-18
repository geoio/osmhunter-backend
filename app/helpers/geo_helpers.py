import itertools
from math import cos,radians,sin,pow,asin,sqrt


def calculate_centroid(shape: list) -> dict:
    """Find the centroid of a shape
        :Parameters:
        - `shape` -a list of lat/lon dicts a
    """

    points = []
    for node in shape:
        points.append([node["lat"], node["lon"]])

    area = area_of_polygon(*zip(*points))
    result_x = 0
    result_y = 0
    N = len(points)
    points = itertools.cycle(points)
    x1, y1 = next(points)
    for i in range(N):
        x0, y0 = x1, y1
        x1, y1 = next(points)
        cross = (x0 * y1) - (x1 * y0)
        result_x += (x0 + x1) * cross
        result_y += (y0 + y1) * cross
    result_x /= (area * 6.0)
    result_y /= (area * 6.0)
    return {"lat": result_x, "lon": result_y}


def area_of_polygon(x, y):
    """Calculates the signed area of an arbitrary polygon given its verticies

    """
    area = 0.0
    for i in range(-1, len(x) - 1):
        area += x[i] * (y[i + 1] - y[i - 1])
    return area / 2.0


def geo_distance(lat1, long1, lat2, long2):
    """calculate distance between to geo points
        `lat1` - 1. Latitude
        `long1` - 1. Longitude
        `lat2` - 2. Latitude
        `long2` - 2. Longitude
    """
    radius = 6371 # radius of the earth in km, roughly https://en.wikipedia.org/wiki/Earth_radius

    # Lat,long are in degrees but we need radians
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    long1 = radians(long1)
    long2 = radians(long2)

    dlat = lat2-lat1
    dlon = long2-long1

    a = pow(sin(dlat/2),2) + cos(lat1)*cos(lat2)*pow(sin(dlon/2),2)
    distance = 2 * radius * asin(sqrt(a))

    return distance