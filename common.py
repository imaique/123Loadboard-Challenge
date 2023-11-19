import geopy.distance
from filters import CORRECTION_FACTOR

MIN_LONGITUDE = -125
MAX_LONGITUDE = -70
MIN_LATITUDE = 20
MAX_LATITUDE = 50


def get_miles(l1: (float, float), l2: (float, float)) -> float:
    return (
        CORRECTION_FACTOR
        * geopy.distance.geodesic(
            l1,
            l2,
        ).miles
    )
