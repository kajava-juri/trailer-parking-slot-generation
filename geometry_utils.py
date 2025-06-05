import math

R = 6371e3  # earth radius in meters

# Converts from degrees to radians.

def toRadians(degrees):
    return degrees * math.pi / 180

# Converts from radians to degrees.

def toDegrees(radians):
    return radians * 180 / math.pi

def bearing(startLat, startLng, destLat, destLng):
    """Calculate the initial bearing between two points in degrees."""
    startLat = toRadians(startLat)
    startLng = toRadians(startLng)
    destLat = toRadians(destLat)
    destLng = toRadians(destLng)

    y = math.sin(destLng - startLng) * math.cos(destLat)
    x = (
        math.cos(startLat) * math.sin(destLat)
        - math.sin(startLat) * math.cos(destLat) * math.cos(destLng - startLng)
    )
    brng = math.atan2(y, x)
    brng = toDegrees(brng)
    return (brng + 360) % 360

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points on Earth in kilometers."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

def get_point_at_distance(lat1, lon1, d, bearing, reverse=False, R=6371):
    """Return new lat/lon coordinate `d` km from the initial point."""
    lat1 = toRadians(lat1)
    lon1 = toRadians(lon1)
    bearing = toRadians(bearing)
    if reverse:
        bearing += math.pi
    lat2 = math.asin(math.sin(lat1) * math.cos(d / R) + math.cos(lat1) * math.sin(d / R) * math.cos(bearing))
    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(d / R) * math.cos(lat1),
        math.cos(d / R) - math.sin(lat1) * math.sin(lat2),
    )
    return (toDegrees(lat2), toDegrees(lon2))

