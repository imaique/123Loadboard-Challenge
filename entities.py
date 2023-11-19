from __future__ import annotations
from datetime import datetime
from common import get_miles
from filters import FUEL_COST_PER_MILE, AVERAGE_SPEED, MINIMUM_DESIRED_HOURLY_WAGE

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
        self.minimum_wage = MINIMUM_DESIRED_HOURLY_WAGE
        self.fuel_cost_per_mile = FUEL_COST_PER_MILE
        self.average_speed = AVERAGE_SPEED

    def matching_equipment(self, load: Load) -> bool:
        return self.equip_type == load.equipment_type

    def desires_long(self) -> bool:
        return self.next_trip_length_preference == "Long"

    def matching_distance(self, mileage: float) -> bool:
        if self.next_trip_length_preference == "Long" and mileage >= 200:
            return True
        elif self.next_trip_length_preference == "Short" and mileage < 200:
            return True
        return False

    def same_location(self, truck: Truck) -> bool:
        return (
            truck.position_latitude == self.position_latitude
            and truck.position_longitude == self.position_longitude
        )

    def pickup_distance(self, load: Load) -> float:
        return get_miles(
            (self.position_latitude, self.position_longitude),
            (load.origin_latitude, load.origin_longitude),
        )

    def get_hourly_from_load(self, load: Load) -> float:
        distance = self.pickup_distance(load) + load.mileage
        profit = self.calculate_profit(load.price, distance)
        hourly = self.get_hourly_wage(profit, distance)
        return hourly

    def calculate_profit(self, price: float, mileage: float) -> float:
        return price - self.travel_cost(mileage)

    # Each truck could have their own fuel efficiency which might greatly impact
    # how good a long-distance package is
    def travel_cost(self, mileage: float) -> float:
        return mileage * FUEL_COST_PER_MILE

    def hourly_lost(self) -> float:
        return AVERAGE_SPEED * FUEL_COST_PER_MILE

    # hours
    def time_to_travel(self, mileage: float) -> float:
        return mileage / AVERAGE_SPEED

    def get_hourly_wage(self, profit: float, mileage: float) -> float:
        return profit / self.time_to_travel(mileage)

    def above_desired_wage(self, wage: float) -> bool:
        return wage >= self.minimum_wage

    # lat long
    def get_location(self) -> (float, float):
        return (self.position_latitude, self.position_longitude)


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

    def get_hourly_rate(self, speed: float) -> float:
        return self.price / (self.mileage / speed)

    # lat long
    def get_original_location(self) -> (float, float):
        return (self.origin_latitude, self.origin_longitude)

    # lat long
    def get_destination_location(self) -> (float, float):
        return (self.destination_latitude, self.destination_longitude)


class DiscardedNotification:
    def __init__(self, truck: Truck, load: Load) -> None:
        self.timestamp = max(truck.timestamp, load.timestamp)
        self.truck_id = truck.truck_id
        self.load_id = load.load_id


class Notification:
    def __init__(
        self,
        notification_id: int,
        truck: Truck,
        load: Load,
        profit: float,
        distance: float,
        wage: float,
        heuristic_wage: float,
    ) -> None:
        # TODO: Update this value to lastest timestamp?
        self.timestamp = max(truck.timestamp, load.timestamp)
        self.id = notification_id
        self.load = load
        self.truck = truck
        self.price = load.price
        self.estimated_profit = profit
        self.estimated_distance = distance
        self.estimated_wage = wage
        self.heuristic_wage = heuristic_wage
