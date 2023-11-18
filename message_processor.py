from __future__ import annotations
from typing import Dict, List
import json
from entities import Truck, Load
from stats import StatCollector


class Notifier:
    def __init__(self) -> None:
        # <truck id,truck object>
        self.trucks: Dict[int, Truck] = {}

        # <load id,load object>
        self.load: Dict[int, Load] = {}

        # <truck id, [notification objects]>
        self.notifications: Dict[int, List[Notification]] = {}

    def add_truck(self, truck: Truck) -> None:
        self.trucks[truck.truck_id] = truck

    def add_load(self, load: Load) -> None:
        self.load[load.load_id] = load

        for truck in self.trucks:
            if self.valid_load(truck, load) and self.should_notify(truck, load):
                self.send_notification(truck, load)

    def send_notification(self, truck: Truck, load: Load) -> None:
        notification = Notification(truck, load)
        truck_id = truck.truck_id
        if truck_id not in self.notifications:
            self.notifications[truck_id] = []

        self.notifications[truck_id].append(notification)

    def matching_equipment(self, truck: Truck, load: Load) -> bool:
        if truck.equip_type == load.equipment_type:
            return True
        return False

    def matching_length(self, truck: Truck, load: Load) -> bool:
        if truck.next_trip_length_preference == "Long" and load.mileage >= 200:
            return True
        elif truck.next_trip_length_preference == "Short" and load.mileage < 200:
            return True
        return False

    def positive_profit(self, truck: Truck, load: Load) -> bool:
        if self.get_profit(truck, load) <= 0:
            return False
        return True

    # If this trucker recently received many notifications, this load should be better than one of them
    def better_load_than_previous_loads(self, truck: Truck, load: Load) -> bool:
        better = True
        load_heuristic = self.get_heuristic(truck, load)
        for notification in self.notifications[truck.truck_id]:
            prev_load = notification.load

        return True

    def valid_load(self, truck: Truck, load: Load) -> bool:
        return (
            self.matching_equipment(truck, load)
            and self.matching_length(truck, load)
            and self.positive_profit(truck, load)
            and self.better_load_than_previous_loads(truck, load)
        )

    """
    profit
    final distance from origin (reverse deadhead)
    deadhead
    
    """

    def get_heuristic(self, truck: Truck, load: Load) -> int:
        # profit = get_profit(truck, load)

        return 30

    def should_notify(self, truck: Truck, load: Load) -> bool:
        HEURISTIC_THRESHOLD = 30
        heuristic_score = self.get_heuristic(truck, load)
        return heuristic_score >= HEURISTIC_THRESHOLD

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


class Notification:
    def __init__(self, truck: Truck, load: Load) -> None:
        # TODO: Update this value to lastest timestamp?
        self.timestamp = max(truck.timestamp, load.timestamp)
        self.load = load
        self.truck = truck


class MessageProcessor:
    def __init__(self) -> None:
        self.notifier = Notifier()
        self.collector = StatCollector()

    def add_raw_message(self, message: str):
        json_msg = json.loads(message)
        self.add_message(json_msg)

    # Message Types: Start, End, Load, Truck
    def add_message(self, message: dict) -> None:
        message_type = message["type"]
        if message_type == "Load":
            collector.add_load(message)
            self.notifier.add_load(Load(message))
        elif message_type == "Truck":
            self.collector.add_truck(message)
            self.notifier.add_truck(Truck(message))
        elif message_type == "Start":
            self.notifier = Notifier()
            self.collector = StatCollector()
        elif message_type == "End":
            collector.to_csv()
            collector.generate_grid()
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
