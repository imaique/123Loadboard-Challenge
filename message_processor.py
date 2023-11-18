from __future__ import annotations
import json
import time


class Notifier:
    def __init__(self) -> None:
        # <truck id,truck object>
        self.trucks = {}

        # <load id,load object>
        self.load = {}

        # <truck id, [notification objects]>
        self.notifications = {}

    def add_truck(self, truck: Truck) -> None:
        self.trucks[truck.truckId] = truck

    def add_load(self, load: Load) -> None:
        self.load[load.loadId] = load

        for truck in self.trucks:
            self

    def matching_equipment(self, truck: Truck, load: Load) -> bool:
        return True

    def matching_length(self, truck: Truck, load: Load) -> bool:
        return True

    def good_profit(self, truck: Truck, load: Load) -> bool:
        return True

    def should_notify(self, truck: Truck, load: Load) -> bool:
        return

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


class Notification:
    def __init__(self, truck: Truck, load: Load) -> None:
        pass


class Truck:
    def __init__(self, message: dict) -> None:
        self.__dict__ = message


class Load:
    def __init__(self, message: dict) -> None:
        self.__dict__ = message


class MessageProcessor:
    def __init__(self) -> None:
        self.notifier = Notifier()

    def add_raw_message(self, message: str):
        json_msg = json.loads(message)
        self.add_message(json_msg)

    # Message Types: Start, End, Load, Truck
    def add_message(self, message: dict) -> None:
        message_type = message["type"]
        print(message["type"])

        if message_type == "Load":
            self.notifier.add_load(Load(message))
        elif message_type == "Truck":
            self.notifier.add_truck(Truck(message))
        elif message_type == "Start":
            self.notifier = Notifier()
        elif message_type == "End":
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
