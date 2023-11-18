from __future__ import annotations
from typing import Dict, List
import json
from entities import Truck, Load, Notification, DATE_FORMAT
from stats import StatCollector
from forwarder import Forwarder
from datetime import datetime, timedelta


class Notifier:
    def __init__(self, collector: StatCollector) -> None:
        # <truck id,truck object>
        self.trucks: Dict[int, Truck] = {}

        # <load id,load object>
        self.load: Dict[int, Load] = {}

        # <truck id, [notification objects]>
        self.notifications: Dict[int, List[Notification]] = {}

        self.collector = collector

    def add_truck(self, truck: Truck) -> None:
        self.trucks[truck.truck_id] = truck

        for load_id, load in self.load.items():
            self.notify_if_good(truck, load)

    def add_load(self, load: Load) -> None:
        self.load[load.load_id] = load

        for truck_id, truck in self.trucks.items():
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
        del dictionary["load"]
        del dictionary["truck"]
        self.collector.add_notification(dictionary)

    def notify_if_good(self, truck: Truck, load: Load) -> bool:
        truck_id = truck.truck_id
        # NON-NEGOTIABLE
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
        CURRENT_TIMESTAMP = max(truck.timestamp, load.timestamp)
        # do not notify unless this new load is better than any of the ones in my recent notifications
        if truck_id in self.notifications:
            MAX_NOTIFICATIONS = 3
            TIME_THRESHOLD = 30  # minutes

            START_TIMESTAMP = CURRENT_TIMESTAMP - timedelta(minutes=TIME_THRESHOLD)
            latest_notifications: List[Notification] = []
            for notification in reversed(self.notifications[truck.truck_id]):
                if notification.timestamp >= START_TIMESTAMP:
                    latest_notifications.append(notification)
                    if len(latest_notifications) == MAX_NOTIFICATIONS:
                        break
                else:
                    break
            # If the max number of notifications is reached, only notify it's better than one of the ones suggested
            if len(latest_notifications) == MAX_NOTIFICATIONS:
                # Recalculate wage per hour if truck moved since the notification
                bad_load = True
                for prev_notification in latest_notifications:
                    prev_hourly = prev_notification.estimated_wage
                    if not truck.same_location(prev_notification.truck):
                        prev_hourly = truck.get_hourly_from_load(prev_notification.load)

                    if wage > prev_hourly:
                        bad_load = False
                        break

                if bad_load:
                    return False

        notification = Notification(truck, load, profit, distance, wage)
        self.send_notification(notification)
        return True

    def generate_summary(self) -> None:
        with open("summary.txt", "w") as file:
            file.write(f"Processed {len(self.trucks)} trucks\n")
            file.write(f"Processed {len(self.load)} loads\n")
            file.close()

    def generate_list(self) -> None:
        """[
        "truck": truck information
        "notifications": [notifications]
        ]
        """
        # Generate a json file with

        pass
        # file = open("notification_list.csv")

    def get_distance(
        self, original_lat, original_long, destination_lat, destination_long
    ) -> float:
        return (
            (original_lat - destination_lat) ** 2
            + (original_long - destination_long) ** 2
        ) ** 0.5

    def truck_load_distance(self, truck: Truck, load: Load) -> float:
        truck_lat = truck.position_latitude
        truck_long = truck.position_longitude
        load_lat = load.origin_latitude
        load_long = load.origin_longitude
        dist = ((truck_lat - load_lat) ** 2 + (truck_long - load_long) ** 2) ** 0.5
        return self.get_distance(
            truck.position_latitude,
            truck.position_longitude,
            load.destination_latitude,
            load.destination_longitude,
        )

    def cost_to_pickup(self, truck: Truck, load: Load) -> float:
        return self.truck_load_distance(truck, load) * 1.38

    def get_profit(self, truck: Truck, load: Load) -> float:
        revenue = load.price
        cost = self.cost_to_pickup(truck, load) + 1.38 * load.mileage
        return revenue - cost


class MessageProcessor:
    def __init__(self) -> None:
        self.collector = StatCollector()
        self.forwarder = Forwarder()
        self.notifier = Notifier(self.collector)

    def add_raw_message(self, message: str):
        json_msg = json.loads(message)
        self.add_message(json_msg)

    # Message Types: Start, End, Load, Truck
    def add_message(self, message: dict) -> None:
        message_type = message["type"]

        # call collector last as it might mutate the dict
        if message_type == "Load":
            self.notifier.add_load(Load(message))
            self.forwarder.add_message(message)
            self.collector.add_load(message)
        elif message_type == "Truck":
            self.notifier.add_truck(Truck(message))
            self.forwarder.add_message(message)
            self.collector.add_truck(message)
        elif message_type == "Start":
            self.notifier = Notifier(self.collector)
            self.collector = StatCollector()
        elif message_type == "End":
            self.collector.to_csv()
            self.notifier.generate_summary()


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
