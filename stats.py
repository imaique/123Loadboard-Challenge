import csv


def dict_to_file(filename: str, dictionary_list: dict):
    if len(dictionary_list) == 0:
        print(f"empty dictionary list for {filename}")
        return
    keys = dictionary_list[0].keys()

    with open(filename, "w", newline="") as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(dictionary_list)


class StatCollector:
    def __init__(self) -> None:
        self.trucks = []
        self.notifications = []
        self.loads = []

    def to_csv(self):
        print("Called to csv!")
        dict_to_file("trucks.csv", self.trucks)
        dict_to_file("notifications.csv", self.notifications)
        dict_to_file("loads.csv", self.loads)

    def add_truck(self, truck: dict) -> None:
        self.trucks.append(truck)

    def add_load(self, load: dict) -> None:
        self.trucks.append(load)

    def add_notification(self, notification: dict) -> None:
        print(notification)
        self.notifications.append(notification)
