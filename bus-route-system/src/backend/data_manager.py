class DataManager:
    def __init__(self, data_file='data.json'):
        self.data_file = data_file
        self.data = self.load_data()

    def load_data(self):
        import json
        try:
            with open(self.data_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {"bus_stops": [], "routes": []}
        except json.JSONDecodeError:
            return {"bus_stops": [], "routes": []}

    def save_data(self):
        import json
        with open(self.data_file, 'w') as file:
            json.dump(self.data, file)

    def add_bus_stop(self, bus_stop):
        self.data['bus_stops'].append(bus_stop)
        self.save_data()

    def add_route(self, route):
        self.data['routes'].append(route)
        self.save_data()

    def get_bus_stops(self):
        return self.data['bus_stops']

    def get_routes(self):
        return self.data['routes']