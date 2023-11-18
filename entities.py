from __future__ import annotations
import geopy.distance
from datetime import datetime

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


class Truck:
    def __init__(self, truck_dict: dict) -> None:
        self.seq = truck_dict["seq"]
        self.type = truck_dict["type"]
        self.timestamp = datetime.strptime(truck_dict["timestamp"], DATE_FORMAT)
        self.truck_id = truck_dict["truckId"]
        self.position_latitude = truck_dict["positionLatitude"]
        self.position_longitude = truck_dict["positionLongitude"]
        self.equip_type = truck_dict["equipType"]
        self.next_trip_length_preference = truck_dict["nextTripLengthPreference"]
        self.minimum_wage = 15

    def matching_equipment(self, load: Load) -> bool:
        return self.equip_type == load.equipment_type

    def matching_distance(self, mileage: float) -> bool:
        if self.next_trip_length_preference == "Long" and mileage >= 200:
            return True
        elif self.next_trip_length_preference == "Short" and mileage < 200:
            return True
        return False

    def pickup_distance(self, load: Load) -> float:
        return geopy.distance.geodesic(
            (self.position_latitude, self.position_longitude),
            (load.origin_latitude, load.origin_longitude),
        ).miles

    # Each truck could have their own fuel efficiency which might greatly impact
    # how good a long-distance package is
    def calculate_profit(self, price: float, mileage: float) -> float:
        FUEL_COST_PER_MILE = 1.38
        return price - mileage * FUEL_COST_PER_MILE

    def get_hourly_wage(self, profit: float, mileage: float) -> float:
        AVERAGE_SPEED = 65
        return profit / (mileage / AVERAGE_SPEED)

    def above_desired_wage(self, wage: float) -> bool:
        return wage >= self.minimum_wage


class Load:
    def __init__(self, load_dict: dict) -> None:
        self.seq = load_dict["seq"]
        self.type = load_dict["type"]
        self.timestamp = datetime.strptime(load_dict["timestamp"], DATE_FORMAT)
        self.load_id = load_dict["loadId"]
        self.origin_latitude = load_dict["originLatitude"]
        self.origin_longitude = load_dict["originLongitude"]
        self.destination_latitude = load_dict["destinationLatitude"]
        self.destination_longitude = load_dict["destinationLongitude"]
        self.equipment_type = load_dict["equipmentType"]
        self.price = load_dict["price"]
        self.mileage = load_dict["mileage"]


class Notification:
    def __init__(
        self, truck: Truck, load: Load, profit: float, distance: float, wage: float
    ) -> None:
        # TODO: Update this value to lastest timestamp?
        self.timestamp = max(truck.timestamp, load.timestamp)
        self.load = load
        self.truck = truck
        self.price = load.price
        self.estimated_profit = profit
        self.estimated_distance = distance
        self.estimated_wage = wage
