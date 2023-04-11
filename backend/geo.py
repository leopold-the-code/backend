import math
import random

mb_float = float | None


def calculate_distance(
    lat1: mb_float, lon1: mb_float, lat2: mb_float, lon2: mb_float
) -> mb_float:
    """
    Calculate distance in kilometers
    """
    if any(x is None for x in [lat1, lon1, lat2, lon2]):
        return None

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371

    # Calculate the distance
    distance = c * r
    return distance


def add_noise(distance: mb_float) -> mb_float:
    if distance is None:
        return None
    return round(distance + random.random() * 3, 1)


def calculate_with_noise(
    lat1: mb_float, lon1: mb_float, lat2: mb_float, lon2: mb_float
) -> mb_float:
    return add_noise(calculate_distance(lat1, lon1, lat2, lon2))
