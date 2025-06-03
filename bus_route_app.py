import tkinter as tk
from tkinter import messagebox
import openrouteservice
from openrouteservice.distance_matrix import distance_matrix
from itertools import permutations
import json
import os
import folium
import webbrowser
import requests  # Import to make HTTP requests
from tkinter import font  # Import the font module

# OpenRouteService API Key
ORS_API_KEY = '5b3ce3597851110001cf62488e38ca427e3c45fdb98c1948f0f06861'  # Replace with your actual API key
client = openrouteservice.Client(key=ORS_API_KEY)

# Stops with coordinates (lon, lat)
stops = {
    'ISBT': (78.0115, 30.2841),
    'Clock Tower': (78.0410, 30.3256),
    'Prince Chowk': (78.0317, 30.3163),
    'Railway Station': (78.0330, 30.3165),
    'Survey Chowk': (78.0419, 30.3275),
    'Rajpur Road': (78.0806, 30.3552),
    'Pacific Mall': (78.0886, 30.3694),
    'Mussoorie Bus Stand': (78.0596, 30.3442),
    'Balliwala Chowk': (78.0125, 30.3033),
    'Doon Hospital': (78.0421, 30.3247),
    'Dilaram Chowk': (78.0517, 30.3369)
}

stop_names = list(stops.keys())
coords = list(stops.values())

# Load or build distance matrix
def load_or_build_matrix():
    if os.path.exists("cached_matrix.json"):
        try:
            with open("cached_matrix.json", "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "cached_matrix.json is corrupted. Rebuilding.")
            return _build_matrix()  # Rebuild the matrix
    else:
        return _build_matrix()

def _build_matrix():
    """Helper function to build the distance matrix."""
    try:
        matrix = distance_matrix(
            client,
            locations=coords,
            profile='driving-car',
            metrics=['distance'],
            units='km'
        )
        with open("cached_matrix.json", "w") as f:
            json.dump(matrix, f)
        return matrix
    except Exception as e:
        messagebox.showerror("Error", f"Error building distance matrix: {e}")
        return None  # Important: Return None on error

matrix = load_or_build_matrix()
if matrix is None:
    # Handle the error case where the matrix couldn't be loaded or built
    print("Failed to load or build distance matrix. Exiting.")
    exit()

def get_optimal_route(start, end, middle_stops):
    start_idx = stop_names.index(start)
    end_idx = stop_names.index(end)
    mid_indices = [stop_names.index(s) for s in middle_stops]

    best_order, min_dist = None, float('inf')

    for perm in permutations(mid_indices):
        path = [start_idx] + list(perm) + [end_idx]
        dist = sum(matrix['distances'][path[i]][path[i + 1]] for i in range(len(path) - 1))
        if dist < min_dist:
            min_dist = dist
            best_order = path

    if not best_order:
        return [], 0
    return [stop_names[i] for i in best_order], min_dist

def show_map(route_stops):
    m = folium.Map(location=stops[route_stops[0]][::-1], zoom_start=13)

    for stop in route_stops:
        folium.Marker(stops[stop][::-1], tooltip=stop).add_to(m)

    coordinates = [stops[stop] for stop in route_stops]
    try:
        res = client.directions(
            coordinates=coordinates,
            profile='driving-car',
            format='geojson'
        )
        folium.GeoJson(res, name='route').add_to(m)
    except Exception as e:
        print("Routing Error:", e)
        messagebox.showerror("Error", f"Could not fetch road-following route from ORS: {e}")

    map_path = "bus_route_map.html"
    m.save(map_path)
    webbrowser.open(f'file://{os.path.abspath(map_path)}')

def fetch_user_requests(flask_url):
    try:
        resp = requests.get(f"{flask_url}/requests")
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Could not fetch user requests: {e}")
        messagebox.showerror("Error", f"Failed to fetch requests: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        messagebox.showerror("Error", f"Error decoding JSON response: {e}")
        return []

def clear_user_requests(flask_url):
    try:
        resp = requests.post(f"{flask_url}/clear_requests")
        resp.raise_for_status()
        if resp.status_code == 200:
            messagebox.showinfo("Data Cleared", "User request data has been cleared.")
        else:
            messagebox.showerror("Error", f"Failed to clear data. Status code: {resp.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Could not clear user requests: {e}")
        messagebox.showerror("Error", f"Failed to clear data: {e}")

class BusRouteApp:
    def __init__(self, root, flask_url):
        self.root = root
        self.root.title("🛰️ Dehradun Futuristic Bus Planner")
        self.root.geometry("520x520")
        self.root.configure(bg="#0f172a")  # Dark slate background

        self.flask_url = flask_url

        # Fonts
        self.title_font = font.Font(family="Segoe UI", size=18, weight="bold")
        self.label_font = font.Font(family="Segoe UI", size=12)
        self.button_font = font.Font(family="Segoe UI", size=11, weight="bold")

        # Title Label
        self.title_label = tk.Label(
            root,
            text="🛰️ Smart Bus Route Planner",
            font=self.title_font,
            fg="#22d3ee",
            bg="#0f172a",
            pady=10
        )
        self.title_label.pack()

        # Info Label
        self.info_label = tk.Label(
            root,
            text="Visit the web app and select your stop preferences 👇",
            font=self.label_font,
            fg="#cbd5e1",
            bg="#0f172a",
            wraplength=480,
            justify="center"
        )
        self.info_label.pack(pady=(10, 25))

        # Generate Route Button
        self.button = tk.Button(
            root,
            text="⚡ Generate Optimized Route",
            command=self.generate_route,
            font=self.button_font,
            bg="#0ea5e9",
            fg="black",
            activebackground="#0284c7",
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=8,
            cursor="hand2"
        )
        self.button.pack(pady=10, ipadx=10, fill="x", padx=40)

        # Clear Data Button
        self.clear_button = tk.Button(
            root,
            text="🧹 Clear All Requests",
            command=self.clear_data,
            font=self.button_font,
            bg="#ef4444",
            fg="black",
            activebackground="#b91c1c",
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=8,
            cursor="hand2"
        )
        self.clear_button.pack(pady=10, ipadx=10, fill="x", padx=40)

        # Quit Button
        self.quit_button = tk.Button(
            root,
            text="🚪 Exit",
            command=root.destroy,
            font=self.button_font,
            bg="#475569",
            fg="black",
            activebackground="#334155",
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=8,
            cursor="hand2"
        )
        self.quit_button.pack(pady=10, ipadx=10, fill="x", padx=40)

        # Result Label
        self.result_label = tk.Label(
            root,
            text="",
            font=self.label_font,
            fg="#22d3ee",
            bg="#0f172a",
            wraplength=480,
            justify="center"
        )
        self.result_label.pack(pady=20, padx=20)

    def generate_route(self):
        requested = fetch_user_requests(self.flask_url)
        if not requested:
            route = ['ISBT', 'Pacific Mall']
            if matrix and stop_names.index('ISBT') < len(matrix['distances']) and stop_names.index('Pacific Mall') < len(matrix['distances'][stop_names.index('ISBT')]):
                dist = matrix['distances'][stop_names.index('ISBT')][stop_names.index('Pacific Mall')]
            else:
                dist = 0
                messagebox.showerror("Error", "Could not calculate distance.  Check ORS API and network.")
        else:
            route, dist = get_optimal_route('ISBT', 'Pacific Mall', requested)
            if dist is None:
                dist = 0

        if not route:
            messagebox.showerror("Error", "Could not find a valid route.")
            return

        route_text = " ➔ ".join(route)
        stats = f"Total Stops: {len(route)}\nTotal Distance: {dist:.2f} km" if dist else f"Total Stops: {len(route)}\nTotal Distance: N/A"
        self.result_label.config(text=f"🛣️ Optimal Route:\n{route_text}\n\n📏 {stats}")
        show_map(route)

    def clear_data(self):
        clear_user_requests(self.flask_url)


if __name__ == "__main__":
    root = tk.Tk()
    #flask_app_url = "http://gunottammaini.pythonanywhere.com"
    flask_app_url = "http://127.0.0.1:5500"
    app = BusRouteApp(root, flask_app_url)
    root.mainloop()