import csv
import os
import json


def dict_to_file(filename: str, dictionary_list: dict):
    if not os.path.exists("output"):
        os.makedirs("output")
    if len(dictionary_list) == 0:
        print(f"empty dictionary list for {filename}")
        return
    keys = dictionary_list[0].keys()

    with open(f"output/{filename}", "w", newline="") as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(dictionary_list)


class StatCollector:
    def __init__(self) -> None:
        self.trucks = []
        self.notifications = []
        self.loads = []
        self.messages = []
        self.discarded_notifs = []

    def to_csv(self):
        print("to csv called!")
        dict_to_file("trucks.csv", self.trucks)
        dict_to_file("notifications.csv", self.notifications)
        dict_to_file("loads.csv", self.loads)
        dict_to_file("discarded_notifications.csv", self.discarded_notifs)

        with open(f"output/messages.json", "w", newline="") as output_file:
            json.dump(self.messages, output_file)

    def add_truck(self, truck: dict) -> None:
        self.trucks.append(truck)

    def add_load(self, load: dict) -> None:
        self.loads.append(load)

    def add_notification(self, notification: dict) -> None:
        self.notifications.append(notification)

    def add_message(self, message: dict) -> None:
        self.messages.append(message)

    def add_discarded(self, discarded: dict) -> None:
        self.discarded_notifs.append(discarded)
