class BusStop:
    def __init__(self, id, name, latitude, longitude):
        self.id = id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

class BusRoute:
    def __init__(self, id, name, stops):
        self.id = id
        self.name = name
        self.stops = stops  # List of BusStop instances

    def add_stop(self, stop):
        self.stops.append(stop)

    def remove_stop(self, stop_id):
        self.stops = [stop for stop in self.stops if stop.id != stop_id]