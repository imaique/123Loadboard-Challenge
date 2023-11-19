import geopy.distance
from filters import CORRECTION_FACTOR


def get_miles(l1: (float, float), l2: (float, float)) -> float:
    return (
        CORRECTION_FACTOR
        * geopy.distance.geodesic(
            l1,
            l2,
        ).miles
    )
