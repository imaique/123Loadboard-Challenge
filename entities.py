class Truck:
    def __init__(self, truck_dict: dict) -> None:
        self.seq = truck_dict["seq"]
        self.type = truck_dict["type"]
        self.timestamp = truck_dict["timestamp"]
        self.truck_id = truck_dict["truckId"]
        self.position_latitude = truck_dict["positionLatitude"]
        self.position_longitude = truck_dict["positionLongitude"]
        self.equip_type = truck_dict["equipType"]
        self.next_trip_length_preference = truck_dict["nextTripLengthPreference"]


class Load:
    def __init__(self, load_dict: dict) -> None:
        self.seq = load_dict["seq"]
        self.type = load_dict["type"]
        self.timestamp = load_dict["timestamp"]
        self.load_id = load_dict["loadId"]
        self.origin_latitude = load_dict["originLatitude"]
        self.origin_longitude = load_dict["originLongitude"]
        self.destination_latitude = load_dict["destinationLatitude"]
        self.destination_longitude = load_dict["destinationLongitude"]
        self.equipment_type = load_dict["equipmentType"]
        self.price = load_dict["price"]
        self.mileage = load_dict["mileage"]
