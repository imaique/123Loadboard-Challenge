import csv
from datetime import datetime, timedelta
import numpy as np

def update_or_create_npz(file_name, new_data):
    try:
        # Try to load the existing file
        with np.load(file_name) as data:
            # Update the array in the file
            existing_data = data['grid'][()]
    except FileNotFoundError:
        # If the file doesn't exist, create a new one
        existing_data = np.zeros_like(new_data)
    
    updated_data = existing_data + new_data
    np.savez(file_name, grid=updated_data)

def dict_to_file(filename: str, dictionary_list: dict):
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

    def to_csv(self):
        print("Called to csv!")
        dict_to_file("trucks.csv", self.trucks)
        dict_to_file("notifications.csv", self.notifications)
        dict_to_file("loads.csv", self.loads)

    def add_truck(self, truck: dict) -> None:
        self.trucks.append(truck)

    def add_load(self, load: dict) -> None:
        self.loads.append(load)

    def add_notification(self, notification: dict) -> None:
        print(notification)
        self.notifications.append(notification)

    def generate_grid(self) -> None:

            # plt.figure()
            # plt.ion()
            # plt.show()
            # Get the min and max lat and long
            min_lat = min(float(load["originLatitude"]) for load in self.loads)
            max_lat = max([float(load["originLatitude"]) for load in self.loads])
            min_long = min([float(load["originLongitude"]) for load in self.loads])
            max_long = max([float(load["originLongitude"]) for load in self.loads])
            print("min_lat: ", min_lat, "max_lat: ", max_lat, "min_long: ", min_long, "max_long: ", max_long)
            # Create grids for each 20 minute interval
            grid = np.zeros((72, 30, 30))
            

            lat_range = max_lat - min_lat
            long_range = max_long - min_long

            for time in range(72):
                # image_data = plt.imshow(grid[time])
                # Iterate through the loads and increment the grid
                for load in self.loads:
                    dt_object = datetime.fromisoformat(load["timestamp"])

                    start_of_day = dt_object.replace(hour=0, minute=0, second=0, microsecond=0)
                    start_time = start_of_day + timedelta(minutes=time*20)
                    end_time = start_time + timedelta(hours=1)

                    if(start_time <= dt_object <= end_time):
                        load_lat = float(load["originLatitude"])
                        load_long = float(load["originLongitude"])
                        # Get the index of the grid
                        lat_index = int((load_lat - min_lat)/lat_range * 29)
                        long_index = int((load_long - min_long)/long_range * 29)
                        # Increment the grid
                        grid[time][lat_index][long_index] += 1
                start_time_string = start_time.strftime("%H_%M")
                # image_data = plt.imshow(grid[time], cmap='viridis')
                # image_data.set_data(grid[time])
                # plt.savefig(f"grid-{start_time_string}.png")
                print("\nhour",start_time_string, ": \n", grid[time])
            
            update_or_create_npz("load_grid.npz", grid)