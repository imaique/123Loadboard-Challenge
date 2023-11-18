from entities import Truck, Load
import csv


class StatCollector:
    def __init__(self) -> None:
        self.trucks = []

    def to_csv(self):
        keys = self.trucks[0].keys()

        with open("trucks.csv", "w", newline="") as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.trucks)

    def add_truck(self, truck: dict) -> None:
        self.trucks.append(truck)
