from __future__ import annotations
from typing import Dict, List
import json
from datetime import timedelta, datetime

from entities import Truck, Load, Notification, DATE_FORMAT
from stats import StatCollector
from forwarder import Forwarder
from common import get_miles
from filters import (
    MAX_DESIRED_NOTIFICATIONS,
    TIME_THRESHOLD,
    FAR_FROM_HOME_PENALTY_RATIO_SHORT,
    FAR_FROM_HOME_PENALTY_RATIO_LONG,
    NEARBY_RANGE,
    DENSITY_RATIO,
    HIGH_PAYING_LOADS_RATIO,
)


class Notifier:
    def __init__(self, collector: StatCollector, forwarder: Forwarder) -> None:
        # <truck id,truck object>
        self.trucks: Dict[int, Truck] = {}
        # <truck id, home (lat, long)>
        self.homes: Dict[int, (float, float)] = {}

        # <load id,load object>
        self.loads: Dict[int, Load] = {}

        # <truck id, [notification objects]>
        self.notifications: Dict[int, List[Notification]] = {}

        self.collector = collector
        self.forwarder = forwarder

    def add_truck(self, truck: Truck) -> None:
        truck_id = truck.truck_id
        self.trucks[truck.truck_id] = truck
        self.homes[truck_id] = truck.get_location()

        for load in self.loads.values():
            self.notify_if_good(truck, load)

    def add_load(self, load: Load) -> None:
        self.loads[load.load_id] = load

        for truck in self.trucks.values():
            self.notify_if_good(truck, load)

    def send_notification(self, notification: Notification) -> None:
        truck_id = notification.truck.truck_id
        if truck_id not in self.notifications:
            self.notifications[truck_id] = []
        self.notifications[truck_id].append(notification)

        dictionary = vars(notification).copy()
        dictionary["truck_id"] = truck_id
        dictionary["load_id"] = notification.load.load_id
        dictionary["timestamp"] = dictionary["timestamp"].strftime(DATE_FORMAT)
        dictionary["type"] = "Notification"
        del dictionary["load"]
        del dictionary["truck"]
        self.collector.add_notification(dictionary)
        self.forwarder.add_message(dictionary)

    def get_recent_notifications(
        self, truck_id: int, current_timestamp: datetime
    ) -> List[Notification]:
        start_timestamp = current_timestamp - timedelta(minutes=TIME_THRESHOLD)
        latest_notifications: List[Notification] = []
        for notification in reversed(self.notifications[truck_id]):
            if notification.timestamp >= start_timestamp:
                latest_notifications.append(notification)
            else:
                break
        return latest_notifications

    def notify_if_good(self, truck: Truck, load: Load) -> bool:
        truck_id = truck.truck_id
        # NON-NEGOTIABLES
        if not truck.matching_equipment(load):
            return False

        distance = truck.pickup_distance(load) + load.mileage
        if not truck.matching_distance(distance):
            return False

        profit = truck.calculate_profit(load.price, distance)
        if profit <= 0:
            return False

        wage = truck.get_hourly_wage(profit, distance)
        if not truck.above_desired_wage(wage):
            return False

        heuristic_wage = self.get_heuristic_wage(truck, load, profit, distance)

        # do not notify unless this new load is better than any of the ones in my recent notifications
        if truck_id in self.notifications:
            current_timestamp = max(truck.timestamp, load.timestamp)
            latest_notifications = self.get_recent_notifications(
                truck_id, current_timestamp
            )

            # If the max number of notifications is reached, only notify it's better than one of the ones suggested
            if len(latest_notifications) >= MAX_DESIRED_NOTIFICATIONS:
                better_count = 0
                for prev_notification in latest_notifications:
                    prev_heuristic_wage = prev_notification.heuristic_wage

                    # Recalculate wage per hour if truck moved since the notification
                    if not truck.same_location(prev_notification.truck):
                        prev_heuristic_wage = self.get_heuristic_wage(
                            truck,
                            prev_notification.load,
                            prev_notification.estimated_profit,
                            prev_notification.estimated_distance,
                        )

                    if heuristic_wage > prev_heuristic_wage:
                        better_count += 1

                if len(latest_notifications) - better_count > MAX_DESIRED_NOTIFICATIONS:
                    return False

        notification = Notification(truck, load, profit, distance, wage, heuristic_wage)
        self.send_notification(notification)
        return True

    def get_heuristic_wage(
        self, truck: Truck, load: Load, profit: float, distance: float
    ) -> float:
        home_location = self.homes[truck.truck_id]
        job_time = truck.time_to_travel(distance)

        heuristic_profit = profit
        heuristic_time = job_time

        if DENSITY_RATIO > 0 or HIGH_PAYING_LOADS_RATIO > 0:
            profit_sum = 0
            job_time_sum = 0
            nearby_count = 0
            truck_location = truck.get_location()
            for nearby_load in self.loads.values():
                distance = get_miles(
                    nearby_load.get_original_location(), truck_location
                )
                if distance <= NEARBY_RANGE:
                    nearby_count += 1
                    profit_sum += truck.calculate_profit(nearby_load.price, distance)
                    job_time_sum += truck.time_to_travel(nearby_load.mileage)

            if DENSITY_RATIO > 0:
                heuristic_profit += DENSITY_RATIO * profit_sum
                heuristic_time += DENSITY_RATIO * job_time_sum

            if nearby_count > 0 and HIGH_PAYING_LOADS_RATIO > 0:
                avg_profit = profit_sum / nearby_count
                avg_time_taken = job_time_sum / nearby_count

                heuristic_profit += HIGH_PAYING_LOADS_RATIO * avg_profit
                heuristic_time += HIGH_PAYING_LOADS_RATIO * avg_time_taken

        FAR_FROM_HOME_RATIO = (
            FAR_FROM_HOME_PENALTY_RATIO_LONG
            if truck.desires_long()
            else FAR_FROM_HOME_PENALTY_RATIO_SHORT
        )

        if FAR_FROM_HOME_RATIO > 0:
            final_distance_from_home = get_miles(
                home_location, load.get_destination_location()
            )
            cost_to_home = truck.travel_cost(final_distance_from_home)
            time_to_home = truck.time_to_travel(final_distance_from_home)
            heuristic_profit -= FAR_FROM_HOME_RATIO * cost_to_home
            heuristic_time += FAR_FROM_HOME_RATIO * time_to_home

        return heuristic_profit / heuristic_time


class MessageProcessor:
    def __init__(self) -> None:
        self.collector = StatCollector()
        self.forwarder = Forwarder()
        self.notifier = Notifier(self.collector, self.forwarder)

    def add_raw_message(self, message: str):
        json_msg = json.loads(message)
        self.add_message(json_msg)

    # Message Types: Start, End, Load, Truck
    def add_message(self, message: dict) -> None:
        message_type = message["type"]
        self.forwarder.add_message(message)

        print(message["seq"])
        # call collector last as it might mutate the dict
        if message_type == "Load":
            self.notifier.add_load(Load(message))
            self.collector.add_load(message)
        elif message_type == "Truck":
            self.notifier.add_truck(Truck(message))
            self.collector.add_truck(message)
        elif message_type == "Start":
            self.collector = StatCollector()
            self.notifier = Notifier(self.collector, self.forwarder)
        elif message_type == "End":
            self.collector.to_csv()


def run_test_messages():
    messages = [
        {"seq": 0, "type": "Start", "timestamp": "2023-11-17T03:00:00.00123-05:00"},
        {
            "seq": 1,
            "type": "Truck",
            "timestamp": "2023-11-17T08:06:23.0406772-05:00",
            "truckId": 114,
            "positionLatitude": 41.425058,
            "positionLongitude": -87.33366,
            "equipType": "Van",
            "nextTripLengthPreference": "Long",
        },
        {
            "seq": 2,
            "type": "Truck",
            "timestamp": "2023-11-17T09:10:23.2531001-05:00",
            "truckId": 346,
            "positionLatitude": 39.195726,
            "positionLongitude": -84.665296,
            "equipType": "Van",
            "nextTripLengthPreference": "Long",
        },
        {
            "seq": 3,
            "type": "Load",
            "timestamp": "2023-11-17T11:31:35.0481646-05:00",
            "loadId": 101,
            "originLatitude": 39.531354,
            "originLongitude": -87.440632,
            "destinationLatitude": 37.639,
            "destinationLongitude": -121.0052,
            "equipmentType": "Van",
            "price": 3150.0,
            "mileage": 2166.0,
        },
        {
            "seq": 4,
            "type": "Load",
            "timestamp": "2023-11-17T11:55:11.2311956-05:00",
            "loadId": 201,
            "originLatitude": 41.621465,
            "originLongitude": -83.605482,
            "destinationLatitude": 37.639,
            "destinationLongitude": -121.0052,
            "equipmentType": "Van",
            "price": 3300.0,
            "mileage": 2334.0,
        },
        {
            "seq": 5,
            "type": "Truck",
            "timestamp": "2023-11-17T16:40:32.7200171-05:00",
            "truckId": 114,
            "positionLatitude": 40.32124710083008,
            "positionLongitude": -86.74946594238281,
            "equipType": "Van",
            "nextTripLengthPreference": "Long",
        },
        {"seq": 6, "type": "End", "timestamp": "2023-11-17T22:52:21.1572422-05:00"},
    ]
    processor = MessageProcessor()
    for message in messages:
        processor.add_message(message)


if __name__ == "__main__":
    run_test_messages()
